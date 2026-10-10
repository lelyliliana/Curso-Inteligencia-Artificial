"""Modelo causal pequeño y referencia de bigramas para continuación condicional."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import torch
from torch import nn
import torch.nn.functional as F

UNIDAD = Path(__file__).resolve().parents[1]
ESPECIALES = ["<pad>", "<bos>", "<eos>", "<unk>"]
PAD, BOS, EOS, UNK = range(4)
ARQUITECTURA = {"dimension": 32, "cabezas": 2, "oculta": 64, "contexto": 24,
                "bloques": 1, "dropout": 0.0, "normalizacion": "previa", "activacion": "gelu"}
ENTRENAMIENTO = {"semilla": 2501, "epocas": 300, "evaluar_cada": 10,
                 "lr": 0.003, "clip": 1.0, "suavizado_bigramas": 0.1}
PREPARACION = {"tokenizador": "espacios_v1", "especiales": ESPECIALES,
               "relleno": "derecha", "objetivos": "continuacion_y_eos", "contexto": 24}


def configurar():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def guardar_json(ruta, valor):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(valor, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def tokens(texto):
    resultado = texto.split()
    if not resultado or set(resultado) & set(ESPECIALES):
        raise ValueError("Texto vacío o token especial escrito como contenido.")
    return resultado


def leer(ruta):
    filas = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if not isinstance(filas, list) or not filas:
        raise ValueError("Corpus vacío o formato inválido.")
    ids = set()
    for r in filas:
        if set(r) != {"id", "familia", "formato", "prefijo", "continuacion"}:
            raise ValueError("Esquema de documento inválido.")
        if r["id"] in ids or not r["familia"] or r["formato"] not in ("breve", "detallado"):
            raise ValueError("ID repetido, familia o formato inválidos.")
        ids.add(r["id"])
        tokens(r["prefijo"])
        tokens(r["continuacion"])
    return filas


def vocabulario(filas):
    palabras = {t for r in filas for campo in ("prefijo", "continuacion") for t in tokens(r[campo])}
    return ESPECIALES + sorted(palabras)


def codificar(texto, vocab):
    indice = {t: i for i, t in enumerate(vocab)}
    return [indice.get(t, UNK) for t in tokens(texto)]


def preparar(filas, vocab):
    if not filas:
        raise ValueError("No hay documentos para preparar.")
    secuencias, inicios = [], []
    for r in filas:
        prefijo = [BOS] + codificar(r["prefijo"], vocab)
        secuencia = prefijo + codificar(r["continuacion"], vocab) + [EOS]
        if len(secuencia) - 1 > ARQUITECTURA["contexto"]:
            raise ValueError("El documento excede el contexto; no se recorta.")
        secuencias.append(secuencia)
        inicios.append(len(prefijo) - 1)
    longitud = max(len(s) - 1 for s in secuencias)
    x = torch.full((len(filas), longitud), PAD, dtype=torch.long)
    y = torch.full_like(x, PAD)
    mascara = torch.zeros_like(x, dtype=torch.bool)
    for i, (s, inicio) in enumerate(zip(secuencias, inicios)):
        x[i, :len(s)-1] = torch.tensor(s[:-1])
        y[i, :len(s)-1] = torch.tensor(s[1:])
        mascara[i, inicio:len(s)-1] = True
    return x, y, mascara


class TransformerPequeno(nn.Module):
    def __init__(self, n_tokens):
        super().__init__()
        d, h = ARQUITECTURA["dimension"], ARQUITECTURA["oculta"]
        self.token = nn.Embedding(n_tokens, d, padding_idx=PAD)
        self.posicion = nn.Embedding(ARQUITECTURA["contexto"], d)
        self.norm1 = nn.LayerNorm(d)
        self.qkv = nn.Linear(d, 3*d)
        self.proyeccion = nn.Linear(d, d)
        self.norm2 = nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, h), nn.GELU(), nn.Linear(h, d))
        self.norm_final = nn.LayerNorm(d)
        self.salida = nn.Linear(d, n_tokens)

    def forward(self, ids, devolver_atencion=False):
        if ids.ndim != 2 or not 0 < ids.shape[1] <= ARQUITECTURA["contexto"]:
            raise ValueError("Se esperan lotes B×T dentro del contexto.")
        if (ids.dtype != torch.long or not ids.shape[0] or (ids[:, 0] != BOS).any()
                or (ids < 0).any() or (ids >= self.token.num_embeddings).any()
                or ((ids[:, :-1] == PAD) & (ids[:, 1:] != PAD)).any()):
            raise ValueError("IDs inválidos: se exige BOS inicial y PAD solo a la derecha.")
        b, t = ids.shape
        d, h = ARQUITECTURA["dimension"], ARQUITECTURA["cabezas"]
        x = self.token(ids) + self.posicion(torch.arange(t, device=ids.device))[None]
        z = self.norm1(x)
        q, k, v = self.qkv(z).reshape(b, t, 3, h, d//h).permute(2, 0, 3, 1, 4).unbind(0)
        puntuaciones = q @ k.transpose(-2, -1) / math.sqrt(d//h)
        futuro = torch.triu(torch.ones(t, t, dtype=torch.bool, device=ids.device), diagonal=1)
        prohibido = futuro[None, None] | ids.eq(PAD)[:, None, None, :]
        pesos = torch.softmax(puntuaciones.masked_fill(prohibido, -torch.inf), dim=-1)
        contexto = (pesos @ v).transpose(1, 2).contiguous().reshape(b, t, d)
        x = x + self.proyeccion(contexto)
        x = x + self.ff(self.norm2(x))
        logits = self.salida(self.norm_final(x))
        return (logits, pesos) if devolver_atencion else logits


class Bigramas(nn.Module):
    def __init__(self, tabla):
        super().__init__()
        self.register_buffer("tabla", tabla.detach().clone().float())

    def forward(self, ids):
        return self.tabla[ids]


def ajustar_bigramas(x, y, mascara, n_tokens):
    conteos = torch.full((n_tokens, n_tokens), ENTRENAMIENTO["suavizado_bigramas"], dtype=torch.float64)
    for anterior, siguiente in zip(x[mascara].tolist(), y[mascara].tolist()):
        conteos[anterior, siguiente] += 1
    return Bigramas((conteos / conteos.sum(dim=1, keepdim=True)).log())


def perdida(logits, y, mascara):
    if mascara.shape != y.shape or not mascara.any():
        raise ValueError("Máscara de objetivos vacía o incompatible.")
    return F.cross_entropy(logits[mascara], y[mascara])


def metricas(logits, y, mascara):
    ce = float(perdida(logits, y, mascara))
    return {"n_tokens": int(mascara.sum()), "ce": ce, "perplejidad": math.exp(ce),
            "exactitud_token": float((logits.argmax(-1)[mascara] == y[mascara]).float().mean())}


def probabilidades(logits, temperatura):
    if not math.isfinite(temperatura) or temperatura <= 0:
        raise ValueError("La temperatura debe ser finita y positiva.")
    if logits.ndim != 1 or not torch.isfinite(logits).all():
        raise ValueError("Logits de generación inválidos.")
    # float64 y resta previa evitan overflow con temperaturas pequeñas.
    z = logits.double()
    z = (z - z.max()) / temperatura
    return torch.softmax(z, dim=-1)


@torch.inference_mode()
def generar(modelo, vocab, prefijo, metodo="codicioso", temperatura=1.0, semilla=2502, max_nuevos=12):
    if metodo not in ("codicioso", "muestreo") or not isinstance(max_nuevos, int) or max_nuevos < 1:
        raise ValueError("Método o límite de generación inválidos.")
    if not math.isfinite(temperatura) or temperatura <= 0:
        raise ValueError("La temperatura debe ser finita y positiva.")
    historia = [BOS] + codificar(prefijo, vocab)
    if len(historia) > ARQUITECTURA["contexto"]:
        raise ValueError("Prefijo mayor que el contexto.")
    rng = torch.Generator(device="cpu").manual_seed(semilla)
    modelo.eval()
    salida, motivo = [], "max_nuevos"
    for _ in range(max_nuevos):
        if len(historia) > ARQUITECTURA["contexto"]:
            motivo = "contexto"
            break
        logits = modelo(torch.tensor([historia]))[0, -1]
        elegido = int(logits.argmax()) if metodo == "codicioso" else int(torch.multinomial(probabilidades(logits, temperatura), 1, generator=rng))
        historia.append(elegido)
        if elegido == EOS:
            motivo = "eos"
            break
        salida.append(vocab[elegido])
        if elegido in (PAD, BOS):
            motivo = "especial_invalido"
            break
    return {"prefijo": prefijo, "tokens": salida, "texto": " ".join(salida), "motivo": motivo,
            "metodo": metodo, "temperatura": temperatura, "semilla": semilla,
            "desconocidos_prefijo": sum(i == UNK for i in codificar(prefijo, vocab))}


@torch.inference_mode()
def evaluar(modelo, vocab, filas, con_generacion=True):
    modelo.eval()
    x, y, mascara = preparar(filas, vocab)
    logits = modelo(x)
    resultado = {"n_documentos": len(filas), "n_familias": len({r["familia"] for r in filas}),
                 **metricas(logits, y, mascara)}
    if con_generacion:
        casos = []
        for i, r in enumerate(filas):
            g = generar(modelo, vocab, r["prefijo"])
            errores = [{"esperado": vocab[int(y[i, t])], "predicho": vocab[int(logits[i, t].argmax())]}
                       for t in torch.where(mascara[i])[0] if logits[i, t].argmax() != y[i, t]]
            casos.append({"id": r["id"], "esperado": r["continuacion"], "generacion": g,
                          "exacta": g["texto"] == r["continuacion"] and g["motivo"] == "eos",
                          "errores_teacher_forcing": errores})
        resultado["casos"] = casos
        resultado["n_exactas"] = sum(c["exacta"] for c in casos)
        resultado["exactitud_secuencia"] = resultado["n_exactas"] / len(casos)
    return resultado


def copiar_estado(modelo):
    return {k: v.detach().clone() for k, v in modelo.state_dict().items()}


def entrenar(vocab, train, val, epocas=ENTRENAMIENTO["epocas"]):
    configurar()
    torch.manual_seed(ENTRENAMIENTO["semilla"])
    modelo = TransformerPequeno(len(vocab))
    opt = torch.optim.Adam(modelo.parameters(), lr=ENTRENAMIENTO["lr"])
    x, y, mascara = preparar(train, vocab)
    mejor_ce, mejor_epoca, mejor, curva = math.inf, None, None, []
    for epoca in range(epocas + 1):
        if epoca:
            modelo.train()
            opt.zero_grad(set_to_none=True)
            loss = perdida(modelo(x), y, mascara)
            loss.backward()
            nn.utils.clip_grad_norm_(modelo.parameters(), ENTRENAMIENTO["clip"])
            opt.step()
        if epoca % ENTRENAMIENTO["evaluar_cada"] == 0:
            a, b = evaluar(modelo, vocab, train, False), evaluar(modelo, vocab, val, False)
            curva.append({"epoca": epoca, "ce_train": a["ce"], "ce_val": b["ce"]})
            if b["ce"] < mejor_ce:
                mejor_ce, mejor_epoca, mejor = b["ce"], epoca, copiar_estado(modelo)
    modelo.load_state_dict(mejor)
    modelo.eval()
    return modelo, {"epoca_elegida": mejor_epoca, "epocas_totales": epocas, "curva": curva,
                    "n_parametros": sum(p.numel() for p in modelo.parameters())}


def empaquetar(modelo, tipo, vocab, metadatos):
    return {"formato": "generador-causal-v1", "tipo": tipo, "preparacion": deepcopy(PREPARACION),
            "arquitectura": deepcopy(ARQUITECTURA) if tipo == "transformer" else {"orden": 1, "suavizado": 0.1},
            "vocabulario": vocab, "estado": {k: v.tolist() for k, v in modelo.state_dict().items()},
            "metadatos": metadatos}


def restaurar(contenido):
    if contenido.get("formato") != "generador-causal-v1" or contenido.get("preparacion") != PREPARACION:
        raise ValueError("Formato o preparación incompatibles.")
    vocab = contenido["vocabulario"]
    if (vocab[:4] != ESPECIALES or len(set(vocab)) != len(vocab)
            or vocab[4:] != sorted(vocab[4:]) or any(not t or len(t.split()) != 1 for t in vocab)):
        raise ValueError("Vocabulario incompatible.")
    with torch.random.fork_rng():
        torch.manual_seed(0)
        if contenido["tipo"] == "transformer" and contenido["arquitectura"] == ARQUITECTURA:
            modelo = TransformerPequeno(len(vocab))
        elif contenido["tipo"] == "bigramas" and contenido["arquitectura"] == {"orden": 1, "suavizado": 0.1}:
            modelo = Bigramas(torch.zeros(len(vocab), len(vocab)))
        else:
            raise ValueError("Tipo o arquitectura incompatibles.")
    valores = {k: torch.tensor(v, dtype=torch.float32) for k, v in contenido["estado"].items()}
    esperado = modelo.state_dict()
    if (valores.keys() != esperado.keys() or any(valores[k].shape != esperado[k].shape
            or not torch.isfinite(valores[k]).all() for k in valores)):
        raise ValueError("Parámetros ausentes, no finitos o con forma incompatible.")
    modelo.load_state_dict(valores, strict=True)
    if isinstance(modelo, Bigramas) and not torch.allclose(modelo.tabla.exp().sum(-1), torch.ones(len(vocab)), atol=1e-6):
        raise ValueError("Probabilidades de bigramas no normalizadas.")
    modelo.eval()
    return modelo, vocab


def cargar(ruta):
    configurar()
    return restaurar(json.loads(Path(ruta).read_text(encoding="utf-8")))


def huella_logits(logits):
    return hashlib.sha256(logits.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def seleccionar(candidatos):
    return min(("bigramas", "transformer"), key=lambda n: candidatos[n]["validacion"]["ce"])


def diagnosticar(modelo, vocab, val):
    prefijos = [val[0]["prefijo"], val[1]["prefijo"]]
    prefijos += ["tema oceano zona norte nivel bajo formato breve salida", "tema agua zona"]
    return [generar(modelo, vocab, p, metodo=m, temperatura=t)
            for p in prefijos for m, t in (("codicioso", 1.0), ("muestreo", .7), ("muestreo", 1.3))]


def desarrollar(datos=UNIDAD / "datos"):
    configurar()
    datos = Path(datos)
    train, val = leer(datos / "entrenamiento.json"), leer(datos / "validacion.json")
    if {r["familia"] for r in train} & {r["familia"] for r in val}:
        raise ValueError("Familias compartidas entre entrenamiento y validación.")
    vocab = vocabulario(train)
    base = ajustar_bigramas(*preparar(train, vocab), len(vocab))
    modelo, historia = entrenar(vocab, train, val)
    modelos = {"bigramas": base, "transformer": modelo}
    resultados = {n: {"entrenamiento": evaluar(m, vocab, train), "validacion": evaluar(m, vocab, val)}
                  for n, m in modelos.items()}
    elegido = seleccionar(resultados)
    fuentes = {p: huella(datos / f"{p}.json") for p in ("entrenamiento", "validacion")}
    meta = {"fuentes": fuentes, "entrenamiento": ENTRENAMIENTO, "epoca_transformer": historia["epoca_elegida"],
            "familias_desarrollo": sorted({r["familia"] for r in train + val})}
    estado = empaquetar(modelos[elegido], elegido, vocab, meta)
    with torch.inference_mode():
        referencia_logits = huella_logits(modelos[elegido](preparar(val, vocab)[0]))
    informe = {"logits_validacion_sha256": referencia_logits, "seleccionado": elegido, "vocabulario": vocab, "fuentes": fuentes,
               "entrenamiento_transformer": historia, "candidatos": resultados,
               "diagnosticos": diagnosticar(modelos[elegido], vocab, val), "prueba": None}
    return estado, informe


def exportar(estado, informe, salida, datos=UNIDAD / "datos"):
    salida = Path(salida)
    guardar_json(salida / "modelo.json", estado)
    nuevo, vocab = cargar(salida / "modelo.json")
    val = leer(Path(datos) / "validacion.json")
    x, _, _ = preparar(val, vocab)
    with torch.inference_mode():
        coinciden_logits = huella_logits(nuevo(x)) == informe["logits_validacion_sha256"]
    iguales = evaluar(nuevo, vocab, val) == informe["candidatos"][estado["tipo"]]["validacion"]
    if not coinciden_logits or not iguales or diagnosticar(nuevo, vocab, val) != informe["diagnosticos"]:
        raise RuntimeError("Recarga distinta de la evaluación guardada.")
    guardar_json(salida / "informe.json", informe)
    guardar_json(salida / "recarga.json", {"logits_iguales_por_sha256": coinciden_logits, "evaluacion_y_generacion_iguales": iguales,
                                           "modelo_sha256": huella(salida / "modelo.json")})


def cerrar(ruta_modelo, datos=UNIDAD / "datos"):
    modelo, vocab = cargar(ruta_modelo)
    ruta = Path(datos) / "prueba.json"
    filas = leer(ruta)
    contenido = json.loads(Path(ruta_modelo).read_text(encoding="utf-8"))
    if {r["familia"] for r in filas} & set(contenido["metadatos"]["familias_desarrollo"]):
        raise ValueError("Familias de prueba ya usadas en desarrollo.")
    return {"modelo_sha256": huella(ruta_modelo), "prueba_sha256": huella(ruta),
            "evaluacion": evaluar(modelo, vocab, filas)}

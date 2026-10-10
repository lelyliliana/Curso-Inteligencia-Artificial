"""Clasificación de trazos PNG con separación por escena y una CNN pequeña."""
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import sys

import numpy as np
import PIL
from PIL import Image
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

UNIDAD = Path(__file__).resolve().parents[1]
_rutas = sys.path.copy()
try:
    sys.path.insert(0, str(UNIDAD.parent/"unidad20-pytorch/ejemplos"))
    from pytorch_curso import copiar_estado, serializar
finally:
    sys.path[:] = _rutas

CLASES = ["horizontal", "vertical", "diagonal"]
CANDIDATOS = ("prevalencia", "lineal", "cnn", "cnn_aumento")
CONFIG = {"epocas": 60, "cada": 5, "lote": 24, "tasa": .01, "semilla_modelo": 21,
          "semilla_orden": 2100, "semilla_aumento": 2121, "tolerancia": 1e-7,
          "optimizador": "Adam", "betas": [.9, .999], "eps": 1e-8, "weight_decay": 0.,
          "dtype": "float32", "dispositivo": "cpu", "hilos": 1, "num_workers": 0,
          "shuffle": True, "drop_last": False, "aumento": "reflejo horizontal p=0.5 solo cnn_aumento y entrenamiento"}


def leer_particion(datos, nombre):
    datos = Path(datos).resolve()
    contenido = (datos/f"{nombre}.csv").read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8")))
    campos = {"imagen_id", "escena_id", "archivo", "clase", "sha256"}
    if not lector.fieldnames or len(lector.fieldnames) != 5 or set(lector.fieldnames) != campos:
        raise ValueError("Manifiesto: imagen_id, escena_id, archivo, clase y sha256 requeridos.")
    filas, imagenes, ids, huellas, escenas = [], [], set(), set(), {}
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Fila incompleta o columnas adicionales.")
        fila = {k: v.strip() for k, v in fila.items()}
        if fila["imagen_id"] in ids or fila["clase"] not in ("0", "1", "2"):
            raise ValueError("ID repetido o clase distinta de 0, 1, 2.")
        ids.add(fila["imagen_id"])
        fila["clase"] = int(fila["clase"])
        grupo = fila["escena_id"]
        if grupo in escenas and escenas[grupo] != fila["clase"]:
            raise ValueError("Una escena no puede tener clases distintas.")
        escenas[grupo] = fila["clase"]
        ruta = (datos/fila["archivo"]).resolve()
        if not ruta.is_relative_to(datos/"imagenes") or ruta.suffix.lower() != ".png":
            raise ValueError("Cada ruta debe apuntar a un PNG dentro de imagenes/.")
        archivo = ruta.read_bytes()
        if hashlib.sha256(archivo).hexdigest() != fila["sha256"]:
            raise ValueError("La huella del PNG no coincide con el manifiesto.")
        with Image.open(io.BytesIO(archivo)) as imagen:
            if imagen.format != "PNG" or imagen.mode != "L" or imagen.size != (16, 16):
                raise ValueError("Se requieren PNG en modo L, de 16×16; no se redimensiona implícitamente.")
            pixeles = np.array(imagen, dtype=np.uint8)
        huella = hashlib.sha256(pixeles.tobytes()).hexdigest()
        if huella in huellas:
            raise ValueError("Píxeles duplicados en una partición.")
        huellas.add(huella)
        fila["sha256_pixeles"] = huella
        filas.append(fila)
        imagenes.append(pixeles)
    if not filas:
        raise ValueError("Partición vacía.")
    return {"filas": filas, "pixeles": np.stack(imagenes), "fuente": {
        "archivo": f"{nombre}.csv", "sha256_manifiesto": hashlib.sha256(contenido).hexdigest(),
        "n_imagenes": len(filas), "n_escenas": len(escenas), "imagenes": filas}}


def comprobar_separacion(*particiones):
    vistos = {k: set() for k in ("imagen_id", "escena_id", "sha256_pixeles")}
    for parte in particiones:
        for k in vistos:
            nuevos = {f[k] for f in parte["filas"]}
            if vistos[k] & nuevos:
                raise ValueError(f"Particiones comparten {k}.")
            vistos[k].update(nuevos)


def ajustar_normalizacion(pixeles):
    x = pixeles.astype(np.float64)/255
    media, escala = float(x.mean()), float(x.std(ddof=0))
    if not np.isfinite(escala) or escala <= 0:
        raise ValueError("Entrenamiento debe tener variación de intensidad.")
    return {"divisor": 255, "media": media, "escala": escala, "forma_chw": [1, 16, 16], "modo": "L"}


def tensor_imagenes(pixeles, preparacion):
    x = torch.tensor(np.array(pixeles), dtype=torch.float32).unsqueeze(1)/preparacion["divisor"]
    return (x-preparacion["media"])/preparacion["escala"]


class Clasificador(nn.Module):
    def __init__(self, nombre):
        super().__init__()
        if nombre not in CANDIDATOS:
            raise ValueError("Arquitectura desconocida.")
        self.nombre = nombre
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(CONFIG["semilla_modelo"])
            if nombre == "prevalencia":
                self.register_buffer("log_prior", torch.zeros(3))
            elif nombre == "lineal":
                self.red = nn.Sequential(nn.Flatten(), nn.Linear(256, 3))
            else:
                self.red = nn.Sequential(nn.Conv2d(1, 4, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                                         nn.Conv2d(4, 8, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
                                         nn.Flatten(), nn.Linear(8, 3))

    def forward(self, x):
        if self.nombre == "prevalencia":
            return self.log_prior.expand(len(x), -1)
        return self.red(x)


def restaurar(nombre, estado):
    modelo = Clasificador(nombre)
    modelo.load_state_dict({k: torch.tensor(v, dtype=torch.float32) for k, v in estado.items()}, strict=True)
    return modelo.eval()


def reflejar_lote(x, generador):
    """Transformación que conserva estas tres clases; devuelve una copia."""
    mascara = torch.rand(len(x), generator=generador) < .5
    resultado = x.clone()
    resultado[mascara] = torch.flip(x[mascara], dims=[-1])
    return resultado, int(mascara.sum())


def perdida(modelo, x, y):
    modelo.eval()
    with torch.no_grad():
        return nn.functional.cross_entropy(modelo(x), y).item()


def entrenar(nombre, x, y, xv, yv, epocas=60):
    if nombre not in ("lineal", "cnn", "cnn_aumento") or type(epocas) is not int or epocas < 1:
        raise ValueError("Candidato entrenable y épocas enteras positivas requeridos.")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    modelo = Clasificador(nombre)
    inicial = copiar_estado(modelo)
    optimizador = torch.optim.Adam(modelo.parameters(), lr=CONFIG["tasa"], betas=tuple(CONFIG["betas"]), eps=CONFIG["eps"], weight_decay=0.)
    orden = torch.Generator().manual_seed(CONFIG["semilla_orden"])
    aumentos = torch.Generator().manual_seed(CONFIG["semilla_aumento"])
    cargador = DataLoader(TensorDataset(x, y), batch_size=CONFIG["lote"], shuffle=True, generator=orden, num_workers=0)
    historial, mejor, pasos, reflejos = [], None, 0, 0
    for epoca in range(epocas+1):
        if epoca % CONFIG["cada"] == 0 or epoca == epocas:
            registro = {"epoca": epoca, "actualizaciones": pasos, "reflejos_acumulados": reflejos,
                        "ce_entrenamiento": perdida(modelo, x, y), "ce_validacion": perdida(modelo, xv, yv)}
            historial.append(registro)
            if mejor is None or registro["ce_validacion"] < mejor["perdida"]-CONFIG["tolerancia"]:
                mejor = {"epoca": epoca, "perdida": registro["ce_validacion"], "estado": copiar_estado(modelo)}
        if epoca == epocas:
            break
        modelo.train()
        for a, b in cargador:
            if nombre == "cnn_aumento":
                a, cantidad = reflejar_lote(a, aumentos)
                reflejos += cantidad
            optimizador.zero_grad(set_to_none=True)
            nn.functional.cross_entropy(modelo(a), b).backward()
            optimizador.step()
            pasos += 1
    return {"estado_inicial": inicial, "estado": mejor["estado"], "estado_final": copiar_estado(modelo),
            "epoca_elegida": mejor["epoca"], "n_parametros": sum(p.numel() for p in modelo.parameters()),
            "historial": historial, "actualizaciones": pasos, "reflejos_entrenamiento": reflejos}


def metricas(logits, etiquetas):
    s, y = np.asarray(logits, dtype=float), np.asarray(etiquetas)
    if (s.ndim != 2 or s.shape[1] != 3 or not len(s) or y.shape != (len(s),)
            or not np.isfinite(s).all() or not np.isin(y, [0, 1, 2]).all()):
        raise ValueError("Logits finitos (n,3) y etiquetas 0,1,2 requeridos.")
    y = y.astype(int)
    z = s-s.max(axis=1, keepdims=True)
    logp = z-np.log(np.exp(z).sum(axis=1, keepdims=True))
    probabilidades = np.exp(logp)
    pred = s.argmax(axis=1)
    matriz = np.zeros((3, 3), dtype=int)
    np.add.at(matriz, (y, pred), 1)
    por_clase = []
    for k, nombre in enumerate(CLASES):
        tp, reales, predichos = int(matriz[k, k]), int(matriz[k].sum()), int(matriz[:, k].sum())
        por_clase.append({"clase": nombre, "soporte": reales, "precision": tp/predichos if predichos else None,
                          "recobrado": tp/reales if reales else None,
                          "f1": 2*tp/(reales+predichos) if reales+predichos else 0.})
    return {"n": len(y), "ce": float(-logp[np.arange(len(y)), y].mean()), "matriz": matriz.tolist(),
            "exactitud": float((pred == y).mean()), "macro_f1": float(np.mean([c["f1"] for c in por_clase])),
            "por_clase": por_clase}, probabilidades


def evaluar(parte, preparacion, modelo):
    x = tensor_imagenes(parte["pixeles"], preparacion)
    y = [f["clase"] for f in parte["filas"]]
    modelo.eval()
    with torch.no_grad():
        logits = modelo(x).tolist()
    m, probabilidades = metricas(logits, y)
    predicciones = []
    for f, s, p in zip(parte["filas"], logits, probabilidades):
        predicciones.append({"imagen_id": f["imagen_id"], "escena_id": f["escena_id"], "real": f["clase"],
                             "prediccion": int(np.argmax(s)), "probabilidades": p.tolist(), "logits": s})
    return {"metricas": m, "predicciones": predicciones}


def seleccionar(candidatos):
    elegido = None
    for n, c in candidatos.items():
        if elegido is None or c["validacion"]["metricas"]["ce"] < candidatos[elegido]["validacion"]["metricas"]["ce"]-CONFIG["tolerancia"]:
            elegido = n
    if elegido is None:
        raise ValueError("No hay candidatos.")
    return elegido


def ejecutar_experimento(datos=None, evaluar_prueba=False, epocas=60):
    torch.set_num_threads(1)
    datos = Path(datos) if datos is not None else UNIDAD/"datos"
    train, val = leer_particion(datos, "entrenamiento"), leer_particion(datos, "validacion")
    comprobar_separacion(train, val)
    if {f["clase"] for f in train["filas"]} != {0, 1, 2}:
        raise ValueError("Entrenamiento requiere las tres clases.")
    preparacion = ajustar_normalizacion(train["pixeles"])
    x, xv = tensor_imagenes(train["pixeles"], preparacion), tensor_imagenes(val["pixeles"], preparacion)
    y, yv = [torch.tensor([f["clase"] for f in p["filas"]], dtype=torch.int64) for p in (train, val)]
    base = Clasificador("prevalencia")
    base.log_prior.copy_(torch.log(torch.bincount(y, minlength=3).float()/len(y)))
    candidatos = {"prevalencia": {"estado": copiar_estado(base), "epoca_elegida": 0, "n_parametros": 2,
                                 "historial": [], "actualizaciones": 0, "reflejos_entrenamiento": 0}}
    for nombre in CANDIDATOS[1:]:
        candidatos[nombre] = entrenar(nombre, x, y, xv, yv, epocas)
    for n, c in candidatos.items():
        modelo = restaurar(n, serializar(c["estado"]))
        c["entrenamiento"], c["validacion"] = evaluar(train, preparacion, modelo), evaluar(val, preparacion, modelo)
    elegido = seleccionar(candidatos)
    informe = {"laboratorio": "trazos", "protocolo": "u21-v1-ce-escenas", "clases": CLASES,
               "configuracion": dict(CONFIG, epocas=epocas), "preparacion": preparacion,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__, "torch": str(torch.__version__), "pillow": PIL.__version__},
               "fuentes": {"entrenamiento": train["fuente"], "validacion": val["fuente"]},
               "casos_validacion": [{"imagen_id": f["imagen_id"], "pixeles": p.tolist()} for f, p in zip(val["filas"], val["pixeles"])],
               "candidatos": candidatos, "seleccionado": elegido, "prueba": None}
    if evaluar_prueba:
        prueba = leer_particion(datos, "prueba")
        comprobar_separacion(train, val, prueba)
        informe["fuentes"]["prueba"] = prueba["fuente"]
        informe["prueba"] = evaluar(prueba, preparacion, restaurar(elegido, serializar(candidatos[elegido]["estado"])))
    return serializar(informe)


def guardar_modelo(informe, ruta):
    nombre = informe["seleccionado"]
    contenido = {"formato": "u21-inferencia-v1", "arquitectura": nombre, "clases": informe["clases"],
                 "preparacion": informe["preparacion"], "epoca": informe["candidatos"][nombre]["epoca_elegida"],
                 "state_dict": copiar_estado(restaurar(nombre, informe["candidatos"][nombre]["estado"]))}
    with Path(ruta).open("xb") as f:
        torch.save(contenido, f)


def cargar_modelo(ruta):
    """Solo artefactos propios de la unidad; preparación y clases son parte del contrato."""
    datos = torch.load(ruta, map_location="cpu", weights_only=True)
    if (not isinstance(datos, dict) or datos.get("formato") != "u21-inferencia-v1"
            or datos.get("arquitectura") not in CANDIDATOS or datos.get("clases") != CLASES
            or type(datos.get("epoca")) is not int or datos["epoca"] < 0):
        raise ValueError("Metadatos de modelo incompatibles.")
    p = datos.get("preparacion")
    if (not isinstance(p, dict) or set(p) != {"divisor", "media", "escala", "forma_chw", "modo"}
            or p["divisor"] != 255 or p["forma_chw"] != [1, 16, 16] or p["modo"] != "L"
            or any(type(p[k]) not in (int, float) or not np.isfinite(p[k]) for k in ("media", "escala"))
            or not 0 <= p["media"] <= 1 or p["escala"] <= 0):
        raise ValueError("Preparación incompatible.")
    modelo = Clasificador(datos["arquitectura"])
    estado, esperado = datos.get("state_dict"), modelo.state_dict()
    if not isinstance(estado, dict) or set(estado) != set(esperado):
        raise ValueError("Claves de estado incompatibles.")
    for k, v in estado.items():
        if (not isinstance(v, torch.Tensor) or v.dtype != torch.float32
                or v.shape != esperado[k].shape or not torch.isfinite(v).all()):
            raise ValueError("Forma, tipo o valores del estado incompatibles.")
    modelo.load_state_dict(estado, strict=True)
    return modelo.eval(), p


def exportar(informe, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    (salida/"informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for fase in ("entrenamiento", "validacion", "prueba"):
        if fase == "prueba":
            resultados = {informe["seleccionado"]: informe["prueba"]} if informe["prueba"] is not None else {}
        else:
            resultados = {n: c[fase] for n, c in informe["candidatos"].items()}
        filas = []
        for nombre, resultado in resultados.items():
            for p in resultado["predicciones"]:
                fila = {k: p[k] for k in ("imagen_id", "escena_id", "real", "prediccion")}
                fila["candidato"] = nombre
                fila.update({f"p_{clase}": v for clase, v in zip(CLASES, p["probabilidades"])})
                filas.append(fila)
        if filas:
            with (salida/f"predicciones_{fase}.csv").open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
                w.writeheader()
                w.writerows(filas)
    ruta = salida/"modelo.pt"
    guardar_modelo(informe, ruta)
    modelo, preparacion = cargar_modelo(ruta)
    parte = {"filas": informe["fuentes"]["validacion"]["imagenes"],
             "pixeles": np.array([f["pixeles"] for f in informe["casos_validacion"]], dtype=np.uint8)}
    nuevas = evaluar(parte, preparacion, modelo)["predicciones"]
    originales = informe["candidatos"][informe["seleccionado"]]["validacion"]["predicciones"]
    error = float(np.max(np.abs(np.array([p["logits"] for p in nuevas])-np.array([p["logits"] for p in originales]))))
    if error != 0.:
        raise RuntimeError("La recarga cambió los logits en este entorno.")
    (salida/"recarga.json").write_text(json.dumps({"max_error_logits": error, "n_imagenes": len(nuevas),
        "sha256_modelo": hashlib.sha256(ruta.read_bytes()).hexdigest(), "uso": "inferencia en CPU"}, indent=2)+"\n", encoding="utf-8")
    return error

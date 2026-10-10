"""Tensores, minilotes y estados para un experimento pequeño en CPU."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

UNIDAD = Path(__file__).resolve().parents[1]
_rutas_previas = sys.path.copy()
try:
    sys.path.insert(0, str(UNIDAD.parent/"unidad19-redes-neuronales/ejemplos"))
    import redes as referencia
finally:
    # La unidad anterior añade también su dependencia; no dejarla ocultar módulos locales.
    sys.path[:] = _rutas_previas

CAPAS = {"prevalencia": [], "lineal": [], "red12_8": [12, 8]}
CONFIG = {"epocas": 120, "cada": 10, "lote": 32, "tasa": .01,
          "semilla_modelo": 20, "semilla_orden": 2020, "umbral": .5,
          "optimizador": "Adam", "betas": [.9, .999], "eps": 1e-8, "weight_decay": 0.,
          "dtype": "float32", "dispositivo": "cpu", "hilos": 1,
          "shuffle": True, "drop_last": False, "num_workers": 0, "tolerancia": 1e-8}


class Red(nn.Module):
    def __init__(self, ocultas, dtype=torch.float32, semilla=20):
        super().__init__()
        # Aísla la inicialización del generador global del programa que nos importe.
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(semilla)
            modulos, entrada = [], 2
            for ancho in ocultas:
                modulos.extend([nn.Linear(entrada, ancho, dtype=dtype), nn.Tanh()])
                entrada = ancho
            modulos.append(nn.Linear(entrada, 1, dtype=dtype))
            self.capas = nn.Sequential(*modulos)

    def forward(self, x):
        # Conserva la dimensión de lote incluso cuando n=1.
        return self.capas(x).squeeze(-1)


def versiones():
    return {"python": platform.python_version(), "numpy": np.__version__, "torch": str(torch.__version__)}


def copiar_estado(modelo):
    return {k: v.detach().cpu().clone() for k, v in modelo.state_dict().items()}


def serializar(valor):
    if isinstance(valor, torch.Tensor):
        return valor.detach().cpu().tolist()
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if isinstance(valor, dict):
        return {k: serializar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [serializar(v) for v in valor]
    return valor


def restaurar(nombre, estado):
    modelo = Red(CAPAS[nombre])
    modelo.load_state_dict({k: torch.tensor(v, dtype=torch.float32) for k, v in estado.items()}, strict=True)
    return modelo.eval()


def tensores(filas, escala):
    x = torch.tensor(referencia.transformar(filas, escala), dtype=torch.float32)
    y = torch.tensor([f["objetivo"] for f in filas], dtype=torch.float32)
    return x, y


def perdida_evaluacion(modelo, x, y, lote=32):
    modelo.eval()
    total = 0.
    with torch.no_grad():
        for a, b in DataLoader(TensorDataset(x, y), batch_size=lote, shuffle=False):
            # Suma por casos: el último lote puede tener menos elementos.
            total += nn.functional.binary_cross_entropy_with_logits(modelo(a), b, reduction="sum").item()
    return total/len(y)


def entrenar(x, y, xv, yv, ocultas, epocas=120, cada=10, lote=32):
    if any(type(v) is not int or v < 1 for v in (epocas, cada, lote)):
        raise ValueError("Épocas, intervalo y lote deben ser enteros positivos.")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    modelo = Red(ocultas, semilla=CONFIG["semilla_modelo"])
    inicial = copiar_estado(modelo)
    optimizador = torch.optim.Adam(modelo.parameters(), lr=CONFIG["tasa"],
                                  betas=tuple(CONFIG["betas"]), eps=CONFIG["eps"], weight_decay=0.)
    generador = torch.Generator().manual_seed(CONFIG["semilla_orden"])
    cargador = DataLoader(TensorDataset(x, y, torch.arange(len(y))), batch_size=lote,
                         shuffle=True, generator=generador, num_workers=0, drop_last=False)
    historial, ordenes, mejor, pasos = [], [], None, 0
    for epoca in range(epocas+1):
        if epoca % cada == 0 or epoca == epocas:
            registro = {"epoca": epoca, "actualizaciones": pasos,
                        "bce_entrenamiento": perdida_evaluacion(modelo, x, y, lote),
                        "bce_validacion": perdida_evaluacion(modelo, xv, yv, lote)}
            historial.append(registro)
            if mejor is None or registro["bce_validacion"] < mejor["bce"]-CONFIG["tolerancia"]:
                mejor = {"epoca": epoca, "bce": registro["bce_validacion"], "estado": copiar_estado(modelo)}
        if epoca == epocas:
            break
        modelo.train()
        orden, tamanos = [], []
        for a, b, indices in cargador:
            optimizador.zero_grad(set_to_none=True)
            logits = modelo(a)
            perdida = nn.functional.binary_cross_entropy_with_logits(logits, b)
            perdida.backward()
            optimizador.step()
            pasos += 1
            orden.extend(indices.tolist())
            tamanos.append(len(b))
        huella = hashlib.sha256(json.dumps(orden, separators=(",", ":")).encode()).hexdigest()
        ordenes.append({"epoca": epoca+1, "sha256_indices": huella, "tamanos": tamanos,
                        "indices": orden if epoca == 0 else None})
    return {"estado_inicial": inicial, "estado": mejor["estado"], "estado_final": copiar_estado(modelo),
            "epoca_elegida": mejor["epoca"], "actualizaciones_totales": pasos,
            "n_parametros": sum(p.numel() for p in modelo.parameters()),
            "historial": historial, "ordenes": ordenes}


def evaluar(filas, escala, modelo):
    x, y = tensores(filas, escala)
    modelo.eval()
    with torch.no_grad():
        logits = modelo(x)
        probabilidades = torch.sigmoid(logits)
    pred = (probabilidades >= .5).to(torch.int64).tolist()
    metricas = referencia.metricas_clasificacion(y.to(torch.int64).tolist(), pred)
    # Referencia NumPy float64 aplicada a los logits float32, independiente del entrenamiento.
    metricas["bce"] = referencia.perdida(y.tolist(), logits.tolist())
    return {"metricas": metricas, "predicciones": [
        {"caso_id": f["caso_id"], "real": f["objetivo"], "logit": s,
         "probabilidad": p, "prediccion": c}
        for f, s, p, c in zip(filas, logits.tolist(), probabilidades.tolist(), pred)]}


def seleccionar(candidatos):
    elegido = None
    for nombre, c in candidatos.items():
        if elegido is None or c["validacion"]["metricas"]["bce"] < candidatos[elegido]["validacion"]["metricas"]["bce"]-CONFIG["tolerancia"]:
            elegido = nombre
    if elegido is None:
        raise ValueError("No hay candidatos.")
    return elegido


def ejecutar_experimento(datos=None, evaluar_prueba=False, epocas=120):
    torch.set_num_threads(1)
    datos = Path(datos) if datos is not None else UNIDAD/"datos/minilotes"
    train, ft = referencia.leer_csv(datos/"entrenamiento.csv")
    val, fv = referencia.leer_csv(datos/"validacion.csv")
    ids = {f["caso_id"] for f in train}
    if ids.intersection(f["caso_id"] for f in val):
        raise ValueError("IDs compartidos entre particiones.")
    ids.update(f["caso_id"] for f in val)
    if {f["objetivo"] for f in train} != {0, 1}:
        raise ValueError("Entrenamiento requiere ambas clases.")
    escala = referencia.ajustar_escala(referencia.matriz(train))
    x, y = tensores(train, escala)
    xv, yv = tensores(val, escala)
    base = Red([])
    prevalencia = float(y.mean())
    with torch.no_grad():
        base.capas[0].weight.zero_()
        base.capas[0].bias.fill_(np.log(prevalencia/(1-prevalencia)))
    candidatos = {"prevalencia": {"estado": copiar_estado(base), "epoca_elegida": 0,
                                 "n_parametros": 1, "historial": [], "ordenes": [],
                                 "actualizaciones_totales": 0}}
    for nombre in ("lineal", "red12_8"):
        candidatos[nombre] = entrenar(x, y, xv, yv, CAPAS[nombre], epocas=epocas)
    for nombre, c in candidatos.items():
        c["capas_ocultas"] = CAPAS[nombre]
        modelo = restaurar(nombre, serializar(c["estado"]))
        c["entrenamiento"] = evaluar(train, escala, modelo)
        c["validacion"] = evaluar(val, escala, modelo)
    elegido = seleccionar(candidatos)
    informe = {"laboratorio": "minilotes", "protocolo": "u20-v1-bce-validacion",
               "versiones": versiones(), "configuracion": dict(CONFIG, epocas=epocas),
               "entradas": list(referencia.ENTRADAS), "escala": escala,
               "fuentes": {"entrenamiento": ft, "validacion": fv}, "puntos_validacion": val,
               "candidatos": candidatos, "seleccionado": elegido, "prueba": None}
    # Solo ahora se abre el cierre. Nunca interviene en gradientes, escala o selección.
    if evaluar_prueba:
        prueba, fp = referencia.leer_csv(datos/"prueba.csv")
        if ids.intersection(f["caso_id"] for f in prueba):
            raise ValueError("IDs compartidos entre particiones.")
        informe["fuentes"]["prueba"] = fp
        informe["prueba"] = evaluar(prueba, escala, restaurar(elegido, serializar(candidatos[elegido]["estado"])))
    return serializar(informe)


def guardar_modelo(informe, ruta):
    nombre = informe["seleccionado"]
    c = informe["candidatos"][nombre]
    contenido = {"formato": "u20-inferencia-v1", "candidato": nombre, "entradas": informe["entradas"],
                 "escala": informe["escala"], "epoca": c["epoca_elegida"],
                 "state_dict": copiar_estado(restaurar(nombre, c["estado"]))}
    with Path(ruta).open("xb") as f:
        torch.save(contenido, f)


def cargar_modelo(ruta):
    """Solo para los archivos propios de esta práctica; no reanuda Adam."""
    contenido = torch.load(ruta, map_location="cpu", weights_only=True)
    if (not isinstance(contenido, dict) or contenido.get("formato") != "u20-inferencia-v1"
            or contenido.get("candidato") not in CAPAS
            or contenido.get("entradas") != list(referencia.ENTRADAS)
            or type(contenido.get("epoca")) is not int or contenido["epoca"] < 0):
        raise ValueError("Metadatos de modelo incompatibles.")
    escala = contenido.get("escala")
    if not isinstance(escala, dict) or set(escala) != {"media", "escala"}:
        raise ValueError("Escala ausente o incompatible.")
    valores = np.asarray([escala["media"], escala["escala"]], dtype=float)
    if valores.shape != (2, 2) or not np.isfinite(valores).all() or (valores[1] <= 0).any():
        raise ValueError("Escala no finita o no positiva.")
    modelo = Red(CAPAS[contenido["candidato"]])
    estado, esperado = contenido.get("state_dict"), modelo.state_dict()
    if not isinstance(estado, dict) or set(estado) != set(esperado):
        raise ValueError("Claves de estado incompatibles.")
    for k, v in estado.items():
        if (not isinstance(v, torch.Tensor) or v.shape != esperado[k].shape
                or v.dtype != torch.float32 or not torch.isfinite(v).all()):
            raise ValueError("Forma, tipo o valor del estado incompatible.")
    modelo.load_state_dict(estado, strict=True)
    return modelo.eval(), escala


def exportar(informe, salida):
    # CSV e informe usan el mismo formato de la unidad anterior.
    referencia.exportar(informe, salida)
    ruta = Path(salida)/"modelo.pt"
    guardar_modelo(informe, ruta)
    modelo, escala = cargar_modelo(ruta)
    recarga = evaluar(informe["puntos_validacion"], escala, modelo)
    original = informe["candidatos"][informe["seleccionado"]]["validacion"]
    error = max(abs(a["logit"]-b["logit"]) for a, b in zip(original["predicciones"], recarga["predicciones"]))
    if error != 0.:
        raise RuntimeError("La recarga cambió las predicciones en este entorno.")
    verificacion = {"max_error_logits": error, "n": len(recarga["predicciones"]),
                    "dispositivo": "cpu", "uso": "inferencia; no reanudación de entrenamiento",
                    "sha256_modelo": hashlib.sha256(ruta.read_bytes()).hexdigest()}
    (Path(salida)/"recarga.json").write_text(json.dumps(verificacion, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return verificacion

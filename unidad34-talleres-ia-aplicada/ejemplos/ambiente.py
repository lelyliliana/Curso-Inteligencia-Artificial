"""Priorizar revisiones ficticias; costo explícito y zonas completas separadas."""

import math
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

CAMPOS = ("residuos_m2", "superficie_afectada_pct", "dias_sin_visita")


def validar(entrada):
    if not isinstance(entrada, dict) or set(entrada) != set(CAMPOS):
        raise ValueError(f"Ambiente requiere exactamente: {', '.join(CAMPOS)}")
    for campo, limite in zip(CAMPOS, (20, 100, 60)):
        valor = entrada[campo]
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or not 0 <= valor <= limite:
            raise ValueError(f"{campo} debe ser finito y estar entre 0 y {limite}")
    if type(entrada["dias_sin_visita"]) is not int:
        raise ValueError("dias_sin_visita debe ser un entero")
    return [entrada[k] for k in CAMPOS]


def entrada(fila):
    return {k: fila[k] for k in CAMPOS}


def ajustar(filas, protocolo):
    x = np.asarray([validar(entrada(f)) for f in filas])
    y = np.asarray([f["revision_prioritaria"] for f in filas])
    escala = StandardScaler().fit(x)
    # Una sola logística; los umbrales no vuelven a entrenarla.
    modelo = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, tol=1e-8).fit(escala.transform(x), y)
    if int(modelo.n_iter_[0]) >= 1000:
        raise RuntimeError("La logística agotó su presupuesto de iteraciones")
    comun = {"minimos": x.min(axis=0).tolist(), "maximos": x.max(axis=0).tolist()}
    estados = {"ninguna": {**comun, "tipo": "constante", "clase": 0},
               "todas": {**comun, "tipo": "constante", "clase": 1}}
    for nombre in protocolo["candidatos"][2:]:
        estados[nombre] = {**comun, "tipo": "logistica", "umbral": float(nombre.split("_")[1]),
                           "media": escala.mean_.tolist(), "escala": escala.scale_.tolist(),
                           "coef": modelo.coef_[0].tolist(), "intercepto": float(modelo.intercept_[0])}
    return estados


def predecir(modelo, consulta):
    x = np.asarray(validar(consulta))
    if modelo["tipo"] == "constante":
        puntuacion = None
        clase = modelo["clase"]
    else:
        z = float(((x - modelo["media"]) / modelo["escala"]) @ modelo["coef"] + modelo["intercepto"])
        puntuacion = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
        clase = int(puntuacion >= modelo["umbral"])
    fuera = bool(np.any((x < modelo["minimos"]) | (x > modelo["maximos"])))
    return {"proponer_revision": clase, "puntuacion": puntuacion,
            "fuera_rango_entrenamiento": fuera, "requiere_revision_humana": True}


def metricas(casos, protocolo):
    tp = sum(c["objetivo"] == 1 and c["proponer_revision"] == 1 for c in casos)
    fp = sum(c["objetivo"] == 0 and c["proponer_revision"] == 1 for c in casos)
    fn = sum(c["objetivo"] == 1 and c["proponer_revision"] == 0 for c in casos)
    tn = len(casos) - tp - fp - fn
    costo = protocolo["costo_fp"] * fp + protocolo["costo_fn"] * fn
    return {"n": len(casos), "tp": tp, "fp": fp, "fn": fn, "tn": tn, "costo": costo,
            "costo_por_caso": costo / len(casos) if casos else None, "propuestas": tp + fp,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None}


def evaluar(modelo, filas, protocolo):
    casos = [{"id": f["id"], "zona": f["zona"], "objetivo": f["revision_prioritaria"],
              **predecir(modelo, entrada(f))} for f in filas]
    zonas = {z: metricas([c for c in casos if c["zona"] == z], protocolo) for z in sorted({c["zona"] for c in casos})}
    return {**metricas(casos, protocolo), "por_zona": zonas, "casos": casos}


def desarrollar(entrenamiento, validacion, protocolo):
    modelos = ajustar(entrenamiento, protocolo)
    candidatos = protocolo["candidatos"]
    resultados = {k: evaluar(modelos[k], validacion, protocolo) for k in candidatos}
    elegido = min(candidatos, key=lambda k: (resultados[k]["costo"], resultados[k]["propuestas"], candidatos.index(k)))
    return elegido, modelos[elegido], resultados

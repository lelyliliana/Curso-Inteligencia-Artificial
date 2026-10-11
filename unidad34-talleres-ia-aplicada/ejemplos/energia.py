"""Pronóstico de una hora: persistencia frente a Ridge, sin aprender del cierre."""

import math
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

CAMPOS = ("consumo_actual_kw", "hora_siguiente", "laboral_siguiente")


def validar(entrada):
    if not isinstance(entrada, dict) or set(entrada) != set(CAMPOS):
        raise ValueError(f"Energía requiere exactamente: {', '.join(CAMPOS)}")
    kw, hora, laboral = (entrada[k] for k in CAMPOS)
    if isinstance(kw, bool) or not isinstance(kw, (int, float)) or not math.isfinite(kw) or not 0 <= kw <= 200:
        raise ValueError("consumo_actual_kw debe ser finito y estar entre 0 y 200")
    if type(hora) is not int or not 0 <= hora <= 23:
        raise ValueError("hora_siguiente debe ser un entero entre 0 y 23")
    if type(laboral) is not int or laboral not in (0, 1):
        raise ValueError("laboral_siguiente debe ser 0 o 1")
    return [kw, math.sin(2 * math.pi * hora / 24), math.cos(2 * math.pi * hora / 24), laboral]


def entrada(fila):
    return {k: fila[k] for k in CAMPOS}


def ajustar(filas):
    x = np.asarray([validar(entrada(f)) for f in filas])
    y = np.asarray([f["objetivo_kw"] for f in filas])
    escala = StandardScaler().fit(x)
    modelo = Ridge(alpha=1.0, solver="svd").fit(escala.transform(x), y)
    base = {"min_kw": float(x[:, 0].min()), "max_kw": float(x[:, 0].max())}
    return {
        "persistencia": {**base, "tipo": "persistencia"},
        "ridge_1": {**base, "tipo": "ridge", "media": escala.mean_.tolist(),
                    "escala": escala.scale_.tolist(), "coef": modelo.coef_.tolist(),
                    "intercepto": float(modelo.intercept_)}
    }


def predecir(modelo, consulta):
    x = np.asarray(validar(consulta))
    if modelo["tipo"] == "persistencia":
        kw = float(x[0])
    else:
        kw = float(((x - modelo["media"]) / modelo["escala"]) @ modelo["coef"] + modelo["intercepto"])
    fuera = not modelo["min_kw"] <= x[0] <= modelo["max_kw"]
    return {"estado": "revisar" if fuera or kw < 0 else "estimacion", "prediccion_kw": kw,
            "fuera_rango_consumo": bool(fuera), "unidad": "kW", "horizonte_horas": 1}


def evaluar(modelo, filas):
    casos = [{"id": f["id"], "origen": f["origen"], "instante_objetivo": f["instante_objetivo"],
              "objetivo_kw": f["objetivo_kw"], **predecir(modelo, entrada(f))} for f in filas]
    errores = [abs(c["objetivo_kw"] - c["prediccion_kw"]) for c in casos]
    return {"n": len(casos), "mae_kw": sum(errores) / len(errores),
            "sesgo_kw": sum(c["prediccion_kw"] - c["objetivo_kw"] for c in casos) / len(casos),
            "revisar": sum(c["estado"] == "revisar" for c in casos), "casos": casos}


def desarrollar(entrenamiento, validacion, protocolo):
    modelos = ajustar(entrenamiento)
    candidatos = protocolo["candidatos"]
    resultados = {k: evaluar(modelos[k], validacion) for k in candidatos}
    elegido = min(candidatos, key=lambda k: (resultados[k]["mae_kw"], candidatos.index(k)))
    return elegido, modelos[elegido], resultados

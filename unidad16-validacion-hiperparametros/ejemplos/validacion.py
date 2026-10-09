"""Selección por CV, preparación dentro de pliegues y reajuste antes de prueba."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GroupKFold, KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_regresion

ENTRADAS = {"ciclos": ("horas_previstas", "carga_prevista"), "equipos": ("senal_a", "senal_b")}
OBJETIVO = {"ciclos": "consumo_kwh", "equipos": "respuesta"}
DOMINIOS = {"ciclos": {"horas_previstas": (0, 24), "carga_prevista": (0, 1500), "consumo_kwh": (0, 1000)},
            "equipos": {"senal_a": (0, 100), "senal_b": (0, 100), "respuesta": (0, 100)}}
CANDIDATOS = {"mediana": None, **{f"knn{k}_{pesos}": {"n_neighbors": k, "weights": pesos}
                for k in (3, 9, 21) for pesos in ("uniform", "distance")}}
SEMILLA_CV = 16
PLIEGUES = 4
TOLERANCIA = 1e-10
DIAGNOSTICO = "knn3_uniform"


def leer_csv(ruta, nombre):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    columnas = {"caso_id", *DOMINIOS[nombre], *(["equipo_id"] if nombre == "equipos" else [])}
    if lector.fieldnames is None or len(lector.fieldnames) != len(columnas) or set(lector.fieldnames) != columnas:
        raise ValueError("Esquema incorrecto, ausente o repetido.")
    filas, ids = [], set()
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Se requieren filas completas sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        if fila["caso_id"] in ids:
            raise ValueError("Identificador repetido.")
        ids.add(fila["caso_id"])
        for c, (a, b) in DOMINIOS[nombre].items():
            fila[c] = float(fila[c])
            if not math.isfinite(fila[c]) or not a <= fila[c] <= b:
                raise ValueError("Valor no finito o fuera del dominio declarado.")
        filas.append(fila)
    if not filas:
        raise ValueError("Partición vacía.")
    return filas, {"archivo": Path(ruta).name, "sha256": hashlib.sha256(contenido).hexdigest(), "n": len(filas)}


def matriz(filas, nombre):
    # Lista explícita: ni identificadores ni objetivo entran en las distancias.
    return np.array([[f[c] for c in ENTRADAS[nombre]] for f in filas], dtype=float)


def crear_modelo(candidato):
    configuracion = CANDIDATOS[candidato]
    if configuracion is None:
        return DummyRegressor(strategy="median")
    return Pipeline([("escala", StandardScaler()),
                     ("vecinos", KNeighborsRegressor(**configuracion, algorithm="brute", metric="euclidean", n_jobs=1))])


def pliegues(filas, nombre, mezclar_equipos=False):
    if nombre == "equipos" and not mezclar_equipos:
        grupos = [f["equipo_id"] for f in filas]
        if len(set(grupos)) < PLIEGUES:
            raise ValueError("Se necesitan al menos cuatro equipos distintos.")
        particiones = list(GroupKFold(n_splits=PLIEGUES).split(filas, groups=grupos))
    else:
        if len(filas) < PLIEGUES:
            raise ValueError("Se necesitan al menos cuatro casos.")
        particiones = list(KFold(n_splits=PLIEGUES, shuffle=True, random_state=SEMILLA_CV).split(filas))
    if min(len(train) for train, _ in particiones) < 21:
        raise ValueError("Cada entrenamiento de pliegue necesita al menos 21 casos para la rejilla.")
    return particiones


def describir_pliegues(filas, particiones):
    resultado = []
    for i, (train, val) in enumerate(particiones, 1):
        grupos_train = sorted({filas[j]["equipo_id"] for j in train if "equipo_id" in filas[j]})
        grupos_val = sorted({filas[j]["equipo_id"] for j in val if "equipo_id" in filas[j]})
        resultado.append({"pliegue": i, "indices_ajuste": train.tolist(), "indices_validacion": val.tolist(),
                          "ids_ajuste": [filas[j]["caso_id"] for j in train],
                          "ids_validacion": [filas[j]["caso_id"] for j in val],
                          "equipos_ajuste": grupos_train, "equipos_validacion": grupos_val,
                          "equipos_compartidos": sorted(set(grupos_train) & set(grupos_val))})
    return resultado


def resumen_modelo(modelo, ids):
    if isinstance(modelo, DummyRegressor):
        return {"tipo": "mediana", "valor": float(modelo.constant_[0, 0]), "n_ajuste": len(ids), "ids_ajuste": ids}
    escala = modelo.named_steps["escala"]
    return {"tipo": "Pipeline", "n_ajuste": len(ids), "ids_ajuste": ids,
            "escala": {"media": escala.mean_.tolist(), "varianza": escala.var_.tolist(), "escala": escala.scale_.tolist()},
            "vecinos": modelo.named_steps["vecinos"].get_params()}


def registros(filas, indices, y, pred, pliegue=None):
    return [{"caso_id": filas[j]["caso_id"], **({"equipo_id": filas[j]["equipo_id"]} if "equipo_id" in filas[j] else {}),
             **({"pliegue": pliegue} if pliegue is not None else {}),
             "real": float(real), "prediccion": float(estimado), "residuo": float(real-estimado)}
            for j, real, estimado in zip(indices, y, pred)]


def evaluar_cv(filas, nombre, particiones, candidato):
    x, y = matriz(filas, nombre), np.array([f[OBJETIVO[nombre]] for f in filas])
    plantilla = crear_modelo(candidato)
    evaluaciones, predicciones = [], []
    for i, (train, val) in enumerate(particiones, 1):
        modelo = clone(plantilla).fit(x[train], y[train])
        pred = modelo.predict(x[val])
        evaluaciones.append({"pliegue": i,
                             "ajuste": resumen_modelo(modelo, [filas[j]["caso_id"] for j in train]),
                             "entrenamiento": metricas_regresion(y[train].tolist(), modelo.predict(x[train]).tolist()),
                             "validacion": metricas_regresion(y[val].tolist(), pred.tolist())})
        predicciones.extend(registros(filas, val, y[val], pred, i))
    maes = [ev["validacion"]["mae"] for ev in evaluaciones]
    return {"mae_medio": float(np.mean(maes)), "desviacion_mae": float(np.std(maes, ddof=0)),
            "mae_oof": float(np.mean([abs(r["residuo"]) for r in predicciones])),
            "pliegues": evaluaciones, "predicciones_oof": predicciones}


def seleccionar(resultados):
    minimo = min(ev["mae_medio"] for ev in resultados.values())
    return next(c for c in CANDIDATOS if c in resultados and resultados[c]["mae_medio"] <= minimo+TOLERANCIA)


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False):
    with threadpool_limits(limits=1):
        return _ejecutar(nombre, Path(carpeta), evaluar_prueba)


def _ejecutar(nombre, carpeta, evaluar_prueba):
    if nombre not in ENTRADAS:
        raise ValueError("Experimento desconocido.")
    filas, fuente = leer_csv(carpeta / "desarrollo.csv", nombre)
    particiones = pliegues(filas, nombre)
    resultados = {c: evaluar_cv(filas, nombre, particiones, c) for c in CANDIDATOS}
    elegido = seleccionar(resultados)
    x, y = matriz(filas, nombre), np.array([f[OBJETIVO[nombre]] for f in filas])
    # Se ajusta una instancia nueva, no se reutiliza el modelo del último pliegue.
    modelo_final = crear_modelo(elegido).fit(x, y)
    informe = {"protocolo": "validacion-cv-v1", "experimento": nombre,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
               "fuentes": {"desarrollo": fuente}, "entradas": list(ENTRADAS[nombre]), "objetivo": OBJETIVO[nombre],
               "cv": {"tipo": "GroupKFold" if nombre == "equipos" else "KFold", "n_splits": PLIEGUES,
                      "shuffle": nombre == "ciclos", "semilla": SEMILLA_CV if nombre == "ciclos" else None,
                      "pliegues": describir_pliegues(filas, particiones)},
               "rejilla": CANDIDATOS, "criterio": {"metrica": "media no ponderada de MAE de validación entre pliegues", "tolerancia_absoluta": TOLERANCIA,
                                                   "desviacion_ddof": 0, "orden_desempate": list(CANDIDATOS)},
               "resultados_cv": resultados, "seleccionado": elegido,
               "reajuste": resumen_modelo(modelo_final, [f["caso_id"] for f in filas]),
               "ajustes_realizados": len(CANDIDATOS)*PLIEGUES+1, "diagnostico_filas": None, "prueba": None}
    if nombre == "equipos":
        particiones_mezcladas = pliegues(filas, nombre, mezclar_equipos=True)
        informe["diagnostico_filas"] = {"candidato_fijo": DIAGNOSTICO, "semilla": SEMILLA_CV,
                                        "pliegues": describir_pliegues(filas, particiones_mezcladas),
                                        "resultado": evaluar_cv(filas, nombre, particiones_mezcladas, DIAGNOSTICO)}
        informe["ajustes_realizados"] += PLIEGUES
    if evaluar_prueba:
        prueba, fuente_prueba = leer_csv(carpeta / "prueba.csv", nombre)
        if {f["caso_id"] for f in filas} & {f["caso_id"] for f in prueba}:
            raise ValueError("Identificadores compartidos entre desarrollo y prueba.")
        if nombre == "equipos" and {f["equipo_id"] for f in filas} & {f["equipo_id"] for f in prueba}:
            raise ValueError("Prueba debe contener equipos nuevos.")
        x_test = matriz(prueba, nombre)
        y_test = np.array([f[OBJETIVO[nombre]] for f in prueba])
        pred = modelo_final.predict(x_test)
        informe["fuentes"]["prueba"] = fuente_prueba
        informe["prueba"] = {"candidato": elegido, "metricas": metricas_regresion(y_test.tolist(), pred.tolist()),
                             "predicciones": registros(prueba, range(len(prueba)), y_test, pred)}
    return informe


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    conjuntos = {"predicciones_oof": [dict(candidato=c, **r) for c, ev in informe["resultados_cv"].items() for r in ev["predicciones_oof"]]}
    if informe["diagnostico_filas"] is not None:
        diag = informe["diagnostico_filas"]
        conjuntos["diagnostico_filas_oof"] = [dict(candidato=diag["candidato_fijo"], **r) for r in diag["resultado"]["predicciones_oof"]]
    if informe["prueba"] is not None:
        conjuntos["predicciones_prueba"] = [dict(candidato=informe["seleccionado"], **r) for r in informe["prueba"]["predicciones"]]
    for nombre, filas in conjuntos.items():
        with (destino / f"{nombre}.csv").open("x", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
    with (destino / "informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

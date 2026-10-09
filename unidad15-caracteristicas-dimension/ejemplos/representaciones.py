"""Transformaciones aprendidas solo con entrenamiento y comparación por MAE."""

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
from sklearn.decomposition import PCA
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_regresion

ENTRADAS = {"interaccion": ("horas_previstas", "potencia_prevista_kw"), "pca": ("senal_a", "senal_b")}
OBJETIVO = {"interaccion": "consumo_final_kwh", "pca": "indice_respuesta"}
DOMINIOS = {"interaccion": {"horas_previstas": (0, 24), "potencia_prevista_kw": (0, 20),
                            "lectura_cierre_kwh": (0, 2000), "consumo_final_kwh": (0, 1000)},
            "pca": {"senal_a": (0, 100), "senal_b": (0, 100), "indice_respuesta": (0, 100)}}
CANDIDATOS = {"interaccion": ("mediana", "originales", "interaccion"),
              "pca": ("mediana", "completa", "pca1", "pca2")}
TOLERANCIA_MAE = 1e-10


def leer_csv(ruta, nombre):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    columnas = {"caso_id", *DOMINIOS[nombre]}
    if lector.fieldnames is None or len(lector.fieldnames) != len(columnas) or set(lector.fieldnames) != columnas:
        raise ValueError("Columnas incorrectas, ausentes o repetidas.")
    filas = []
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Se requieren filas completas, sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        for c, (a, b) in DOMINIOS[nombre].items():
            fila[c] = float(fila[c])
            if not math.isfinite(fila[c]) or not a <= fila[c] <= b:
                raise ValueError("Valor no finito o fuera del dominio declarado.")
        filas.append(fila)
    if not filas:
        raise ValueError("Cada partición debe contener casos.")
    return filas, hashlib.sha256(contenido).hexdigest()


def matriz(filas, nombre, campos=None):
    campos = ENTRADAS[nombre] if campos is None else tuple(campos)
    if not campos or any(c not in ENTRADAS[nombre] for c in campos):
        raise ValueError("Solo se permiten entradas previas declaradas; identificador, cierre y objetivo quedan excluidos.")
    return np.array([[f[c] for c in campos] for f in filas], dtype=float)


def caracteristicas(x, candidato):
    return np.column_stack((x, x[:, 0] * x[:, 1])) if candidato == "interaccion" else x.copy()


def crear_modelo(candidato):
    if candidato == "mediana":
        return DummyRegressor(strategy="median")
    pasos = [("escala", StandardScaler())]
    if candidato in ("pca1", "pca2"):
        pasos.append(("pca", PCA(n_components=int(candidato[-1]), svd_solver="full", whiten=False)))
    pasos.append(("regresion", LinearRegression(fit_intercept=True)))
    return Pipeline(pasos)


def resumen(modelo, nombre, candidato):
    if candidato == "mediana":
        return {"tipo": "mediana", "valor": float(modelo.constant_[0, 0]), "dimension_regresion": 0}
    escala, regresion = modelo.named_steps["escala"], modelo.named_steps["regresion"]
    nombres = [*ENTRADAS[nombre], *(["energia_nominal_kwh"] if candidato == "interaccion" else [])]
    resultado = {"tipo": "Pipeline", "caracteristicas_antes_de_escalar": nombres,
                 "escala": {"media": escala.mean_.tolist(), "varianza": escala.var_.tolist(), "escala": escala.scale_.tolist()},
                 "regresion": {"intercepto": float(regresion.intercept_), "coeficientes": regresion.coef_.tolist(),
                               "rango": int(regresion.rank_), "singulares": regresion.singular_.tolist(),
                               "parametros": regresion.get_params()},
                 "dimension_regresion": int(regresion.n_features_in_)}
    if "pca" in modelo.named_steps:
        pca = modelo.named_steps["pca"]
        resultado["pca"] = {"parametros": pca.get_params(), "media": pca.mean_.tolist(),
                            "componentes": pca.components_.tolist(), "varianza": pca.explained_variance_.tolist(),
                            "proporcion_varianza": pca.explained_variance_ratio_.tolist(),
                            "singulares": pca.singular_values_.tolist()}
    return resultado


def representar(modelo, x):
    z = modelo.named_steps["escala"].transform(x)
    if "pca" not in modelo.named_steps:
        return z, z.copy(), z
    pca = modelo.named_steps["pca"]
    t = pca.transform(z)
    return z, pca.inverse_transform(t), t


def evaluar(modelo, candidato, filas, informe):
    nombre = informe["experimento"]
    x = matriz(filas, nombre)
    features = caracteristicas(x, candidato)
    pred = modelo.predict(features).tolist()
    y = [f[OBJETIVO[nombre]] for f in filas]
    metricas = metricas_regresion(y, pred)
    sst = sum((v - np.mean(y))**2 for v in y)
    metricas["r2"] = None if len(y) < 2 or sst == 0 else float(1 - sum((a-b)**2 for a, b in zip(y, pred))/sst)
    reconstruccion = None
    t = None
    if nombre == "pca" and candidato != "mediana":
        z, z_recon, t = representar(modelo, features)
        error_z = ((z-z_recon)**2).mean(axis=1)
        reconstruccion = modelo.named_steps["escala"].inverse_transform(z_recon)
        metricas["mse_reconstruccion_z"] = float(error_z.mean())
        metricas["mse_reconstruccion_original"] = float(((x-reconstruccion)**2).mean())
    else:
        metricas["mse_reconstruccion_z"] = None
        metricas["mse_reconstruccion_original"] = None
    registros = []
    representaciones = []
    for i, (fila, real, estimado) in enumerate(zip(filas, y, pred)):
        registro = {"caso_id": fila["caso_id"], **{c: fila[c] for c in ENTRADAS[nombre]},
                    "real": real, "prediccion": estimado, "residuo": real-estimado,
                    "fuera_rango": any(not a <= fila[c] <= b for c, (a, b) in informe["rangos_entrenamiento"].items())}
        registros.append(registro)
        if reconstruccion is not None:
            representaciones.append({"caso_id": fila["caso_id"], "coordenadas": t[i].tolist(),
                                     "reconstruccion": reconstruccion[i].tolist(), "error_cuadrado_medio_z": float(error_z[i])})
    return {"metricas": metricas, "predicciones": registros, "representaciones": representaciones}


def seleccionar(validacion, candidatos):
    minimo = min(validacion[c]["metricas"]["mae"] for c in candidatos)
    return next(c for c in candidatos if validacion[c]["metricas"]["mae"] <= minimo + TOLERANCIA_MAE)


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False):
    with threadpool_limits(limits=1):
        return _ejecutar(nombre, Path(carpeta), evaluar_prueba)


def _ejecutar(nombre, carpeta, evaluar_prueba):
    if nombre not in CANDIDATOS:
        raise ValueError("Experimento desconocido.")
    datos, fuentes = {}, {}
    def cargar(fase):
        filas, sha = leer_csv(carpeta / f"{fase}.csv", nombre)
        ids = {f["caso_id"] for anteriores in datos.values() for f in anteriores}
        for fila in filas:
            if fila["caso_id"] in ids:
                raise ValueError("Identificador repetido dentro o entre particiones.")
            ids.add(fila["caso_id"])
        datos[fase] = filas
        fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": sha, "n": len(filas)}
    cargar("entrenamiento")
    cargar("validacion")
    x = matriz(datos["entrenamiento"], nombre)
    y = [f[OBJETIVO[nombre]] for f in datos["entrenamiento"]]
    if len(x) < 4:
        raise ValueError("Se necesitan al menos cuatro casos de entrenamiento.")
    informe = {"protocolo": "representaciones-v1", "experimento": nombre,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__,
                            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
               "entradas": list(ENTRADAS[nombre]), "objetivo": OBJETIVO[nombre],
               "columnas_excluidas": ["caso_id", OBJETIVO[nombre], *(["lectura_cierre_kwh"] if nombre == "interaccion" else [])],
               "fuentes": fuentes, "modelos": {}, "prueba": None,
               "rangos_entrenamiento": {c: [float(x[:, j].min()), float(x[:, j].max())] for j, c in enumerate(ENTRADAS[nombre])},
               "criterio": {"metrica": "mae", "sentido": "minimizar", "conjunto": "validacion", "reajuste": False,
                            "tolerancia_absoluta": TOLERANCIA_MAE, "orden_desempate": list(CANDIDATOS[nombre])},
               "azar_ajuste": "Sin muestreo ni inicialización aleatoria; PCA usa SVD completa."}
    modelos = {}
    for c in CANDIDATOS[nombre]:
        features = caracteristicas(x, c)
        if c != "mediana" and np.linalg.matrix_rank(np.column_stack((np.ones(len(x)), features))) < features.shape[1]+1:
            raise ValueError("Representación sin rango suficiente: revisar constantes o columnas redundantes.")
        modelos[c] = crear_modelo(c).fit(features, y)
        informe["modelos"][c] = resumen(modelos[c], nombre, c)
    for fase in ("entrenamiento", "validacion"):
        informe[fase] = {c: evaluar(m, c, datos[fase], informe) for c, m in modelos.items()}
    informe["seleccionado"] = seleccionar(informe["validacion"], CANDIDATOS[nombre])
    if evaluar_prueba:
        cargar("prueba")
        c = informe["seleccionado"]
        informe["prueba"] = {"candidato": c, **evaluar(modelos[c], c, datos["prueba"], informe)}
    return informe, modelos


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    for fase in ("entrenamiento", "validacion", "prueba"):
        if informe[fase] is None:
            continue
        evaluaciones = {informe["seleccionado"]: informe[fase]} if fase == "prueba" else informe[fase]
        filas = [dict(candidato=c, **r) for c, ev in evaluaciones.items() for r in ev["predicciones"]]
        with (destino / f"predicciones_{fase}.csv").open("x", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
    with (destino / "informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

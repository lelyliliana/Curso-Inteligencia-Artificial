"""Agrupamiento inductivo y alertas con ajuste, selección y cierre separados."""

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
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion, resultado_binario

ENTRADAS = {"grupos": ("horas_uso", "consumo_kwh"), "anomalias": ("senal_a", "senal_b")}
LIMITES = {"grupos": (24., 500.), "anomalias": (100., 100.)}
KS = (2, 3, 4)
CANDIDATOS = ("sin_alertas", "distancia_centro", "aislamiento")
SEMILLAS_ESTABILIDAD = (29, 47)


def huella(valor):
    return hashlib.sha256(json.dumps(valor, sort_keys=True, allow_nan=False).encode()).hexdigest()


def leer_csv(ruta, nombre, fase):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    etiquetado = nombre == "anomalias" and fase in ("validacion", "prueba")
    columnas = {"caso_id", *ENTRADAS[nombre], *(["anomalia_sintetica"] if etiquetado else [])}
    if lector.fieldnames is None or len(lector.fieldnames) != len(columnas) or set(lector.fieldnames) != columnas:
        raise ValueError("Columnas incorrectas, repetidas o ausentes.")
    filas = []
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Cada fila requiere todos sus campos, sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        for campo, maximo in zip(ENTRADAS[nombre], LIMITES[nombre]):
            fila[campo] = float(fila[campo])
            if not math.isfinite(fila[campo]) or not 0 <= fila[campo] <= maximo:
                raise ValueError("Entrada no finita o fuera del dominio declarado.")
        if etiquetado:
            if fila["anomalia_sintetica"] not in ("0", "1"):
                raise ValueError("La referencia sintética debe ser 0 o 1.")
            fila["anomalia_sintetica"] = int(fila["anomalia_sintetica"])
        filas.append(fila)
    if not filas:
        raise ValueError("La partición está vacía.")
    return filas, hashlib.sha256(contenido).hexdigest()


def matriz(filas, nombre):
    return np.array([[f[c] for c in ENTRADAS[nombre]] for f in filas], dtype=float)


def cargar(fase, nombre, carpeta, datos, fuentes):
    filas, sha = leer_csv(Path(carpeta) / f"{fase}.csv", nombre, fase)
    ids_previos = {f["caso_id"] for filas_previas in datos.values() for f in filas_previas}
    for fila in filas:
        if fila["caso_id"] in ids_previos:
            raise ValueError("Identificador repetido dentro o entre particiones.")
        ids_previos.add(fila["caso_id"])
    datos[fase] = filas
    fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": sha, "n": len(filas)}
    if "anomalia_sintetica" in filas[0]:
        fuentes[fase]["positivos"] = sum(f["anomalia_sintetica"] for f in filas)
    return matriz(filas, nombre)


def iniciar(nombre, carpeta, semilla):
    if type(semilla) is not int or not 0 <= semilla < 2 ** 32:
        raise ValueError("La semilla debe ser un entero entre 0 y 2**32−1.")
    datos, fuentes = {}, {}
    x = cargar("entrenamiento", nombre, carpeta, datos, fuentes)
    if len(x) < 5 or len(np.unique(x, axis=0)) < 5:
        raise ValueError("Se requieren al menos cinco filas distintas en entrenamiento.")
    escala = StandardScaler().fit(x)
    informe = {"protocolo": "no-supervisado-v1", "experimento": nombre, "semilla": semilla,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__,
                            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
               "entradas": list(ENTRADAS[nombre]), "fuentes": fuentes,
               "escala": {"media": escala.mean_.tolist(), "varianza": escala.var_.tolist(), "escala": escala.scale_.tolist()},
               "rangos_entrenamiento": {c: [float(x[:, j].min()), float(x[:, j].max())] for j, c in enumerate(ENTRADAS[nombre])},
               "modelos": {}, "prueba": None}
    return datos, informe, escala


def registros_base(filas, informe):
    return [{"caso_id": f["caso_id"], **{c: f[c] for c in informe["entradas"]},
             "fuera_rango": any(not a <= f[c] <= b for c, (a, b) in informe["rangos_entrenamiento"].items())} for f in filas]


def silueta(x, grupos):
    cantidad = len(set(grupos))
    return float(silhouette_score(x, grupos)) if 2 <= cantidad < len(x) else None


def elegir(evaluaciones, candidatos, metrica):
    permitidos = [c for c in candidatos if evaluaciones[c]["metricas"][metrica] is not None]
    if not permitidos:
        raise ValueError(f"No hay candidatos con {metrica} definida para seleccionar.")
    return max(permitidos, key=lambda c: evaluaciones[c]["metricas"][metrica])


def nuevo_kmeans(k, semilla):
    return KMeans(n_clusters=k, init="k-means++", n_init=10, max_iter=300,
                  tol=1e-4, algorithm="lloyd", random_state=semilla)


def evaluar_grupos(modelo, escala, filas, informe):
    z = escala.transform(matriz(filas, "grupos"))
    grupos = modelo.predict(z)
    d2 = ((z - modelo.cluster_centers_[grupos]) ** 2).sum(axis=1)
    registros = registros_base(filas, informe)
    for r, grupo, distancia in zip(registros, grupos, d2):
        r.update(grupo=int(grupo), distancia_centro=float(np.sqrt(distancia)))
    return {"metricas": {"n": len(filas), "distancia_cuadrada_media": float(d2.mean()),
                         "silueta": silueta(z, grupos),
                         "tamanos": [int(np.sum(grupos == i)) for i in range(modelo.n_clusters)]},
            "predicciones": registros}


def ejecutar_grupos(carpeta, evaluar_prueba=False, semilla=14):
    # Limita BLAS/OpenMP en este pequeño experimento, también al invocarlo desde pruebas.
    with threadpool_limits(limits=1):
        return _grupos(carpeta, evaluar_prueba, semilla)


def _grupos(carpeta, evaluar_prueba, semilla):
    datos, informe, escala = iniciar("grupos", carpeta, semilla)
    x_val = cargar("validacion", "grupos", carpeta, datos, informe["fuentes"])
    z = escala.transform(matriz(datos["entrenamiento"], "grupos"))
    modelos = {f"k{k}": nuevo_kmeans(k, semilla).fit(z) for k in KS}
    for c, modelo in modelos.items():
        informe["modelos"][c] = {"parametros": modelo.get_params(), "centros_z": modelo.cluster_centers_.tolist(),
                                  "centros_originales": escala.inverse_transform(modelo.cluster_centers_).tolist(),
                                  "inercia_entrenamiento": float(modelo.inertia_), "iteraciones": int(modelo.n_iter_)}
    for fase in ("entrenamiento", "validacion"):
        informe[fase] = {c: evaluar_grupos(m, escala, datos[fase], informe) for c, m in modelos.items()}
    informe["criterio"] = {"metrica": "silueta", "conjunto": "validacion", "orden_desempate": list(modelos),
                            "sentido": "maximizar", "reajuste": False}
    informe["seleccionado"] = elegir(informe["validacion"], modelos, "silueta")
    informe["estabilidad"] = {}
    for c, modelo in modelos.items():
        base = modelo.predict(escala.transform(x_val))
        informe["estabilidad"][c] = [{"semilla": s, "ari": float(adjusted_rand_score(base,
                                        nuevo_kmeans(modelo.n_clusters, s).fit(z).predict(escala.transform(x_val))))}
                                     for s in SEMILLAS_ESTABILIDAD]
    if evaluar_prueba:
        cargar("prueba", "grupos", carpeta, datos, informe["fuentes"])
        c = informe["seleccionado"]
        informe["prueba"] = {"candidato": c, **evaluar_grupos(modelos[c], escala, datos["prueba"], informe)}
    return informe, {"escala": escala, "modelos": modelos}


def umbral_orden(puntuaciones, q=.95):
    valores = np.asarray(puntuaciones, dtype=float)
    if valores.ndim != 1 or not len(valores) or not np.isfinite(valores).all() or not 0 < q <= 1:
        raise ValueError("Puntuaciones finitas no vacías y cuantil entre 0 y 1 requeridos.")
    return float(np.sort(valores)[math.ceil(q * len(valores)) - 1])


def puntuar(nombre, modelo, z):
    if nombre == "sin_alertas":
        return None
    if nombre == "distancia_centro":
        return np.linalg.norm(z, axis=1)
    return -modelo.score_samples(z)  # Mayor = más inusual; no es probabilidad.


def evaluar_anomalias(nombre, modelo, umbral, escala, filas, informe):
    puntuaciones = puntuar(nombre, modelo, escala.transform(matriz(filas, "anomalias")))
    alertas = np.zeros(len(filas), dtype=int) if puntuaciones is None else (puntuaciones > umbral).astype(int)
    registros = registros_base(filas, informe)
    reales = [f["anomalia_sintetica"] for f in filas] if "anomalia_sintetica" in filas[0] else None
    for i, r in enumerate(registros):
        r.update(puntuacion=None if puntuaciones is None else float(puntuaciones[i]), umbral=umbral, alerta=int(alertas[i]))
        if reales is not None:
            r.update(real=reales[i], resultado=resultado_binario(reales[i], int(alertas[i])))
    metricas = {"n": len(filas), "alertas": int(alertas.sum()), "fraccion_alertas": float(alertas.mean())}
    if reales is not None:
        metricas.update(metricas_clasificacion(reales, alertas.tolist()))
    return {"metricas": metricas, "predicciones": registros}


def ejecutar_anomalias(carpeta, evaluar_prueba=False, semilla=14):
    with threadpool_limits(limits=1):
        return _anomalias(carpeta, evaluar_prueba, semilla)


def _anomalias(carpeta, evaluar_prueba, semilla):
    datos, informe, escala = iniciar("anomalias", carpeta, semilla)
    x_cal = cargar("calibracion", "anomalias", carpeta, datos, informe["fuentes"])
    z = escala.transform(matriz(datos["entrenamiento"], "anomalias"))
    aislamiento = IsolationForest(n_estimators=64, max_samples=min(64, len(z)), contamination="auto",
                                  max_features=1.0, bootstrap=False, random_state=semilla, n_jobs=1).fit(z)
    modelos = {"sin_alertas": None, "distancia_centro": None, "aislamiento": aislamiento}
    umbrales = {c: None if c == "sin_alertas" else umbral_orden(puntuar(c, m, escala.transform(x_cal)))
               for c, m in modelos.items()}
    for c, modelo in modelos.items():
        resumen = {"tipo": c, "umbral": umbrales[c]}
        if modelo is not None:
            estructuras = [{k: getattr(t.tree_, k).tolist() for k in
                            ("children_left", "children_right", "feature", "threshold", "n_node_samples")}
                           for t in modelo.estimators_]
            resumen.update(parametros=modelo.get_params(), sha256_estructuras=huella(estructuras))
        informe["modelos"][c] = resumen
    informe["regla_alerta"] = {"puntuacion": "mayor significa más inusual; no es probabilidad", "comparacion": ">",
                               "q": .95, "umbral": "estadístico de orden ceil(q*n) en calibracion", "usa_predict_sklearn": False}
    cargar("validacion", "anomalias", carpeta, datos, informe["fuentes"])
    if {f["anomalia_sintetica"] for f in datos["validacion"]} != {0, 1}:
        raise ValueError("Validación requiere ambas clases para este protocolo de comparación.")
    for fase in ("entrenamiento", "calibracion", "validacion"):
        informe[fase] = {c: evaluar_anomalias(c, m, umbrales[c], escala, datos[fase], informe) for c, m in modelos.items()}
    informe["criterio"] = {"metrica": "f1", "conjunto": "validacion", "orden_desempate": list(modelos),
                            "sentido": "maximizar", "reajuste": False, "usa_referencia_sintetica_para_seleccionar": True}
    informe["seleccionado"] = elegir(informe["validacion"], CANDIDATOS, "f1")
    if evaluar_prueba:
        cargar("prueba", "anomalias", carpeta, datos, informe["fuentes"])
        c = informe["seleccionado"]
        informe["prueba"] = {"candidato": c, **evaluar_anomalias(c, modelos[c], umbrales[c], escala, datos["prueba"], informe)}
    return informe, {"escala": escala, "modelos": modelos}


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    for fase in ("entrenamiento", "calibracion", "validacion", "prueba"):
        if informe.get(fase) is None:
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

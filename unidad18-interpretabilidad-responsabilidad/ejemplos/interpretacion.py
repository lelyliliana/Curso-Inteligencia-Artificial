"""Inspección de dos modelos fijados antes de leer validación y prueba."""

import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
import sklearn
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent/"unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion, metricas_regresion

ENTRADAS = {"consumo": ("horas", "minutos", "temperatura_c"), "alertas": ("lectura",)}
OBJETIVO = {"consumo": "consumo_kwh", "alertas": "requiere_revision"}
GRUPOS = ("estandar", "desplazado", "escaso", "nuevo")
SEMILLA_PERMUTACION = 1818
REPETICIONES = 30


def leer_csv(ruta, nombre):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig")))
    columnas = {"caso_id", OBJETIVO[nombre], *ENTRADAS[nombre]}
    if nombre == "alertas":
        columnas.add("grupo")
    if not lector.fieldnames or len(lector.fieldnames) != len(columnas) or set(lector.fieldnames) != columnas:
        raise ValueError(f"Esquema incorrecto en {ruta}.")
    filas, vistos = [], set()
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Fila incompleta o con columnas adicionales.")
        fila = {k: v.strip() for k, v in fila.items()}
        if fila["caso_id"] in vistos:
            raise ValueError("ID repetido dentro de una partición.")
        vistos.add(fila["caso_id"])
        for c in (*ENTRADAS[nombre], OBJETIVO[nombre]):
            fila[c] = float(fila[c])
            if not np.isfinite(fila[c]):
                raise ValueError("Las entradas y objetivos deben ser finitos.")
        if nombre == "consumo":
            if not (0 <= fila["horas"] <= 24 and 0 <= fila["minutos"] <= 1440
                    and -50 <= fila["temperatura_c"] <= 100 and fila["consumo_kwh"] >= 0):
                raise ValueError("Consumo: valor fuera del dominio declarado.")
            if not np.isclose(fila["minutos"], 60*fila["horas"], rtol=0, atol=1e-7):
                raise ValueError("El laboratorio exige minutos = 60 × horas.")
        else:
            if fila["grupo"] not in GRUPOS or not 0 <= fila["lectura"] <= 1 or fila[OBJETIVO[nombre]] not in (0, 1):
                raise ValueError("Alerta: grupo, lectura o etiqueta fuera del dominio.")
            fila[OBJETIVO[nombre]] = int(fila[OBJETIVO[nombre]])
        filas.append(fila)
    if not filas:
        raise ValueError("La partición no puede estar vacía.")
    return filas, {"archivo": Path(ruta).name, "n": len(filas), "sha256": hashlib.sha256(contenido).hexdigest()}


def matriz(filas, nombre):
    return np.array([[f[c] for c in ENTRADAS[nombre]] for f in filas], dtype=float)


def ajustar(filas, nombre):
    x, y = matriz(filas, nombre), [f[OBJETIVO[nombre]] for f in filas]
    if nombre == "consumo":
        modelo = make_pipeline(StandardScaler(), LinearRegression())
        base = DummyRegressor(strategy="mean")
    else:
        if set(y) != {0, 1}:
            raise ValueError("El árbol requiere ambas clases en entrenamiento.")
        modelo = DecisionTreeClassifier(max_depth=2, min_samples_leaf=8, random_state=18)
        base = DummyClassifier(strategy="most_frequent")
    modelo.fit(x, y)
    base.fit(x, y)
    return modelo, base


def explicar_lineal(modelo, x):
    """Contribución respecto del vector de medias de entrenamiento; unidades de y."""
    escala, regresor = modelo.steps[0][1], modelo.steps[1][1]
    x = np.asarray(x, dtype=float)
    z = (x-escala.mean_)/escala.scale_
    contribuciones = z*regresor.coef_
    coef_original = regresor.coef_/escala.scale_
    return {"entrada": x.tolist(), "z": z.tolist(), "base": float(regresor.intercept_),
            "contribuciones": contribuciones.tolist(),
            "reconstruccion": float(regresor.intercept_+contribuciones.sum()),
            "prediccion": float(modelo.predict(x.reshape(1, -1))[0]),
            "coef_original": coef_original.tolist(),
            "intercepto_original": float(regresor.intercept_-coef_original @ escala.mean_)}


def permutar(modelo, x, y, bloques, repeticiones=REPETICIONES, semilla=SEMILLA_PERMUTACION):
    """MAE permutado − MAE original; mismos índices en todos los bloques por repetición."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 2 or y.shape != (len(x),) or len(x) < 2 or repeticiones < 1:
        raise ValueError("La permutación requiere X, y compatibles y repeticiones positivas.")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("La permutación requiere valores finitos.")
    for cols in bloques.values():
        if not cols or len(set(cols)) != len(cols) or any(c < 0 or c >= x.shape[1] for c in cols):
            raise ValueError("Bloque de columnas inválido.")
    original = float(np.mean(np.abs(y-modelo.predict(x))))
    rng = np.random.Generator(np.random.PCG64(semilla))
    indices = [rng.permutation(len(x)) for _ in range(repeticiones)]
    resultado = {}
    for etiqueta, cols in bloques.items():
        deltas = []
        for orden in indices:
            cambiado = x.copy()
            cambiado[:, cols] = x[orden][:, cols]
            deltas.append(float(np.mean(np.abs(y-modelo.predict(cambiado))))-original)
        resultado[etiqueta] = {"columnas": list(cols), "deltas": deltas,
                               "media": float(np.mean(deltas)), "desviacion": float(np.std(deltas, ddof=0))}
    return {"mae_original": original, "repeticiones": repeticiones, "semilla": semilla, "bloques": resultado}


def resumen_binario(y, pred):
    if not y:
        return {"n": 0, "VP": 0, "VN": 0, "FP": 0, "FN": 0, "positivos": 0,
                "exactitud": None, "precision": None, "recobrado": None, "f1": None,
                "negativos": 0, "alertas": 0, "tasa_fp": None, "tasa_fn": None, "tasa_alerta": None}
    m = metricas_clasificacion(y, pred)
    m.update(negativos=m["VN"]+m["FP"], alertas=m["VP"]+m["FP"])
    m["tasa_fp"] = m["FP"]/m["negativos"] if m["negativos"] else None
    m["tasa_fn"] = m["FN"]/m["positivos"] if m["positivos"] else None
    m["tasa_alerta"] = m["alertas"]/m["n"]
    return m


def auditar(filas, pred):
    if len(filas) != len(pred) or not filas:
        raise ValueError("Auditoría: se requieren filas y decisiones de igual tamaño no vacío.")
    if any(f["grupo"] not in GRUPOS for f in filas):
        raise ValueError("Grupo desconocido.")
    grupos = {}
    for grupo in GRUPOS:
        ids = [i for i, f in enumerate(filas) if f["grupo"] == grupo]
        m = resumen_binario([filas[i]["requiere_revision"] for i in ids], [pred[i] for i in ids])
        m["fraccion_muestra"] = len(ids)/len(filas)
        grupos[grupo] = m
    return grupos


def explicar_arbol(modelo, x):
    """Reconstruye reglas y frecuencia de hoja; sklearn compara entradas float32."""
    entrada = np.asarray(x, dtype=np.float32)
    arbol, nodo, pasos = modelo.tree_, 0, []
    while arbol.children_left[nodo] != arbol.children_right[nodo]:
        c = int(arbol.feature[nodo])
        limite = float(arbol.threshold[nodo])
        # Convertir el escalar a float evita redondear también el umbral a
        # float32 por las reglas de promoción de NumPy 2.
        izquierda = float(entrada[c]) <= limite
        siguiente = int(arbol.children_left[nodo] if izquierda else arbol.children_right[nodo])
        pasos.append({"nodo": nodo, "columna": c, "valor_float32": float(entrada[c]), "umbral": limite,
                      "operador": "<=" if izquierda else ">", "siguiente": siguiente})
        nodo = siguiente
    pesos = arbol.value[nodo, 0]
    proporciones = pesos/pesos.sum()
    indice = int(np.argmax(proporciones))
    return {"entrada": np.asarray(x).tolist(), "pasos": pasos, "hoja": nodo,
            "n_entrenamiento_hoja": int(arbol.n_node_samples[nodo]),
            "fracciones_clase": proporciones.tolist(), "clases": modelo.classes_.tolist(),
            "clase_reconstruida": int(modelo.classes_[indice]), "prediccion": int(modelo.predict([x])[0])}


def estado_modelo(modelo, nombre):
    if nombre == "consumo":
        e, r = modelo.steps[0][1], modelo.steps[1][1]
        return {"tipo": "StandardScaler + LinearRegression", "media": e.mean_.tolist(), "escala": e.scale_.tolist(),
                "coef": r.coef_.tolist(), "intercepto": float(r.intercept_), "rango": int(r.rank_),
                "singulares": r.singular_.tolist(), "parametros": {"fit_intercept": True, "with_mean": True, "with_std": True}}
    a = modelo.tree_
    return {"tipo": "DecisionTreeClassifier", "parametros": modelo.get_params(), "clases": modelo.classes_.tolist(),
            "hijo_izquierdo": a.children_left.tolist(), "hijo_derecho": a.children_right.tolist(),
            "variable": a.feature.tolist(), "umbral": a.threshold.tolist(), "valor": a.value.tolist(),
            "n_muestras": a.n_node_samples.tolist()}


def evaluar(modelo, filas, nombre):
    pred = modelo.predict(matriz(filas, nombre)).tolist()
    y = [f[OBJETIVO[nombre]] for f in filas]
    metricas = metricas_regresion(y, pred) if nombre == "consumo" else resumen_binario(y, pred)
    registros = [{"caso_id": f["caso_id"], "real": f[OBJETIVO[nombre]], "prediccion": p,
                  **({"grupo": f["grupo"]} if nombre == "alertas" else {})} for f, p in zip(filas, pred)]
    return {"metricas": metricas, "predicciones": registros,
            "grupos": auditar(filas, pred) if nombre == "alertas" else None}


def ejecutar_experimento(nombre, datos=None, evaluar_prueba=False):
    if nombre not in ENTRADAS:
        raise ValueError("Laboratorio desconocido.")
    datos = Path(datos) if datos is not None else UNIDAD/"datos"/nombre
    with threadpool_limits(limits=1):
        train, ft = leer_csv(datos/"entrenamiento.csv", nombre)
        # El modelo se fija y ajusta ANTES de leer cualquier fila de validación.
        modelo, base = ajustar(train, nombre)
        val, fv = leer_csv(datos/"validacion.csv", nombre)
        ids = {f["caso_id"] for f in train}
        if ids.intersection(f["caso_id"] for f in val):
            raise ValueError("IDs compartidos entre particiones.")
        ids.update(f["caso_id"] for f in val)
        informe = {"laboratorio": nombre, "protocolo": "u18-v1-modelos-fijos", "entradas": list(ENTRADAS[nombre]),
                   "versiones": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__},
                   "fuentes": {"entrenamiento": ft, "validacion": fv}, "estado": estado_modelo(modelo, nombre),
                   "entrenamiento": evaluar(modelo, train, nombre), "validacion": evaluar(modelo, val, nombre),
                   "linea_base_validacion": evaluar(base, val, nombre), "prueba": None}
        if nombre == "consumo":
            caso = min(val, key=lambda f: f["caso_id"])
            informe["caso_local"] = {"caso_id": caso["caso_id"], **explicar_lineal(modelo, matriz([caso], nombre)[0])}
            informe["permutacion"] = permutar(modelo, matriz(val, nombre), [f[OBJETIVO[nombre]] for f in val],
                                              {"horas": [0], "minutos": [1], "temperatura_c": [2], "horas_y_minutos": [0, 1]})
        else:
            # Caso fijado por ID en un grupo; no se elige por el error observado.
            candidatos = [f for f in val if f["grupo"] == "desplazado"] or val
            caso = min(candidatos, key=lambda f: f["caso_id"])
            informe["caso_local"] = {"caso_id": caso["caso_id"], **explicar_arbol(modelo, matriz([caso], nombre)[0])}
            informe["permutacion"] = None
        # Esta apertura ocurre después de terminar los diagnósticos de desarrollo.
        if evaluar_prueba:
            prueba, fp = leer_csv(datos/"prueba.csv", nombre)
            if ids.intersection(f["caso_id"] for f in prueba):
                raise ValueError("IDs compartidos entre particiones.")
            informe["fuentes"]["prueba"] = fp
            informe["prueba"] = evaluar(modelo, prueba, nombre)
    return informe


def exportar(informe, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    (salida/"informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for particion in ("entrenamiento", "validacion", "prueba"):
        if informe[particion] is not None:
            filas = informe[particion]["predicciones"]
            with (salida/f"predicciones_{particion}.csv").open("w", encoding="utf-8", newline="") as f:
                escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
                escritor.writeheader()
                escritor.writerows(filas)

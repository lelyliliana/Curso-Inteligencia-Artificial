"""Comparaciones de árboles y ensambles con datos y selección separados."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys

try:
    import numpy as np
    import scipy
    import sklearn
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier, export_text
except ImportError as error:
    raise RuntimeError("Instala dependencias: python -m pip install -r unidad13-arboles-ensambles/requirements.txt") from error

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion, resultado_binario  # noqa: E402

ENTRADAS = {"franja": ("senal_a",), "region": ("senal_a", "senal_b")}
CANDIDATOS = {"franja": ("mayoria", "arbol_1", "arbol_3", "arbol_libre"),
              "region": ("mayoria", "arbol", "bagging", "bosque")}


def gini(ys):
    if not ys or any(type(y) is not int or y not in (0, 1) for y in ys):
        raise ValueError("Se requieren etiquetas enteras 0/1 no vacías.")
    p = sum(ys) / len(ys)
    return 2 * p * (1 - p)


def cortes_gini(xs, ys, min_hoja=1):
    """Referencia exhaustiva de un solo nodo y una entrada; no entrena un árbol."""
    gini(ys)
    if len(xs) != len(ys) or any(type(x) not in (int, float) or not math.isfinite(x) for x in xs):
        raise ValueError("Entradas finitas y etiquetas deben tener igual longitud.")
    if type(min_hoja) is not int or min_hoja < 1:
        raise ValueError("El mínimo por hoja debe ser un entero positivo.")
    unicos, resultados = sorted(set(xs)), []
    for a, b in zip(unicos, unicos[1:]):
        corte = a / 2 + b / 2
        izquierda = [y for x, y in zip(xs, ys) if x <= corte]
        derecha = [y for x, y in zip(xs, ys) if x > corte]
        if min(len(izquierda), len(derecha)) < min_hoja:
            continue
        ponderado = (len(izquierda) * gini(izquierda) + len(derecha) * gini(derecha)) / len(ys)
        resultados.append({"corte": corte, "n_izquierda": len(izquierda), "n_derecha": len(derecha),
                           "gini_hijos": ponderado, "reduccion": gini(ys) - ponderado})
    return resultados


def crear_modelos(nombre, semilla=13):
    if nombre not in CANDIDATOS or type(semilla) is not int or not 0 <= semilla < 2 ** 32:
        raise ValueError("Experimento válido y semilla entera entre 0 y 2**32−1 requeridos.")
    modelos = {"mayoria": DummyClassifier(strategy="prior")}
    def arbol(profundidad, hoja):
        return DecisionTreeClassifier(criterion="gini", splitter="best", max_depth=profundidad,
                                      min_samples_leaf=hoja, max_features=None, random_state=semilla)
    if nombre == "franja":
        modelos.update(arbol_1=arbol(1, 1), arbol_3=arbol(3, 5), arbol_libre=arbol(None, 1))
    else:
        modelos["arbol"] = arbol(6, 2)
        modelos["bagging"] = BaggingClassifier(estimator=arbol(6, 2), n_estimators=31,
                                               max_samples=1.0, max_features=1.0, bootstrap=True,
                                               bootstrap_features=False, random_state=semilla, n_jobs=1)
        modelos["bosque"] = RandomForestClassifier(n_estimators=31, criterion="gini", max_depth=6,
                                                   min_samples_leaf=2, max_features=1, bootstrap=True,
                                                   max_samples=None, random_state=semilla, n_jobs=1)
    return modelos


def huella_json(valor):
    texto = json.dumps(valor, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def estructura(arbol):
    t = arbol.tree_
    return {campo: getattr(t, campo).tolist() for campo in
            ("children_left", "children_right", "feature", "threshold", "value", "n_node_samples", "weighted_n_node_samples")}


def resumen_modelo(modelo):
    parametros = modelo.get_params(deep=True)
    # El objeto estimator no es JSON; sus parámetros aparecen como estimator__... .
    parametros = {k: v for k, v in parametros.items() if k != "estimator"}
    resultado = {"tipo": type(modelo).__name__, "parametros": parametros,
                 "clases": modelo.classes_.tolist()}
    if isinstance(modelo, DummyClassifier):
        resultado["frecuencias"] = modelo.class_prior_.tolist()
        return resultado
    arboles = [modelo] if isinstance(modelo, DecisionTreeClassifier) else modelo.estimators_
    resultado["arboles"] = [{"profundidad": int(a.get_depth()), "hojas": int(a.get_n_leaves()),
                             "nodos": int(a.tree_.node_count), "semilla": int(a.random_state),
                             "sha256_estructura": huella_json(estructura(a))} for a in arboles]
    if not isinstance(modelo, DecisionTreeClassifier):
        muestras = modelo.estimators_samples_
        resultado["bootstrap"] = [{"extracciones": len(v), "casos_distintos": len(set(v.tolist())),
                                    "sha256_indices": huella_json(v.tolist())} for v in muestras]
        if isinstance(modelo, BaggingClassifier):
            resultado["variables_por_arbol"] = [v.tolist() for v in modelo.estimators_features_]
    return resultado


def leer_csv(ruta, nombre):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    columnas = {"caso_id", *ENTRADAS[nombre], "revision_confirmada"}
    if lector.fieldnames is None or len(lector.fieldnames) != len(columnas) or set(lector.fieldnames) != columnas:
        raise ValueError("Columnas incorrectas, repetidas o ausentes para este experimento.")
    filas = []
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Las filas deben estar completas y sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        for campo in ENTRADAS[nombre]:
            fila[campo] = float(fila[campo])
            if not math.isfinite(fila[campo]) or not 0 <= fila[campo] <= 100:
                raise ValueError("Las señales deben ser finitas y estar entre 0 y 100.")
        if fila["revision_confirmada"] not in ("0", "1"):
            raise ValueError("La etiqueta debe ser 0 o 1.")
        fila["revision_confirmada"] = int(fila["revision_confirmada"])
        filas.append(fila)
    if not filas:
        raise ValueError("Cada partición debe contener casos.")
    return filas, hashlib.sha256(contenido).hexdigest()


def validar_ids(particiones):
    vistos = set()
    for filas in particiones.values():
        for fila in filas:
            if fila["caso_id"] in vistos:
                raise ValueError("Identificador repetido dentro o entre particiones.")
            vistos.add(fila["caso_id"])


def matriz(filas, entradas):
    return np.asarray([[f[c] for c in entradas] for f in filas], dtype=float)


def fuera_rango(fila, rangos):
    return any(not limites[0] <= fila[campo] <= limites[1] for campo, limites in rangos.items())


def evaluar(modelo, filas, entradas, rangos):
    x = matriz(filas, entradas)
    reales = [f["revision_confirmada"] for f in filas]
    predicciones = modelo.predict(x).astype(int).tolist()
    columna = modelo.classes_.tolist().index(1)
    probabilidades = modelo.predict_proba(x)[:, columna].tolist()
    registros = [{"caso_id": f["caso_id"], **{c: f[c] for c in entradas}, "real": y,
                  "probabilidad_1": p, "prediccion": pred, "resultado": resultado_binario(y, pred),
                  "fuera_rango": fuera_rango(f, rangos)}
                 for f, y, p, pred in zip(filas, reales, probabilidades, predicciones)]
    return {"metricas": metricas_clasificacion(reales, predicciones), "predicciones": registros,
            "fuera_rango": sum(r["fuera_rango"] for r in registros)}


def seleccionar(validacion, candidatos):
    if any(validacion[c]["metricas"]["f1"] is None for c in candidatos):
        raise ValueError("Este protocolo requiere F1 definido para seleccionar.")
    return max(candidatos, key=lambda c: validacion[c]["metricas"]["f1"])


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False, semilla=13, consulta=None):
    modelos = crear_modelos(nombre, semilla)
    entradas, carpeta = ENTRADAS[nombre], Path(carpeta)
    if consulta is not None and (len(consulta) != len(entradas) or
            any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100 for v in consulta)):
        raise ValueError(f"La consulta requiere {len(entradas)} señales finitas entre 0 y 100.")
    datos, fuentes = {}, {}
    def cargar(fase):
        datos[fase], huella = leer_csv(carpeta / f"{fase}.csv", nombre)
        validar_ids(datos)
        ys = [f["revision_confirmada"] for f in datos[fase]]
        if fase != "prueba" and set(ys) != {0, 1}:
            raise ValueError("Entrenamiento y validación requieren ambas clases para este protocolo.")
        fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": huella, "n": len(ys), "positivos": sum(ys)}
    cargar("entrenamiento")
    cargar("validacion")
    x = matriz(datos["entrenamiento"], entradas)
    y = [f["revision_confirmada"] for f in datos["entrenamiento"]]
    rangos = {c: [float(x[:, i].min()), float(x[:, i].max())] for i, c in enumerate(entradas)}
    for modelo in modelos.values():
        modelo.fit(x, y)
    entrenamiento = {c: evaluar(m, datos["entrenamiento"], entradas, rangos) for c, m in modelos.items()}
    validacion = {c: evaluar(m, datos["validacion"], entradas, rangos) for c, m in modelos.items()}
    elegido = seleccionar(validacion, CANDIDATOS[nombre])
    informe = {"protocolo": "arboles-v1", "experimento": nombre, "semilla_modelos": semilla,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__,
                            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
               "entradas": list(entradas), "rangos_entrenamiento": rangos, "fuentes": fuentes,
               "modelos": {c: resumen_modelo(m) for c, m in modelos.items()},
               "criterio": {"metrica": "f1", "clase_positiva": 1, "sentido": "maximizar",
                            "orden_desempate": list(CANDIDATOS[nombre]), "reajuste_con_validacion": False,
                            "decision": "mayor probabilidad; empate de clases a 0"},
               "entrenamiento": entrenamiento, "validacion": validacion, "seleccionado": elegido,
               "prueba": None, "consulta": None,
               "reglas": {c: export_text(m, feature_names=list(entradas), decimals=3)
                          for c, m in modelos.items() if isinstance(m, DecisionTreeClassifier)}}
    if consulta is not None:
        fila = dict(zip(entradas, consulta))
        m = modelos[elegido]
        indice = m.classes_.tolist().index(1)
        informe["consulta"] = {"entradas": fila, "candidato": elegido,
                               "probabilidad_1": float(m.predict_proba([consulta])[0, indice]),
                               "clase": int(m.predict([consulta])[0]), "fuera_rango": fuera_rango(fila, rangos)}
    if evaluar_prueba:
        cargar("prueba")  # Después de ajustar y seleccionar; sin reajuste con validación.
        informe["prueba"] = {"candidato": elegido, **evaluar(modelos[elegido], datos["prueba"], entradas, rangos)}
    return informe, modelos


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    for fase in ("entrenamiento", "validacion", "prueba"):
        if informe[fase] is None:
            continue
        evaluaciones = {informe["seleccionado"]: informe[fase]} if fase == "prueba" else informe[fase]
        registros = [dict(candidato=c, **r) for c, ev in evaluaciones.items() for r in ev["predicciones"]]
        with (destino / f"predicciones_{fase}.csv").open("x", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(registros)
    for nombre, reglas in informe["reglas"].items():
        with (destino / f"reglas_{nombre}.txt").open("x", encoding="utf-8") as archivo:
            archivo.write(reglas)
    with (destino / "informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

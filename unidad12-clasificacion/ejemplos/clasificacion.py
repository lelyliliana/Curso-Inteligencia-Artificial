"""Regresión logística binaria con ajuste, umbral y evaluación separados."""

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
except ImportError as error:
    raise RuntimeError("Instala dependencias: python -m pip install -r unidad12-clasificacion/requirements.txt") from error

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion, resultado_binario  # noqa: E402

CONFIGURACION = {"tasa": 0.2, "iteraciones": 3000, "penalizacion": 0.01}
CANDIDATOS = {
    "equilibrado": ("mayoria", "siempre_1", "logistica_050"),
    "desbalanceado": ("mayoria", "siempre_1", "logistica_050", "logistica_020", "logistica_080"),
}
UMBRALES = {"logistica_050": 0.5, "logistica_020": 0.2, "logistica_080": 0.8}


def vector_finito(valores):
    if not valores or any(type(v) not in (int, float) or not math.isfinite(v) for v in valores):
        raise ValueError("Se requiere una lista no vacía de números finitos.")
    return np.asarray(valores, dtype=float)


def etiquetas(valores, ambas=False):
    if not valores or any(type(v) is not int or v not in (0, 1) for v in valores):
        raise ValueError("Las etiquetas deben ser enteros 0 o 1.")
    if ambas and set(valores) != {0, 1}:
        raise ValueError("Entrenamiento y validación requieren ambas clases para este protocolo.")
    return np.asarray(valores, dtype=float)


def sigmoide(puntuaciones):
    s = np.asarray(puntuaciones, dtype=float)
    if not np.isfinite(s).all():
        raise ValueError("Las puntuaciones deben ser finitas.")
    # Evita exp(1000); los extremos pueden redondearse numéricamente a 0 o 1.
    return np.exp(-np.logaddexp(0, -s))


def perdida_logits(reales, puntuaciones):
    y = etiquetas(reales)
    s = vector_finito(puntuaciones)
    if y.shape != s.shape:
        raise ValueError("Etiquetas y puntuaciones deben tener igual longitud.")
    return float(np.logaddexp(0, np.where(y == 1, -s, s)).mean())


def objetivo_gradiente(z, y, parametros, penalizacion):
    a, b = parametros
    s = a + b * z
    p = sigmoide(s)
    perdida = float(np.logaddexp(0, np.where(y == 1, -s, s)).mean())
    objetivo = perdida + penalizacion * b * b / 2
    gradiente = np.array([(p - y).mean(), ((p - y) * z).mean() + penalizacion * b])
    return objetivo, gradiente


def ajustar_logistica(xs, ys, tasa=0.2, iteraciones=3000, penalizacion=0.01):
    x, y = vector_finito(xs), etiquetas(ys, ambas=True)
    if x.shape != y.shape:
        raise ValueError("Entradas y etiquetas deben tener igual longitud.")
    if (type(iteraciones) is not int or iteraciones <= 0 or not math.isfinite(tasa)
            or not 0 < tasa <= 1 or not math.isfinite(penalizacion) or not 0 < penalizacion <= 1):
        raise ValueError("Se requieren iteraciones positivas, tasa en (0, 1] y penalización en (0, 1].")
    centro, escala = float(x.mean()), float(x.std(ddof=0))
    if not math.isfinite(centro) or not math.isfinite(escala) or escala == 0:
        raise ValueError("La entrada debe variar y permitir un escalado finito.")
    z = (x - centro) / escala
    parametros = np.zeros(2)
    historial = []
    for paso in range(iteraciones + 1):
        objetivo, gradiente = objetivo_gradiente(z, y, parametros, penalizacion)
        if not math.isfinite(objetivo) or not np.isfinite(gradiente).all():
            raise ValueError("El ajuste excede la escala representable.")
        if paso % 100 == 0 or paso == iteraciones:
            historial.append({"paso": paso, "objetivo": objetivo})
        if paso < iteraciones:
            parametros -= tasa * gradiente
    return {"intercepto": float(parametros[0]), "coeficiente": float(parametros[1]),
            "centro": centro, "escala": escala, "rango_x": [float(x.min()), float(x.max())],
            "tasa": tasa, "iteraciones": iteraciones, "penalizacion": penalizacion,
            "norma_gradiente_final": float(np.linalg.norm(gradiente)), "historial": historial}


def probabilidades(modelo, xs):
    x = vector_finito(xs)
    s = modelo["intercepto"] + modelo["coeficiente"] * (x - modelo["centro"]) / modelo["escala"]
    return sigmoide(s).tolist(), s.tolist()


def decidir(ps, umbral):
    p = vector_finito(ps)
    if np.any((p < 0) | (p > 1)) or not math.isfinite(umbral) or not 0 <= umbral <= 1:
        raise ValueError("Probabilidades y umbral deben estar entre 0 y 1.")
    return (p >= umbral).astype(int).tolist()


def leer_csv(ruta):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    esperadas = {"caso_id", "senal_previa", "revision_confirmada"}
    if lector.fieldnames is None or len(lector.fieldnames) != 3 or set(lector.fieldnames) != esperadas:
        raise ValueError("Se requieren caso_id, senal_previa y revision_confirmada una sola vez.")
    filas = []
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("No se aceptan celdas vacías ni columnas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        fila["senal_previa"] = float(fila["senal_previa"])
        if not math.isfinite(fila["senal_previa"]) or not 0 <= fila["senal_previa"] <= 100:
            raise ValueError("La señal sintética debe estar entre 0 y 100.")
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
                raise ValueError("Un identificador se repite dentro o entre particiones.")
            vistos.add(fila["caso_id"])


def evaluar(modelo, referencia, filas, candidato):
    xs = [f["senal_previa"] for f in filas]
    ys = [f["revision_confirmada"] for f in filas]
    ps, puntuaciones = probabilidades(modelo, xs)
    if candidato in UMBRALES:
        predicciones = decidir(ps, UMBRALES[candidato])
        perdida = perdida_logits(ys, puntuaciones)
    elif candidato == "mayoria":
        predicciones = [referencia["clase_mayoritaria"]] * len(filas)
        ps = [referencia["frecuencia_positiva"]] * len(filas)
        logit = math.log(ps[0]) - math.log1p(-ps[0])
        perdida = perdida_logits(ys, [logit] * len(filas))
    elif candidato == "siempre_1":
        predicciones, ps, perdida = [1] * len(filas), [None] * len(filas), None
    else:
        raise ValueError("Candidato desconocido.")
    inferior, superior = modelo["rango_x"]
    registros = [{"caso_id": f["caso_id"], "senal_previa": x, "real": y,
                  "probabilidad_1": p, "prediccion": pred, "resultado": resultado_binario(y, pred),
                  "fuera_rango": not inferior <= x <= superior}
                 for f, x, y, p, pred in zip(filas, xs, ys, ps, predicciones)]
    return {"metricas": {**metricas_clasificacion(ys, predicciones), "perdida_log": perdida},
            "predicciones": registros, "fuera_rango": sum(r["fuera_rango"] for r in registros)}


def seleccionar(validacion, candidatos):
    if any(validacion[c]["metricas"]["f1"] is None for c in candidatos):
        raise ValueError("La selección exige F1 definido para todos los candidatos.")
    return max(candidatos, key=lambda c: validacion[c]["metricas"]["f1"])


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False, senal=None):
    if nombre not in CANDIDATOS:
        raise ValueError("Experimento desconocido.")
    if senal is not None and (not math.isfinite(senal) or not 0 <= senal <= 100):
        raise ValueError("La consulta debe estar entre 0 y 100 y ser finita.")
    carpeta = Path(carpeta)
    datos, fuentes = {}, {}

    def cargar(fase):
        datos[fase], huella = leer_csv(carpeta / f"{fase}.csv")
        validar_ids(datos)
        ys = [f["revision_confirmada"] for f in datos[fase]]
        etiquetas(ys, ambas=fase in ("entrenamiento", "validacion"))
        fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": huella, "n": len(ys), "positivos": sum(ys)}

    cargar("entrenamiento")
    cargar("validacion")
    xs = [f["senal_previa"] for f in datos["entrenamiento"]]
    ys = [f["revision_confirmada"] for f in datos["entrenamiento"]]
    modelo = ajustar_logistica(xs, ys, **CONFIGURACION)
    referencia = {"frecuencia_positiva": sum(ys) / len(ys), "clase_mayoritaria": int(sum(ys) > len(ys) / 2)}
    candidatos = CANDIDATOS[nombre]
    entrenamiento = {c: evaluar(modelo, referencia, datos["entrenamiento"], c) for c in candidatos}
    validacion = {c: evaluar(modelo, referencia, datos["validacion"], c) for c in candidatos}
    elegido = seleccionar(validacion, candidatos)
    informe = {"protocolo": "clasificacion-v1", "experimento": nombre,
               "versiones": {"python": platform.python_version(), "numpy": np.__version__},
               "fuentes": fuentes, "modelo_logistico": modelo, "referencia": referencia,
               "candidatos": {c: {"umbral": UMBRALES.get(c)} for c in candidatos},
               "criterio": {"metrica": "f1", "clase_positiva": 1, "sentido": "maximizar",
                            "orden_desempate": list(candidatos), "reajuste_con_validacion": False},
               "entrenamiento": entrenamiento, "validacion": validacion,
               "seleccionado": elegido, "prueba": None, "consulta": None}
    if senal is not None:
        p = probabilidades(modelo, [senal])[0][0]
        if elegido in UMBRALES:
            clase = decidir([p], UMBRALES[elegido])[0]
        elif elegido == "mayoria":
            clase, p = referencia["clase_mayoritaria"], referencia["frecuencia_positiva"]
        else:
            clase, p = 1, None
        informe["consulta"] = {"senal": senal, "candidato": elegido, "probabilidad_1": p,
                               "clase": clase, "fuera_rango": not modelo["rango_x"][0] <= senal <= modelo["rango_x"][1]}
    if evaluar_prueba:
        cargar("prueba")  # Solo después de elegir candidato y umbral con validación.
        informe["prueba"] = {"candidato": elegido, **evaluar(modelo, referencia, datos["prueba"], elegido)}
    return informe


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
    with (destino / "informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

"""Separar puntuaciones, políticas, costos, ordenación y probabilidad."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import sys

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion

COSTOS = {"costos": {"FP": 1, "FN": 6}, "capacidad": {"FP": 1, "FN": 4}}
CUPO = 6
POLITICAS = {
    "costos": {"nadie": {"umbral": None, "cupo": None},
               **{f"umbral{int(t*100):03d}": {"umbral": t, "cupo": None} for t in (.8, .6, .5, .4, .2, .1, 0.)}},
    "capacidad": {"nadie": {"umbral": None, "cupo": CUPO},
                  "top6": {"umbral": 0., "cupo": CUPO},
                  **{f"umbral{int(t*100):03d}_top6": {"umbral": t, "cupo": CUPO} for t in (.3, .5, .7)}}}


def leer_csv(ruta, nombre):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    columnas = {"caso_id", "senal_a", "senal_b", "puntuacion", "requiere_revision", *(["lote_id"] if nombre == "capacidad" else [])}
    if lector.fieldnames is None or set(lector.fieldnames) != columnas or len(lector.fieldnames) != len(columnas):
        raise ValueError("Esquema incorrecto, incompleto o repetido.")
    filas, ids = [], set()
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Se requieren filas completas sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        if fila["caso_id"] in ids:
            raise ValueError("Identificador repetido.")
        ids.add(fila["caso_id"])
        for c in ("senal_a", "senal_b", "puntuacion"):
            fila[c] = float(fila[c])
            if not math.isfinite(fila[c]) or not 0 <= fila[c] <= 1:
                raise ValueError("Señales y puntuaciones deben ser finitas en [0,1].")
        if fila["requiere_revision"] not in ("0", "1"):
            raise ValueError("La etiqueta debe ser 0 o 1.")
        fila["requiere_revision"] = int(fila["requiere_revision"])
        filas.append(fila)
    if not filas:
        raise ValueError("Partición vacía.")
    return filas, {"archivo": Path(ruta).name, "n": len(filas), "sha256": hashlib.sha256(contenido).hexdigest()}


def decidir(filas, politica):
    """Solo consulta puntuación, lote e ID; devuelve decisiones en orden original."""
    umbral, cupo = politica["umbral"], politica["cupo"]
    if umbral is not None and (not math.isfinite(umbral) or not 0 <= umbral <= 1):
        raise ValueError("Umbral fuera de [0,1].")
    if cupo is not None and (type(cupo) is not int or cupo < 0):
        raise ValueError("Cupo debe ser entero no negativo.")
    grupos = {}
    for i, f in enumerate(filas):
        grupos.setdefault(f.get("lote_id", "conjunto"), []).append(i)
    decisiones = [0]*len(filas)
    for indices in grupos.values():
        elegibles = [i for i in indices if umbral is not None and filas[i]["puntuacion"] >= umbral]
        elegibles.sort(key=lambda i: (-filas[i]["puntuacion"], filas[i]["caso_id"]))
        for i in elegibles if cupo is None else elegibles[:cupo]:
            decisiones[i] = 1
    return decisiones


def medidas(y, pred, costos):
    m = metricas_clasificacion(y, pred)
    negativos = m["VN"]+m["FP"]
    m.update(prevalencia=m["positivos"]/m["n"], alertas=m["VP"]+m["FP"],
             especificidad=m["VN"]/negativos if negativos else None,
             tasa_fp=m["FP"]/negativos if negativos else None,
             costo_total=costos["FP"]*m["FP"]+costos["FN"]*m["FN"])
    m["costo_por_caso"] = m["costo_total"]/m["n"]
    return m


def evaluar(filas, politica, costos):
    pred = decidir(filas, politica)
    y = [f["requiere_revision"] for f in filas]
    registros = [{"caso_id": f["caso_id"], **({"lote_id": f["lote_id"]} if "lote_id" in f else {}),
                  "puntuacion": f["puntuacion"], "real": real, "decision": decision,
                  "resultado": {(1, 1): "VP", (0, 0): "VN", (0, 1): "FP", (1, 0): "FN"}[(real, decision)]}
                 for f, real, decision in zip(filas, y, pred)]
    lotes = {}
    if "lote_id" in filas[0]:
        for lote in sorted({f["lote_id"] for f in filas}):
            indices = [i for i, f in enumerate(filas) if f["lote_id"] == lote]
            lotes[lote] = medidas([y[i] for i in indices], [pred[i] for i in indices], costos)
    return {"metricas": medidas(y, pred, costos), "por_lote": lotes, "decisiones": registros}


def seleccionar(evaluaciones):
    # Los costos son enteros; se comparan sin tolerancias ni redondeo.
    return min(evaluaciones, key=lambda c: (evaluaciones[c]["metricas"]["costo_total"],
                                          evaluaciones[c]["metricas"]["alertas"], list(evaluaciones).index(c)))


def ordenacion(y, scores):
    if not y or len(y) != len(scores) or any(v not in (0, 1) for v in y):
        raise ValueError("Se requieren pares no vacíos y etiquetas binarias.")
    if any(not math.isfinite(s) or not 0 <= s <= 1 for s in scores):
        raise ValueError("Puntuaciones finitas en [0,1].")
    positivos, negativos = sum(y), len(y)-sum(y)
    puntos = [{"umbral": None, "VP": 0, "FP": 0,
               "recobrado": 0. if positivos else None, "tasa_fp": 0. if negativos else None, "precision": None}]
    vp, fp = 0, 0
    for t in sorted(set(scores), reverse=True):
        etiquetas = [real for real, s in zip(y, scores) if s == t]
        vp += sum(etiquetas)
        fp += len(etiquetas)-sum(etiquetas)
        puntos.append({"umbral": t, "VP": vp, "FP": fp,
                       "recobrado": vp/positivos if positivos else None,
                       "tasa_fp": fp/negativos if negativos else None, "precision": vp/(vp+fp)})
    auc = None if not positivos or not negativos else sum(
        (b["tasa_fp"]-a["tasa_fp"])*(a["recobrado"]+b["recobrado"])/2 for a, b in zip(puntos, puntos[1:]))
    ap = None if not positivos else sum((b["recobrado"]-a["recobrado"])*b["precision"] for a, b in zip(puntos, puntos[1:]))
    brier = sum((s-real)**2 for real, s in zip(y, scores))/len(y)
    bordes = [0., .2, .4, .6, .8, 1.]
    fiabilidad = []
    for i, (a, b) in enumerate(zip(bordes, bordes[1:])):
        indices = [j for j, s in enumerate(scores) if a <= s and (s < b or (i == 4 and s == b))]
        fiabilidad.append({"desde": a, "hasta": b, "incluye_derecha": i == 4, "n": len(indices),
                           "puntuacion_media": sum(scores[j] for j in indices)/len(indices) if indices else None,
                           "fraccion_positiva": sum(y[j] for j in indices)/len(indices) if indices else None})
    return {"auc_roc": auc, "ap": ap, "brier": brier, "prevalencia": positivos/len(y),
            "puntos": puntos, "fiabilidad": fiabilidad}


def sensibilidad_prevalencia(m):
    tpr, fpr = m["recobrado"], m["tasa_fp"]
    resultado = []
    for pi in (.05, .2, .5):
        denominador = None if tpr is None or fpr is None else tpr*pi + fpr*(1-pi)
        resultado.append({"prevalencia_hipotetica": pi,
                          "precision_hipotetica": tpr*pi/denominador if denominador else None})
    return resultado


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False):
    if nombre not in POLITICAS:
        raise ValueError("Experimento desconocido.")
    carpeta = Path(carpeta)
    filas, fuente = leer_csv(carpeta/"validacion.csv", nombre)
    evaluaciones = {c: evaluar(filas, p, COSTOS[nombre]) for c, p in POLITICAS[nombre].items()}
    elegido = seleccionar(evaluaciones)
    y, scores = [f["requiere_revision"] for f in filas], [f["puntuacion"] for f in filas]
    informe = {"protocolo": "metricas-decisiones-v1", "experimento": nombre, "versiones": {"python": platform.python_version()},
               "fuentes": {"validacion": fuente}, "costos": COSTOS[nombre], "cupo_por_lote": CUPO if nombre == "capacidad" else None,
               "politicas": POLITICAS[nombre], "criterio": ["menor costo total de validación", "menos alertas", "orden publicado"],
               "desempate_en_cupo": "puntuación descendente, caso_id ascendente; no se usan etiquetas",
               "ajuste_predictor": "ninguno; puntuaciones sintéticas previas fijas", "reajuste": False,
               "validacion": evaluaciones, "seleccionado": elegido, "politica_elegida": POLITICAS[nombre][elegido],
               "diagnostico_ordenacion": ordenacion(y, scores), "diagnostico_cuadrado": ordenacion(y, [s*s for s in scores]),
               "sensibilidad_prevalencia": sensibilidad_prevalencia(evaluaciones[elegido]["metricas"]),
               "diagnostico_sin_cupo": None, "prueba": None}
    if nombre == "capacidad":
        informe["diagnostico_sin_cupo"] = evaluar(filas, {"umbral": .5, "cupo": None}, COSTOS[nombre])
    if evaluar_prueba:
        prueba, fuente_prueba = leer_csv(carpeta/"prueba.csv", nombre)
        if {f["caso_id"] for f in filas} & {f["caso_id"] for f in prueba}:
            raise ValueError("Identificadores compartidos entre validación y prueba.")
        if nombre == "capacidad" and {f["lote_id"] for f in filas} & {f["lote_id"] for f in prueba}:
            raise ValueError("Prueba debe tener lotes distintos.")
        informe["fuentes"]["prueba"] = fuente_prueba
        informe["prueba"] = {"politica": elegido, **evaluar(prueba, informe["politica_elegida"], COSTOS[nombre])}
    return informe


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    conjuntos = {"decisiones_validacion": [dict(politica=c, **r) for c, ev in informe["validacion"].items() for r in ev["decisiones"]]}
    if informe["diagnostico_sin_cupo"] is not None:
        conjuntos["diagnostico_sin_cupo"] = [dict(politica="umbral050_sin_cupo", **r) for r in informe["diagnostico_sin_cupo"]["decisiones"]]
    if informe["prueba"] is not None:
        conjuntos["decisiones_prueba"] = [dict(politica=informe["seleccionado"], **r) for r in informe["prueba"]["decisiones"]]
    for nombre, filas in conjuntos.items():
        with (destino/f"{nombre}.csv").open("x", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
    with (destino/"informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

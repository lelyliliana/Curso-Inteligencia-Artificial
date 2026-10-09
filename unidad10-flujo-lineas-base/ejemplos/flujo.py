"""Ajuste, selección y evaluación separados; biblioteca estándar de Python."""

import csv
from datetime import datetime, timedelta
import hashlib
import io
import json
import math
from pathlib import Path
import platform
from statistics import mean, median

UNIDAD = Path(__file__).resolve().parents[1]
FASES = ("entrenamiento", "validacion", "prueba")
VERSION_PROTOCOLO = "lineas-base-v1"
CANDIDATOS = {"regresion": ("mediana", "media", "persistencia"),
              "clasificacion": ("mayoria", "por_senal")}
COLUMNAS = {
    "regresion": {"caso_id", "momento_prediccion", "entrada_disponible", "objetivo_disponible",
                  "consumo_anterior_kwh", "consumo_objetivo_kwh"},
    "clasificacion": {"caso_id", "equipo_id", "senal_previa", "fallo_24h"},
}


def instante(texto):
    valor = datetime.fromisoformat(texto)
    if valor.utcoffset() is None:
        raise ValueError("Las fechas necesitan zona horaria explícita.")
    return valor


def leer_csv(ruta, tarea):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    if (lector.fieldnames is None or len(lector.fieldnames) != len(COLUMNAS[tarea])
            or set(lector.fieldnames) != COLUMNAS[tarea]):
        raise ValueError(f"Columnas incorrectas para {tarea}.")
    filas = []
    for numero, fila in enumerate(lector, start=2):
        if None in fila or any(v is None for v in fila.values()):
            raise ValueError(f"Registro {numero}: faltan o sobran celdas.")
        fila = {k: v.strip() for k, v in fila.items()}
        opcional = {"consumo_anterior_kwh"} if tarea == "regresion" else set()
        if any(not valor for campo, valor in fila.items() if campo not in opcional):
            raise ValueError(f"Registro {numero}: campo obligatorio vacío.")
        if tarea == "regresion":
            for campo in ("consumo_anterior_kwh", "consumo_objetivo_kwh"):
                fila[campo] = None if not fila[campo] else float(fila[campo])
                if fila[campo] is not None and (not math.isfinite(fila[campo]) or fila[campo] < 0):
                    raise ValueError("Los consumos presentes deben ser finitos y no negativos.")
            decision = instante(fila["momento_prediccion"])
            if instante(fila["entrada_disponible"]) > decision:
                raise ValueError("La entrada no estaba disponible al predecir.")
            if instante(fila["objetivo_disponible"]) != decision + timedelta(hours=24):
                raise ValueError("El objetivo de este contrato se conoce exactamente 24 horas después.")
        else:
            if fila["senal_previa"] not in ("baja", "alta") or fila["fallo_24h"] not in ("0", "1"):
                raise ValueError("Se esperan señal baja/alta y objetivo 0/1.")
            fila["fallo_24h"] = int(fila["fallo_24h"])
        filas.append(fila)
    if not filas:
        raise ValueError("Cada partición debe contener casos.")
    return filas, hashlib.sha256(contenido).hexdigest()


def validar_separacion(particiones, tarea):
    ids = set()
    grupos = set()
    ultima_decision = ultimo_objetivo = None
    for fase in FASES:
        if fase not in particiones:
            continue
        filas = particiones[fase]
        if not filas:
            raise ValueError("Cada partición debe contener casos.")
        nuevos = [f["caso_id"] for f in filas]
        if len(nuevos) != len(set(nuevos)) or ids.intersection(nuevos):
            raise ValueError("Hay identificadores repetidos dentro o entre particiones.")
        ids.update(nuevos)
        if tarea == "regresion":
            decisiones = [instante(f["momento_prediccion"]) for f in filas]
            if len(decisiones) != len(set(decisiones)):
                raise ValueError("Hay momentos de predicción repetidos.")
            if ultima_decision is not None and (ultima_decision >= min(decisiones)
                                               or ultimo_objetivo > min(decisiones)):
                raise ValueError("Las particiones se solapan o las etiquetas llegan después del siguiente corte.")
            ultima_decision = max(decisiones)
            ultimo_objetivo = max(instante(f["objetivo_disponible"]) for f in filas)
        else:
            actuales = {f["equipo_id"] for f in filas}
            if grupos.intersection(actuales):
                raise ValueError("Un equipo aparece en más de una partición.")
            grupos.update(actuales)


def pares_validos(reales, predicciones):
    if not reales or len(reales) != len(predicciones):
        raise ValueError("La evaluación exige listas no vacías y de la misma longitud.")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in [*reales, *predicciones]):
        raise ValueError("Las métricas requieren números finitos.")


def metricas_regresion(reales, predicciones):
    pares_validos(reales, predicciones)
    errores = [y - p for y, p in zip(reales, predicciones)]
    resultado = {"n": len(reales), "mae": mean(abs(e) for e in errores),
                 "rmse": math.sqrt(mean(e * e for e in errores)), "sesgo": mean(errores)}
    if any(not math.isfinite(v) for v in resultado.values()):
        raise ValueError("La escala de los errores excede los cálculos representables de esta práctica.")
    return resultado


def metricas_clasificacion(reales, predicciones):
    pares_validos(reales, predicciones)
    if any(v not in (0, 1) for v in [*reales, *predicciones]):
        raise ValueError("Esta práctica solo acepta las etiquetas 0 y 1.")
    conteos = dict.fromkeys(("VP", "VN", "FP", "FN"), 0)
    for real, prediccion in zip(reales, predicciones):
        conteos[resultado_binario(real, prediccion)] += 1
    vp, vn, fp, fn = (conteos[k] for k in ("VP", "VN", "FP", "FN"))
    return {"n": len(reales), **conteos, "positivos": vp + fn,
            "exactitud": (vp + vn) / len(reales),
            "precision": vp / (vp + fp) if vp + fp else None,
            "recobrado": vp / (vp + fn) if vp + fn else None,
            "f1": 2 * vp / (2 * vp + fp + fn) if 2 * vp + fp + fn else None}


def resultado_binario(real, prediccion):
    return {(1, 1): "VP", (0, 0): "VN", (0, 1): "FP", (1, 0): "FN"}[(real, prediccion)]


def mayoria(etiquetas):
    if not etiquetas or any(type(v) is not int or v not in (0, 1) for v in etiquetas):
        raise ValueError("La mayoría requiere etiquetas enteras 0/1.")
    return int(sum(etiquetas) > len(etiquetas) / 2)  # Empate: clase 0, fijado antes de evaluar.


def ajustar(entrenamiento, tarea):
    if tarea == "regresion":
        objetivos = [f["consumo_objetivo_kwh"] for f in entrenamiento]
        entradas = [f["consumo_anterior_kwh"] for f in entrenamiento if f["consumo_anterior_kwh"] is not None]
        if not entradas:
            raise ValueError("No hay entradas observadas en entrenamiento para imputar persistencia.")
        return {"mediana": median(objetivos), "media": mean(objetivos),
                "mediana_entrada": median(entradas)}
    global_ = mayoria([f["fallo_24h"] for f in entrenamiento])
    por_senal, soportes = {}, {}
    for senal in ("baja", "alta"):
        etiquetas = [f["fallo_24h"] for f in entrenamiento if f["senal_previa"] == senal]
        soportes[senal] = len(etiquetas)
        por_senal[senal] = mayoria(etiquetas) if etiquetas else global_
    return {"mayoria": global_, "por_senal": por_senal, "soportes": soportes}


def entradas_de(filas, tarea):
    """Proyección explícita: los predictores no reciben objetivos ni identificadores."""
    campo = "consumo_anterior_kwh" if tarea == "regresion" else "senal_previa"
    return [{campo: fila[campo]} for fila in filas]


def predecir(entradas, ajuste, candidato, tarea):
    if candidato not in CANDIDATOS[tarea]:
        raise ValueError("Candidato ajeno al protocolo.")
    if tarea == "regresion":
        if candidato != "persistencia":
            return [ajuste[candidato]] * len(entradas)
        return [e["consumo_anterior_kwh"] if e["consumo_anterior_kwh"] is not None
                else ajuste["mediana_entrada"] for e in entradas]
    if candidato == "mayoria":
        return [ajuste["mayoria"]] * len(entradas)
    return [ajuste["por_senal"][e["senal_previa"]] for e in entradas]


def evaluar(filas, predicciones, tarea):
    objetivo = "consumo_objetivo_kwh" if tarea == "regresion" else "fallo_24h"
    reales = [f[objetivo] for f in filas]
    funcion = metricas_regresion if tarea == "regresion" else metricas_clasificacion
    metricas = funcion(reales, predicciones)
    registros = []
    for fila, prediccion in zip(filas, predicciones):
        registro = {"caso_id": fila["caso_id"], "real": fila[objetivo], "prediccion": prediccion}
        if tarea == "regresion":
            registro.update(error=fila[objetivo] - prediccion,
                            error_absoluto=abs(fila[objetivo] - prediccion),
                            entrada_faltante=fila["consumo_anterior_kwh"] is None)
        else:
            registro.update(equipo_id=fila["equipo_id"], resultado=resultado_binario(fila[objetivo], prediccion))
        registros.append(registro)
    return {"metricas": metricas, "predicciones": registros}


def seleccionar(resultados, tarea):
    metrica = "mae" if tarea == "regresion" else "f1"
    if tarea == "clasificacion" and any(r["metricas"]["positivos"] == 0 for r in resultados.values()):
        raise ValueError("Validación no contiene positivos: revisar el diseño antes de seleccionar por F1.")
    valores = {c: resultados[c]["metricas"][metrica] for c in CANDIDATOS[tarea]}
    if any(v is None or not math.isfinite(v) for v in valores.values()):
        raise ValueError("La métrica de selección no está definida.")
    elegir = min if tarea == "regresion" else max
    return elegir(CANDIDATOS[tarea], key=valores.get)


def ejecutar_experimento(tarea, carpeta, evaluar_prueba=False):
    carpeta = Path(carpeta)
    particiones, fuentes = {}, {}

    def cargar(fase):
        filas, huella = leer_csv(carpeta / f"{fase}.csv", tarea)
        particiones[fase] = filas
        fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": huella, "n": len(filas)}

    cargar("entrenamiento")
    cargar("validacion")
    validar_separacion(particiones, tarea)
    parametros = ajustar(particiones["entrenamiento"], tarea)
    entradas = entradas_de(particiones["validacion"], tarea)
    validacion = {c: evaluar(particiones["validacion"], predecir(entradas, parametros, c, tarea), tarea)
                  for c in CANDIDATOS[tarea]}
    elegido = seleccionar(validacion, tarea)
    informe = {
        "protocolo": VERSION_PROTOCOLO, "python": platform.python_version(), "tarea": tarea,
        "criterio": {"metrica": "mae" if tarea == "regresion" else "f1",
                     "sentido": "minimizar" if tarea == "regresion" else "maximizar",
                     "orden_desempate": list(CANDIDATOS[tarea]), "reajuste_con_validacion": False},
        "fuentes": fuentes, "ajuste": parametros, "validacion": validacion,
        "seleccionado": elegido, "prueba": None,
    }
    # Prueba se abre después de seleccionar y solo por solicitud explícita.
    if evaluar_prueba:
        cargar("prueba")
        validar_separacion(particiones, tarea)
        predicciones = predecir(entradas_de(particiones["prueba"], tarea), parametros, elegido, tarea)
        informe["prueba"] = {"candidato": elegido, **evaluar(particiones["prueba"], predicciones, tarea)}
    return informe


def exportar(informe, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    tablas = {"predicciones_validacion.csv": [dict(candidato=c, **fila)
              for c, evaluacion in informe["validacion"].items() for fila in evaluacion["predicciones"]]}
    if informe["prueba"] is not None:
        tablas["predicciones_prueba.csv"] = [dict(candidato=informe["seleccionado"], **fila)
                                             for fila in informe["prueba"]["predicciones"]]
    for nombre, registros in tablas.items():
        with (destino / nombre).open("x", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(registros[0]))
            escritor.writeheader()
            escritor.writerows(registros)
    with (destino / "informe.json").open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")

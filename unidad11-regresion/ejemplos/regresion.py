"""Regresión de una entrada: ajuste, predicción, residuos y evaluación separada."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
from statistics import mean, median
import sys

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_regresion  # noqa: E402

CANDIDATOS = {"lineal": ("mediana", "media", "recta"),
              "curva": ("mediana", "media", "recta", "cuadratica", "grado9")}


def numpy_disponible():
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("Instala dependencias: python -m pip install -r unidad11-regresion/requirements.txt") from error
    return np


def validar_pares(xs, ys):
    if not xs or len(xs) != len(ys):
        raise ValueError("Se necesitan pares no vacíos y de la misma longitud.")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in [*xs, *ys]):
        raise ValueError("Se requieren números finitos.")


def ajustar_recta(xs, ys):
    validar_pares(xs, ys)
    centro_x, centro_y = mean(xs), mean(ys)
    sxx = math.fsum((x - centro_x) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("La entrada es constante: no se puede identificar una pendiente.")
    pendiente = math.fsum((x - centro_x) * (y - centro_y) for x, y in zip(xs, ys)) / sxx
    intercepto = centro_y - pendiente * centro_x
    if not all(math.isfinite(v) for v in (intercepto, pendiente, sxx)):
        raise ValueError("El ajuste excede la escala representable de esta práctica.")
    return {"tipo": "recta", "coeficientes": [intercepto, pendiente],
            "centro": 0.0, "escala": 1.0, "rango_x": [min(xs), max(xs)]}


def ajustar_polinomio(xs, ys, grado):
    validar_pares(xs, ys)
    if type(grado) is not int or grado < 1 or grado >= len(xs):
        raise ValueError("El grado debe ser entero positivo y menor que el número de casos.")
    centro = mean(xs)
    escala = max(abs(x - centro) for x in xs)
    if escala == 0:
        raise ValueError("La entrada es constante: no permite construir este polinomio.")
    np = numpy_disponible()
    z = (np.asarray(xs, dtype=float) - centro) / escala
    matriz = np.vander(z, N=grado + 1, increasing=True)
    coeficientes, _, rango, _ = np.linalg.lstsq(matriz, ys, rcond=None)
    if rango != grado + 1 or not np.isfinite(coeficientes).all():
        raise ValueError("La matriz no tiene rango suficiente para identificar los coeficientes.")
    return {"tipo": "polinomio", "coeficientes": coeficientes.tolist(),
            "centro": centro, "escala": escala, "rango_x": [min(xs), max(xs)]}


def ajustar_candidato(xs, ys, candidato):
    validar_pares(xs, ys)
    if candidato in ("mediana", "media"):
        valor = median(ys) if candidato == "mediana" else mean(ys)
        return {"tipo": "constante", "coeficientes": [valor], "centro": 0.0,
                "escala": 1.0, "rango_x": [min(xs), max(xs)]}
    if candidato == "recta":
        return ajustar_recta(xs, ys)
    if candidato not in ("cuadratica", "grado9"):
        raise ValueError("Candidato desconocido.")
    return ajustar_polinomio(xs, ys, 2 if candidato == "cuadratica" else 9)


def predecir(modelo, xs):
    resultado = []
    for x in xs:
        if type(x) not in (int, float) or not math.isfinite(x):
            raise ValueError("La entrada de predicción debe ser un número finito.")
        z = (x - modelo["centro"]) / modelo["escala"]
        # Horner evalúa c0 + c1*z + ... sin construir potencias por separado.
        valor = 0.0
        for coeficiente in reversed(modelo["coeficientes"]):
            valor = valor * z + coeficiente
        if not math.isfinite(valor):
            raise ValueError("La predicción excede la escala representable.")
        resultado.append(valor)
    return resultado


def medir(ys, predicciones):
    resultado = metricas_regresion(ys, predicciones)
    centro_y = mean(ys)
    sst = math.fsum((y - centro_y) ** 2 for y in ys)
    sse = math.fsum((y - p) ** 2 for y, p in zip(ys, predicciones))
    r2 = None if len(ys) < 2 or sst == 0 else 1 - sse / sst
    if not math.isfinite(sst) or not math.isfinite(sse) or (r2 is not None and not math.isfinite(r2)):
        raise ValueError("Las métricas exceden la escala representable.")
    return {**resultado, "r2": r2}


def leer_csv(ruta):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig"), newline=""))
    columnas = {"caso_id", "horas_planificadas", "consumo_kwh"}
    if lector.fieldnames is None or len(lector.fieldnames) != 3 or set(lector.fieldnames) != columnas:
        raise ValueError("Se esperan caso_id, horas_planificadas y consumo_kwh una sola vez.")
    filas = []
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("La práctica requiere filas completas, sin celdas extra.")
        fila = {k: v.strip() for k, v in fila.items()}
        for campo in ("horas_planificadas", "consumo_kwh"):
            fila[campo] = float(fila[campo])
            if not math.isfinite(fila[campo]) or fila[campo] < 0:
                raise ValueError("Horas y consumo deben ser finitos y no negativos.")
        if fila["horas_planificadas"] > 24:
            raise ValueError("Las horas planificadas deben estar entre 0 y 24.")
        filas.append(fila)
    if not filas:
        raise ValueError("Cada partición debe contener casos.")
    return filas, hashlib.sha256(contenido).hexdigest()


def validar_ids(particiones):
    conocidos = set()
    for filas in particiones.values():
        for fila in filas:
            if fila["caso_id"] in conocidos:
                raise ValueError("Identificador repetido dentro o entre particiones.")
            conocidos.add(fila["caso_id"])


def evaluar(modelo, filas):
    xs = [f["horas_planificadas"] for f in filas]
    ys = [f["consumo_kwh"] for f in filas]
    predicciones = predecir(modelo, xs)
    inferior, superior = modelo["rango_x"]
    registros = [{"caso_id": f["caso_id"], "horas_planificadas": x, "real": y,
                  "prediccion": p, "residuo": y - p, "error_absoluto": abs(y - p),
                  "fuera_rango": not inferior <= x <= superior}
                 for f, x, y, p in zip(filas, xs, ys, predicciones)]
    return {"metricas": medir(ys, predicciones), "predicciones": registros,
            "fuera_rango": sum(r["fuera_rango"] for r in registros)}


def seleccionar(validacion, candidatos):
    # isclose no interviene: empate exacto conserva el orden prefijado.
    return min(candidatos, key=lambda c: validacion[c]["metricas"]["mae"])


def ejecutar_experimento(nombre, carpeta, evaluar_prueba=False, horas=None):
    if nombre not in CANDIDATOS:
        raise ValueError("Experimento desconocido.")
    if horas is not None and (not math.isfinite(horas) or not 0 <= horas <= 24):
        raise ValueError("La consulta de horas debe estar entre 0 y 24 y ser finita.")
    carpeta = Path(carpeta)
    datos, fuentes = {}, {}

    def cargar(fase):
        datos[fase], huella = leer_csv(carpeta / f"{fase}.csv")
        fuentes[fase] = {"archivo": f"{fase}.csv", "sha256": huella, "n": len(datos[fase])}
        validar_ids(datos)

    cargar("entrenamiento")
    cargar("validacion")
    xs = [f["horas_planificadas"] for f in datos["entrenamiento"]]
    ys = [f["consumo_kwh"] for f in datos["entrenamiento"]]
    candidatos = CANDIDATOS[nombre]
    modelos = {c: ajustar_candidato(xs, ys, c) for c in candidatos}
    entrenamiento = {c: evaluar(m, datos["entrenamiento"]) for c, m in modelos.items()}
    validacion = {c: evaluar(m, datos["validacion"]) for c, m in modelos.items()}
    elegido = seleccionar(validacion, candidatos)
    versiones = {"python": platform.python_version()}
    if nombre == "curva":
        versiones["numpy"] = numpy_disponible().__version__
    informe = {"protocolo": "regresion-v1", "experimento": nombre, "versiones": versiones,
               "fuentes": fuentes, "modelos": modelos, "entrenamiento": entrenamiento,
               "validacion": validacion, "seleccionado": elegido, "prueba": None, "consulta": None,
               "criterio": {"metrica": "mae", "sentido": "minimizar",
                            "orden_desempate": list(candidatos), "reajuste_con_validacion": False}}
    if horas is not None:
        modelo = modelos[elegido]
        informe["consulta"] = {"horas": horas, "consumo_predicho": predecir(modelo, [horas])[0],
                               "fuera_rango": not modelo["rango_x"][0] <= horas <= modelo["rango_x"][1]}
    if evaluar_prueba:
        cargar("prueba")  # El archivo permanece sin leer hasta después de seleccionar.
        informe["prueba"] = {"candidato": elegido, **evaluar(modelos[elegido], datos["prueba"])}
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

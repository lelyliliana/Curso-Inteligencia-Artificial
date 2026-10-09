"""Cálculos descriptivos sin paquetes externos; los faltantes no se vuelven cero."""

from bisect import bisect_right
import csv
from datetime import date, timedelta
import hashlib
import math
from pathlib import Path
from statistics import StatisticsError, correlation, mean, median
import sys

UNIDAD = Path(__file__).resolve().parents[1]
RAIZ = UNIDAD.parent
sys.path.insert(0, str(RAIZ / "unidad08-preparacion-datos/ejemplos"))
from preparacion import generar_informe  # noqa: E402


def cuantil(valores, proporcion):
    """Interpolación lineal, posición (n-1)*p sobre los datos ordenados."""
    if not valores or not 0 <= proporcion <= 1:
        raise ValueError("Se necesitan valores y una proporción entre 0 y 1.")
    ordenados = sorted(valores)
    posicion = (len(ordenados) - 1) * proporcion
    inferior = math.floor(posicion)
    superior = math.ceil(posicion)
    return ordenados[inferior] + (posicion - inferior) * (ordenados[superior] - ordenados[inferior])


def describir(valores):
    presentes = [v for v in valores if v is not None]
    if any(not math.isfinite(v) for v in presentes):
        raise ValueError("Los valores presentes deben ser finitos.")
    resultado = {"n": len(presentes), "faltantes": len(valores) - len(presentes)}
    resultado.update(dict.fromkeys(("minimo", "q1", "mediana", "media", "q3", "maximo")))
    if presentes:
        resultado.update(minimo=min(presentes), q1=cuantil(presentes, 0.25),
                         mediana=median(presentes), media=mean(presentes),
                         q3=cuantil(presentes, 0.75), maximo=max(presentes))
    return resultado


def correlacion_pares(filas):
    """Pearson sobre pares completos; no inventa r=0 para varianza nula."""
    pares = [(f["horas_uso"], f["consumo_kwh"]) for f in filas
             if f["horas_uso"] is not None and f["consumo_kwh"] is not None]
    if any(not math.isfinite(v) for par in pares for v in par):
        raise ValueError("Los pares deben contener valores finitos.")
    try:
        r = correlation([p[0] for p in pares], [p[1] for p in pares])
    except StatisticsError:
        r = None
    return {"n_pares": len(pares), "r": r}


def resumir_lecturas(informe):
    plan = informe["plan_cobertura"]
    inicio, fin = date.fromisoformat(plan["inicio"]), date.fromisoformat(plan["fin"])
    fechas = [(inicio + timedelta(days=i)).isoformat() for i in range((fin - inicio).days + 1)]
    if not fechas or not plan["sensores"]:
        raise ValueError("El plan debe tener fechas y sensores.")
    por_clave = {}
    for registro in informe["resultado"]["preparados"]:
        fila = registro["valores"]
        clave = fila["fecha"], fila["sensor_id"]
        if fila["fecha"] not in fechas or fila["sensor_id"] not in plan["sensores"]:
            raise ValueError("Hay una lectura preparada fuera del plan.")
        if clave in por_clave:
            raise ValueError("Hay claves preparadas repetidas.")
        por_clave[clave] = fila
    sensores = {}
    for sensor in plan["sensores"]:
        filas = [por_clave[(f, sensor)] for f in fechas if (f, sensor) in por_clave]
        sensores[sensor] = {
            "esperados": len(fechas), "preparados": len(filas),
            "sin_preparar": len(fechas) - len(filas),
            "consumo": describir([f["consumo_kwh"] for f in filas]),
            "serie": [por_clave[(f, sensor)]["consumo_kwh"] if (f, sensor) in por_clave
                      else None for f in fechas],
        }
    return {"fechas": fechas, "sensores": sensores}


def analizar_lecturas(correcciones=None):
    fuente = RAIZ / "unidad07-obtencion-datos/datos/lecturas_sinteticas.csv"
    informe = generar_informe(fuente, correcciones)
    return {"preparacion": informe, "resumen": resumir_lecturas(informe)}


def leer_grupos(ruta):
    columnas = {"caso_id", "grupo", "horas_uso", "consumo_kwh"}
    filas, ids = [], set()
    with Path(ruta).open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None or len(lector.fieldnames) != 4 or set(lector.fieldnames) != columnas:
            raise ValueError("Se esperan caso_id, grupo, horas_uso y consumo_kwh, sin repeticiones.")
        for numero, fila in enumerate(lector, start=2):
            if None in fila or any(v is None or not v.strip() for v in fila.values()):
                raise ValueError(f"Registro {numero}: faltan o sobran celdas.")
            fila = {k: v.strip() for k, v in fila.items()}
            if fila["caso_id"] in ids or fila["grupo"] not in ("A", "B"):
                raise ValueError(f"Registro {numero}: id repetido o grupo distinto de A/B.")
            ids.add(fila["caso_id"])
            for campo in ("horas_uso", "consumo_kwh"):
                try:
                    fila[campo] = float(fila[campo])
                except ValueError as error:
                    raise ValueError(f"Registro {numero}: {campo} no es numérico.") from error
                if not math.isfinite(fila[campo]) or fila[campo] < 0:
                    raise ValueError(f"Registro {numero}: {campo} inválido.")
            if fila["horas_uso"] > 24:
                raise ValueError(f"Registro {numero}: horas_uso supera 24.")
            filas.append(fila)
    if {f["grupo"] for f in filas} != {"A", "B"}:
        raise ValueError("Esta práctica requiere casos de ambos grupos A y B.")
    return filas


def contar_intervalos(valores, bordes):
    """[izquierda, derecha), salvo el último intervalo, cerrado a la derecha."""
    if (len(bordes) < 2 or any(not math.isfinite(b) for b in bordes)
            or any(a >= b for a, b in zip(bordes, bordes[1:]))):
        raise ValueError("Los bordes deben ser finitos y estrictamente crecientes.")
    conteos = [0] * (len(bordes) - 1)
    for valor in valores:
        if not math.isfinite(valor) or not bordes[0] <= valor <= bordes[-1]:
            raise ValueError("Hay valores no finitos o fuera del rango del histograma.")
        indice = min(bisect_right(bordes, valor) - 1, len(conteos) - 1)
        conteos[indice] += 1
    return conteos


def analizar_grupos(ruta, intervalos=8):
    if intervalos not in (4, 8, 16):
        raise ValueError("Elige 4, 8 o 16 intervalos de igual ancho.")
    filas = leer_grupos(ruta)
    consumos = [f["consumo_kwh"] for f in filas]
    limite = max(4, math.ceil(max(consumos) / 4) * 4)
    bordes = [i * limite / intervalos for i in range(intervalos + 1)]
    grupos = {}
    for grupo in ("A", "B"):
        parte = [f for f in filas if f["grupo"] == grupo]
        grupos[grupo] = {"consumo": describir([f["consumo_kwh"] for f in parte]),
                         "correlacion": correlacion_pares(parte)}
    resumen = {"archivo_origen": Path(ruta).name,
               "sha256_origen": hashlib.sha256(Path(ruta).read_bytes()).hexdigest(),
               "total": describir(consumos), "correlacion_total": correlacion_pares(filas),
               "grupos": grupos, "bordes_kwh": bordes,
               "frecuencias": contar_intervalos(consumos, bordes)}
    return filas, resumen


def numero(valor, decimales=3):
    return "no definido" if valor is None else f"{valor:.{decimales}f}"

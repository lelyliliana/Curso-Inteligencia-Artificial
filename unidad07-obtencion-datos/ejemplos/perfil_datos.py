"""Lectura y perfil de un CSV pequeño sin corregir ni descartar registros."""

from collections import Counter, defaultdict
import csv
from datetime import date, timedelta
import hashlib
import io
import math
from pathlib import Path
import re

COLUMNAS = ("fecha", "sensor_id", "consumo_kwh", "temperatura_c", "horas_uso")
RANGOS = {"consumo_kwh": (0, None), "temperatura_c": (None, None), "horas_uso": (0, 24)}
FALTANTES = {"", "NA"}


def fecha_iso(texto):
    if not isinstance(texto, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        raise ValueError("Se requiere una fecha AAAA-MM-DD.")
    return date.fromisoformat(texto)


def leer_csv(ruta):
    contenido = Path(ruta).read_bytes()
    # Mismos bytes para la huella y para el análisis; se admite BOM de UTF-8.
    lector = csv.reader(io.StringIO(contenido.decode("utf-8-sig"), newline=""), strict=True)
    encabezado = next(lector, None)
    if encabezado is None or len(encabezado) != len(COLUMNAS) or set(encabezado) != set(COLUMNAS):
        raise ValueError("Encabezado incorrecto: se requiere cada columna del esquema una sola vez.")
    registros = []
    for numero, valores in enumerate(lector, 1):
        if len(valores) != len(encabezado):
            raise ValueError(f"Registro {numero}: cantidad de campos distinta del encabezado.")
        registros.append(dict(zip(encabezado, valores)))
    return registros, hashlib.sha256(contenido).hexdigest()


def interpretar(campo, texto):
    """Devuelve valor/estado; interpreta espacios sin modificar el texto de origen."""
    valor = texto.strip()
    if valor in FALTANTES:
        return None, "faltante"
    if campo == "sensor_id":
        return valor, "valido"
    try:
        if campo == "fecha":
            return fecha_iso(valor), "valido"
        numero = float(valor)
        minimo, maximo = RANGOS[campo]
        if not math.isfinite(numero):
            raise ValueError("Número no finito.")
        if minimo is not None and numero < minimo:
            raise ValueError("Debajo del mínimo.")
        if maximo is not None and numero > maximo:
            raise ValueError("Sobre el máximo.")
        return numero, "valido"
    except (ValueError, OverflowError):
        return None, "invalido"


def perfilar(registros, inicio, fin, sensores):
    if inicio > fin or (fin - inicio).days > 365:
        raise ValueError("El periodo debe ser creciente y abarcar como máximo 366 días.")
    if (not sensores or len(set(sensores)) != len(sensores)
            or any(s != s.strip() or s in FALTANTES for s in sensores)):
        raise ValueError("Declara sensores sin repeticiones, espacios exteriores ni marcadores de ausencia.")
    columnas = {c: {"validos": 0, "faltantes": 0, "invalidos": 0} for c in COLUMNAS}
    estados = {"valido": "validos", "faltante": "faltantes", "invalido": "invalidos"}
    incidencias, sin_clave = [], []
    firmas = Counter()
    grupos = defaultdict(list)
    for n, registro in enumerate(registros, 1):
        valores = {}
        firma = tuple(registro[c] for c in COLUMNAS)
        firmas[firma] += 1
        for campo in COLUMNAS:
            valor, estado = interpretar(campo, registro[campo])
            valores[campo] = valor
            columnas[campo][estados[estado]] += 1
            if estado != "valido":
                incidencias.append({"registro": n, "campo": campo, "estado": estado, "texto": registro[campo]})
        if valores["fecha"] is None or valores["sensor_id"] is None:
            sin_clave.append(n)
        else:
            clave = (valores["fecha"].isoformat(), valores["sensor_id"])
            grupos[clave].append((n, firma))
    dias = [inicio + timedelta(days=i) for i in range((fin - inicio).days + 1)]
    esperadas = {(dia.isoformat(), sensor) for dia in dias for sensor in sensores}
    observadas = set(grupos)
    repetidas = []
    for clave, filas in sorted(grupos.items()):
        if len(filas) > 1:
            repetidas.append({
                "clave": list(clave), "registros": [n for n, _ in filas],
                "textos_distintos": len({firma for _, firma in filas}) > 1,
            })
    return {
        "filas": len(registros), "columnas": columnas, "incidencias": incidencias,
        "duplicados_exactos_adicionales": sum(n - 1 for n in firmas.values()),
        "claves_repetidas": repetidas, "registros_sin_clave": sin_clave,
        "cobertura": {
            "esperadas": len(esperadas), "presentes": len(esperadas & observadas),
            "porcentaje": round(100 * len(esperadas & observadas) / len(esperadas), 2),
            "ausentes": [list(c) for c in sorted(esperadas - observadas)],
            "fuera_del_plan": [list(c) for c in sorted(observadas - esperadas)],
        },
    }

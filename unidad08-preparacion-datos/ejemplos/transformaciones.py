"""Imputación por mediana y escalado min-max para una única variable numérica."""

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from statistics import median


def validar_valor(valor):
    if valor is None:
        return
    if type(valor) not in (int, float):
        raise ValueError("Los valores deben ser números o null; no texto ni booleanos.")
    try:
        finito = math.isfinite(valor)
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError("Los valores numéricos deben ser finitos y representables.")


@dataclass(frozen=True)
class Parametros:
    mediana: float
    minimo: float
    maximo: float


def ajustar(valores):
    for valor in valores:
        validar_valor(valor)
    observados = [float(v) for v in valores if v is not None]
    if not observados:
        raise ValueError("No hay valores observados en entrenamiento para calcular una mediana.")
    minimo, maximo = min(observados), max(observados)
    if minimo == maximo:
        raise ValueError("El rango de entrenamiento es cero; este ejemplo exige una política distinta para columnas constantes.")
    mediana = float(median(observados))
    if not math.isfinite(maximo - minimo) or not math.isfinite(mediana):
        raise ValueError("La escala numérica excede el rango representable del laboratorio.")
    return Parametros(mediana, minimo, maximo)


def transformar(valores, parametros):
    if (not all(math.isfinite(v) for v in (parametros.mediana, parametros.minimo, parametros.maximo))
            or not parametros.minimo <= parametros.mediana <= parametros.maximo
            or not parametros.minimo < parametros.maximo
            or not math.isfinite(parametros.maximo - parametros.minimo)):
        raise ValueError("Parámetros de transformación inválidos.")
    resultado = []
    for original in valores:
        validar_valor(original)
        faltante = original is None
        valor = parametros.mediana if faltante else float(original)
        escalado = (valor - parametros.minimo) / (parametros.maximo - parametros.minimo)
        if not math.isfinite(escalado):
            raise ValueError("El resultado escalado no es finito.")
        resultado.append({"original": original, "imputado": valor, "era_faltante": faltante, "escalado": escalado})
    return resultado


def objeto_unico(pares):
    objeto = {}
    for clave, valor in pares:
        if clave in objeto:
            raise ValueError(f"Clave JSON repetida: {clave}")
        objeto[clave] = valor
    return objeto


def leer_particiones(ruta):
    contenido = Path(ruta).read_bytes()
    datos = json.loads(contenido.decode("utf-8-sig"), object_pairs_hook=objeto_unico)
    if not isinstance(datos, dict) or set(datos) != {"variable", "unidad", "entrenamiento", "validacion"}:
        raise ValueError("Se requieren variable, unidad, entrenamiento y validacion.")
    if any(not isinstance(datos[k], str) or not datos[k].strip() for k in ("variable", "unidad")):
        raise ValueError("Variable y unidad deben ser textos no vacíos.")
    ids = set()
    for particion in ("entrenamiento", "validacion"):
        if not isinstance(datos[particion], list):
            raise ValueError("Cada partición debe ser una lista.")
        for registro in datos[particion]:
            if not isinstance(registro, dict) or set(registro) != {"id", "valor"}:
                raise ValueError("Cada registro requiere id y valor.")
            identificador = registro["id"]
            if not isinstance(identificador, str) or not identificador.strip() or identificador in ids:
                raise ValueError("Los identificadores deben ser textos únicos, también entre particiones.")
            ids.add(identificador)
            validar_valor(registro["valor"])
    return datos, hashlib.sha256(contenido).hexdigest()

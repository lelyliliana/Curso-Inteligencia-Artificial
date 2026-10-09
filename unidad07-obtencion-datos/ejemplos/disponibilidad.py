"""Valida una exportación JSON y audita entradas según el instante de decisión."""

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

CAMPOS = {"id", "sensor_id", "variable", "rol", "valor", "observado_en", "disponible_en"}
ROLES = {"consumo_kwh": "entrada", "temperatura_c": "entrada", "fallo_confirmado": "objetivo"}


def instante(texto):
    if not isinstance(texto, str) or "T" not in texto:
        raise ValueError("Indica fecha y hora ISO con T y zona, por ejemplo 2026-09-05T09:00:00+00:00.")
    valor = datetime.fromisoformat(texto)
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise ValueError("Cada instante necesita una zona horaria explícita.")
    return valor


def objeto_sin_repetidos(pares):
    objeto = {}
    for clave, valor in pares:
        if clave in objeto:
            raise ValueError(f"Clave JSON repetida: {clave}")
        objeto[clave] = valor
    return objeto


def rechazar_constante(valor):
    raise ValueError(f"Constante no admitida en JSON: {valor}")


def leer_eventos(ruta):
    contenido = Path(ruta).read_bytes()
    datos = json.loads(contenido.decode("utf-8-sig"), object_pairs_hook=objeto_sin_repetidos,
                       parse_constant=rechazar_constante)
    if not isinstance(datos, dict) or set(datos) != {"origen", "registros"}:
        raise ValueError("Se requieren origen y registros, sin otras claves.")
    origen = datos["origen"]
    if not isinstance(origen, dict) or set(origen) != {"tipo", "version", "descripcion"}:
        raise ValueError("El origen debe contener tipo, version y descripcion.")
    if any(not isinstance(v, str) or not v.strip() for v in origen.values()):
        raise ValueError("Los campos de origen deben ser textos no vacíos.")
    if not isinstance(datos["registros"], list):
        raise ValueError("Registros debe ser una lista, incluso si está vacía.")
    ids = set()
    for n, registro in enumerate(datos["registros"], 1):
        if not isinstance(registro, dict) or set(registro) != CAMPOS:
            raise ValueError(f"Registro {n}: campos diferentes del esquema.")
        for campo in CAMPOS - {"valor"}:
            if not isinstance(registro[campo], str) or not registro[campo].strip():
                raise ValueError(f"Registro {n}: {campo} debe ser texto no vacío.")
        if registro["id"] in ids:
            raise ValueError(f"Identificador de evento repetido: {registro['id']}")
        ids.add(registro["id"])
        variable = registro["variable"]
        if variable not in ROLES or registro["rol"] != ROLES[variable]:
            raise ValueError(f"Registro {n}: variable o rol incompatible con el caso.")
        valor = registro["valor"]
        if variable == "fallo_confirmado":
            if type(valor) is not bool:
                raise ValueError("fallo_confirmado requiere true o false, no números ni texto.")
        elif type(valor) not in (int, float) or not math.isfinite(valor):
            raise ValueError(f"Registro {n}: la medición debe ser numérica y finita, no booleana.")
        elif variable == "consumo_kwh" and valor < 0:
            raise ValueError("El consumo de este caso debe ser no negativo.")
        observado = instante(registro["observado_en"])
        disponible = instante(registro["disponible_en"])
        if disponible < observado:
            raise ValueError(f"Registro {n}: una observación no puede recibirse antes de ocurrir en este esquema.")
    return datos, hashlib.sha256(contenido).hexdigest()


def auditar(registros, decision):
    """Recibe registros validados; no agrega eventos ni construye un dataset de ML."""
    if decision.tzinfo is None or decision.utcoffset() is None:
        raise ValueError("La decisión requiere zona horaria.")
    resultado = {"entradas_disponibles": [], "entradas_excluidas": [], "objetivos": []}
    for registro in registros:
        if registro["rol"] == "objetivo":
            resultado["objetivos"].append(registro["id"])
            continue
        if instante(registro["observado_en"]) > decision:
            razon = "observación posterior a la decisión"
        elif instante(registro["disponible_en"]) > decision:
            razon = "observada antes, recibida después de la decisión"
        else:
            resultado["entradas_disponibles"].append(registro["id"])
            continue
        resultado["entradas_excluidas"].append({"id": registro["id"], "razon": razon})
    return resultado

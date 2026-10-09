"""Inferencia proposicional positiva; no interpreta negación ni ejecuta acciones."""

from dataclasses import dataclass
import json
from pathlib import Path
import re


def simbolo(valor):
    if not isinstance(valor, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", valor):
        raise ValueError("Cada símbolo debe empezar por a-z y usar a-z, 0-9 o _.")
    return valor


@dataclass(frozen=True)
class Regla:
    nombre: str
    condiciones: tuple[str, ...]
    conclusion: str


def validar(hechos, reglas, incompatibles):
    for hecho in hechos:
        simbolo(hecho)
    nombres = set()
    for regla in reglas:
        simbolo(regla.nombre)
        if regla.nombre in nombres:
            raise ValueError(f"Identificador de regla repetido: {regla.nombre}")
        nombres.add(regla.nombre)
        if not regla.condiciones:
            raise ValueError("Una regla requiere condiciones; registra los hechos por separado.")
        for condicion in regla.condiciones:
            simbolo(condicion)
        simbolo(regla.conclusion)
    for par in incompatibles:
        if not isinstance(par, (tuple, list)) or len(par) != 2:
            raise ValueError("Cada incompatibilidad debe contener dos símbolos.")
        a, b = map(simbolo, par)
        if a == b:
            raise ValueError("Una incompatibilidad requiere dos símbolos diferentes.")


def leer_base(ruta):
    base = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if not isinstance(base, dict) or set(base) != {"hechos", "reglas", "incompatibles"}:
        raise ValueError("La base requiere hechos, reglas e incompatibles, sin otras claves.")
    if any(not isinstance(base[k], list) for k in base):
        raise ValueError("Hechos, reglas e incompatibles deben ser listas.")
    reglas = []
    for dato in base["reglas"]:
        if not isinstance(dato, dict) or set(dato) != {"id", "si", "entonces"}:
            raise ValueError("Cada regla requiere id, si y entonces.")
        if not isinstance(dato["si"], list):
            raise ValueError("El campo si debe ser una lista de símbolos.")
        reglas.append(Regla(dato["id"], tuple(dato["si"]), dato["entonces"]))
    validar(base["hechos"], reglas, base["incompatibles"])
    return set(base["hechos"]), reglas, [tuple(p) for p in base["incompatibles"]]


def inferir(hechos, reglas, incompatibles=()):
    """Calcula el cierre y conserva la primera justificación de cada conclusión."""
    validar(hechos, reglas, incompatibles)
    conocidos = set(hechos)
    soportes = {hecho: None for hecho in conocidos}
    traza = []
    cambio = True
    while cambio:
        cambio = False
        for regla in reglas:
            if regla.conclusion not in conocidos and all(c in conocidos for c in regla.condiciones):
                conocidos.add(regla.conclusion)
                soportes[regla.conclusion] = regla
                traza.append(regla)
                cambio = True
    conflictos = [par for par in incompatibles if all(s in conocidos for s in par)]
    return {"hechos": conocidos, "soportes": soportes, "traza": traza, "conflictos": conflictos}


def explicar(consulta, resultado):
    """Recorre una prueba ya construida; no es encadenamiento hacia atrás."""
    simbolo(consulta)
    if consulta not in resultado["hechos"]:
        return [f"{consulta}: no se deriva con esta base; no equivale a demostrar su negación."]
    lineas = []
    pendientes = [(consulta, 0)]
    while pendientes:
        hecho, nivel = pendientes.pop()
        regla = resultado["soportes"][hecho]
        origen = "hecho inicial" if regla is None else f"por {regla.nombre}"
        lineas.append(f"{'  ' * nivel}{hecho}: {origen}")
        if regla is not None:
            pendientes.extend((c, nivel + 1) for c in reversed(regla.condiciones))
    return lineas

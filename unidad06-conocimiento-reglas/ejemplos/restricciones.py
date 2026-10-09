"""CSP pequeño con dominios enteros y restricciones binarias != y <."""

from itertools import product
import json
from pathlib import Path


def validar(dominios, restricciones):
    if not isinstance(dominios, dict) or not 1 <= len(dominios) <= 8:
        raise ValueError("Declara entre una y ocho variables.")
    for variable, valores in dominios.items():
        if not isinstance(variable, str) or not variable.strip():
            raise ValueError("Los nombres de variables deben ser textos no vacíos.")
        if not isinstance(valores, list) or len(valores) > 8:
            raise ValueError("Cada dominio debe ser una lista de hasta ocho enteros.")
        if any(type(v) is not int for v in valores) or len(set(valores)) != len(valores):
            raise ValueError("Los dominios requieren enteros únicos; no se aceptan booleanos.")
    if not isinstance(restricciones, list):
        raise ValueError("Las restricciones deben ser una lista.")
    for r in restricciones:
        if not isinstance(r, dict) or set(r) != {"a", "op", "b"}:
            raise ValueError("Cada restricción requiere a, op y b.")
        if any(not isinstance(r[k], str) for k in r):
            raise ValueError("Los campos a, op y b deben ser textos.")
        if r["a"] not in dominios or r["b"] not in dominios or r["a"] == r["b"]:
            raise ValueError("Cada restricción debe relacionar dos variables declaradas diferentes.")
        if r["op"] not in ("!=", "<"):
            raise ValueError("Operadores permitidos: != y <.")


def leer_problema(ruta):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if not isinstance(datos, dict) or set(datos) != {"dominios", "restricciones"}:
        raise ValueError("El problema requiere dominios y restricciones, sin otras claves.")
    validar(datos["dominios"], datos["restricciones"])
    return datos["dominios"], datos["restricciones"]


def compatible(asignacion, restricciones):
    """Una asignación parcial solo evalúa pares que ya tienen ambos valores."""
    for r in restricciones:
        if r["a"] in asignacion and r["b"] in asignacion:
            a, b = asignacion[r["a"]], asignacion[r["b"]]
            if r["op"] == "!=" and a == b:
                return False
            if r["op"] == "<" and not a < b:
                return False
    return True


def resolver(dominios, restricciones, orden="mrv", poda=True):
    """Enumera todas las soluciones; MRV desempata por orden del archivo."""
    validar(dominios, restricciones)
    if orden not in ("fija", "mrv"):
        raise ValueError("El orden debe ser fija o mrv.")
    # Evita explorar otras variables cuando la entrada ya hace imposible
    # completar la asignación, incluso si se desactiva la poda durante búsqueda.
    if any(not valores for valores in dominios.values()):
        return {"soluciones": [], "intentos": 0, "traza": ["SIN SOLUCIÓN: dominio inicial vacío"]}
    soluciones, traza = [], []
    intentos = 0

    def visitar(asignacion):
        nonlocal intentos
        if len(asignacion) == len(dominios):
            soluciones.append(dict(asignacion))
            traza.append(f"SOLUCIÓN {asignacion}")
            return
        pendientes = [v for v in dominios if v not in asignacion]
        # Filtrado respecto de las variables asignadas. No aplica AC-3.
        disponibles = {
            v: [x for x in dominios[v] if compatible({**asignacion, v: x}, restricciones)]
            for v in pendientes
        } if poda or orden == "mrv" else {v: dominios[v] for v in pendientes}
        if poda and any(not disponibles[v] for v in pendientes):
            traza.append(f"PODA {asignacion}: algún dominio restante está vacío")
            return
        variable = min(pendientes, key=lambda v: len(disponibles[v])) if orden == "mrv" else pendientes[0]
        candidatos = disponibles[variable] if poda else dominios[variable]
        for valor in candidatos:
            intentos += 1
            nueva = {**asignacion, variable: valor}
            if compatible(nueva, restricciones):
                traza.append(f"ACEPTA PARCIAL {nueva}")
                visitar(nueva)
            else:
                traza.append(f"RECHAZA {nueva}")

    visitar({})
    return {"soluciones": soluciones, "intentos": intentos, "traza": traza}


def enumerar(dominios, restricciones):
    """Línea base: genera todas las asignaciones completas antes de filtrarlas."""
    validar(dominios, restricciones)
    soluciones = []
    evaluadas = 0
    for valores in product(*dominios.values()):
        evaluadas += 1
        asignacion = dict(zip(dominios, valores))
        if compatible(asignacion, restricciones):
            soluciones.append(asignacion)
    return soluciones, evaluadas

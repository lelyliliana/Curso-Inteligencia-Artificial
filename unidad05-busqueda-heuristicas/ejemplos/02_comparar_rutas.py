"""Compara pasos, costo y heurística en un grafo dirigido sintético."""

import argparse
from pathlib import Path
import sys
from busqueda import (ALGORITMOS, buscar, imprimir_resultado, leer_problema,
                      numero, validar_heuristica, violaciones_consistencia)


DATOS = Path(__file__).resolve().parents[1] / "datos" / "grafo_rutas.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--factor-heuristica", type=float, default=1.0)
    parser.add_argument("--traza", action="store_true")
    args = parser.parse_args()
    try:
        g, inicio, meta, h = leer_problema(args.datos)
        factor = numero(args.factor_heuristica, "Factor de heurística")
        h = validar_heuristica(g, meta, {s: factor * v for s, v in h.items()})
        violaciones = violaciones_consistencia(g, h)
        resultados = [(nombre, buscar(g, inicio, meta, nombre, h)) for nombre in ALGORITMOS]
    except (OSError, UnicodeError, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Inicio={inicio}; meta={meta}; factor h={factor:g}")
    print("Heurística:", h)
    print("Aristas que violan consistencia:", violaciones)
    print("No se certifica admisibilidad solamente porque los valores sean finitos.")
    for nombre, resultado in resultados:
        imprimir_resultado(nombre.upper(), resultado, args.traza)
    print("Caso sintético. Expansiones y costos no validan desplazamientos reales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Compara BFS y DFS en un grafo unitario con un ciclo."""

import argparse
from busqueda import buscar, imprimir_resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traza", action="store_true")
    args = parser.parse_args()
    grafo = {
        "S": [("A", 1), ("B", 1)],
        "A": [("C", 1)],
        "B": [("G", 1)],
        "C": [("D", 1)],
        "D": [("A", 1), ("G", 1)],
        "G": [],
    }
    for algoritmo in ("bfs", "dfs"):
        imprimir_resultado(algoritmo.upper(), buscar(grafo, "S", "G", algoritmo), args.traza)
    print("Costos unitarios. El ciclo D → A no genera exploración infinita.")
    print("DFS respeta el primer vecino declarado al apilar en orden inverso.")


if __name__ == "__main__":
    main()

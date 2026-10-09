"""Audita h contra costos óptimos del grafo finito; no valida un entorno real."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from busqueda import buscar, leer_problema, numero, validar_heuristica, violaciones_consistencia


DATOS = Path(__file__).resolve().parents[1] / "datos" / "grafo_rutas.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--factor-heuristica", type=float, default=1.0)
    args = parser.parse_args()
    try:
        g, _, meta, h = leer_problema(args.datos)
        factor = numero(args.factor_heuristica, "Factor de heurística")
        h = validar_heuristica(g, meta, {s: factor * v for s,v in h.items()})
        sobreestimados = []
        print("estado    h       costo óptimo restante")
        for estado in g:
            resultado = buscar(g, estado, meta, "ucs")
            costo = resultado["costo"]
            texto = "sin ruta (infinito)" if costo is None else f"{costo:g}"
            print(f"{estado:6s} {h[estado]:7g} {texto:>24s}")
            if costo is not None and h[estado] > costo:
                sobreestimados.append(estado)
        violaciones = violaciones_consistencia(g,h)
    except (OSError, UnicodeError, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print("Estados que sobreestiman:", sobreestimados)
    print("Aristas que violan consistencia:", violaciones)
    print("Admisible en este grafo:", not sobreestimados)
    print("Consistente en este grafo:", not violaciones)
    print("La auditoría usa UCS en cada estado; su costo puede superar el de una sola búsqueda.")
    # Una heurística inválida como cota es un resultado didáctico, no un error de ejecución.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Compara distribuciones y asociaciones en 48 casos sintéticos completos."""

import argparse
import csv
from pathlib import Path
from exploracion import UNIDAD, analizar_grupos, numero


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos/consumos_por_grupo.csv")
    parser.add_argument("--intervalos", type=int, choices=(4, 8, 16), default=8)
    parser.add_argument("--salida", type=Path, help="Carpeta nueva para PNG, SVG y JSON; requiere Matplotlib.")
    args = parser.parse_args()
    try:
        filas, resumen = analizar_grupos(args.datos, args.intervalos)
        if args.salida is not None:
            from graficos import figura_distribuciones, figura_relaciones, guardar_entrega
            figuras = {"distribuciones": figura_distribuciones(filas, resumen),
                       "relaciones": figura_relaciones(filas, resumen)}
            guardar_entrega(args.salida, resumen, figuras)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Casos sintéticos: {resumen['total']['n']}; faltantes de consumo: {resumen['total']['faltantes']}")
    print("grupo | n | media | mediana | Q1 | Q3 | r de Pearson")
    for grupo, datos in resumen["grupos"].items():
        c = datos["consumo"]
        print(f"{grupo} | {c['n']} | {numero(c['media'])} | {numero(c['mediana'])} | "
              f"{numero(c['q1'])} | {numero(c['q3'])} | {numero(datos['correlacion']['r'])}")
    print("Media global:", numero(resumen["total"]["media"]))
    print("Correlación global:", numero(resumen["correlacion_total"]["r"]))
    print("Bordes (kWh):", ", ".join(f"{b:g}" for b in resumen["bordes_kwh"]))
    print("Frecuencias:", ", ".join(map(str, resumen["frecuencias"])))
    print("Una asociación en estos datos no demuestra una relación causal.")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

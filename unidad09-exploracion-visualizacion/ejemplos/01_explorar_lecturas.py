"""Explora las lecturas de la Unidad 8 sin imputar ni borrar su trazabilidad."""

import argparse
from pathlib import Path
from exploracion import analizar_lecturas, numero


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--correcciones", type=Path, help="Lote opcional de la Unidad 8.")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva para PNG, SVG y JSON; requiere Matplotlib.")
    args = parser.parse_args()
    try:
        analisis = analizar_lecturas(args.correcciones)
        if args.salida is not None:
            from graficos import figura_lecturas, guardar_entrega
            guardar_entrega(args.salida, analisis, {"lecturas": figura_lecturas(analisis)})
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")
    origen = analisis["preparacion"]
    resultado = origen["resultado"]
    print(f"Origen: {origen['antes']['filas']}; preparados: {len(resultado['preparados'])}; "
          f"duplicados: {len(resultado['duplicados'])}; cuarentena: {len(resultado['cuarentena'])}")
    print("sensor | días esperados | preparados | n consumo | faltante | sin preparar | media kWh")
    for sensor, datos in analisis["resumen"]["sensores"].items():
        c = datos["consumo"]
        print(f"{sensor} | {datos['esperados']} | {datos['preparados']} | {c['n']} | {c['faltantes']} | "
              f"{datos['sin_preparar']} | {numero(c['media'])}")
    print("Las medias describen días disponibles; no permiten ordenar eficiencia.")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

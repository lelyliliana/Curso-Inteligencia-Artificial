"""Genera 48 casos sintéticos deterministas; no simula una población real."""

import argparse
import csv
import io
from pathlib import Path

COLUMNAS = ("caso_id", "grupo", "horas_uso", "consumo_kwh")


def contenido_csv():
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(COLUMNAS)
    for grupo, inicio, base in (("A", 1, 14), ("B", 5, 36)):
        caso = 0
        for paso in range(6):
            horas = inicio + paso / 2
            for residuo in (-0.6, -0.2, 0.2, 0.6):
                caso += 1
                consumo = base - 1.5 * horas + residuo
                escritor.writerow((f"{grupo}{caso:02d}", grupo, f"{horas:.1f}", f"{consumo:.2f}"))
    return salida.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path, help="Archivo nuevo; no se sobrescribe.")
    args = parser.parse_args()
    try:
        with args.salida.open("x", encoding="utf-8", newline="") as archivo:
            archivo.write(contenido_csv())
    except OSError as error:
        parser.exit(2, f"Error: {error}\n")
    print("Generados 48 casos sintéticos:", args.salida)


if __name__ == "__main__":
    main()

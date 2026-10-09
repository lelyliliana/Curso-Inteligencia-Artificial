"""Genera seis CSV didácticos mediante una rejilla determinista, sin azar."""

import argparse
import csv
import io
import math
from pathlib import Path


def contenidos():
    archivos = {}
    for nombre in ("equilibrado", "desbalanceado"):
        for fase, particion in enumerate(("entrenamiento", "validacion", "prueba")):
            if nombre == "equilibrado":
                niveles, repeticiones = 10, (8 if fase == 0 else 4)
                inicio, paso, corte = (5, 7, 6)[fase], (10, 9, 9.5)[fase], 55
            else:
                niveles, repeticiones = 20, (10 if fase == 0 else 5)
                inicio, paso, corte = (2.5, 3.5, 1.5)[fase], (5, 4.8, 4.9)[fase], 95
            salida = io.StringIO(newline="")
            escritor = csv.writer(salida, lineterminator="\n")
            escritor.writerow(("caso_id", "senal_previa", "revision_confirmada"))
            numero = 0
            for i in range(niveles):
                x = round(inicio + paso * i, 2)
                referencia = 1 / (1 + math.exp(-(x - corte) / 15))
                for j in range(repeticiones):
                    numero += 1
                    u = (j + (0.5, 0.35, 0.65)[fase]) / repeticiones
                    y = int(u < referencia)
                    escritor.writerow((f"{nombre}-{particion}-{numero:03d}", f"{x:.2f}", y))
            archivos[f"{nombre}/{particion}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Directorio nuevo para los seis CSV.")
    args = parser.parse_args()
    try:
        args.salida.mkdir(parents=True, exist_ok=False)
        for nombre, contenido in contenidos().items():
            ruta = args.salida / nombre
            ruta.parent.mkdir(exist_ok=True)
            with ruta.open("x", encoding="utf-8", newline="") as archivo:
                archivo.write(contenido)
    except OSError as error:
        parser.exit(2, f"Error: {error}\n")
    print("Seis CSV sintéticos generados en", args.salida)


if __name__ == "__main__":
    main()

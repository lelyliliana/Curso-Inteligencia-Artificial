"""Genera ciclos sintéticos nuevos, con particiones fijas y sin azar."""

import argparse
import csv
import io
from pathlib import Path


def contenidos():
    archivos = {}
    lineal = {
        "entrenamiento": [(x, 3 + 2 * x + e) for x in range(1, 9) for e in (-.4, 0, .4)],
        "validacion": [(x + .5, 3 + 2 * (x + .5) + e) for x in range(1, 7) for e in (-.3, .3)],
        "prueba": [(x + .25, 3 + 2 * (x + .25) + e) for x in range(1, 7) for e in (-.2, .2)],
    }
    ruido = (-.8, .6, -.4, .7, -.6, .5, -.7, .9, -.5, .3)
    curva = {
        "entrenamiento": [(i + .5, 5 + .75 * (i + .5) ** 2 + e) for i, e in enumerate(ruido)],
        "validacion": [(x, 5 + .75 * x ** 2 + (-.2 if x % 2 else .2)) for x in range(1, 10)],
        "prueba": [(x + .25, 5 + .75 * (x + .25) ** 2 + (-.15 if x % 2 else .15)) for x in range(1, 9)],
    }
    for nombre, datos in (("lineal", lineal), ("curva", curva)):
        for fase, pares in datos.items():
            salida = io.StringIO(newline="")
            escritor = csv.writer(salida, lineterminator="\n")
            escritor.writerow(("caso_id", "horas_planificadas", "consumo_kwh"))
            for i, (x, y) in enumerate(pares, start=1):
                escritor.writerow((f"{nombre}-{fase}-{i:02d}", f"{x:.2f}", f"{y:.5f}"))
            archivos[f"{nombre}/{fase}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path, help="Directorio nuevo para los seis CSV.")
    args = parser.parse_args()
    try:
        args.salida.mkdir(parents=True, exist_ok=False)
        for nombre, texto in contenidos().items():
            ruta = args.salida / nombre
            ruta.parent.mkdir(exist_ok=True)
            with ruta.open("x", encoding="utf-8", newline="") as archivo:
                archivo.write(texto)
    except OSError as error:
        parser.exit(2, f"Error: {error}\n")
    print("Seis CSV sintéticos generados en", args.salida)


if __name__ == "__main__":
    main()

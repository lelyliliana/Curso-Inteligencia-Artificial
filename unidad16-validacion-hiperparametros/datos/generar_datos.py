"""Cuatro CSV nuevos para validación cruzada: ciclos independientes y equipos."""

import argparse
import csv
import io
from pathlib import Path
import numpy as np


def contenidos():
    archivos = {}
    for j, fase in enumerate(("desarrollo", "prueba")):
        rng = np.random.Generator(np.random.PCG64(2026161+j))
        n = (160, 64)[j]
        horas = np.round(rng.uniform(1, 9, n), 3)
        carga = np.round(rng.uniform(100, 900, n), 3)
        consumo = np.round(5 + .55*horas**2 + .018*carga + rng.normal(0, 1.2, n), 3)
        salida = io.StringIO(newline="")
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(["caso_id", "horas_previstas", "carga_prevista", "consumo_kwh"])
        for i, valores in enumerate(zip(horas, carga, consumo), 1):
            escritor.writerow([f"ciclos-{fase}-{i:03d}", *(f"{v:.3f}" for v in valores)])
        archivos[f"ciclos/{fase}.csv"] = salida.getvalue()

        rng = np.random.Generator(np.random.PCG64(2026163+j))
        salida = io.StringIO(newline="")
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(["caso_id", "equipo_id", "senal_a", "senal_b", "respuesta"])
        for g in range((12, 4)[j]):
            centro = rng.uniform(10, 90, 2)
            respuesta_base = rng.uniform(15, 85)
            senales = np.round(centro + rng.normal(0, .35, (12, 2)), 3)
            y = np.round(respuesta_base + rng.normal(0, .6, 12), 3)
            equipo = f"{'D' if j == 0 else 'P'}{g+1:02d}"
            for i, (x, real) in enumerate(zip(senales, y), 1):
                escritor.writerow([f"equipos-{equipo}-{i:02d}", equipo, *(f"{v:.3f}" for v in (*x, real))])
        archivos[f"equipos/{fase}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path, help="Carpeta nueva.")
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
    print("Cuatro CSV sintéticos generados en", args.salida)


if __name__ == "__main__":
    main()

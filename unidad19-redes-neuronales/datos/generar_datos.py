"""Seis CSV sintéticos nuevos, independientes por partición y regenerables."""
import argparse
import csv
from pathlib import Path
import numpy as np

PARTICIONES = ("entrenamiento", "validacion", "prueba")
TAMANOS = {"xor": (192, 96, 96), "ruido": (64, 160, 160)}


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    for nombre, tamanos in TAMANOS.items():
        (salida/nombre).mkdir()
        for p, (particion, n) in enumerate(zip(PARTICIONES, tamanos)):
            rng = np.random.Generator(np.random.PCG64(2026191+p+(10 if nombre == "ruido" else 0)))
            if nombre == "xor":
                signos = np.tile([[-1, -1], [-1, 1], [1, -1], [1, 1]], (n//4, 1))
                x = np.round(signos*rng.uniform(.25, 1, size=(n, 2)), 5)
                y = (x[:, 0]*x[:, 1] < 0).astype(int)
                orden = rng.permutation(n)
                x, y = x[orden], y[orden]
            else:
                x = np.round(rng.uniform(-1, 1, size=(n, 2)), 5)
                y = (np.sum(x*x, axis=1) < .55).astype(int)
                y = np.logical_xor(y, rng.random(n) < .15).astype(int)
            with (salida/nombre/f"{particion}.csv").open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["caso_id", "senal_a", "senal_b", "objetivo"])
                for i, (fila, etiqueta) in enumerate(zip(x, y)):
                    w.writerow([f"{nombre}-{particion}-{i:03d}", f"{fila[0]:.5f}", f"{fila[1]:.5f}", int(etiqueta)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    generar(args.salida)
    print("Datos generados:", args.salida)

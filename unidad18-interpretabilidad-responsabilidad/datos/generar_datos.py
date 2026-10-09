"""Datos sintéticos nuevos; solo escribe en una carpeta inexistente."""

import argparse
import csv
from pathlib import Path
import numpy as np

PARTICIONES = ("entrenamiento", "validacion", "prueba")
TAMANOS = {"consumo": (160, 80, 80), "alertas": ((180, 50, 6), (100, 40, 4), (80, 30, 4))}


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    for laboratorio in TAMANOS:
        (salida/laboratorio).mkdir()
        for p, particion in enumerate(PARTICIONES):
            semilla = 2026181 + p + (10 if laboratorio == "alertas" else 0)
            rng = np.random.Generator(np.random.PCG64(semilla))
            filas = []
            if laboratorio == "consumo":
                for i in range(TAMANOS[laboratorio][p]):
                    horas = round(float(rng.uniform(1, 9)), 4)
                    temperatura = round(float(rng.uniform(15, 35)), 4)
                    consumo = 4 + 3*horas + .2*temperatura + rng.normal(0, .4)
                    filas.append({"caso_id": f"C-{particion}-{i:03d}", "horas": f"{horas:.4f}",
                                  "minutos": f"{60*horas:.4f}", "temperatura_c": f"{temperatura:.4f}",
                                  "consumo_kwh": f"{consumo:.4f}"})
            else:
                for grupo, n in zip(("estandar", "desplazado", "escaso"), TAMANOS[laboratorio][p]):
                    for i in range(n):
                        latente = rng.uniform(0, .25 if grupo == "escaso" else 1)
                        lectura = np.clip(latente + rng.normal(0, .035) - (.30 if grupo == "desplazado" else 0), 0, 1)
                        filas.append({"caso_id": f"A-{particion}-{grupo}-{i:03d}", "grupo": grupo,
                                      "lectura": f"{lectura:.5f}", "requiere_revision": int(latente >= .55)})
            with (salida/laboratorio/f"{particion}.csv").open("w", encoding="utf-8", newline="") as f:
                escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
                escritor.writeheader()
                escritor.writerows(filas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    generar(args.salida)
    print("Datos generados:", args.salida)

"""Genera datos nuevos: una franja determinista y una región con azar fijado."""

import argparse
import csv
import io
from pathlib import Path
import numpy as np

SEMILLAS_DATOS = (2026131, 2026132, 2026133)


def contenidos():
    archivos = {}
    for fase, particion in enumerate(("entrenamiento", "validacion", "prueba")):
        for nombre in ("franja", "region"):
            if nombre == "franja":
                n = (80, 40, 40)[fase]
                x = ((np.arange(n) + (.5, .25, .75)[fase]) * 100 / n).reshape(-1, 1)
                y = ((x[:, 0] >= 30) & (x[:, 0] < 70)).astype(int)
                cambios = ([6, 18, 32, 46, 51, 65, 73], [3, 22], [8, 30])[fase]
                y[cambios] = 1 - y[cambios]
                decimales = 3
            else:
                n = (180, 120, 120)[fase]
                rng = np.random.Generator(np.random.PCG64(SEMILLAS_DATOS[fase]))
                x = np.round(rng.uniform(5, 95, (n, 2)), 2)
                y = (((x[:, 0] - 50) ** 2 + (x[:, 1] - 50) ** 2) < 30 ** 2).astype(int)
                cambios = rng.random(n) < .08
                y[cambios] = 1 - y[cambios]
                decimales = 2
            salida = io.StringIO(newline="")
            escritor = csv.writer(salida, lineterminator="\n")
            entradas = ["senal_a"] if nombre == "franja" else ["senal_a", "senal_b"]
            escritor.writerow(["caso_id", *entradas, "revision_confirmada"])
            for i, (fila, etiqueta) in enumerate(zip(x, y), start=1):
                escritor.writerow([f"{nombre}-{particion}-{i:03d}",
                                   *(f"{valor:.{decimales}f}" for valor in fila), int(etiqueta)])
            archivos[f"{nombre}/{particion}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Directorio nuevo para los seis CSV.")
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

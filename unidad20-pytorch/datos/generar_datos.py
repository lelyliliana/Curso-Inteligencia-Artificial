"""Crea datos nuevos y pequeños; no usa archivos de unidades anteriores."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

PARTICIONES = {"entrenamiento": (150, 20262001), "validacion": (80, 20262002),
               "prueba": (80, 20262003)}


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    ejemplo = {"x": [[-1., -.5], [-.5, .8], [0., -.2], [.3, .7], [.8, -.6], [1., .4]],
               "y": [0, 1, 0, 1, 0, 1], "ocultas": 3, "semilla": 20, "l2": .05, "tasa": .1}
    (salida/"equivalencia.json").write_text(json.dumps(ejemplo, indent=2)+"\n", encoding="utf-8")
    (salida/"minilotes").mkdir()
    for nombre, (n, semilla) in PARTICIONES.items():
        rng = np.random.Generator(np.random.PCG64(semilla))
        x = np.round(rng.uniform(-1, 1, (n, 2)), 5)
        s = 6*(x[:, 1]-.5*np.sin(np.pi*x[:, 0]))
        y = (rng.uniform(size=n) < 1/(1+np.exp(-s))).astype(int)
        with (salida/"minilotes"/f"{nombre}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["caso_id", "senal_a", "senal_b", "objetivo"])
            for i, (par, etiqueta) in enumerate(zip(x, y), 1):
                w.writerow([f"u20-{nombre}-{i:03d}", *[f"{v:.5f}" for v in par], int(etiqueta)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta nueva.")
    generar(parser.parse_args().salida)

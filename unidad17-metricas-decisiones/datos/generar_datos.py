"""Puntuaciones previas fijas y etiquetas posteriores de cuatro CSV sintéticos."""

import argparse
import csv
import io
from pathlib import Path
import numpy as np


def contenidos():
    archivos = {}
    for j, fase in enumerate(("validacion", "prueba")):
        for nombre, base in (("costos", 2026171), ("capacidad", 2026173)):
            rng = np.random.Generator(np.random.PCG64(base+j))
            salida = io.StringIO(newline="")
            escritor = csv.writer(salida, lineterminator="\n")
            escritor.writerow(["caso_id", *(["lote_id"] if nombre == "capacidad" else []), "senal_a", "senal_b", "puntuacion", "requiere_revision"])
            lotes = (8, 4)[j] if nombre == "capacidad" else 1
            for lote in range(lotes):
                n = 30 if nombre == "capacidad" else (240, 120)[j]
                a = np.round(rng.uniform(0, 1, n), 3)
                b = np.round(rng.uniform(0, 1, n), 3)
                intercepto = (-4.8 if lote % 3 == 0 else -2.8) if nombre == "capacidad" else -4.
                p = 1/(1+np.exp(-(intercepto+3*a+2*b)))
                puntuacion = np.round(p, 1)
                etiquetas = (rng.uniform(0, 1, n) < p).astype(int)
                for i in range(n):
                    id_lote = f"{fase}-L{lote+1:02d}"
                    identificador = f"{nombre}-{fase}-{lote*n+i+1:03d}"
                    escritor.writerow([identificador, *([id_lote] if nombre == "capacidad" else []),
                                       f"{a[i]:.3f}", f"{b[i]:.3f}", f"{puntuacion[i]:.1f}", str(etiquetas[i])])
            archivos[f"{nombre}/{fase}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta nueva.")
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

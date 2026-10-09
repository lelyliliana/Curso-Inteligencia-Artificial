"""Seis CSV nuevos: interacción con significado y dirección de baja varianza."""

import argparse
import csv
import io
from pathlib import Path
import numpy as np


def contenidos():
    archivos = {}
    for j, fase in enumerate(("entrenamiento", "validacion", "prueba")):
        n = (96, 48, 48)[j]
        for nombre, semilla in (("interaccion", 2026151+j), ("pca", 2026154+j)):
            rng = np.random.Generator(np.random.PCG64(semilla))
            if nombre == "interaccion":
                horas = np.round(rng.uniform(2, 10, n), 2)
                potencia = np.round(rng.uniform(2, 8, n), 2)
                y = np.round(3 + .8 * horas * potencia + rng.normal(0, .6, n), 3)
                columnas = ("horas_previstas", "potencia_prevista_kw", "lectura_cierre_kwh", "consumo_final_kwh")
                x = np.column_stack((horas, potencia, np.round(1000+y, 3), y))
            else:
                u = rng.uniform(-2, 2, n)
                v = rng.uniform(-1, 1, n)
                a = np.round(50 + 10*u + .6*v, 3)
                b = np.round(50 + 10*u - .6*v, 3)
                y = np.round(20 + 4*v + rng.normal(0, .2, n), 3)
                columnas = ("senal_a", "senal_b", "indice_respuesta")
                x = np.column_stack((a, b, y))
            salida = io.StringIO(newline="")
            escritor = csv.writer(salida, lineterminator="\n")
            escritor.writerow(["caso_id", *columnas])
            for i, fila in enumerate(x, 1):
                escritor.writerow([f"{nombre}-{fase}-{i:03d}", *(f"{valor:.3f}" for valor in fila)])
            archivos[f"{nombre}/{fase}.csv"] = salida.getvalue()
    return archivos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True, type=Path, help="Directorio nuevo.")
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

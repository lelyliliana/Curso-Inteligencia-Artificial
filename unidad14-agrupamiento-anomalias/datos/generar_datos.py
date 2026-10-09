"""Siete CSV sintéticos nuevos, con flujos PCG64 fijados por partición."""

import argparse
import csv
import io
from pathlib import Path
import numpy as np


def contenidos():
    archivos = {}
    for fase, n, semilla in (("entrenamiento", 90, 2026141), ("validacion", 60, 2026142), ("prueba", 60, 2026143)):
        rng = np.random.Generator(np.random.PCG64(semilla))
        centros = np.array([[3., 60.], [11., 230.], [19., 80.]])
        x = centros[np.arange(n) % 3] + rng.normal(size=(n, 2)) * [1., 18.]
        x = np.round(np.clip(x, [0, 0], [24, 500]), 2)
        x = x[rng.permutation(n)]
        archivos[f"grupos/{fase}.csv"] = serializar("grupos", fase, x, ("horas_uso", "consumo_kwh"))
    for fase, n, semilla in (("entrenamiento", 120, 2026144), ("calibracion", 60, 2026145),
                            ("validacion", 80, 2026146), ("prueba", 80, 2026147)):
        rng = np.random.Generator(np.random.PCG64(semilla))
        etiquetado = fase in ("validacion", "prueba")
        ordinarios = n - 16 if etiquetado else n
        centros = np.array([[30., 35.], [70., 65.]])
        normal = centros[np.arange(ordinarios) % 2] + rng.normal(size=(ordinarios, 2)) * [6., 5.]
        if etiquetado:
            # Dos regiones alejadas y dos cercanas al borde: detección imperfecta.
            centros_inusuales = np.array([[30., 70.], [70., 30.], [44., 44.], [58., 56.]])
            inusual = centros_inusuales[np.arange(16) % 4] + rng.normal(size=(16, 2)) * [4., 4.]
            x = np.vstack((normal, inusual))
            y = np.array([0] * ordinarios + [1] * 16)
        else:
            x, y = normal, None
        x = np.round(np.clip(x, 0, 100), 2)
        orden = rng.permutation(n)
        archivos[f"anomalias/{fase}.csv"] = serializar("anomalias", fase, x[orden],
                                                       ("senal_a", "senal_b"), None if y is None else y[orden])
    return archivos


def serializar(nombre, fase, x, entradas, y=None):
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(["caso_id", *entradas, *([] if y is None else ["anomalia_sintetica"])])
    for i, valores in enumerate(x):
        escritor.writerow([f"{nombre}-{fase}-{i+1:03d}", *(f"{v:.2f}" for v in valores),
                            *([] if y is None else [int(y[i])])])
    return salida.getvalue()


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
    print("Siete CSV sintéticos generados en", args.salida)


if __name__ == "__main__":
    main()

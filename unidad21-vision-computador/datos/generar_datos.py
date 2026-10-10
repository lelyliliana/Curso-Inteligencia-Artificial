"""Imágenes propias del curso: cada escena y sus dos vistas comparten partición."""
import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

PARTICIONES = {"entrenamiento": (60, 20262101), "validacion": (30, 20262102), "prueba": (30, 20262103)}
CLASES = ["horizontal", "vertical", "diagonal"]


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    (salida/"imagenes").mkdir()
    yy, xx = np.mgrid[:24, :24]
    rgb = np.stack([xx*10, yy*10, np.where((xx >= 8) & (xx < 16), 230, 30)], axis=-1).astype(np.uint8)
    Image.fromarray(rgb).save(salida/"colores.png")
    for particion, (n, semilla) in PARTICIONES.items():
        rng = np.random.Generator(np.random.PCG64(semilla))
        registros = []
        for i in range(n):
            clase = i % 3
            escena = f"u21-{particion}-{i:03d}"
            largo, ancho = int(rng.integers(6, 11)), int(rng.integers(1, 3))
            cy, cx = (int(v) for v in rng.integers(5, 11, 2))
            y0, x0 = cy-largo//2, cx-largo//2
            fondo, tinta = int(rng.integers(15, 51)), int(rng.integers(150, 241))
            base = np.full((16, 16), fondo, dtype=float)
            if clase == 0:
                base[cy-ancho//2:cy-ancho//2+ancho, x0:x0+largo] = tinta
            elif clase == 1:
                base[y0:y0+largo, cx-ancho//2:cx-ancho//2+ancho] = tinta
            else:
                inversa = bool(rng.integers(2))
                for paso in range(largo):
                    x = x0+(largo-1-paso if inversa else paso)
                    base[y0+paso, x:x+ancho] = tinta
            # La textura compartida hace explícita la dependencia de las dos vistas.
            base += rng.normal(0, 7, base.shape)
            for vista in range(2):
                valores = base+rng.normal(0, 9, base.shape)
                if vista == 1:
                    # Oclusión parcial nueva; etiqueta de escena conservada.
                    fy, fx = (int(v) for v in rng.integers(0, 13, 2))
                    valores[fy:fy+4, fx:fx+4] = fondo
                pixeles = np.clip(np.rint(valores), 0, 255).astype(np.uint8)
                imagen_id = f"{escena}-v{vista}"
                archivo = f"imagenes/{imagen_id}.png"
                Image.fromarray(pixeles).save(salida/archivo)
                registros.append({"imagen_id": imagen_id, "escena_id": escena, "archivo": archivo,
                                  "clase": clase, "sha256": hashlib.sha256((salida/archivo).read_bytes()).hexdigest()})
        with (salida/f"{particion}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(registros[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(registros)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta nueva.")
    generar(parser.parse_args().salida)

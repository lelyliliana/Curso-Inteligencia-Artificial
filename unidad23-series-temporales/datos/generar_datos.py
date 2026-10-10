"""Serie sintética horaria y muestra de calidad, creadas para la Unidad 23."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import math
from pathlib import Path
import random

INICIO = datetime(2026, 8, 1, tzinfo=timezone(timedelta(hours=-5)))
CAMPOS = ("id", "sensor", "instante", "disponible", "temperatura_c")


def lectura(hora, valor, retraso=10, sufijo=""):
    instante = INICIO + timedelta(hours=hora)
    return {"id": f"s1-{hora:04d}{sufijo}", "sensor": "s1", "instante": instante.isoformat(),
            "disponible": (instante + timedelta(minutes=retraso)).isoformat(),
            "temperatura_c": "" if valor is None else f"{valor:.6f}"}


def escribir(ruta, filas):
    with Path(ruta).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2301)
    huecos = {10, 130, 260, 601, 698, 809, 875, 933}
    vacios = {45, 180, 420, 635, 711, 847, 903}
    atrasados = {80, 222, 360, 575, 650, 767, 900, 955}
    particiones = {"entrenamiento": [], "validacion": [], "prueba": []}
    for t in range(960):
        # La fórmula es solo para generar datos, nunca una característica del modelo.
        valor = (19 + 3 * math.sin(2 * math.pi * (t % 24 - 8) / 24)
                 + .04 * (t / 24) + .45 * math.sin(2 * math.pi * t / 168)
                 + (2.5 if t >= 672 else 0) - (1.8 if t >= 864 else 0)
                 + rng.gauss(0, .15))
        if t in huecos:
            continue
        nombre = "entrenamiento" if t < 576 else "validacion" if t < 768 else "prueba"
        fila = lectura(t, None if t in vacios else valor, 90 if t in atrasados else 10)
        particiones[nombre].append(fila)
        if t == 100:
            particiones[nombre].append(dict(fila))
        if t == 690:
            particiones[nombre].append(lectura(t, valor + 5, 10, "-conflicto"))
    for nombre, filas in particiones.items():
        escribir(salida / f"{nombre}.csv", filas)
    muestra = [lectura(t, None if t == 8 else 20 + t, 150 if t == 7 else 10)
               for t in range(12) if t != 2]
    muestra.extend([lectura(3, 23), lectura(5, 35, sufijo="-conflicto")])
    # El archivo se entrega desordenado: su posición no equivale al tiempo.
    escribir(salida / "muestra.csv", list(reversed(muestra)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    generar(parser.parse_args().salida)

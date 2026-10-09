"""Construye dos experimentos sintéticos con particiones fijadas, sin azar."""

import argparse
import csv
from datetime import datetime, timedelta, timezone
import io
from pathlib import Path


def csv_texto(columnas, filas):
    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(columnas)
    escritor.writerows(filas)
    return salida.getvalue()


def contenidos():
    archivos = {}
    fases = ("entrenamiento", "validacion", "prueba")
    columnas = ("caso_id", "momento_prediccion", "entrada_disponible", "objetivo_disponible",
                "consumo_anterior_kwh", "consumo_objetivo_kwh")
    patron = (0, 1, -1, 2, 0, -2, 1, 0)
    consumos = [20 + 2 * (i // 8) + patron[i % 8] for i in range(33)]
    inicio = datetime(2026, 1, 2, tzinfo=timezone(timedelta(hours=-5)))
    bloques = {fase: [] for fase in fases}
    for i in range(32):
        instante = inicio + timedelta(days=i)
        fase = "entrenamiento" if i < 20 else "validacion" if i < 26 else "prueba"
        anterior = "" if i in (3, 12, 22, 28) else consumos[i]
        bloques[fase].append((f"R{i + 1:02d}", instante.isoformat(), instante.isoformat(),
                             (instante + timedelta(days=1)).isoformat(), anterior, consumos[i + 1]))
    for fase in fases:
        archivos[f"regresion/{fase}.csv"] = csv_texto(columnas, bloques[fase])

    columnas = ("caso_id", "equipo_id", "senal_previa", "fallo_24h")
    bloques = {fase: [] for fase in fases}
    for equipo in range(1, 9):
        fase = "entrenamiento" if equipo <= 4 else "validacion" if equipo <= 6 else "prueba"
        for caso in range(8):
            senal = "alta" if caso >= 6 else "baja"
            fallo = int(caso == 6 or (caso == 7 and equipo % 3 != 0)
                        or (caso == 0 and equipo % 4 == 0))
            bloques[fase].append((f"C{equipo:02d}-{caso + 1:02d}", f"E{equipo:02d}", senal, fallo))
    for fase in fases:
        archivos[f"clasificacion/{fase}.csv"] = csv_texto(columnas, bloques[fase])
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

"""Ajusta y = wx + b con gradientes completos en datos sintéticos declarados."""

import argparse
import csv
import math
from pathlib import Path
import sys


DATOS = Path(__file__).resolve().parents[1] / "datos" / "consumo_lineal.csv"


def leer_datos(ruta):
    conjuntos = {"entrenamiento": [], "prueba": []}
    ids = set()
    with Path(ruta).open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        campos = ["registro_id", "particion", "horas", "consumo_kwh"]
        if lector.fieldnames != campos:
            raise ValueError(f"El encabezado debe ser: {','.join(campos)}")
        for linea, fila in enumerate(lector, start=2):
            if None in fila or any(v is None or not v.strip() for v in fila.values()):
                raise ValueError(f"Fila {linea}: campos vacíos o cantidad de columnas incorrecta.")
            identificador = fila["registro_id"].strip()
            if identificador in ids:
                raise ValueError(f"Fila {linea}: identificador repetido.")
            ids.add(identificador)
            particion = fila["particion"].strip()
            if particion not in conjuntos:
                raise ValueError(f"Fila {linea}: partición desconocida.")
            try:
                x, y = float(fila["horas"]), float(fila["consumo_kwh"])
            except ValueError as exc:
                raise ValueError(f"Fila {linea}: horas y consumo deben ser numéricos.") from exc
            if not all(math.isfinite(v) and v >= 0 for v in (x, y)):
                raise ValueError(f"Fila {linea}: horas y consumo deben ser finitos y no negativos.")
            conjuntos[particion].append((x, y))
    if any(not casos for casos in conjuntos.values()):
        raise ValueError("Se requiere al menos un registro de entrenamiento y uno de prueba.")
    return conjuntos


def evaluar(casos, w, b):
    """Devuelve MSE; usa el signo residual = predicción - referencia."""
    return sum((w * x + b - y) ** 2 for x, y in casos) / len(casos)


def gradientes(casos, w, b):
    residuos = [(x, w * x + b - y) for x, y in casos]
    n = len(casos)
    dw = 2.0 * sum(x * e for x, e in residuos) / n
    db = 2.0 * sum(e for _, e in residuos) / n
    return dw, db


def entrenar(casos, tasa, pasos):
    if not casos:
        raise ValueError("Se requiere un conjunto de entrenamiento no vacío.")
    if not math.isfinite(tasa) or tasa <= 0:
        raise ValueError("La tasa debe ser finita y positiva.")
    if isinstance(pasos, bool) or not isinstance(pasos, int) or not 0 <= pasos <= 10000:
        raise ValueError("Pasos debe ser un entero entre 0 y 10000.")
    w, b = 0.0, 0.0
    historia = []
    try:
        for paso in range(pasos + 1):
            mse = evaluar(casos, w, b)
            dw, db = gradientes(casos, w, b)
            if not all(math.isfinite(v) for v in (w, b, mse, dw, db)):
                raise ValueError("Entrenamiento no finito; revisa escala y tasa.")
            historia.append((paso, w, b, mse))
            if paso < pasos:
                # Ambos gradientes corresponden al mismo estado anterior.
                w, b = w - tasa * dw, b - tasa * db
    except OverflowError as exc:
        raise ValueError("Desbordamiento numérico; revisa escala y tasa.") from exc
    return w, b, historia


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--tasa", type=float, default=0.05)
    parser.add_argument("--pasos", type=int, default=500)
    args = parser.parse_args()
    try:
        datos = leer_datos(args.datos)
        entrenamiento, prueba = datos["entrenamiento"], datos["prueba"]
        w, b, historia = entrenar(entrenamiento, args.tasa, args.pasos)
        # La línea base usa exclusivamente el promedio de las referencias de ajuste.
        promedio = sum(y for _, y in entrenamiento) / len(entrenamiento)
        base = evaluar(prueba, 0.0, promedio)
        final = evaluar(prueba, w, b)
        if not all(math.isfinite(v) for v in (promedio, base, final)):
            raise ValueError("Evaluación no finita; revisa los valores de los datos.")
    except (OSError, UnicodeError, csv.Error, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Casos: {len(entrenamiento)} entrenamiento, {len(prueba)} prueba.")
    print("paso          w           b       MSE entrenamiento")
    mostrar = {0, 1, 2, 10, 100, args.pasos}
    for paso, peso, sesgo, mse in historia:
        if paso in mostrar:
            print(f"{paso:4d} {peso:11.6f} {sesgo:11.6f} {mse:23.10f}")
    print(f"Línea base constante = {promedio:.6f}; MSE prueba = {base:.10f}")
    print(f"Recta final: consumo = {w:.6f} × horas + {b:.6f}")
    print(f"MSE prueba recta = {final:.10f}")
    for x, y in prueba:
        print(f"horas={x:g}; referencia={y:g}; predicción={w * x + b:.6f}")
    print("Datos sintéticos exactos: el ajuste no demuestra eficacia en consumos reales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Resume consumos sintéticos sin eliminar valores señalados por una regla."""

import argparse
import csv
import math
from pathlib import Path
import statistics
import sys


DATOS = Path(__file__).resolve().parents[1] / "datos" / "consumos_sinteticos.csv"


def leer_datos(ruta):
    valores, ids = [], set()
    with Path(ruta).open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != ["registro_id", "consumo_kwh"]:
            raise ValueError("Encabezado esperado: registro_id,consumo_kwh")
        for linea, fila in enumerate(lector, start=2):
            if None in fila or any(v is None or not v.strip() for v in fila.values()):
                raise ValueError(f"Fila {linea}: campos vacíos o columnas incorrectas.")
            identificador = fila["registro_id"].strip()
            if identificador in ids:
                raise ValueError(f"Fila {linea}: identificador repetido.")
            ids.add(identificador)
            try:
                valor = float(fila["consumo_kwh"])
            except ValueError as exc:
                raise ValueError(f"Fila {linea}: consumo no numérico.") from exc
            if not math.isfinite(valor) or valor < 0:
                raise ValueError(f"Fila {linea}: consumo debe ser finito y no negativo.")
            valores.append(valor)
    if not valores:
        raise ValueError("Se requiere al menos un registro.")
    return valores


def cuartiles_mitades(valores):
    """Medianas de las mitades; excluye la observación central si n es impar."""
    ordenados = sorted(valores)
    if len(ordenados) < 2:
        raise ValueError("Se requieren al menos dos datos para esta convención de cuartiles.")
    medio = len(ordenados) // 2
    inferior = ordenados[:medio]
    superior = ordenados[medio + len(ordenados) % 2:]
    return statistics.median(inferior), statistics.median(superior)


def resumir(valores):
    if not valores or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in valores):
        raise ValueError("Se requieren valores numéricos no vacíos.")
    if not all(math.isfinite(v) and v >= 0 for v in valores):
        raise ValueError("Los consumos deben ser finitos y no negativos.")
    resultado = {
        "n": len(valores), "media": statistics.mean(valores),
        "mediana": statistics.median(valores), "modas": statistics.multimode(valores),
        "minimo": min(valores), "maximo": max(valores),
        "varianza_poblacional": statistics.pvariance(valores),
        "varianza_muestral": statistics.variance(valores) if len(valores) > 1 else None,
        "desviacion_muestral": statistics.stdev(valores) if len(valores) > 1 else None,
        "q1": None, "q3": None, "iqr": None, "limites": None, "senalados": [],
    }
    if len(valores) > 1:
        q1, q3 = cuartiles_mitades(valores)
        iqr = q3 - q1
        limites = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        resultado.update(q1=q1, q3=q3, iqr=iqr, limites=limites,
                         senalados=[v for v in valores if v < limites[0] or v > limites[1]])
    for nombre in ("media", "varianza_poblacional", "varianza_muestral", "desviacion_muestral", "iqr"):
        if resultado[nombre] is not None and not math.isfinite(resultado[nombre]):
            raise ValueError("Resumen fuera del rango numérico; revisa escala de los datos.")
    if resultado["limites"] is not None and not all(math.isfinite(v) for v in resultado["limites"]):
        raise ValueError("Límites fuera del rango numérico.")
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    args = parser.parse_args()
    try:
        valores = leer_datos(args.datos)
        r = resumir(valores)
    except (OSError, UnicodeError, csv.Error, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print("Datos:", valores)
    print(f"n={r['n']}; media={r['media']:.6f}; mediana={r['mediana']:.6f}; modas={r['modas']}")
    print(f"Mínimo={r['minimo']:g}; máximo={r['maximo']:g}; rango={r['maximo']-r['minimo']:g}")
    print(f"Varianza con divisor n = {r['varianza_poblacional']:.6f} kWh²")
    if r["varianza_muestral"] is not None:
        print(f"Varianza con divisor n-1 = {r['varianza_muestral']:.6f} kWh²")
        print(f"Desviación muestral = {r['desviacion_muestral']:.6f} kWh")
        print(f"Q1={r['q1']:g}; Q3={r['q3']:g}; IQR={r['iqr']:g}; límites={r['limites']}")
        print("Señalados por la regla de 1.5 IQR:", r["senalados"])
    else:
        print("Con un dato no se calculan varianza muestral ni cuartiles de mitades.")
    print("No se elimina ningún registro. Señalado no significa incorrecto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

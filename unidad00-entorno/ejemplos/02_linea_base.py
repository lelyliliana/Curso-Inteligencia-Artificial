"""Resume lecturas ficticias y aplica una regla de alerta configurable.

No entrena un modelo. Usa exclusivamente la biblioteca estándar de Python.
"""

import argparse
import csv
from datetime import date
import math
from pathlib import Path
import statistics

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "datos" / "consumo_sintetico.csv"


def cargar_lecturas(ruta: Path) -> list[dict]:
    """Valida el esquema, las fechas y los valores; nunca descarta filas en silencio."""
    lecturas = []
    fechas = set()
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = csv.DictReader(archivo)
        if filas.fieldnames != ["fecha", "consumo_kwh"]:
            raise ValueError("El CSV debe tener las columnas fecha,consumo_kwh, en ese orden.")
        for numero, fila in enumerate(filas, start=2):
            try:
                if None in fila or any(valor is None for valor in fila.values()):
                    raise ValueError("cantidad de columnas incorrecta")
                texto_fecha = fila["fecha"].strip()
                fecha = date.fromisoformat(texto_fecha)
                if fecha.isoformat() != texto_fecha:
                    raise ValueError("la fecha debe usar AAAA-MM-DD")
                consumo = float(fila["consumo_kwh"])
                if not math.isfinite(consumo) or consumo < 0:
                    raise ValueError("el consumo debe ser finito y no negativo")
                if fecha in fechas:
                    raise ValueError("fecha repetida")
            except (ValueError, TypeError) as error:
                raise ValueError(f"Fila {numero}: {error}") from error
            fechas.add(fecha)
            lecturas.append({"fecha": fecha.isoformat(), "consumo_kwh": consumo})
    if not lecturas:
        raise ValueError("El CSV no contiene lecturas.")
    return lecturas


def resumir(lecturas: list[dict], umbral: float) -> dict:
    if not math.isfinite(umbral) or umbral < 0:
        raise ValueError("El umbral debe ser finito y no negativo.")
    if not lecturas:
        raise ValueError("No se puede resumir una lista vacía.")
    consumos = [lectura["consumo_kwh"] for lectura in lecturas]
    return {
        "registros": len(lecturas),
        "total_kwh": sum(consumos),
        "promedio_kwh": statistics.mean(consumos),
        "minimo_kwh": min(consumos),
        "maximo_kwh": max(consumos),
        "umbral_kwh": umbral,
        "alertas": [lectura for lectura in lecturas if lectura["consumo_kwh"] > umbral],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS, help="Ruta de un CSV de lecturas.")
    parser.add_argument("--umbral", type=float, default=16.0, help="Consumo diario límite en kWh.")
    args = parser.parse_args()
    try:
        resumen = resumir(cargar_lecturas(args.datos), args.umbral)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Registros: {resumen['registros']}")
    print(f"Total: {resumen['total_kwh']:.2f} kWh")
    print(f"Promedio: {resumen['promedio_kwh']:.2f} kWh")
    print(f"Mínimo: {resumen['minimo_kwh']:.2f} kWh")
    print(f"Máximo: {resumen['maximo_kwh']:.2f} kWh")
    print(f"Umbral de alerta: > {resumen['umbral_kwh']:.2f} kWh")
    print(f"Días con alerta: {len(resumen['alertas'])}")
    for lectura in resumen["alertas"]:
        print(f"  {lectura['fecha']}: {lectura['consumo_kwh']:.2f} kWh")


if __name__ == "__main__":
    main()

"""Compara reglas en un lote sintético según errores, costos y capacidad.

Comparación exploratoria: no entrena un modelo ni valida eficacia real.
"""

import argparse
import csv
import math
from pathlib import Path

DATOS = Path(__file__).resolve().parents[1] / "datos" / "casos_revision.csv"


def cargar(ruta: Path) -> list[dict]:
    casos = []
    ids = set()
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = csv.DictReader(archivo)
        if filas.fieldnames != ["caso_id", "consumo_parcial_kwh", "revision_referencia"]:
            raise ValueError("Columnas incorrectas: revisa el diccionario de datos.")
        for numero, fila in enumerate(filas, start=2):
            try:
                if None in fila or any(valor is None for valor in fila.values()):
                    raise ValueError("cantidad de columnas incorrecta")
                identificador = fila["caso_id"].strip()
                consumo = float(fila["consumo_parcial_kwh"])
                etiqueta = fila["revision_referencia"].strip()
                if not identificador or identificador in ids:
                    raise ValueError("identificador vacío o repetido")
                if not math.isfinite(consumo) or consumo < 0:
                    raise ValueError("consumo inválido")
                if etiqueta not in {"0", "1"}:
                    raise ValueError("etiqueta inválida")
            except (ValueError, TypeError) as error:
                raise ValueError(f"Fila {numero}: {error}") from error
            ids.add(identificador)
            casos.append({"caso_id": identificador, "consumo_parcial_kwh": consumo, "revision_referencia": int(etiqueta)})
    if not casos:
        raise ValueError("El CSV no contiene casos.")
    return casos


def evaluar(casos: list[dict], umbral: float | None, costo_omision: float, costo_innecesaria: float, capacidad: int) -> dict:
    if not casos:
        raise ValueError("Se necesitan casos para evaluar.")
    if umbral is not None and (not math.isfinite(umbral) or umbral < 0):
        raise ValueError("El umbral debe ser finito y no negativo.")
    if any(not math.isfinite(costo) or costo < 0 for costo in [costo_omision, costo_innecesaria]):
        raise ValueError("Los costos deben ser finitos y no negativos.")
    if type(capacidad) is not int or capacidad < 0:
        raise ValueError("La capacidad debe ser un entero no negativo.")
    tp = fp = tn = fn = 0
    for caso in casos:
        prediccion = 0 if umbral is None else int(caso["consumo_parcial_kwh"] > umbral)
        referencia = caso["revision_referencia"]
        if prediccion == 1 and referencia == 1:
            tp += 1
        elif prediccion == 1 and referencia == 0:
            fp += 1
        elif prediccion == 0 and referencia == 0:
            tn += 1
        else:
            fn += 1
    costo = fn * costo_omision + fp * costo_innecesaria
    if not math.isfinite(costo):
        raise ValueError("El costo calculado excede el rango numérico.")
    alertas = tp + fp
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "aciertos": tp + tn,
            "cantidad": len(casos), "exactitud": (tp + tn) / len(casos),
            "costo": costo, "alertas": alertas, "cumple_capacidad": alertas <= capacidad}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--capacidad", type=int, default=4)
    parser.add_argument("--costo-omision", type=float, default=5.0)
    parser.add_argument("--costo-innecesaria", type=float, default=1.0)
    args = parser.parse_args()
    propuestas = [("Ninguna alerta", None), ("Consumo > 18", 18.0), ("Consumo > 20", 20.0), ("Consumo > 22", 22.0)]
    try:
        casos = cargar(args.datos)
        resultados = [(nombre, evaluar(casos, umbral, args.costo_omision, args.costo_innecesaria, args.capacidad)) for nombre, umbral in propuestas]
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Lote: {len(casos)} casos; capacidad: {args.capacidad}")
    print(f"Costo de omisión: {args.costo_omision:g}; revisión innecesaria: {args.costo_innecesaria:g}")
    print("Propuesta | TP | FP | TN | FN | Exactitud | Costo | Alertas | Capacidad")
    for nombre, r in resultados:
        print(f"{nombre} | {r['tp']} | {r['fp']} | {r['tn']} | {r['fn']} | {r['exactitud']:.1%} | {r['costo']:g} | {r['alertas']} | {'cumple' if r['cumple_capacidad'] else 'excede'}")
    admisibles = [(nombre, r) for nombre, r in resultados if r["cumple_capacidad"]]
    nombre, mejor = min(admisibles, key=lambda item: (item[1]["costo"], item[1]["alertas"], item[0]))
    print(f"Candidata por costo y capacidad en este lote: {nombre} (costo {mejor['costo']:g}).")
    base = resultados[0][1]["costo"]
    if base > 0:
        print(f"Reducción de costo frente a ninguna alerta: {(base - mejor['costo']) / base:.1%}")
    else:
        print("Reducción porcentual no definida: el costo de la línea base es cero.")
    print("Selección exploratoria: requiere otra evaluación independiente antes de aprobar una aplicación.")


if __name__ == "__main__":
    main()

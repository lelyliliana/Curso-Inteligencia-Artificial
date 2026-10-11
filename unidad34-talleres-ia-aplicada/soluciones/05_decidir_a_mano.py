"""Tres poblaciones y tres unidades de medida: no promediar métricas distintas."""

import argparse
import json
from pathlib import Path


def calcular():
    reales, predichos = [10, 14, 12], [11, 11, 14]
    mae = sum(abs(y - p) for y, p in zip(reales, predichos)) / len(reales)
    # Etiquetas [1,1,0,0], decisiones [1,0,1,0]: un FP y un FN.
    costo = 1 * 1 + 4 * 1
    # Respondible correcta, fuera de corpus respondida, respondible omitida, fuera omitida.
    costos_documentos = [0, 3, 1, 0]
    return {"energia": {"n": 3, "mae_kw": mae},
            "ambiente": {"n": 4, "fp": 1, "fn": 1, "costo": costo},
            "documentos": {"n": 4, "respondidas": 2, "aceptadas": 2,
                           "cobertura": 0.5, "precision_respondidas": 0.5,
                           "costo": sum(costos_documentos)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    resultado = calcular()
    print("Decisión manual: MAE=2 kW; costo ambiental=5; costo documental=4; cobertura=2/4.")
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(resultado, indent=2) + "\n", encoding="utf-8")

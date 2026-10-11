"""Criterios simultáneos: mejora, error absoluto y cobertura no se sustituyen entre sí."""

import argparse
import json
from pathlib import Path


def calcular():
    return {"mae_modelo_kw": 1.5, "mae_referencia_kw": 2.0, "reduccion_relativa": 1 - 1.5 / 2,
            "admitidas": 94, "total": 100, "cobertura": .94,
            "condiciones": {"mae": True, "mejora": True, "cobertura": False}, "aceptado": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    print("Aceptación manual: mejora=25%; cobertura=94%; criterio conjunto=False.")
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(calcular(), indent=2) + "\n", encoding="utf-8")

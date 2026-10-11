"""Cinco solicitudes artificiales: denominadores, objetivo y percentil exacto."""
import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from observacion import Observador


def calcular():
    estados, tiempos = [200, 200, 422, 503, 500], [10, 30, 5, 2, 90]
    obs = Observador("artificial-sin-modelo", objetivo_ms=20)
    for i, (status, duracion) in enumerate(zip(estados, tiempos)):
        obs.iniciar()
        obs.terminar(f"manual-{i}", "prediccion", "POST", status, "ninguno", duracion)
    return {"tipo": "datos_artificiales_para_calculo", "status": estados, "tiempos_ms": tiempos,
            "resumen": obs.resumen(), "p95_rango_mas_cercano_ms": sorted(tiempos)[math.ceil(.95 * len(tiempos)) - 1]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida")
    args = p.parse_args()
    r = calcular()
    if args.salida:
        salida = Path(args.salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Métricas artificiales: 5 solicitudes; 5xx=2/5; buenas=1/5; media=27.4 ms.")


if __name__ == "__main__":
    main()

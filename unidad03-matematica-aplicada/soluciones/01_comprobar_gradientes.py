"""Contrasta las derivadas del laboratorio con diferencias centrales."""

import argparse
import importlib.util
import math
from pathlib import Path
import sys


def cargar_laboratorio():
    ruta = Path(__file__).resolve().parents[1] / "ejemplos" / "03_ajustar_recta.py"
    spec = importlib.util.spec_from_file_location("laboratorio_recta", ruta)
    if spec is None or spec.loader is None:
        raise ValueError("No se pudo cargar el laboratorio de la recta.")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def diferencias_centrales(evaluar, casos, w, b, epsilon):
    dw = (evaluar(casos, w + epsilon, b) - evaluar(casos, w - epsilon, b)) / (2 * epsilon)
    db = (evaluar(casos, w, b + epsilon) - evaluar(casos, w, b - epsilon)) / (2 * epsilon)
    return dw, db


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epsilon", type=float, default=1e-6)
    parser.add_argument("--tolerancia", type=float, default=1e-7)
    args = parser.parse_args()
    try:
        if not all(math.isfinite(v) and v > 0 for v in (args.epsilon, args.tolerancia)):
            raise ValueError("Epsilon y tolerancia deben ser finitos y positivos.")
        laboratorio = cargar_laboratorio()
        casos = laboratorio.leer_datos(laboratorio.DATOS)["entrenamiento"]
        resultados = []
        for w, b in ((0.0, 0.0), (1.2, 0.7), (2.0, 1.0)):
            analiticos = laboratorio.gradientes(casos, w, b)
            numericos = diferencias_centrales(laboratorio.evaluar, casos, w, b, args.epsilon)
            if not all(math.isfinite(v) for v in (*analiticos, *numericos)):
                raise ValueError("Resultado no finito; revisa epsilon.")
            resultados.append((w, b, analiticos, numericos))
    except (OSError, UnicodeError, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    correcto = True
    for w, b, analiticos, numericos in resultados:
        print(f"w={w:g}, b={b:g}")
        for nombre, a, n in zip(("dw", "db"), analiticos, numericos, strict=True):
            coincide = math.isclose(a, n, rel_tol=0.0, abs_tol=args.tolerancia)
            correcto = correcto and coincide
            print(f"  {nombre}: analítico={a:.10f}; numérico={n:.10f}; diferencia={abs(a-n):.3e}")
    print("Coinciden dentro de la tolerancia." if correcto else "Hay diferencias mayores que la tolerancia.")
    print("La comprobación cubre estos puntos; no constituye una demostración general.")
    return 0 if correcto else 1


if __name__ == "__main__":
    raise SystemExit(main())

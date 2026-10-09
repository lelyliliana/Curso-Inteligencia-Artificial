"""Simula ensayos Bernoulli independientes y cobertura del intervalo de Wilson."""

import argparse
import math
import random
from statistics import NormalDist
import sys


def wilson(k, n, confianza=0.95):
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (k, n)) or n < 1 or not 0 <= k <= n:
        raise ValueError("Se requieren enteros n >= 1 y 0 <= k <= n.")
    if not math.isfinite(confianza) or not 0 < confianza < 1:
        raise ValueError("Confianza debe estar entre 0 y 1, sin incluir extremos.")
    z = NormalDist().inv_cdf(0.5 + confianza / 2)
    p = k / n
    divisor = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / divisor
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / divisor
    inferior = 0.0 if k == 0 else max(0.0, centro - mitad)
    superior = 1.0 if k == n else min(1.0, centro + mitad)
    return inferior, superior


def simular(probabilidad, n, repeticiones, semilla):
    if isinstance(probabilidad, bool) or not isinstance(probabilidad, (int, float)) or not math.isfinite(probabilidad) or not 0 <= probabilidad <= 1:
        raise ValueError("Probabilidad debe ser finita y estar entre 0 y 1.")
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (n, repeticiones, semilla)):
        raise ValueError("n, repeticiones y semilla deben ser enteros.")
    if not 1 <= n <= 10000 or not 1 <= repeticiones <= 5000 or n * repeticiones > 2000000:
        raise ValueError("Usa 1..10000 datos, 1..5000 repeticiones y hasta 2000000 ensayos totales.")
    rng = random.Random(semilla)
    cubren, suma_estimaciones, suma_anchos = 0, 0.0, 0.0
    primera = None
    for _ in range(repeticiones):
        k = sum(rng.random() < probabilidad for _ in range(n))
        inferior, superior = wilson(k, n)
        if primera is None:
            primera = (k, k / n, inferior, superior)
        cubren += inferior <= probabilidad <= superior
        suma_estimaciones += k / n
        suma_anchos += superior - inferior
    return {"primera": primera, "cobertura": cubren / repeticiones,
            "media_estimaciones": suma_estimaciones / repeticiones,
            "ancho_medio": suma_anchos / repeticiones, "cubren": cubren}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probabilidad", type=float, default=0.30)
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--repeticiones", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        r = simular(args.probabilidad, args.n, args.repeticiones, args.seed)
    except (ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    k, estimacion, inferior, superior = r["primera"]
    print(f"Supuesto conocido: ensayos independientes con p={args.probabilidad:g} constante.")
    print(f"n={args.n}; repeticiones={args.repeticiones}; semilla={args.seed}")
    print(f"Primera muestra: k={k}; proporción={estimacion:.6f}")
    print(f"Wilson nominal 95 %: [{inferior:.6f}, {superior:.6f}]")
    print(f"Promedio de proporciones = {r['media_estimaciones']:.6f}")
    print(f"Ancho medio de intervalos = {r['ancho_medio']:.6f}")
    print(f"Intervalos que contienen p: {r['cubren']}/{args.repeticiones}; cobertura={100*r['cobertura']:.2f} %")
    print("La cobertura observada varía; no se exige que sea exactamente 95 %.")
    print("La simulación no certifica cobertura en datos reales con dependencia o sesgo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Descenso para L(w) = (w - 3)^2; imprime el estado inicial y cada paso."""

import argparse
import math
import sys


def perdida(w):
    return (w - 3.0) ** 2


def derivada(w):
    return 2.0 * (w - 3.0)


def descender(inicio, tasa, pasos):
    if not all(math.isfinite(v) for v in (inicio, tasa)) or tasa <= 0:
        raise ValueError("Inicio y tasa deben ser finitos; la tasa debe ser positiva.")
    if isinstance(pasos, bool) or not isinstance(pasos, int) or not 0 <= pasos <= 10000:
        raise ValueError("Pasos debe ser un entero entre 0 y 10000.")
    w = inicio
    historia = []
    try:
        for paso in range(pasos + 1):
            valor, pendiente = perdida(w), derivada(w)
            if not all(math.isfinite(v) for v in (w, valor, pendiente)):
                raise ValueError("La trayectoria dejó de ser finita; reduce la tasa o los pasos.")
            historia.append((paso, w, valor, pendiente))
            if paso < pasos:
                w = w - tasa * pendiente
    except OverflowError as exc:
        raise ValueError("Desbordamiento numérico; reduce la tasa o los pasos.") from exc
    return historia


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inicio", type=float, default=0.0)
    parser.add_argument("--tasa", type=float, default=0.1)
    parser.add_argument("--pasos", type=int, default=5)
    args = parser.parse_args()
    try:
        historia = descender(args.inicio, args.tasa, args.pasos)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print("paso          w        L(w)       L'(w)")
    for paso, w, valor, pendiente in historia:
        print(f"{paso:4d} {w:10.6f} {valor:11.6f} {pendiente:11.6f}")
    print("Mínimo conocido: w = 3, L(w) = 0.")
    print("La condición 0 < tasa < 1 corresponde a esta función concreta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

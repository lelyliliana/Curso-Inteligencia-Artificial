"""Calcula conteos esperados y Bayes en un escenario ficticio de alertas."""

import argparse
import math
import sys


def escenario(prevalencia, sensibilidad, especificidad, total):
    for nombre, valor in (("prevalencia", prevalencia), ("sensibilidad", sensibilidad),
                          ("especificidad", especificidad)):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or not 0 <= valor <= 1:
            raise ValueError(f"{nombre} debe ser una probabilidad finita entre 0 y 1.")
    if isinstance(total, bool) or not isinstance(total, int) or not 1 <= total <= 10**9:
        raise ValueError("Total debe ser entero entre 1 y 1000000000.")
    tp = total * prevalencia * sensibilidad
    fn = total * prevalencia * (1 - sensibilidad)
    fp = total * (1 - prevalencia) * (1 - especificidad)
    tn = total * (1 - prevalencia) * especificidad
    prob_alerta = prevalencia * sensibilidad + (1 - prevalencia) * (1 - especificidad)
    posterior = prevalencia * sensibilidad / prob_alerta if prob_alerta > 0 else None
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "prob_alerta": prob_alerta, "posterior": posterior}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prevalencia", type=float, default=0.01)
    parser.add_argument("--sensibilidad", type=float, default=0.90)
    parser.add_argument("--especificidad", type=float, default=0.95)
    parser.add_argument("--total", type=int, default=10000)
    args = parser.parse_args()
    try:
        r = escenario(args.prevalencia, args.sensibilidad, args.especificidad, args.total)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print("Supuestos ficticios; conteos esperados, no observaciones de un clasificador.")
    print(f"Prevalencia={args.prevalencia:.6f}; sensibilidad={args.sensibilidad:.6f}; especificidad={args.especificidad:.6f}")
    print(f"Total de referencia={args.total}")
    print(f"TP={r['tp']:.6f}; FN={r['fn']:.6f}; FP={r['fp']:.6f}; TN={r['tn']:.6f}")
    print(f"P(alerta)={r['prob_alerta']:.6f}; alertas esperadas={r['tp']+r['fp']:.6f}")
    if r["posterior"] is None:
        print("P(evento | alerta): no definida, porque P(alerta)=0.")
    else:
        print(f"P(evento | alerta)={r['posterior']:.6f} ({100*r['posterior']:.4f} %)")
    print("Las probabilidades condicionales se suponen iguales en el contexto comparado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

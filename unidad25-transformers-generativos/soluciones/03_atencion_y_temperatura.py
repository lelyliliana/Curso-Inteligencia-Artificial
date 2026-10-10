"""Pesos de atención, pérdida de un token y temperatura a mano."""
from math import exp, isclose, log, sqrt
from pathlib import Path
import sys
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from atencion import experimento
from transformer_curso import probabilidades


def main():
    r = experimento()
    fila = r["pesos_causales"][1]
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(fila, [1/3, 2/3, 0]))
    ce = -log(2/3)
    assert isclose(exp(ce), 1.5)
    logits = torch.tensor([log(4), log(2), 0.0], dtype=torch.float64)
    a, b = probabilidades(logits, 1), probabilidades(logits, 2)
    torch.testing.assert_close(a, torch.tensor([4/7, 2/7, 1/7], dtype=torch.float64))
    esperado = torch.tensor([2, sqrt(2), 1], dtype=torch.float64) / (3 + sqrt(2))
    torch.testing.assert_close(b, esperado)
    print("Pesos causales de la segunda posición: 1/3, 2/3, 0")
    print(f"CE de un token={ce:.6f}; perplejidad={exp(ce):.1f}")
    print("Temperatura 1:", [round(float(x), 6) for x in a])
    print("Temperatura 2:", [round(float(x), 6) for x in b])


if __name__ == "__main__":
    main()

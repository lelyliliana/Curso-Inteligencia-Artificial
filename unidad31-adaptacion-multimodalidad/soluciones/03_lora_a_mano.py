"""Producto de bajo rango y conservación de la capa base; datos artificiales."""

import argparse
from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from comun import guardar


def calcular():
    w = torch.tensor([[1., 0., -1.], [0., 2., 1.]], dtype=torch.float64)
    a = torch.tensor([[1., -1., 0.]], dtype=torch.float64)
    b = torch.tensor([[.5], [-.5]], dtype=torch.float64)
    x = torch.tensor([2., 1., 3.], dtype=torch.float64)
    antes = w @ x
    delta = b @ a
    salida = antes + b @ (a @ x)
    fusion = (w + delta) @ x
    assert torch.equal(salida, fusion)
    assert salida.tolist() == [-.5, 4.5]
    return {"origen": "matrices_artificiales", "W": w.tolist(), "A": a.tolist(), "B": b.tolist(),
            "x": x.tolist(), "base": antes.tolist(), "delta": delta.tolist(), "salida": salida.tolist(),
            "parametros_base": w.numel(), "parametros_adaptacion": a.numel() + b.numel()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    r = calcular()
    print("LoRA manual: salida base=[-1.0, 5.0]; adaptada=[-0.5, 4.5]; fusión idéntica.")
    print("En esta matriz diminuta: 5 parámetros de adaptación frente a 6 de la base.")
    if a.salida:
        guardar(a.salida / "lora_manual.json", r)


if __name__ == "__main__":
    main()

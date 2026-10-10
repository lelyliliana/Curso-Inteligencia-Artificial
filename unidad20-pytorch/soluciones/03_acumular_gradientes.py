"""Verifica a mano la acumulación y la actualización de un escalar."""
import torch


def demostrar():
    w = torch.tensor(2., dtype=torch.float64, requires_grad=True)
    perdida = lambda: .5*(3*w-1)**2
    perdida().backward()
    primero = w.grad.item()
    # Se construye un grafo NUEVO; el gradiente de la hoja continúa acumulándose.
    perdida().backward()
    acumulado = w.grad.item()
    w.grad = None
    perdida().backward()
    limpio = w.grad.item()
    with torch.no_grad():
        w -= .1*w.grad
    return primero, acumulado, limpio, w.item(), perdida().item()


if __name__ == "__main__":
    a, b, c, w, perdida = demostrar()
    print(f"Gradiente primero={a:.0f}; acumulado={b:.0f}; tras limpiar={c:.0f}")
    print(f"Peso tras SGD={w:.3f}; pérdida=12.500 -> {perdida:.3f}")

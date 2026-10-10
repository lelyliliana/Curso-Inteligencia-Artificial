"""Contrasta forward, BCE + L2, gradientes y un paso SGD con NumPy."""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn

from pytorch_curso import UNIDAD, Red, referencia, versiones


def como_numpy(modelo, gradientes=False):
    def extraer(p):
        return (p.grad if gradientes else p).detach().numpy().copy()
    a, b = modelo.capas[0], modelo.capas[2]
    return {"W1": extraer(a.weight).T, "b1": extraer(a.bias),
            "W2": extraer(b.weight).reshape(-1), "b2": extraer(b.bias)}


def comprobar(ruta=None):
    torch.set_num_threads(1)
    ruta = Path(ruta) if ruta is not None else UNIDAD/"datos/equivalencia.json"
    contenido = ruta.read_bytes()
    datos = json.loads(contenido)
    if not isinstance(datos, dict) or set(datos) != {"x", "y", "ocultas", "semilla", "l2", "tasa"}:
        raise ValueError("El JSON debe contener x, y, ocultas, semilla, l2 y tasa.")
    if (type(datos["semilla"]) is not int or datos["semilla"] < 0
            or any(type(datos[k]) not in (int, float) or not np.isfinite(datos[k]) for k in ("l2", "tasa"))
            or datos["l2"] < 0):
        raise ValueError("Semilla entera no negativa; L2 y tasa finitas; L2 no negativa.")
    x, y = referencia.validar_xy(datos["x"], datos["y"])
    if x.shape[1] != 2 or datos["ocultas"] != 3 or datos["tasa"] <= 0:
        raise ValueError("El caso de equivalencia requiere dos entradas, tres ocultas y tasa positiva.")
    p = referencia.inicializar(2, 3, datos["semilla"])
    modelo = Red([3], dtype=torch.float64)
    with torch.no_grad():
        modelo.capas[0].weight.copy_(torch.from_numpy(p["W1"].T))
        modelo.capas[0].bias.copy_(torch.from_numpy(p["b1"]))
        modelo.capas[2].weight.copy_(torch.from_numpy(p["W2"].reshape(1, -1)))
        modelo.capas[2].bias.copy_(torch.from_numpy(p["b2"]))
    xt, yt = torch.tensor(x, dtype=torch.float64), torch.tensor(y, dtype=torch.float64)
    optimizador = torch.optim.SGD(modelo.parameters(), lr=datos["tasa"])
    optimizador.zero_grad(set_to_none=True)
    logits = modelo(xt)
    objetivo = nn.BCEWithLogitsLoss()(logits, yt)
    objetivo = objetivo + datos["l2"]/2*sum((v*v).sum() for n, v in modelo.named_parameters() if n.endswith("weight"))
    objetivo.backward()
    valor, g = referencia.objetivo_gradiente(x, y, p, datos["l2"])
    gt = como_numpy(modelo, gradientes=True)
    nuevos = {k: p[k]-datos["tasa"]*g[k] for k in p}
    optimizador.step()
    pt = como_numpy(modelo)
    errores = {"logits": float(np.max(np.abs(logits.detach().numpy()-referencia.adelante(x, p)[0]))),
               "objetivo": abs(objetivo.item()-valor),
               "gradientes": max(float(np.max(np.abs(gt[k]-g[k]))) for k in g),
               "parametros_tras_paso": max(float(np.max(np.abs(pt[k]-nuevos[k]))) for k in p)}
    if not all(np.isfinite(e) for e in errores.values()) or max(errores.values()) > 1e-12:
        raise RuntimeError(f"Las implementaciones no coinciden: {errores}")
    return {"laboratorio": "equivalencia", "versiones": versiones(), "dtype": "float64", "dispositivo": "cpu",
            "fuente": {"archivo": ruta.name, "sha256": hashlib.sha256(contenido).hexdigest()},
            "configuracion": datos, "objetivo_numpy": valor, "objetivo_torch": objetivo.item(),
            "logits_numpy": referencia.adelante(x, p)[0].tolist(), "logits_torch": logits.detach().tolist(),
            "gradientes_numpy": {k: v.tolist() for k, v in g.items()},
            "gradientes_torch": {k: v.tolist() for k, v in gt.items()},
            "estado_inicial_numpy": {k: v.tolist() for k, v in p.items()},
            "estado_tras_paso_torch": {k: v.tolist() for k, v in pt.items()}, "errores_maximos": errores}

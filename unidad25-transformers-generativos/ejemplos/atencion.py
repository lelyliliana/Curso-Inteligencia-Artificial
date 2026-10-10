"""Atención explícita para comparar máscara, álgebra manual y biblioteca."""
import math
import numpy as np
import torch
import torch.nn.functional as F


def atender(q, k, v, causal=True):
    q, k, v = (np.asarray(a, dtype=np.float64) for a in (q, k, v))
    if (q.ndim != 2 or k.shape != q.shape or v.ndim != 2 or len(v) != len(q)
            or not q.size or not v.size or not all(np.isfinite(a).all() for a in (q, k, v))):
        raise ValueError("Se esperan Q,K compatibles y V con las mismas posiciones, todos finitos.")
    puntuaciones = q @ k.T / math.sqrt(q.shape[1])
    if causal:
        puntuaciones = np.where(np.tril(np.ones_like(puntuaciones, dtype=bool)), puntuaciones, -np.inf)
    exp = np.exp(puntuaciones - puntuaciones.max(axis=-1, keepdims=True))
    pesos = exp / exp.sum(axis=-1, keepdims=True)
    return pesos, pesos @ v


def experimento():
    q = np.array([[1, 0], [0, 1], [1, 1]], dtype=float) * math.sqrt(2)
    k = np.array([[1, 0], [0, 1], [1, 1]], dtype=float) * math.log(2)
    v = np.array([[2, 0], [0, 2], [2, 2]], dtype=float)
    causal, salida = atender(q, k, v)
    libre, sin_mascara = atender(q, k, v, False)
    referencia = F.scaled_dot_product_attention(*(torch.tensor(a)[None, None] for a in (q, k, v)),
                                                 is_causal=True, dropout_p=0.0)[0, 0].numpy()
    manual = np.array([[2, 0], [2/3, 4/3], [1.5, 1.5]])
    np.testing.assert_allclose(salida, referencia, atol=1e-12, rtol=0)
    np.testing.assert_allclose(salida, manual, atol=1e-12, rtol=0)
    futuro = v.copy()
    futuro[2] = [100, -100]
    _, cambiada = atender(q, k, futuro)
    _, libre_cambiada = atender(q, k, futuro, False)
    return {"q": q.tolist(), "k": k.tolist(), "v": v.tolist(),
            "pesos_causales": causal.tolist(), "pesos_libres": libre.tolist(),
            "salida": salida.tolist(), "salida_sin_mascara": sin_mascara.tolist(),
            "error_biblioteca": float(np.max(np.abs(referencia - salida))),
            "error_manual": float(np.max(np.abs(manual - salida))),
            "cambio_pasado_causal": float(np.max(np.abs(cambiada[:2] - salida[:2]))),
            "cambio_pasado_libre": float(np.max(np.abs(libre_cambiada[:2] - sin_mascara[:2])))}

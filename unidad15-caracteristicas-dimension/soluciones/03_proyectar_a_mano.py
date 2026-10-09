"""PCA centrado por autovectores: referencia pequeña independiente de la SVD."""

import numpy as np


def proyeccion_manual(x, k=1):
    x = np.asarray(x, dtype=float)
    if (x.ndim != 2 or len(x) < 2 or x.shape[1] < 1 or not np.isfinite(x).all()
            or type(k) is not int or not 1 <= k <= min(x.shape[1], len(x)-1)):
        raise ValueError("Matriz finita, dos casos como mínimo y dimensión válida requeridos.")
    media = x.mean(axis=0)
    centrada = x-media
    cov = centrada.T @ centrada / (len(x)-1)
    valores, vectores = np.linalg.eigh(cov)
    orden = np.argsort(valores)[::-1]
    valores = valores[orden]
    if valores.sum() <= 0:
        raise ValueError("La varianza total debe ser positiva.")
    ejes = vectores[:, orden[:k]].T
    for eje in ejes:
        if eje[np.argmax(np.abs(eje))] < 0:
            eje *= -1
    t = centrada @ ejes.T
    reconstruida = t @ ejes + media
    return {"media": media, "covarianza": cov, "ejes": ejes, "varianzas": valores,
            "proporcion": valores[:k].sum()/valores.sum(), "coordenadas": t, "reconstruccion": reconstruida,
            "mse": np.mean((x-reconstruida)**2)}


def main():
    resultado = proyeccion_manual([[2, 1], [-2, -1], [1, 2], [-1, -2]])
    print("Media:", resultado["media"].tolist())
    print("Varianzas:", ", ".join(f"{v:.6f}" for v in resultado["varianzas"]))
    print(f"Varianza retenida: {resultado['proporcion']:.3f}")
    print("Reconstrucción del primer caso:", resultado["reconstruccion"][0].round(6).tolist())
    print(f"MSE de reconstrucción por celda: {resultado['mse']:.3f}")
    print("Cambiar el signo de un eje y su coordenada conserva la reconstrucción.")


if __name__ == "__main__":
    main()

"""Una asignación y actualización de Lloyd, silueta y cambio de unidades."""

import numpy as np


def paso_lloyd(x, centros):
    """Paso didáctico: exige grupos no vacíos; empate a primer centro."""
    x, centros = np.asarray(x, dtype=float), np.asarray(centros, dtype=float)
    if (x.ndim != 2 or centros.ndim != 2 or not len(x) or not len(centros)
            or x.shape[1] != centros.shape[1] or not x.shape[1]
            or not np.isfinite(x).all() or not np.isfinite(centros).all()):
        raise ValueError("Puntos y centros deben ser matrices finitas compatibles y no vacías.")
    distancias2 = ((x[:, None, :] - centros[None, :, :]) ** 2).sum(axis=2)
    grupos = distancias2.argmin(axis=1)
    if len(set(grupos)) != len(centros):
        raise ValueError("Un grupo quedó vacío; este ejemplo no implementa reinicialización.")
    nuevos = np.array([x[grupos == i].mean(axis=0) for i in range(len(centros))])
    antes = float(distancias2[np.arange(len(x)), grupos].sum())
    despues = float(((x - nuevos[grupos]) ** 2).sum())
    return grupos, nuevos, antes, despues


def main():
    x = [[1., 1.], [1., 3.], [7., 7.], [9., 7.]]
    grupos, centros, antes, despues = paso_lloyd(x, [[1., 1.], [9., 7.]])
    print("Grupos:", grupos.tolist())
    print("Centros actualizados:", centros.tolist())
    print(f"Suma de distancias cuadradas: {antes:.3f} -> {despues:.3f}")
    # Para el primer punto: distancia media al mismo grupo = 2.
    a, b = 2., (np.sqrt(72) + 10) / 2
    print(f"Silueta del primer punto: {(b-a)/max(a,b):.6f}")
    # Consulta (0 h, 0 kWh), centros (1 h, 20 kWh) y (4 h, 0 kWh).
    print("Distancia sin escalar en kWh: el centro (4 h, 0 kWh) queda más cerca.")
    print("Al expresar energía en MWh: el centro (1 h, 0.020 MWh) queda más cerca.")
    print("Cambiar unidades puede cambiar la geometría si no se declara una escala.")


if __name__ == "__main__":
    main()

"""Dos descomposiciones de la misma predicción y tasas con denominadores."""


def reconstruir(base, coeficientes, z):
    if len(coeficientes) != len(z):
        raise ValueError("Dimensiones incompatibles.")
    return base + sum(c*v for c, v in zip(coeficientes, z))


if __name__ == "__main__":
    # Las dos primeras columnas estandarizadas son idénticas: z0 = z1.
    z = [1., 1., -1.]
    print(f"Contribuciones A: [3, 3, -1]; predicción={reconstruir(10, [3, 3, 1], z):.3f}")
    print(f"Contribuciones B: [6, 0, -1]; predicción={reconstruir(10, [6, 0, 1], z):.3f}")
    print("Recobrado: A=8/10=0.800; B=1/2=0.500; conjunto=9/12=0.750")
    print("Sin positivos: recobrado no definido; no se reemplaza por cero.")

"""Operaciones pequeñas para entender dimensiones; solo biblioteca estándar."""

import math


def vector(valores):
    if not isinstance(valores, (list, tuple)) or not valores:
        raise ValueError("Un vector debe ser una lista o tupla no vacía.")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in valores):
        raise ValueError("Cada componente debe ser numérico; no se aceptan booleanos.")
    try:
        resultado = [float(v) for v in valores]
    except OverflowError as exc:
        raise ValueError("Componente fuera del rango numérico.") from exc
    if not all(math.isfinite(v) for v in resultado):
        raise ValueError("Las componentes deben ser finitas.")
    return resultado


def pares(a, b):
    a, b = vector(a), vector(b)
    if len(a) != len(b):
        raise ValueError("Los vectores deben tener la misma longitud.")
    return a, b


def suma(a, b):
    a, b = pares(a, b)
    return vector([x + y for x, y in zip(a, b, strict=True)])


def escalar(a, factor):
    a, factor = vector(a), vector([factor])[0]
    return vector([factor * x for x in a])


def producto_punto(a, b):
    a, b = pares(a, b)
    return vector([sum(x * y for x, y in zip(a, b, strict=True))])[0]


def norma(a):
    return vector([math.hypot(*vector(a))])[0]


def distancia(a, b):
    a, b = pares(a, b)
    return norma(vector([x - y for x, y in zip(a, b, strict=True)]))


def matriz(filas):
    if not isinstance(filas, (list, tuple)) or not filas:
        raise ValueError("Una matriz debe contener al menos una fila.")
    resultado = [vector(fila) for fila in filas]
    if len({len(fila) for fila in resultado}) != 1:
        raise ValueError("Todas las filas deben tener la misma longitud.")
    return resultado


def transpuesta(a):
    a = matriz(a)
    return [list(columna) for columna in zip(*a, strict=True)]


def matriz_vector(a, b):
    a, b = matriz(a), vector(b)
    if len(a[0]) != len(b):
        raise ValueError("Columnas de la matriz y longitud del vector incompatibles.")
    return [producto_punto(fila, b) for fila in a]


def matriz_matriz(a, b):
    a, b = matriz(a), matriz(b)
    if len(a[0]) != len(b):
        raise ValueError("Columnas de A y filas de B deben coincidir.")
    columnas_b = transpuesta(b)
    return [[producto_punto(fila, columna) for columna in columnas_b] for fila in a]


def main():
    a, b = [2, 3], [6, 2]
    x = [a, b, [3, 5]]
    pesos, sesgo = [0.5, 2], 1
    print("a =", a, "b =", b)
    print("a + b =", suma(a, b))
    print("2a =", escalar(a, 2))
    print("a · b =", producto_punto(a, b))
    print(f"Norma de a = {norma(a):.6f}")
    print(f"Distancia(a, b) = {distancia(a, b):.6f}")
    print(f"Forma de X: {len(x)} filas × {len(x[0])} columnas")
    print("X transpuesta =", transpuesta(x))
    print("Xw =", matriz_vector(x, pesos))
    predicciones = suma(matriz_vector(x, pesos), [sesgo] * len(x))
    print("Xw + b =", predicciones)
    print("XW =", matriz_matriz(x, [[1, 2], [2, 0]]))
    print("Coeficientes ilustrativos: este programa no entrena un modelo.")


if __name__ == "__main__":
    main()

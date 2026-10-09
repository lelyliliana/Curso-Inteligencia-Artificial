"""Corte manual, cambio de una etiqueta y límite de extrapolación en regresión."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from arboles import cortes_gini, DecisionTreeClassifier, gini
from sklearn.tree import DecisionTreeRegressor


def main():
    xs, ys = list(range(1, 9)), [0, 0, 0, 0, 1, 1, 1, 1]
    mejor = min(cortes_gini(xs, ys), key=lambda c: c["gini_hijos"])
    print(f"Gini inicial={gini(ys):.3f}; mejor corte={mejor['corte']:.3f}; reducción={mejor['reduccion']:.3f}")
    variante = ys.copy()
    variante[3] = 1
    for nombre, etiquetas in (("original", ys), ("una etiqueta cambiada", variante)):
        arbol = DecisionTreeClassifier(max_depth=1, random_state=13).fit([[x] for x in xs], etiquetas)
        print(f"{nombre}: corte={arbol.tree_.threshold[0]:.3f}; clase para x=4: {arbol.predict([[4]])[0]}")
    print("Cambio solo en memoria; no es una corrección verificada ni modifica archivos.")
    regresor = DecisionTreeRegressor(max_depth=1, random_state=13).fit([[1], [2], [3], [4]], [2, 4, 6, 8])
    print(f"Árbol de regresión: x=4 -> {regresor.predict([[4]])[0]:.3f}; x=10 -> {regresor.predict([[10]])[0]:.3f}")
    print("La hoja devuelve su media: no prolonga la tendencia lineal.")


if __name__ == "__main__":
    main()

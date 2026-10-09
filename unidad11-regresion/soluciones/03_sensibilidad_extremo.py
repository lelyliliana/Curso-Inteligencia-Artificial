"""Perturba una copia en memoria del entrenamiento; no consulta prueba ni corrige datos."""

from pathlib import Path
import sys

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
from regresion import ajustar_recta, evaluar, leer_csv  # noqa: E402


def main():
    entrenamiento, _ = leer_csv(UNIDAD / "datos/lineal/entrenamiento.csv")
    validacion, _ = leer_csv(UNIDAD / "datos/lineal/validacion.csv")
    xs = [f["horas_planificadas"] for f in entrenamiento]
    ys = [f["consumo_kwh"] for f in entrenamiento]
    alterados = list(ys)
    alterados[-1] += 20
    print(f"Perturbación artificial: +20 kWh solo a {entrenamiento[-1]['caso_id']}, en memoria.")
    for nombre, valores in (("original", ys), ("perturbado", alterados)):
        modelo = ajustar_recta(xs, valores)
        a, b = modelo["coeficientes"]
        mae = evaluar(modelo, validacion)["metricas"]["mae"]
        print(f"{nombre}: intercepto={a:.3f}; pendiente={b:.3f}; MAE validación={mae:.3f}")
    print("No se excluye el punto ni se modifica el CSV; investigar un extremo requiere contexto.")


if __name__ == "__main__":
    main()

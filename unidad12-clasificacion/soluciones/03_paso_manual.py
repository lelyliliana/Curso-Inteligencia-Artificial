"""Un paso de gradiente y dos umbrales; no lee datos ni prueba."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from clasificacion import ajustar_logistica, decidir, probabilidades, sigmoide


def main():
    modelo = ajustar_logistica([40, 60], [0, 1], iteraciones=1)
    ps, _ = probabilidades(modelo, [40, 60])
    print("Dos casos: x=[40, 60]; y=[0, 1]; centro=50; escala=10; z=[-1, 1].")
    print("Inicio: a=0, b=0; p=[0.5, 0.5]; gradiente=[0, -0.5]; tasa=0.2.")
    print(f"Tras un paso: a={modelo['intercepto']:.3f}; b={modelo['coeficiente']:.3f}")
    print(f"Probabilidades: {ps[0]:.6f}, {ps[1]:.6f}")
    print(f"Objetivo penalizado: {modelo['historial'][0]['objetivo']:.6f} -> {modelo['historial'][-1]['objetivo']:.6f}")
    p = float(sigmoide(1))
    for umbral in (0.5, 0.8):
        print(f"Mismo logit=1, p={p:.6f}; umbral={umbral:.1f}; clase={decidir([p], umbral)[0]}")
    print("Cambiar el umbral modifica la clase, no la probabilidad ni los parámetros.")


if __name__ == "__main__":
    main()

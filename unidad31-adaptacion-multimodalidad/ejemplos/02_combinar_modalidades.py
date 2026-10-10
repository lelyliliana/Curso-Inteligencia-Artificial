"""Ablaciones por modalidad y cierre desde el modelo guardado."""

import argparse
from pathlib import Path

import multimodal as curso
from comun import guardar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path)
    p.add_argument("--graficos", action="store_true")
    p.add_argument("--evaluar-prueba", action="store_true")
    p.add_argument("--modelo", type=Path)
    a = p.parse_args()
    if a.evaluar_prueba != (a.modelo is not None):
        p.error("El cierre requiere --evaluar-prueba y --modelo juntos")
    if a.graficos and (not a.salida or a.evaluar_prueba):
        p.error("Los gráficos requieren desarrollo y --salida")
    if a.evaluar_prueba:
        r = curso.cerrar(a.modelo)
        e = r["evaluacion"]
        print(f"Cierre multimodal: {r['modo']}; correctas={e['correctas']}/{e['total']}; CE={e['ce']:.6f}")
        print("Diagnósticos:", r["diagnosticos"])
        if a.salida:
            guardar(a.salida / "cierre.json", r)
    else:
        _, r = curso.desarrollar(a.salida)
        for nombre, c in r["candidatos"].items():
            e = c["validacion"]
            print(f"{nombre}: correctas={e['correctas']}/{e['total']}; CE={e['ce']:.6f}")
        print(f"Seleccionado con validación: {r['seleccionado']}")
        print("Recarga: logits y predicciones idénticos; prueba reservada.")
        if a.graficos:
            from figuras import multimodal
            multimodal(r, a.salida)


if __name__ == "__main__":
    main()

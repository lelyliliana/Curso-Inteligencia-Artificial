"""Entrena en desarrollo; --evaluar-prueba recarga sin entrenar."""

import argparse
from pathlib import Path

import adaptacion as curso
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
        print(f"Cierre adaptación: {r['metodo']}; exactas={e['n_exactas']}/{e['n_documentos']}; CE={e['ce']:.6f}")
        if a.salida:
            guardar(a.salida / "cierre.json", r)
    else:
        _, r = curso.desarrollar(a.salida)
        for nombre, c in r["candidatos"].items():
            e = c["validacion"]
            print(f"{nombre}: exactas={e['n_exactas']}/{e['n_documentos']}; CE={e['ce']:.6f}; entrenables={c['entrenamiento']['entrenables']}")
        print(f"Seleccionado con validación: {r['seleccionado']}")
        print("Recarga: logits y generaciones idénticos; prueba reservada.")
        if a.graficos:
            from figuras import adaptacion
            adaptacion(r, a.salida)


if __name__ == "__main__":
    main()

"""Inspecciona una tarea conservada; nunca solicita inferencia nueva."""

import argparse
import json

from experimento import analizar
from herramientas import UNIDAD, cargar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fase", choices=("desarrollo", "cierre"), default="desarrollo")
    p.add_argument("--caso", default="A04a")
    a = p.parse_args()
    registro = cargar(UNIDAD / f"recursos/{a.fase}/registro.json")
    informe = analizar(registro)
    tareas = [t for t in registro["tareas"] if t["caso"] == a.caso]
    if not tareas:
        p.error("El caso no pertenece a esa fase")
    tarea = tareas[0]
    fila = next(f for f in informe["filas"] if f["caso"] == a.caso and f["metodo"] == "agente")
    for i, e in enumerate(tarea["eventos"], 1):
        print(f"{i}. {e['nombre']} {e['argumentos']} -> {e['etapa']}: {e['resultado']['codigo']}")
        print(json.dumps(e["resultado"]["datos"], ensure_ascii=False))
    print("Final:", json.dumps(tarea["final"], ensure_ascii=False))
    print(f"Parada: {tarea['parada']}; apoyo={fila['apoyo']}; aceptada={fila['aceptada']}")
    for i, llamada in enumerate(tarea["llamadas"], 1):
        if "error" in llamada:
            print(f"Solicitud {i}: error={llamada['error']}; pared={llamada['pared_s']:.3f} s")


if __name__ == "__main__":
    main()

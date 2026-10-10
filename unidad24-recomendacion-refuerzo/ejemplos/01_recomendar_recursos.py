"""Compara popularidad y coseno; el cierre requiere un estado ya guardado."""
import argparse
from pathlib import Path
import recomendacion_curso as curso


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--datos", type=Path, default=curso.UNIDAD / "datos")
    p.add_argument("--salida", type=Path)
    p.add_argument("--graficos", action="store_true")
    p.add_argument("--evaluar-prueba", action="store_true")
    p.add_argument("--modelo", type=Path)
    a = p.parse_args()
    if a.evaluar_prueba != (a.modelo is not None):
        p.error("El cierre requiere juntos --evaluar-prueba y --modelo.")
    if a.graficos and (a.salida is None or a.evaluar_prueba):
        p.error("--graficos requiere --salida y una ejecución de desarrollo.")
    try:
        if a.evaluar_prueba:
            informe = curso.cerrar(a.modelo, a.datos)
            m = informe["evaluacion"]["global"]
            print(f"Cierre sin reajuste: {informe['seleccionado']}; n={m['n']}; Recall@3={m['recall_3']:.4f}")
            if a.salida:
                curso.guardar_json(a.salida / "cierre.json", informe)
        else:
            modelo, informe = curso.desarrollar(a.datos)
            for nombre, r in informe["validacion"].items():
                m = r["global"]
                print(f"{nombre}: aciertos={m['aciertos']}/{m['n']}; Recall@3={m['recall_3']:.4f}; NDCG@3={m['ndcg_3']:.4f}; cobertura={m['cobertura']:.4f}")
                for grupo, g in r["grupos"].items():
                    print(f"  {grupo}: n={g['n']}; aciertos={g['aciertos']}")
            print(f"Seleccionado por Recall@3 de validación: {modelo['seleccionado']}")
            print("Prueba reservada; historial fijo de entrenamiento.")
            if a.salida:
                curso.exportar(modelo, informe, a.salida)
                print("Recarga: todas las listas coinciden.")
                if a.graficos:
                    from figuras_aplicaciones import recomendacion
                    recomendacion(informe, a.salida)
        if a.salida:
            print("Exportación:", a.salida)
    except (OSError, ValueError, KeyError, RuntimeError) as e:
        p.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    main()

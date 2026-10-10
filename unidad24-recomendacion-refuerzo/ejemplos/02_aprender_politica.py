"""Entrena cinco tablas Q y compara con una ruta fija informada."""
import argparse
from pathlib import Path
import refuerzo_curso as curso


def imprimir(e):
    b = e["referencia"]
    print(f"Referencia: éxito={b['exito']:.3f}; retorno={b['retorno']:.4f}")
    for r in e["q_learning"]:
        print(f"Q semilla {r['semilla_entrenamiento']}: éxito={r['exito']:.3f}; retorno={r['retorno']:.4f}; pozo={r['pozo']:.3f}; truncado={r['truncado']:.3f}")
    g = e["entre_semillas"]
    print(f"Cinco entrenamientos: éxito medio={g['exito']['media']:.3f}; desviación={g['exito']['desviacion']:.4f}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
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
            informe = curso.cerrar(a.modelo)
            imprimir(informe["evaluacion"])
            print("Cierre: cinco tablas recargadas; sin entrenamiento.")
            if a.salida:
                curso.guardar_json(a.salida / "cierre.json", informe)
        else:
            modelo, informe = curso.desarrollar()
            imprimir(informe["desarrollo"])
            print("Evaluación: sin exploración ni actualizaciones; cierre reservado.")
            if a.salida:
                curso.exportar(modelo, informe, a.salida)
                print("Recarga: tablas y evaluación idénticas.")
                if a.graficos:
                    from figuras_aplicaciones import refuerzo
                    refuerzo(modelo, informe, a.salida)
        if a.salida:
            print("Exportación:", a.salida)
    except (OSError, ValueError, KeyError, RuntimeError) as e:
        p.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    main()

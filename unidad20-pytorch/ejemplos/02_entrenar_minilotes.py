"""Entrenamiento en CPU; selección en validación y cierre opcional."""
import argparse
import csv
from pathlib import Path
from pytorch_curso import UNIDAD, ejecutar_experimento, exportar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD/"datos/minilotes")
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = ejecutar_experimento(args.datos, args.evaluar_prueba)
        if args.salida is not None:
            recarga = exportar(informe, args.salida)
            print(f"Recarga en CPU: error máximo en logits={recarga['max_error_logits']:.1f}")
            if args.graficos:
                from figuras import guardar_figuras
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print("candidato | parámetros libres | época elegida | BCE entrenamiento | BCE validación | exactitud validación")
    for nombre, c in informe["candidatos"].items():
        a, b = c["entrenamiento"]["metricas"], c["validacion"]["metricas"]
        print(f"{nombre} | {c['n_parametros']} | {c['epoca_elegida']} | {a['bce']:.4f} | {b['bce']:.4f} | {b['exactitud']:.3f}")
    c = informe["candidatos"][informe["seleccionado"]]
    print(f"Seleccionado por BCE de validación: {informe['seleccionado']}; época={c['epoca_elegida']}")
    entrenamiento = informe["candidatos"]["lineal"]
    print(f"Cada candidato entrenado: {informe['configuracion']['epocas']} épocas, "
          f"{len(entrenamiento['ordenes'][0]['tamanos'])} minilotes por época, "
          f"{entrenamiento['actualizaciones_totales']} actualizaciones.")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; BCE={m['bce']:.4f}; exactitud={m['exactitud']:.3f}; FN={m['FN']}; FP={m['FP']}")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

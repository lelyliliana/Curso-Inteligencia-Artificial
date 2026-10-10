"""Compara prevalencia, modelo lineal y CNN con separación por escena."""
import argparse
import csv
from pathlib import Path
from vision import CLASES, UNIDAD, ejecutar_experimento, exportar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD/"datos")
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = ejecutar_experimento(args.datos, args.evaluar_prueba)
        if args.salida is not None:
            error = exportar(informe, args.salida)
            print(f"Recarga en CPU: error máximo en logits={error:.1f}")
            if args.graficos:
                from figuras_vision import guardar_figuras
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print("candidato | parámetros libres | época | CE entrenamiento | CE validación | exactitud | macro F1")
    for nombre, c in informe["candidatos"].items():
        a, b = c["entrenamiento"]["metricas"], c["validacion"]["metricas"]
        print(f"{nombre} | {c['n_parametros']} | {c['epoca_elegida']} | {a['ce']:.4f} | {b['ce']:.4f} | {b['exactitud']:.3f} | {b['macro_f1']:.3f}")
    c = informe["candidatos"][informe["seleccionado"]]
    print(f"Seleccionado por CE de validación: {informe['seleccionado']}; época={c['epoca_elegida']}")
    print("Matriz de validación: filas reales, columnas predichas; orden:", ", ".join(CLASES))
    for fila in c["validacion"]["metricas"]["matriz"]:
        print(fila)
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su manifiesto ni sus imágenes.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; CE={m['ce']:.4f}; exactitud={m['exactitud']:.3f}; macro F1={m['macro_f1']:.3f}")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

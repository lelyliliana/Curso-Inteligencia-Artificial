"""Compara prevalencia y TF-IDF con logística sobre familias separadas."""
import argparse
import csv
from pathlib import Path
from texto_curso import UNIDAD, ejecutar_experimento, exportar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos")
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = ejecutar_experimento(args.datos, args.evaluar_prueba)
        if args.salida is not None:
            error = exportar(informe, args.salida)
            print(f"Recarga: error máximo en probabilidades={error:.1f}")
            if args.graficos:
                from figuras_texto import guardar_figuras
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print("candidato | columnas | CE entrenamiento | CE validación | exactitud | macro F1")
    for nombre, c in informe["candidatos"].items():
        train, val = c["entrenamiento"]["metricas"], c["validacion"]["metricas"]
        print(f"{nombre} | {len(c['estado'].get('vocabulario', []))} | {train['ce']:.4f} | {val['ce']:.4f} | {val['exactitud']:.3f} | {val['macro_f1']:.3f}")
    print("Seleccionado por CE de validación:", informe["seleccionado"])
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su CSV ni su huella.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; CE={m['ce']:.4f}; exactitud={m['exactitud']:.3f}; macro F1={m['macro_f1']:.3f}")
    print("Diagnósticos del elegido; referencias ambiguas no se puntúan:")
    for r in informe["diagnosticos"][informe["seleccionado"]]["registros"]:
        print(f"{r['id']} | {r['tipo']} | referencia={r['clase']} | predicha={r['predicha']} | p_máxima={max(r['probabilidades']):.3f} | vector_cero={r['vector_cero']}")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

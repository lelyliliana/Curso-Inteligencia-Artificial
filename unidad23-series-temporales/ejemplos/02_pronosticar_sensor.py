"""Compara pronósticos directos con observaciones disponibles en cada origen."""
import argparse
import csv
from pathlib import Path
from series_curso import UNIDAD, ejecutar_experimento, exportar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos")
    parser.add_argument("--horizonte", type=int, choices=(1, 6), default=1)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        r = ejecutar_experimento(args.datos, args.horizonte, args.evaluar_prueba)
        if args.salida is not None:
            error = exportar(r, args.salida)
            print(f"Recarga: error máximo={error:.1f} °C")
            if args.graficos:
                from figuras_series import guardar_figuras
                guardar_figuras(r, args.salida)
    except (OSError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Horizonte: {args.horizonte} h; decisión: origen + 10 min; orígenes sucesivos.")
    print("candidato | MAE entrenamiento | MAE validación | RMSE validación | sesgo validación")
    for nombre, c in r["candidatos"].items():
        train, val = c["entrenamiento"]["metricas"], c["validacion"]["metricas"]
        print(f"{nombre} | {train['mae']:.4f} | {val['mae']:.4f} | {val['rmse']:.4f} | {val['sesgo']:.4f}")
    print(f"Seleccionado por MAE de validación: {r['seleccionado']}; horizonte={args.horizonte} h")
    for p, c in r["conjuntos"].items():
        print(f"{p}: evaluables={c['evaluables']}; exclusiones={c['exclusiones']}")
    elegido = r["candidatos"][r["seleccionado"]]["validacion"]
    transicion = elegido["transicion_24h"]
    if transicion["n"]:
        print(f"Primeras 24 h tras cambio de validación: MAE={transicion['mae']:.4f} °C")
    else:
        print("Primeras 24 h tras cambio de validación: sin objetivos evaluables.")
    if r["prueba"] is None:
        print("Prueba reservada: no se abrió su CSV ni su huella.")
    else:
        m = r["prueba"]["evaluacion"]["metricas"]
        print(f"Prueba final: solo {r['seleccionado']}; h={args.horizonte}; n={m['n']}; MAE={m['mae']:.4f}; RMSE={m['rmse']:.4f}")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

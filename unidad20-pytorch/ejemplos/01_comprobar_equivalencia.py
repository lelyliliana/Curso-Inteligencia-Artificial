"""Ejecuta una comprobación numérica; no mide generalización."""
import argparse
import json
from pathlib import Path
from equivalencia import comprobar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, help="JSON de equivalencia; por defecto, el caso incluido.")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = comprobar(args.datos)
        if args.salida is not None:
            args.salida.mkdir(parents=True, exist_ok=False)
            (args.salida/"informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
            if args.graficos:
                from figuras import guardar_figuras
                guardar_figuras(informe, args.salida)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")
    for nombre, error in informe["errores_maximos"].items():
        print(f"Error máximo {nombre}: {error:.3e}")
    print("Equivalencia comprobada: tolerancia=1e-12; 13 parámetros; float64; CPU.")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

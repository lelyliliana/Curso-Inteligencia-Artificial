"""Canales y filtros fijos; no entrena un predictor."""
import argparse
import json
from pathlib import Path
from filtros import ejecutar_filtros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = ejecutar_filtros()
        if args.salida is not None:
            args.salida.mkdir(parents=True, exist_ok=False)
            (args.salida/"informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
            if args.graficos:
                from figuras_vision import guardar_figuras
                guardar_figuras(informe, args.salida)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")
    print("RGB: HWC=(24,24,3); NCHW=(1,3,24,24); gris=(24,24).")
    print("Filtros 3×3 sin relleno: salida 22×22; no son filtros aprendidos.")
    print(f"Referencia manual y conv2d: error máximo={informe['manual']['error_maximo']:.1f}")
    if args.salida is not None:
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

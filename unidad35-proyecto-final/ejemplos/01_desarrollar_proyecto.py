"""Selecciona con validación o evalúa el cierre de un estado ya guardado."""

import argparse
from pathlib import Path
import sys

from proyecto import desarrollar, cerrar, guardar


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--modelo", type=Path)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    if args.evaluar_prueba != (args.modelo is not None):
        parser.error("--evaluar-prueba y --modelo se usan juntos")
    try:
        if args.evaluar_prueba:
            informe = cerrar(args.modelo)
            for nombre, r in ((informe["elegido"], informe["resultado"]), ("persistencia", informe["referencia"])):
                print(f"Cierre {nombre}: MAE={r['mae_kw']:.4f} kW; admitidas={r['admitidas']}/{r['total']}.")
            print(f"Criterio didáctico de cierre: {informe['aceptacion']['cumple_criterio_didactico']}; uso real no autorizado.")
            if args.salida:
                guardar(args.salida / "prueba.json", informe)
        else:
            modelo, informe = desarrollar()
            for nombre, r in informe["resultados"].items():
                print(f"{nombre}: MAE={r['mae_kw']:.4f} kW; admitidas={r['admitidas']}/{r['total']}.")
            print(f"Proyecto elegido: {informe['elegido']}; recarga idéntica; prueba sin abrir.")
            if args.salida:
                guardar(args.salida / "modelo.json", modelo)
                guardar(args.salida / "validacion.json", informe)
    except (OSError, ValueError, KeyError) as error:
        print(f"Error de proyecto: {error}", file=sys.stderr)
        raise SystemExit(2)

"""Separa duplicados y cuarentena, conserva faltantes y aplica correcciones opcionales."""

import argparse
import csv
from pathlib import Path
from preparacion import UNIDAD07, exportar, generar_informe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=UNIDAD07 / "datos/lecturas_sinteticas.csv")
    parser.add_argument("--correcciones", type=Path, help="Lote explícito ligado a la huella de la fuente.")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva para dos CSV y el informe.")
    args = parser.parse_args()
    try:
        informe = generar_informe(args.datos, args.correcciones)
        if args.salida is not None:
            exportar(informe, args.salida)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    resultado = informe["resultado"]
    print(f"Origen: {informe['antes']['filas']} registros; correcciones: {len(informe['correcciones'])}")
    print(f"Preparados: {len(resultado['preparados'])}; duplicados: {len(resultado['duplicados'])}; cuarentena: {len(resultado['cuarentena'])}")
    print("Preparados con faltantes:", sum(bool(r["faltantes"]) for r in resultado["preparados"]))
    for etapa in ("antes", "despues"):
        c = informe[etapa]["cobertura"]
        print(f"Cobertura {etapa}: {c['presentes']}/{c['esperadas']} = {c['porcentaje']:.2f}%")
    for r in resultado["cuarentena"]:
        print(f"Cuarentena registro {r['registro']}: {', '.join(r['motivos'])}")
    print("Los faltantes permanecen; preparado no significa listo para cualquier modelo.")
    if args.salida is not None:
        print("Exportación:", args.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

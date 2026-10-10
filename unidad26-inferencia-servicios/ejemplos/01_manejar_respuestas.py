"""Doce escenarios simulados para distinguir transporte, contrato y contenido."""

import argparse
from pathlib import Path
from evaluacion import guardar
from simulacion import ejecutar_simulaciones


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    informe = ejecutar_simulaciones()
    print("Simulación de contrato: no hay red ni modelo.")
    for f in informe["filas"]:
        print(f"{f['id']}: contrato={f['contrato_valido']}; aceptada={f['aceptada']}; error={f.get('error', '-')}")
    n = sum(f["aceptada"] for f in informe["filas"])
    print(f"Escenarios simulados: 12; aceptados por el criterio: {n}.")
    if args.salida:
        guardar(args.salida / "informe.json", informe)
        print(f"Exportación: {args.salida}")


if __name__ == "__main__":
    main()

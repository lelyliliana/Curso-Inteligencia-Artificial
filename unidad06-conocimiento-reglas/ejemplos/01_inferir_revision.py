"""Deriva propuestas de revisión y muestra su justificación, sin ejecutar visitas."""

import argparse
from pathlib import Path
from reglas import explicar, inferir, leer_base, simbolo

DATOS = Path(__file__).resolve().parents[1] / "datos" / "reglas_revision.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--consulta", default="proponer_visita")
    parser.add_argument("--agregar", action="append", default=[], help="Hecho adicional; opción repetible.")
    parser.add_argument("--quitar", action="append", default=[], help="Hecho inicial a retirar; opción repetible.")
    args = parser.parse_args()
    try:
        hechos, reglas, incompatibles = leer_base(args.datos)
        agregar = {simbolo(s) for s in args.agregar}
        quitar = {simbolo(s) for s in args.quitar}
        if agregar & quitar:
            raise ValueError("No agregues y retires el mismo hecho en una ejecución.")
        if not quitar <= hechos:
            raise ValueError("Solo puedes retirar hechos iniciales presentes en el archivo.")
        resultado = inferir((hechos - quitar) | agregar, reglas, incompatibles)
        explicacion = explicar(args.consulta, resultado)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print("Hechos iniciales:", ", ".join(sorted((hechos - quitar) | agregar)) or "ninguno")
    for paso, regla in enumerate(resultado["traza"], 1):
        print(f"{paso}. {regla.nombre}: {' y '.join(regla.condiciones)} -> {regla.conclusion}")
    print("Consulta:")
    print("\n".join(explicacion))
    if resultado["conflictos"]:
        for a, b in resultado["conflictos"]:
            print(f"INCOMPATIBILIDAD declarada: {a} / {b}")
        print("Requiere revisión de la base; el programa no elige una propuesta.")
    else:
        print("Sin incompatibilidades declaradas activas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

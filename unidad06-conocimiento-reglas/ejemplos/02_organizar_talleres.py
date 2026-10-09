"""Compara enumeración completa, retroceso y filtrado en horarios sintéticos."""

import argparse
from pathlib import Path
from restricciones import enumerar, leer_problema, resolver

DATOS = Path(__file__).resolve().parents[1] / "datos" / "horarios.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--orden", choices=("fija", "mrv"), default="mrv")
    parser.add_argument("--sin-poda", action="store_true")
    parser.add_argument("--traza", action="store_true")
    args = parser.parse_args()
    try:
        dominios, restricciones = leer_problema(args.datos)
        # La línea base y las trazas son didácticas: limitamos su tamaño explícitamente.
        combinaciones = 1
        for valores in dominios.values():
            combinaciones *= len(valores)
        if combinaciones > 100000:
            raise ValueError("El laboratorio admite hasta 100000 combinaciones completas.")
        base, evaluadas = enumerar(dominios, restricciones)
        resultado = resolver(dominios, restricciones, args.orden, not args.sin_poda)
        normalizar = lambda ss: {tuple(s[v] for v in dominios) for s in ss}
        if normalizar(base) != normalizar(resultado["soluciones"]):
            raise RuntimeError("Los métodos no coinciden: revisa el algoritmo antes de interpretar.")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Enumeración: {evaluadas} asignaciones completas evaluadas.")
    print(f"Retroceso: orden={args.orden}; poda={not args.sin_poda}; intentos={resultado['intentos']}.")
    print(f"Soluciones: {len(resultado['soluciones'])}; coinciden con la línea base.")
    for n, solucion in enumerate(resultado["soluciones"], 1):
        print(f"{n}. " + "; ".join(f"{v}={solucion[v]}" for v in dominios))
    if not resultado["soluciones"]:
        print("Sin solución en este modelo; se agotó la búsqueda, sin corte por tiempo.")
    if args.traza:
        print("\n".join(resultado["traza"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

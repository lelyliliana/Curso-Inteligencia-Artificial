"""Laboratorio 2: peticiones reales a un servidor temporal en 127.0.0.1."""
import argparse

from apoyo import comprobar, guardar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida")
    args = parser.parse_args()
    informe = comprobar()
    if args.salida:
        guardar(args.salida, informe)
    print(f'HTTP local: {informe["cumplen"]}/{informe["total"]} comprobaciones correctas; servidor cerrado.')


if __name__ == "__main__":
    main()

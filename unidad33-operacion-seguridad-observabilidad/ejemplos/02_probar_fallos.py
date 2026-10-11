"""Laboratorio 2: saturación, mantenimiento, fallo y abandono de cliente."""
import argparse
from laboratorio import fallos, guardar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida")
    args = p.parse_args()
    r = fallos()
    if args.salida:
        guardar(args.salida, r)
    print(f'Fallos controlados: {len(r["casos"])} respuestas recibidas; timeout de cliente no cancela el servidor.')


if __name__ == "__main__":
    main()

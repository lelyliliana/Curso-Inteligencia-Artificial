"""Laboratorio 1: correlación y métricas sobre solicitudes reales."""
import argparse
from laboratorio import guardar, observar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida")
    args = p.parse_args()
    r = observar()
    if args.salida:
        guardar(args.salida, r)
    print(f'Observación HTTP: {len(r["casos"])} respuestas; {len(r["eventos"])} eventos correlacionados.')


if __name__ == "__main__":
    main()

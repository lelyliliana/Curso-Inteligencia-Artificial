"""Laboratorio 1: una entrada válida y una rechazada en la capa de servicio."""
import argparse

from apoyo import Servicio, entrada, guardar
from contrato import ErrorEntrada


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida")
    args = parser.parse_args()
    servicio = Servicio()
    respuesta = servicio.predecir(entrada())
    try:
        servicio.predecir({**entrada(), "texto": "no consultes derecha"})
        raise RuntimeError("La entrada inválida se aceptó")
    except ErrorEntrada as exc:
        rechazo = exc.respuesta()
    informe = {"consulta": respuesta, "rechazo": rechazo}
    if args.salida:
        guardar(args.salida, informe)
    print(f'Servicio: luz derecha -> {respuesta["resultado"]["clase"]}; texto libre rechazado.')


if __name__ == "__main__":
    main()

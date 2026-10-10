"""Una llamada opcional y potencialmente pagada a Responses; nunca en el verificador."""

import argparse
import os
import time

from evaluacion import CASOS, cargar
from servicios import ErrorServicio, OPENAI, leer_remota, peticion_remota, solicitar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    casos = {c["id"]: c for c in cargar(CASOS)}
    parser.add_argument("--caso", choices=casos, default="suma")
    parser.add_argument("--limite", type=int, default=256)
    args = parser.parse_args()
    modelo, clave = os.environ.get("OPENAI_MODEL", ""), os.environ.get("OPENAI_API_KEY", "")
    if not modelo.strip() or not clave.strip():
        parser.error("Configura OPENAI_MODEL y OPENAI_API_KEY fuera del código; no se ha enviado ninguna petición")
    caso = casos[args.caso]
    cuerpo = peticion_remota(modelo, caso["prompt"], args.limite)
    inicio = time.perf_counter()
    resultado = leer_remota(solicitar(OPENAI, cuerpo, clave=clave, timeout=120))
    print(f"Tiempo de pared: {time.perf_counter() - inicio:.3f} s")
    print(f"Estado={resultado['estado']}; rechazo={resultado['rechazo']}")
    print(f"Texto: {resultado['texto']!r}")
    print(f"Uso informado: {resultado['uso']}")
    print(f"Detalle incompleto: {resultado['detalle_incompleto']}")
    coincide = resultado['texto'].strip() == caso['esperado']
    print(f"Coincide={coincide}; aceptada={coincide and resultado['finalizada']}")


if __name__ == "__main__":
    try:
        main()
    except (ErrorServicio, ValueError) as exc:
        raise SystemExit(str(exc)) from None

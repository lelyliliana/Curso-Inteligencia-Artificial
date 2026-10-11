"""Consulta local al proyecto, sin abrir una API ni controlar dispositivos."""

import argparse
import json
from pathlib import Path
import sys

from proyecto import RAIZ, guardar
from servicio import MAX_BYTES, Servicio


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--modelo", type=Path, default=RAIZ / "recursos/modelo.json")
    parser.add_argument("--referencia", action="store_true", help="Usar explícitamente persistencia como reversión local.")
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    try:
        servicio = Servicio(args.modelo, referencia=args.referencia)
        with args.entrada.open("rb") as archivo:
            contenido = archivo.read(MAX_BYTES + 1)
        respuesta = servicio.responder(contenido)
        print(json.dumps(respuesta, ensure_ascii=False, indent=2, allow_nan=False))
        print(json.dumps(servicio.eventos[-1], ensure_ascii=False), file=sys.stderr)
        if args.salida:
            guardar(args.salida, respuesta)
        raise SystemExit(0 if "resultado" in respuesta else 2)
    except (OSError, ValueError, KeyError) as error:
        print(f"No se inició la consulta: {error}", file=sys.stderr)
        raise SystemExit(2)

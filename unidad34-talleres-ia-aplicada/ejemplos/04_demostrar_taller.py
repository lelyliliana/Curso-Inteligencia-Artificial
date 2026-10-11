"""Inferencia con el estado publicado y una entrada JSON, sin entrenamiento."""

import argparse
import json
from pathlib import Path
import sys

from talleres import RAIZ, MODULOS, cargar_modelo, guardar

CONSULTAS = {
    "energia": {"consumo_actual_kw": 35.0, "hora_siguiente": 14, "laboral_siguiente": 1},
    "ambiente": {"residuos_m2": 8.0, "superficie_afectada_pct": 65.0, "dias_sin_visita": 20},
    "documentos": {"pregunta": "¿Cómo reservar la sala Aurora?"}
}


def leer_entrada(ruta):
    with Path(ruta).open("rb") as archivo:
        datos = archivo.read(16385)
    if len(datos) > 16384:
        raise ValueError("La entrada supera 16 KiB")
    return json.loads(datos.decode("utf-8"))


def demostrar(taller, consulta, modelo=None):
    paquete = cargar_modelo(modelo or RAIZ / "recursos" / taller / "modelo.json", taller)
    return {"taller": taller, "modelo_sha256": paquete["sha256"],
            "salida": MODULOS[taller].predecir(paquete["estado"], consulta)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taller", choices=sorted(MODULOS), default="energia")
    parser.add_argument("--entrada", type=Path, help="JSON; se usa una consulta ilustrativa si se omite.")
    parser.add_argument("--modelo", type=Path, help="Por defecto, el estado publicado del taller.")
    parser.add_argument("--salida", type=Path, help="Archivo JSON de salida.")
    args = parser.parse_args()
    try:
        consulta = leer_entrada(args.entrada) if args.entrada else CONSULTAS[args.taller]
        respuesta = demostrar(args.taller, consulta, args.modelo)
        print(json.dumps(respuesta, ensure_ascii=False, indent=2, allow_nan=False))
        if args.salida:
            guardar(args.salida, respuesta)
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        print(f"Entrada o modelo rechazado: {error}", file=sys.stderr)
        raise SystemExit(2)

"""Exporta un resumen junto con parámetros, versión y huella del CSV utilizado."""

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path

EJEMPLOS = Path(__file__).resolve().parents[1] / "ejemplos"
SPEC = importlib.util.spec_from_file_location("linea_base", EJEMPLOS / "02_linea_base.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("No se pudo localizar el ejemplo de línea base.")
linea_base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(linea_base)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=linea_base.DATOS)
    parser.add_argument("--umbral", type=float, default=16.0)
    parser.add_argument("--salida", type=Path, default=linea_base.RAIZ / "resultados" / "resumen.json")
    args = parser.parse_args()
    try:
        origen = args.datos.resolve()
        destino = args.salida.resolve()
        if origen == destino:
            raise ValueError("La salida debe ser diferente del CSV de entrada.")
        # Una única lectura evita registrar una huella de una versión diferente
        # si el archivo cambia mientras se procesa. Se reutiliza la validación
        # de la línea base para mantener la misma definición de una lectura válida.
        contenido = origen.read_bytes()
        import tempfile
        with tempfile.TemporaryDirectory() as temporal:
            copia = Path(temporal) / "lecturas.csv"
            copia.write_bytes(contenido)
            resumen = linea_base.resumir(linea_base.cargar_lecturas(copia), args.umbral)
        registro = {
            "python": platform.python_version(),
            "sistema": platform.system(),
            "archivo_datos": origen.name,
            "sha256_datos": hashlib.sha256(contenido).hexdigest(),
            "regla": "consumo_kwh > umbral_kwh",
            "resumen": resumen,
        }
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Registro guardado en: {destino}")


if __name__ == "__main__":
    main()

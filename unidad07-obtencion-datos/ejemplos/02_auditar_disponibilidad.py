"""Revisa qué eventos podían utilizarse al decidir y separa los objetivos."""

import argparse
import json
from pathlib import Path
import platform
from disponibilidad import auditar, instante, leer_eventos

DATOS = Path(__file__).resolve().parents[1] / "datos/eventos_disponibilidad.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--decision", default="2026-09-05T09:00:00+00:00")
    parser.add_argument("--salida", type=Path, help="JSON opcional en un archivo nuevo.")
    args = parser.parse_args()
    try:
        datos, huella = leer_eventos(args.datos)
        decision = instante(args.decision)
        resultado = auditar(datos["registros"], decision)
        informe = {
            "archivo": args.datos.name, "sha256": huella, "python": platform.python_version(),
            "origen": datos["origen"], "decision": decision.isoformat(), "auditoria": resultado,
        }
        if args.salida is not None:
            args.salida.parent.mkdir(parents=True, exist_ok=True)
            with args.salida.open("x", encoding="utf-8") as destino:
                json.dump(informe, destino, ensure_ascii=False, indent=2)
                destino.write("\n")
    except (OSError, UnicodeError, ValueError, OverflowError) as error:
        parser.exit(2, f"Error: {error}\n")
    print("Origen:", datos["origen"]["tipo"], "versión", datos["origen"]["version"])
    print("Decisión:", decision.isoformat())
    print("Entradas disponibles:", ", ".join(resultado["entradas_disponibles"]) or "ninguna")
    for caso in resultado["entradas_excluidas"]:
        print(f"Excluida {caso['id']}: {caso['razon']}")
    print("Objetivos separados:", ", ".join(resultado["objetivos"]) or "ninguno")
    print("SHA-256:", huella)
    if args.salida is not None:
        print("Informe guardado:", args.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

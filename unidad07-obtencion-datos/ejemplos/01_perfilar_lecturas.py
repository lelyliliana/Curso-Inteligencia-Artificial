"""Perfila lecturas de sensores conservando faltantes, inválidos y duplicados."""

import argparse
import csv
import json
from pathlib import Path
import platform
from perfil_datos import fecha_iso, leer_csv, perfilar

DATOS = Path(__file__).resolve().parents[1] / "datos/lecturas_sinteticas.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--inicio", default="2026-09-01")
    parser.add_argument("--fin", default="2026-09-04")
    parser.add_argument("--sensores", nargs="+", default=["S1", "S2", "S3"])
    parser.add_argument("--salida", type=Path, help="JSON opcional en un archivo nuevo.")
    args = parser.parse_args()
    try:
        registros, huella = leer_csv(args.datos)
        perfil = perfilar(registros, fecha_iso(args.inicio), fecha_iso(args.fin), args.sensores)
        informe = {
            "archivo": args.datos.name, "sha256": huella, "python": platform.python_version(),
            "plan": {"inicio": args.inicio, "fin": args.fin, "sensores": args.sensores}, "perfil": perfil,
        }
        if args.salida is not None:
            args.salida.parent.mkdir(parents=True, exist_ok=True)
            with args.salida.open("x", encoding="utf-8") as destino:
                json.dump(informe, destino, ensure_ascii=False, indent=2)
                destino.write("\n")
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Filas: {perfil['filas']}; duplicados exactos adicionales: {perfil['duplicados_exactos_adicionales']}")
    for campo, conteos in perfil["columnas"].items():
        print(f"{campo}: válidos={conteos['validos']}; faltantes={conteos['faltantes']}; inválidos={conteos['invalidos']}")
    for caso in perfil["claves_repetidas"]:
        tipo = "textos distintos; requiere revisión" if caso["textos_distintos"] else "registros idénticos"
        print(f"Clave repetida {caso['clave']}: registros {caso['registros']}; {tipo}")
    cobertura = perfil["cobertura"]
    print(f"Cobertura de claves: {cobertura['presentes']}/{cobertura['esperadas']} = {cobertura['porcentaje']:.2f}%")
    print("Ausentes:", cobertura["ausentes"])
    print("Fuera del plan:", cobertura["fuera_del_plan"])
    print("Registros sin clave interpretable:", perfil["registros_sin_clave"])
    for incidencia in perfil["incidencias"]:
        print(f"Registro {incidencia['registro']}: {incidencia['campo']} {incidencia['estado']} ({incidencia['texto']!r})")
    print("SHA-256:", huella)
    if args.salida is not None:
        print("Informe guardado:", args.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

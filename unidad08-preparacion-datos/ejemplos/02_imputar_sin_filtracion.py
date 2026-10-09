"""Ajusta con entrenamiento y reutiliza parámetros sin aprender de validación."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform
from transformaciones import ajustar, leer_particiones, transformar

DATOS = Path(__file__).resolve().parents[1] / "datos/particiones_sinteticas.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--comparar-filtracion", action="store_true", help="Muestra aparte el ajuste incorrecto con ambas particiones.")
    parser.add_argument("--salida", type=Path, help="Archivo JSON nuevo para el resultado correcto.")
    args = parser.parse_args()
    try:
        datos, huella = leer_particiones(args.datos)
        valores = {p: [r["valor"] for r in datos[p]] for p in ("entrenamiento", "validacion")}
        parametros = ajustar(valores["entrenamiento"])
        resultados = {}
        for particion, lista in valores.items():
            resultados[particion] = [{"id": registro["id"], **salida}
                                    for registro, salida in zip(datos[particion], transformar(lista, parametros))]
        informe = {
            "archivo": args.datos.name, "sha256": huella, "python": platform.python_version(),
            "variable": datos["variable"], "unidad_original": datos["unidad"],
            "parametros_entrenamiento": asdict(parametros), "resultados": resultados,
        }
        incorrectos = ajustar(valores["entrenamiento"] + valores["validacion"]) if args.comparar_filtracion else None
        if args.salida is not None:
            args.salida.parent.mkdir(parents=True, exist_ok=True)
            with args.salida.open("x", encoding="utf-8") as f:
                json.dump(informe, f, ensure_ascii=False, indent=2, allow_nan=False)
                f.write("\n")
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Ajuste solo con entrenamiento: mediana={parametros.mediana:g}; mínimo={parametros.minimo:g}; máximo={parametros.maximo:g}")
    for particion, filas in resultados.items():
        print(particion.upper())
        for fila in filas:
            print(f"{fila['id']}: original={fila['original']}; imputado={fila['imputado']:g}; faltante={fila['era_faltante']}; escalado={fila['escalado']:.3f}")
    if incorrectos is not None:
        print("CONTRAEJEMPLO: mezclar validación al ajustar produce filtración; no usar estos parámetros.")
        print(f"Ajuste incorrecto: mediana={incorrectos.mediana:g}; mínimo={incorrectos.minimo:g}; máximo={incorrectos.maximo:g}")
    if args.salida is not None:
        print("Informe correcto guardado:", args.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

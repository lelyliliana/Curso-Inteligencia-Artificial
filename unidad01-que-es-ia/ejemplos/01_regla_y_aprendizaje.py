"""Compara una regla escrita y un umbral ajustado solo con entrenamiento.

Todos los datos son sintéticos. No usa bibliotecas externas ni sirve como
diagnóstico energético de una instalación.
"""

import argparse
import json
import math
from pathlib import Path

DATOS = Path(__file__).resolve().parents[1] / "datos" / "casos_sinteticos.json"


def validar_grupo(casos: object, nombre: str) -> list[dict]:
    if not isinstance(casos, list) or not casos:
        raise ValueError(f"{nombre}: se necesita una lista no vacía.")
    for numero, caso in enumerate(casos, start=1):
        if not isinstance(caso, dict) or set(caso) != {"consumo_kwh", "revision"}:
            raise ValueError(f"{nombre}, caso {numero}: campos incorrectos.")
        valor = caso["consumo_kwh"]
        if type(valor) not in (int, float) or not math.isfinite(valor) or valor < 0:
            raise ValueError(f"{nombre}, caso {numero}: consumo inválido.")
        if type(caso["revision"]) is not int or caso["revision"] not in (0, 1):
            raise ValueError(f"{nombre}, caso {numero}: etiqueta inválida.")
    return casos


def cargar_datos(ruta: Path) -> dict:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    grupos = {"entrenamiento", "prueba", "cambio_contexto"}
    if not isinstance(datos, dict) or set(datos) != grupos:
        raise ValueError("El JSON debe contener entrenamiento, prueba y cambio_contexto.")
    for nombre in sorted(grupos):
        validar_grupo(datos[nombre], nombre)
    return datos


def predecir(consumo: float, umbral: float) -> int:
    """Convierte una lectura en etiqueta usando la regla explícita >."""
    return int(consumo > umbral)


def contar_errores(casos: list[dict], umbral: float) -> int:
    return sum(predecir(caso["consumo_kwh"], umbral) != caso["revision"] for caso in casos)


def ajustar_umbral(entrenamiento: list[dict]) -> tuple[float, list[tuple[float, int]]]:
    validar_grupo(entrenamiento, "entrenamiento")
    valores = sorted({float(caso["consumo_kwh"]) for caso in entrenamiento})
    # Un punto entre cada par consecutivo cubre las separaciones internas.
    # Los extremos representan predecir revisión para todos o para ninguno.
    inferior = valores[0] - 1.0
    if inferior == valores[0]:
        inferior = math.nextafter(valores[0], -math.inf)
    candidatos = [inferior]
    candidatos.extend(izq / 2 + der / 2 for izq, der in zip(valores, valores[1:]))
    candidatos.append(valores[-1])
    evaluacion = [(umbral, contar_errores(entrenamiento, umbral)) for umbral in candidatos]
    # Criterio de empate explícito: menor umbral entre los de menor error.
    mejor, _ = min(evaluacion, key=lambda resultado: (resultado[1], resultado[0]))
    return mejor, evaluacion


def mostrar_resultados(nombre: str, casos: list[dict], fijo: float, aprendido: float) -> None:
    print(f"\n{nombre} ({len(casos)} casos)")
    print("Consumo | Etiqueta | Regla fija | Umbral aprendido")
    for caso in casos:
        consumo = caso["consumo_kwh"]
        print(f"{consumo:7.1f} | {caso['revision']:8d} | {predecir(consumo, fijo):10d} | {predecir(consumo, aprendido):16d}")
    for etiqueta, umbral in [("Regla fija", fijo), ("Umbral aprendido", aprendido)]:
        errores = contar_errores(casos, umbral)
        aciertos = len(casos) - errores
        palabra = "error" if errores == 1 else "errores"
        print(f"{etiqueta}: {aciertos}/{len(casos)} aciertos; {errores} {palabra}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--umbral-fijo", type=float, default=18.0)
    args = parser.parse_args()
    try:
        if not math.isfinite(args.umbral_fijo) or args.umbral_fijo < 0:
            raise ValueError("El umbral fijo debe ser finito y no negativo.")
        datos = cargar_datos(args.datos)
        aprendido, evaluacion = ajustar_umbral(datos["entrenamiento"])
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(2, f"Error: {error}\n")
    print("Ajuste: candidatos y errores solo en entrenamiento")
    for umbral, errores in evaluacion:
        palabra = "error" if errores == 1 else "errores"
        print(f"  umbral > {umbral!r}: {errores} {palabra}")
    print(f"Regla fija: consumo > {args.umbral_fijo:.2f}")
    print(f"Umbral aprendido: consumo > {aprendido:.2f}")
    mostrar_resultados("Prueba", datos["prueba"], args.umbral_fijo, aprendido)
    mostrar_resultados("Cambio de contexto", datos["cambio_contexto"], args.umbral_fijo, aprendido)
    print("\nResultados didácticos: no prueban eficacia sobre datos reales.")


if __name__ == "__main__":
    main()

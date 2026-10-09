"""Interfaz de las comparaciones de árboles y ensambles."""

import argparse
import csv
from pathlib import Path
from arboles import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definida" if valor is None else f"{valor:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Árboles: {nombre}, selección por F1 de validación.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--evaluar-prueba", action="store_true", help="Evalúa solo al elegido, sin reajuste.")
    parser.add_argument("--semilla", type=int, default=13, help="Semilla de modelos; otra semilla es otra variante.")
    parser.add_argument("--consulta", type=float, nargs="+", help="Una señal para franja; dos para región, entre 0 y 100.")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo para informe, reglas y CSV.")
    parser.add_argument("--graficos", action="store_true", help="Añade PNG/SVG de desarrollo; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida con un directorio nuevo.")
    try:
        informe, modelos = ejecutar_experimento(nombre, args.datos, args.evaluar_prueba, args.semilla, args.consulta)
        if args.graficos:
            from figuras import guardar_figuras, VERSIONES_GRAFICAS
            informe["versiones"].update(VERSIONES_GRAFICAS)
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, modelos, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, OverflowError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}")
    print("Semilla de modelos:", informe["semilla_modelos"])
    for fase in ("entrenamiento", "validacion"):
        fuente = informe["fuentes"][fase]
        print(f"{fase}: n={fuente['n']}; positivos={fuente['positivos']}")
    print("candidato | F1 entrenamiento | F1 validación | precisión | recobrado | FP | FN")
    for c, ev in informe["validacion"].items():
        m = ev["metricas"]
        print(f"{c} | {numero(informe['entrenamiento'][c]['metricas']['f1'])} | {numero(m['f1'])} | "
              f"{numero(m['precision'])} | {numero(m['recobrado'])} | {m['FP']} | {m['FN']}")
    print("Seleccionado por F1 de validación:", informe["seleccionado"])
    if informe["consulta"] is not None:
        c = informe["consulta"]
        print(f"Consulta: p(1)={c['probabilidad_1']:.3f}; clase={c['clase']}; "
              f"fuera del rango de entrenamiento: {'sí' if c['fuera_rango'] else 'no'}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: n={m['n']}; solo {informe['seleccionado']}; sin reajuste")
        print(f"VP={m['VP']}; VN={m['VN']}; FP={m['FP']}; FN={m['FN']}; F1={numero(m['f1'])}")
    print("Datos sintéticos; más árboles no garantizan mejor rendimiento ni calibración.")
    if args.salida is not None:
        print("Exportación:", args.salida)

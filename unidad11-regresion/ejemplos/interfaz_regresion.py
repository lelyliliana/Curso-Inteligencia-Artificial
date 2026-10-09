"""Interfaz compartida de los dos laboratorios de regresión."""

import argparse
import csv
from pathlib import Path
from regresion import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definido" if valor is None else f"{valor:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Regresión: experimento {nombre}, ajuste y selección separados.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--evaluar-prueba", action="store_true", help="Evalúa solo al elegido, sin reajuste.")
    parser.add_argument("--horas", type=float, help="Consulta al elegido; marca extrapolación, no mide error.")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo para informe y predicciones.")
    parser.add_argument("--graficos", action="store_true", help="Añade figuras PNG/SVG; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida con un directorio nuevo.")
    try:
        informe = ejecutar_experimento(nombre, args.datos, args.evaluar_prueba, args.horas)
        if args.graficos:
            from figuras import VERSIONES_GRAFICAS, guardar_figuras
            informe["versiones"].update(VERSIONES_GRAFICAS)
            # Cargar el renderizador antes de crear la entrega para detectar dependencias ausentes.
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, OverflowError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}")
    print(f"Entrenamiento: {informe['fuentes']['entrenamiento']['n']}; validación: {informe['fuentes']['validacion']['n']}")
    a, b = informe["modelos"]["recta"]["coeficientes"]
    print(f"Recta: consumo = {a:.3f} + {b:.3f} * horas")
    print("candidato | MAE entrenamiento | MAE validación | RMSE validación | R² validación")
    for candidato, ev in informe["validacion"].items():
        m = ev["metricas"]
        print(f"{candidato} | {numero(informe['entrenamiento'][candidato]['metricas']['mae'])} | "
              f"{numero(m['mae'])} | {numero(m['rmse'])} | {numero(m['r2'])}")
    print("Seleccionado por MAE de validación:", informe["seleccionado"])
    if informe["consulta"] is not None:
        c = informe["consulta"]
        print(f"Consulta: {c['horas']:g} h -> {c['consumo_predicho']:.3f} kWh; "
              f"fuera del rango de entrenamiento: {'sí' if c['fuera_rango'] else 'no'}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: n={m['n']}; solo {informe['seleccionado']}; sin reajuste")
        print(f"MAE={numero(m['mae'])}; RMSE={numero(m['rmse'])}; R²={numero(m['r2'])}")
    print("Datos sintéticos; ajuste y asociación no demuestran causalidad ni utilidad real.")
    if args.salida is not None:
        print("Exportación:", args.salida)

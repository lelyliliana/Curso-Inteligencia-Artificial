"""Interfaz de los laboratorios de clasificación binaria."""

import argparse
import csv
from pathlib import Path
from clasificacion import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definida" if valor is None else f"{valor:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Clasificación: {nombre}, selección por F1 de validación.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--evaluar-prueba", action="store_true", help="Evalúa solo la decisión elegida, sin reajuste.")
    parser.add_argument("--senal", type=float, help="Consulta al elegido, entre 0 y 100; no tiene etiqueta real.")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo para JSON y CSV.")
    parser.add_argument("--graficos", action="store_true", help="Añade PNG/SVG de desarrollo; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida con un directorio nuevo.")
    try:
        informe = ejecutar_experimento(nombre, args.datos, args.evaluar_prueba, args.senal)
        if args.graficos:
            from figuras import guardar_figuras, VERSIONES_GRAFICAS
            informe["versiones"].update(VERSIONES_GRAFICAS)
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, OverflowError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}")
    for fase in ("entrenamiento", "validacion"):
        fuente = informe["fuentes"][fase]
        print(f"{fase}: n={fuente['n']}; positivos={fuente['positivos']}")
    modelo = informe["modelo_logistico"]
    print(f"Logit: {modelo['intercepto']:.3f} + {modelo['coeficiente']:.3f} * z")
    print(f"z = (señal - {modelo['centro']:.3f}) / {modelo['escala']:.3f}")
    print(f"Ajuste: {modelo['iteraciones']} pasos; norma del gradiente final={modelo['norma_gradiente_final']:.2e}")
    print("candidato | exactitud | precisión | recobrado | F1 | FP | FN")
    for candidato, evaluacion in informe["validacion"].items():
        m = evaluacion["metricas"]
        valores = " | ".join(numero(m[k]) for k in ("exactitud", "precision", "recobrado", "f1"))
        print(f"{candidato} | {valores} | {m['FP']} | {m['FN']}")
    print("Seleccionado por F1 de validación:", informe["seleccionado"])
    if informe["consulta"] is not None:
        c = informe["consulta"]
        print(f"Consulta: señal={c['senal']:g}; p(1)={numero(c['probabilidad_1'])}; clase={c['clase']}; "
              f"fuera del rango de entrenamiento: {'sí' if c['fuera_rango'] else 'no'}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: n={m['n']}; solo {informe['seleccionado']}; sin reajuste")
        print(f"VP={m['VP']}; VN={m['VN']}; FP={m['FP']}; FN={m['FN']}; F1={numero(m['f1'])}")
    print("Datos sintéticos; una probabilidad estimada no garantiza calibración ni utilidad real.")
    if args.salida is not None:
        print("Exportación:", args.salida)

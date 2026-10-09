"""Interfaz común para ejecutar los dos protocolos sin cambiar sus criterios."""

import argparse
import csv
from pathlib import Path
from flujo import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definida" if valor is None else f"{valor:.3f}"


def ejecutar(tarea):
    parser = argparse.ArgumentParser(description=f"Líneas base de {tarea}: ajuste, selección y cierre separados.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / tarea,
                        help="Carpeta con entrenamiento.csv, validacion.csv y prueba.csv.")
    parser.add_argument("--evaluar-prueba", action="store_true", help="Abrir prueba tras seleccionar; no reajusta.")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo para informe JSON y predicciones CSV.")
    args = parser.parse_args()
    try:
        informe = ejecutar_experimento(tarea, args.datos, args.evaluar_prueba)
        if args.salida is not None:
            exportar(informe, args.salida)
    except (OSError, UnicodeError, ValueError, csv.Error, OverflowError) as error:
        parser.exit(2, f"Error: {error}\n")
    fuentes = informe["fuentes"]
    print(f"Protocolo: {informe['protocolo']}; tarea: {tarea}")
    print(f"Entrenamiento: {fuentes['entrenamiento']['n']}; validación: {fuentes['validacion']['n']}")
    print("Ajuste:", informe["ajuste"])
    if tarea == "regresion":
        print("Validación: candidato | MAE kWh | RMSE kWh | sesgo (real - predicción) kWh")
        campos = ("mae", "rmse", "sesgo")
    else:
        print("Validación: candidato | exactitud | precisión | recobrado | F1")
        campos = ("exactitud", "precision", "recobrado", "f1")
    for candidato, resultado in informe["validacion"].items():
        print(candidato + " | " + " | ".join(numero(resultado["metricas"][k]) for k in campos))
    print(f"Seleccionado por {informe['criterio']['metrica']}: {informe['seleccionado']}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        print(f"Prueba final: n={fuentes['prueba']['n']}; solo {informe['seleccionado']}; sin reajuste")
        print(" | ".join(f"{k}={numero(informe['prueba']['metricas'][k])}" for k in campos))
    print("Datos sintéticos: estas métricas no demuestran utilidad en equipos reales.")
    if args.salida is not None:
        print("Exportación:", args.salida)

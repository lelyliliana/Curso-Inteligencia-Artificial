"""Interfaz de los laboratorios de características y PCA."""

import argparse
import csv
from pathlib import Path
from representaciones import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definido" if valor is None else f"{valor:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Representaciones: {nombre}, selección por MAE de validación.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo.")
    parser.add_argument("--graficos", action="store_true", help="Añade figuras de desarrollo; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe, modelos = ejecutar_experimento(nombre, args.datos, args.evaluar_prueba)
        if args.graficos:
            from figuras import guardar_figuras, VERSIONES_GRAFICAS
            informe["versiones"].update(VERSIONES_GRAFICAS)
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, modelos, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}")
    print("candidato | dimensión regresión | MAE entrenamiento | MAE validación | RMSE validación | R² validación")
    for c, ev in informe["validacion"].items():
        m = ev["metricas"]
        print(f"{c} | {informe['modelos'][c]['dimension_regresion']} | "
              f"{numero(informe['entrenamiento'][c]['metricas']['mae'])} | {numero(m['mae'])} | {numero(m['rmse'])} | {numero(m['r2'])}")
    if nombre == "pca":
        for c in ("pca1", "pca2"):
            proporcion = sum(informe["modelos"][c]["pca"]["proporcion_varianza"])
            mse = informe["validacion"][c]["metricas"]["mse_reconstruccion_z"]
            print(f"{c}: varianza retenida entrenamiento={proporcion:.6f}; MSE reconstrucción z validación={mse:.6f}")
    print("Seleccionado por MAE de validación:", informe["seleccionado"])
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; MAE={numero(m['mae'])}; RMSE={numero(m['rmse'])}; R²={numero(m['r2'])}")
    print("Datos sintéticos; varianza conservada no equivale a utilidad predictiva ni causalidad.")
    if args.salida is not None:
        print("Exportación:", args.salida)

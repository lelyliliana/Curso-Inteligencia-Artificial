"""Interfaz de los dos laboratorios de validación cruzada."""

import argparse
import csv
from pathlib import Path
from validacion import UNIDAD, ejecutar_experimento, exportar


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Validación cruzada y reajuste: {nombre}.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true", help="Figuras de desarrollo; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        informe = ejecutar_experimento(nombre, args.datos, args.evaluar_prueba)
        if args.graficos:
            from figuras import guardar_figuras, VERSIONES_GRAFICAS
            informe["versiones"].update(VERSIONES_GRAFICAS)
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}; CV: {informe['cv']['tipo']}")
    print("candidato | MAE medio CV | desviación entre pliegues | MAE OOF")
    for c, ev in informe["resultados_cv"].items():
        print(f"{c} | {ev['mae_medio']:.3f} | {ev['desviacion_mae']:.3f} | {ev['mae_oof']:.3f}")
    print("Seleccionado por MAE medio de CV:", informe["seleccionado"])
    print(f"Reajuste: {informe['reajuste']['n_ajuste']} casos de desarrollo; ajustes totales: {informe['ajustes_realizados']}")
    if informe["diagnostico_filas"] is not None:
        diag = informe["diagnostico_filas"]
        c = diag["candidato_fijo"]
        print(f"Diagnóstico fijo {c}: MAE por filas={diag['resultado']['mae_medio']:.3f}; "
              f"MAE por equipos={informe['resultados_cv'][c]['mae_medio']:.3f}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; MAE={m['mae']:.3f}; RMSE={m['rmse']:.3f}")
    print("Datos sintéticos; dispersión entre pliegues no es un intervalo de confianza.")
    if args.salida is not None:
        print("Exportación:", args.salida)

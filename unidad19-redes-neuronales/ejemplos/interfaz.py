"""Entrenar, seleccionar en validación y abrir opcionalmente el cierre."""
import argparse
import csv
from pathlib import Path
from redes import UNIDAD, ejecutar_experimento, exportar


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Red neuronal pequeña: {nombre}.")
    parser.add_argument("--datos", type=Path, default=UNIDAD/"datos"/nombre)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true", help="Solo desarrollo; requiere --salida.")
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
    print("candidato | parámetros libres | época elegida | BCE entrenamiento | BCE validación | exactitud validación")
    for n, c in informe["candidatos"].items():
        a, b = c["entrenamiento"]["metricas"], c["validacion"]["metricas"]
        print(f"{n} | {c['n_parametros']} | {c['epoca_elegida']} | {a['bce']:.4f} | {b['bce']:.4f} | {b['exactitud']:.3f}")
    c = informe["candidatos"][informe["seleccionado"]]
    print(f"Seleccionado por BCE de validación: {informe['seleccionado']}; época={c['epoca_elegida']}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; BCE={m['bce']:.4f}; exactitud={m['exactitud']:.3f}; FN={m['FN']}; FP={m['FP']}")
    print("Datos sintéticos; una frontera aprendida no es una explicación causal.")
    if args.salida is not None:
        print("Exportación:", args.salida)

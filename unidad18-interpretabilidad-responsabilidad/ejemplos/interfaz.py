"""CLI para inspeccionar modelos y, opcionalmente, abrir su cierre."""

import argparse
import csv
from pathlib import Path
from interpretacion import UNIDAD, ejecutar_experimento, exportar


def numero(valor):
    return "no definida" if valor is None else f"{valor:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Interpretabilidad: {nombre}")
    parser.add_argument("--datos", type=Path, default=UNIDAD/"datos"/nombre)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Carpeta nueva.")
    parser.add_argument("--graficos", action="store_true", help="Figuras de validación; requiere --salida.")
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
    print("Modelo fijado antes de validación:", informe["estado"]["tipo"])
    if nombre == "consumo":
        for clave, etiqueta in (("linea_base_validacion", "Media de entrenamiento"), ("validacion", "Modelo lineal")):
            print(f"{etiqueta}: MAE validación={informe[clave]['metricas']['mae']:.3f} kWh")
        caso = informe["caso_local"]
        print(f"Caso {caso['caso_id']}: base={caso['base']:.3f}; reconstrucción={caso['reconstruccion']:.3f} kWh")
        for etiqueta, r in informe["permutacion"]["bloques"].items():
            print(f"Permutar {etiqueta}: ΔMAE={r['media']:.3f} ± {r['desviacion']:.3f} kWh")
    else:
        print("grupo | n | positivos | FN | FP | recobrado | tasa FP | fracción de la muestra")
        for g, m in informe["validacion"]["grupos"].items():
            print(f"{g} | {m['n']} | {m['positivos']} | {m['FN']} | {m['FP']} | {numero(m['recobrado'])} | {numero(m['tasa_fp'])} | {numero(m['fraccion_muestra'])}")
        caso = informe["caso_local"]
        print(f"Caso {caso['caso_id']}: hoja={caso['hoja']}; clase reconstruida={caso['clase_reconstruida']}")
        for paso in caso["pasos"]:
            print(f"  Nodo {paso['nodo']}: lectura={paso['valor_float32']:.8f} {paso['operador']} {paso['umbral']:.8f} -> nodo {paso['siguiente']}")
        print(f"  Hoja: n entrenamiento={caso['n_entrenamiento_hoja']}; fracción positiva={caso['fracciones_clase'][1]:.6f}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    elif nombre == "consumo":
        print(f"Prueba final: modelo fijo; MAE={informe['prueba']['metricas']['mae']:.3f} kWh")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: modelo fijo; VP={m['VP']}; FP={m['FP']}; FN={m['FN']}")
    print("Explicación del modelo; no demuestra causalidad ni utilidad real.")
    if args.salida is not None:
        print("Exportación:", args.salida)

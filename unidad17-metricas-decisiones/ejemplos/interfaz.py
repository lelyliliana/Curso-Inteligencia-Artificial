"""Comparar políticas y cerrar sin volver a elegir con prueba."""

import argparse
import csv
from pathlib import Path
from decisiones import UNIDAD, ejecutar_experimento, exportar


def numero(v):
    return "no definida" if v is None else f"{v:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Métricas y decisiones: {nombre}.")
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
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}")
    print("política | alertas | VP | FP | FN | precisión | recobrado | F1 | costo total")
    for c, ev in informe["validacion"].items():
        m = ev["metricas"]
        print(f"{c} | {m['alertas']} | {m['VP']} | {m['FP']} | {m['FN']} | {numero(m['precision'])} | {numero(m['recobrado'])} | {numero(m['f1'])} | {m['costo_total']}")
    print("Seleccionada por costo de validación:", informe["seleccionado"])
    for etiqueta, clave in (("Original", "diagnostico_ordenacion"), ("Cuadrado, diagnóstico fijo", "diagnostico_cuadrado")):
        m = informe[clave]
        print(f"{etiqueta}: ROC AUC={numero(m['auc_roc'])}; AP={numero(m['ap'])}; Brier={numero(m['brier'])}")
    if informe["diagnostico_sin_cupo"] is not None:
        lotes = informe["diagnostico_sin_cupo"]["por_lote"]
        exceden = sum(m["alertas"] > informe["cupo_por_lote"] for m in lotes.values())
        print(f"Umbral 0.5 sin cupo: {exceden} de {len(lotes)} lotes exceden la capacidad.")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        print(f"Prueba final: solo {informe['seleccionado']}; VP={m['VP']}; FP={m['FP']}; FN={m['FN']}; costo={m['costo_total']}")
    print("Datos sintéticos; costos convencionales de error, sin eficacia real demostrada.")
    if args.salida is not None:
        print("Exportación:", args.salida)

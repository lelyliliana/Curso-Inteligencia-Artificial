"""Comandos de los dos laboratorios de la Unidad 14."""

import argparse
import csv
from pathlib import Path
from flujo_no_supervisado import UNIDAD, ejecutar_grupos, ejecutar_anomalias, exportar


def numero(v):
    return "no definida" if v is None else f"{v:.3f}"


def ejecutar(nombre):
    parser = argparse.ArgumentParser(description=f"Experimento {nombre}: ajuste, selección y cierre separados.")
    parser.add_argument("--datos", type=Path, default=UNIDAD / "datos" / nombre)
    parser.add_argument("--semilla", type=int, default=14)
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--salida", type=Path, help="Directorio nuevo para informe y predicciones.")
    parser.add_argument("--graficos", action="store_true", help="Figuras de desarrollo; requiere --salida.")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    try:
        funcion = ejecutar_grupos if nombre == "grupos" else ejecutar_anomalias
        informe, ajuste = funcion(args.datos, args.evaluar_prueba, args.semilla)
        if args.graficos:
            from figuras import guardar_figuras, VERSIONES_GRAFICAS
            informe["versiones"].update(VERSIONES_GRAFICAS)
        if args.salida is not None:
            exportar(informe, args.salida)
            if args.graficos:
                guardar_figuras(informe, ajuste, args.salida)
    except (OSError, UnicodeError, ValueError, RuntimeError, csv.Error) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Protocolo: {informe['protocolo']}; experimento: {nombre}; semilla: {args.semilla}")
    for fase, fuente in informe["fuentes"].items():
        print(f"{fase}: n={fuente['n']}")
    if nombre == "grupos":
        print("candidato | inercia entrenamiento | silueta validación | tamaños validación | ARI con semillas 29 y 47")
        for c, modelo in informe["modelos"].items():
            m = informe["validacion"][c]["metricas"]
            ari = ", ".join(numero(v["ari"]) for v in informe["estabilidad"][c])
            print(f"{c} | {modelo['inercia_entrenamiento']:.3f} | {numero(m['silueta'])} | {m['tamanos']} | {ari}")
    else:
        print("candidato | umbral | alertas calibración | precisión validación | recobrado | F1 | FP | FN")
        for c, modelo in informe["modelos"].items():
            m = informe["validacion"][c]["metricas"]
            alertas = informe["calibracion"][c]["metricas"]["alertas"]
            print(f"{c} | {numero(modelo['umbral'])} | {alertas} | {numero(m['precision'])} | "
                  f"{numero(m['recobrado'])} | {numero(m['f1'])} | {m['FP']} | {m['FN']}")
    print(f"Seleccionado por {informe['criterio']['metrica']} de validación: {informe['seleccionado']}")
    if informe["prueba"] is None:
        print("Prueba reservada: no se leyó su archivo.")
    else:
        m = informe["prueba"]["metricas"]
        if nombre == "grupos":
            print(f"Prueba final: silueta={numero(m['silueta'])}; tamaños={m['tamanos']}")
        else:
            print(f"Prueba final: VP={m['VP']}; VN={m['VN']}; FP={m['FP']}; FN={m['FN']}; F1={numero(m['f1'])}")
    print("Datos sintéticos: un grupo no es una clase verdadera; una alerta no confirma un problema.")
    if args.salida is not None:
        print("Exportación:", args.salida)

"""Por defecto analiza la captura publicada; --en-vivo llama a Ollama."""

import argparse
from pathlib import Path

from evaluacion import UNIDAD, analizar, cargar, ejecutar_real, guardar
from servicios import ErrorServicio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registro", type=Path, default=UNIDAD / "recursos/local/registro.json")
    parser.add_argument("--en-vivo", action="store_true")
    parser.add_argument("--modelo", default="qwen3:8b")
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.en_vivo and not args.salida:
        parser.error("--en-vivo requiere --salida para conservar cada intento")
    if args.graficos and not args.salida:
        parser.error("--graficos requiere --salida")
    if args.en_vivo and (args.salida / "registro.json").exists():
        parser.error("Utiliza una carpeta nueva para no sobrescribir llamadas anteriores")
    registro = ejecutar_real(args.modelo, args.salida, args.timeout) if args.en_vivo else cargar(args.registro)
    informe = analizar(registro)
    print("Inferencia local real." if args.en_vivo else "Análisis sin red de la captura publicada; no es una nueva inferencia.")
    for r in informe["resumen"]:
        print(f"Límite {r['limite']}: aceptadas={r['aceptada']}/{r['solicitudes']}; "
              f"coinciden={r['coincide']}; finalizadas={r['finalizada']}; contratos={r['contrato_valido']}")
    for fila in informe["filas"]:
        print(f"{fila['caso']} | {fila['limite']} | {fila.get('razon', fila.get('error'))} | {fila.get('texto', '')!r}")
    if args.salida:
        guardar(args.salida / "informe.json", informe)
        if args.graficos:
            from figuras import dibujar
            dibujar(informe, args.salida)
        print(f"Exportación: {args.salida}")


if __name__ == "__main__":
    try:
        main()
    except (ErrorServicio, ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from None

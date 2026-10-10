"""Analiza capturas por defecto; --en-vivo es una ejecución local opcional."""

import argparse
from pathlib import Path
from experimento import (UNIDAD, ErrorServicio, analizar, cargar, congelar, ejecutar_real,
                         guardar)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fase', choices=['desarrollo', 'cierre'], default='desarrollo')
    p.add_argument('--en-vivo', action='store_true')
    p.add_argument('--modelo', default='qwen3:8b')
    p.add_argument('--registro', type=Path)
    p.add_argument('--seleccion', type=Path, default=UNIDAD/'recursos/desarrollo/seleccion.json')
    p.add_argument('--salida', type=Path)
    p.add_argument('--graficos', action='store_true')
    args = p.parse_args()
    if (args.en_vivo or args.graficos) and not args.salida:
        p.error('--en-vivo y --graficos requieren --salida')
    seleccion = cargar(args.seleccion) if args.fase == 'cierre' else None
    registro = (ejecutar_real(args.fase, args.modelo, args.salida, seleccion) if args.en_vivo else
                cargar(args.registro or UNIDAD/f'recursos/{args.fase}/registro.json'))
    if registro['fase'] != args.fase:
        p.error('La fase del archivo no coincide con --fase')
    informe = analizar(registro, seleccion)
    print('Inferencia local real.' if args.en_vivo else 'Análisis de captura sin red; no es nueva inferencia.')
    for r in informe['resumen']:
        print(f"{r['candidato']}: aceptadas={r['aceptada']}/{r['intentos']}; forma={r['forma']}; "
              f"contenido={r['contenido']}; familias completas={r['familias_completas']}/{r['familias']}")
    if args.fase == 'desarrollo':
        seleccion = congelar(registro)
        print(f"Seleccionado con desarrollo: {seleccion['candidato']}")
    else:
        print(f"Cierre del candidato congelado: {seleccion['candidato']}")
    if args.salida:
        # El cierre jamás escribe ni modifica la selección.
        guardar(args.salida/'informe.json', informe)
        if args.fase == 'desarrollo':
            guardar(args.salida/'seleccion.json', seleccion)
        if args.graficos:
            from figuras import dibujar
            dibujar(informe, args.salida)
        print(f'Exportación: {args.salida}')


if __name__ == '__main__':
    try:
        main()
    except (ErrorServicio, ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from None

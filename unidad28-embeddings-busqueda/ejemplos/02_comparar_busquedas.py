"""Reanaliza la captura publicada por defecto. Solo --en-vivo llama a Ollama."""
import argparse
from pathlib import Path
from busqueda import cargar, guardar
from experimento import RECURSOS, capturar, cierre, comprobar_seleccion, desarrollo


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fase', choices=('desarrollo','cierre'), default='desarrollo')
    p.add_argument('--en-vivo', action='store_true')
    p.add_argument('--registro', type=Path)
    p.add_argument('--registro-desarrollo', type=Path, default=RECURSOS/'desarrollo/registro.json')
    p.add_argument('--indice', type=Path, default=RECURSOS/'desarrollo/indice.json')
    p.add_argument('--seleccion', type=Path, default=RECURSOS/'desarrollo/seleccion.json')
    p.add_argument('--salida', type=Path)
    p.add_argument('--graficos', action='store_true')
    args = p.parse_args()
    if (args.en_vivo or args.graficos) and args.salida is None:
        p.error('--en-vivo y --graficos necesitan --salida')
    if args.en_vivo and args.registro:
        p.error('--registro y --en-vivo son excluyentes')
    registro_dev = None
    if args.fase == 'cierre':
        indice, seleccion = cargar(args.indice), cargar(args.seleccion)
        registro_dev = cargar(args.registro_desarrollo)
        comprobar_seleccion(indice, seleccion, registro_dev)
    if args.en_vivo:
        registro = capturar(args.fase, args.salida, seleccion if args.fase == 'cierre' else None)
    else:
        ruta = args.registro or RECURSOS/args.fase/'registro.json'
        registro = cargar(ruta) if args.fase == 'desarrollo' or seleccion['metodo'] == 'bge_m3' else None
        print('Análisis sin red: se reutilizan embeddings reales guardados.')
    if args.fase == 'desarrollo':
        indice, seleccion, informe = desarrollo(registro)
        print(f"Seleccionado con desarrollo: {seleccion['metodo']}")
    else:
        informe = cierre(indice, seleccion, registro_dev, registro)
        print('Cierre: índice y elección congelados; sin reajuste.')
    for e in informe['evaluaciones']:
        r = e['resumen']
        print(f"{r['metodo']}: MRR@3={r['rr']:.4f}; Recall@3={r['recall']:.4f}; "
              f"sin respuesta con candidatos={r['sin_respuesta_con_candidatos']}/{r['sin_respuesta']}")
    if args.salida:
        guardar(args.salida/'informe.json', informe)
        if args.fase == 'desarrollo':
            guardar(args.salida/'indice.json', indice)
            guardar(args.salida/'seleccion.json', seleccion)
            indice2 = cargar(args.salida/'indice.json')
            comprobar_seleccion(indice2, cargar(args.salida/'seleccion.json'), registro)
            print('Recarga: índice, rankings y selección idénticos.')
        if args.graficos:
            from figuras import dibujar
            dibujar(informe, args.salida)
        print(f'Exportación: {args.salida}')


if __name__ == '__main__':
    main()

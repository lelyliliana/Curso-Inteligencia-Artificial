"""Reanálisis sin red por defecto; --en-vivo ejecuta los dos modelos locales."""
import argparse
from pathlib import Path
from rag import cargar, guardar
from motor import RECURSOS, analizar, capturar, congelar, indice_de_desarrollo, verificar_seleccion


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fase',choices=('desarrollo','cierre'),default='desarrollo')
    p.add_argument('--registro',type=Path)
    p.add_argument('--registro-desarrollo',type=Path,default=RECURSOS/'desarrollo/registro.json')
    p.add_argument('--indice',type=Path,default=RECURSOS/'desarrollo/indice.json')
    p.add_argument('--seleccion',type=Path,default=RECURSOS/'desarrollo/seleccion.json')
    p.add_argument('--en-vivo',action='store_true')
    p.add_argument('--salida',type=Path)
    p.add_argument('--graficos',action='store_true')
    args=p.parse_args()
    if (args.en_vivo or args.graficos) and args.salida is None: p.error('Necesitas --salida')
    if args.en_vivo and args.registro: p.error('--en-vivo y --registro son excluyentes')
    indice=seleccion=dev=None
    if args.fase=='cierre':
        dev=cargar(args.registro_desarrollo); indice=cargar(args.indice); seleccion=cargar(args.seleccion)
        verificar_seleccion(dev,indice,seleccion)
    if args.en_vivo:
        registro,indice=capturar(args.fase,args.salida,indice,seleccion,dev)
    else:
        registro=cargar(args.registro or RECURSOS/args.fase/'registro.json')
        print('Reanálisis sin red: no se generan embeddings ni respuestas nuevas.')
    if args.fase=='desarrollo':
        indice=indice_de_desarrollo(registro)
        seleccion=congelar(registro,indice)
        print(f"Seleccionado con desarrollo: k={seleccion['k']}")
    else:
        print('Cierre: selección e índice congelados; sin reajuste.')
    informe=analizar(registro,indice,seleccion if args.fase=='cierre' else None)
    for r in informe['resumenes']:
        print(f"k={r['k']}: aceptadas={r['aceptada']}/{r['n']}; contexto suficiente={r['contexto_suficiente']}/{r['n']}; extractiva útil={r['extractiva_util']}/{r['n']}")
    if args.salida:
        guardar(args.salida/'informe.json',informe)
        if args.fase=='desarrollo':
            guardar(args.salida/'indice.json',indice); guardar(args.salida/'seleccion.json',seleccion)
            nuevo=cargar(args.salida/'indice.json')
            verificar_seleccion(registro,nuevo,cargar(args.salida/'seleccion.json'))
            if analizar(registro,nuevo)!=informe: raise ValueError('Cambió el análisis al recargar')
            print('Recarga: contexto, respuestas evaluadas y elección idénticos.')
        if args.graficos:
            from figuras import dibujar
            dibujar(informe,args.salida)
        print(f'Exportación: {args.salida}')


if __name__=='__main__': main()

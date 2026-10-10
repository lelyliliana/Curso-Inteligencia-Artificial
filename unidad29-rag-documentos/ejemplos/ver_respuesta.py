"""Muestra una respuesta guardada y sus fuentes originales; no llama modelos."""
import argparse
from rag import cargar, extraer, UNIDAD
from motor import RECURSOS, analizar, indice_de_desarrollo, verificar_seleccion


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fase',choices=('desarrollo','cierre'),default='desarrollo')
    p.add_argument('--caso',default='R03a')
    p.add_argument('--k',type=int,choices=(1,3))
    args=p.parse_args()
    dev=cargar(RECURSOS/'desarrollo/registro.json')
    indice=indice_de_desarrollo(dev)
    seleccion=cargar(RECURSOS/'desarrollo/seleccion.json')
    verificar_seleccion(dev,indice,seleccion)
    informe=analizar(cargar(RECURSOS/args.fase/'registro.json'),indice,seleccion if args.fase=='cierre' else None)
    k=args.k or seleccion['k']
    f=next((f for f in informe['filas'] if f['caso']==args.caso and f['k']==k),None)
    if f is None: p.error('Ese caso/k no está en la fase guardada')
    print(f"Captura {args.fase} · {args.caso} · k={k}")
    print(f.get('texto','No hay texto válido de respuesta.'))
    print(f"Contexto suficiente={f['contexto_suficiente']}; apoyo={f['apoyo']}; objetivo={f['objetivo']}; aceptada={f['aceptada']}")
    por_id={f['id']:f for f in extraer()}
    for cita in f.get('objeto',{}).get('citas',[]):
        fuente=por_id.get(cita)
        if fuente is None:
            print(f'{cita}: fuente inexistente'); continue
        print(f"\n[{cita}] {fuente['titulo']}, versión {fuente['version']}\n"
              f"{UNIDAD/'datos'/fuente['ruta']} · líneas {fuente['linea_inicio']}–{fuente['linea_fin']}\n{fuente['texto']}")
    print('\nReferencia extractiva del primer fragmento:')
    print(f['extractiva']['texto'])


if __name__=='__main__': main()

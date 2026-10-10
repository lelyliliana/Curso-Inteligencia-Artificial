"""Extrae párrafos con procedencia y muestra el efecto de un presupuesto."""
import argparse
from pathlib import Path
from rag import extraer, guardar, preparar_contexto


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida',type=Path)
    args=p.parse_args()
    fs=extraer()
    top=[{'id':f['id'],'puntuacion':1/(i+1)} for i,f in enumerate(fs[:3])]
    completo=preparar_contexto(fs,top)
    limitado=preparar_contexto(fs,top,300)
    print(f'Documentos: {len({f["documento"] for f in fs})}; fragmentos: {len(fs)}; texto original conservado.')
    print('Ranking artificial para mostrar presupuesto; no es búsqueda medida.')
    print(f"Contexto habitual: {len(completo['fragmentos'])}; con 300 caracteres: {len(limitado['fragmentos'])}.")
    if args.salida:
        guardar(args.salida/'fragmentos.json',fs)
        guardar(args.salida/'presupuesto.json',{'ranking_artificial':top,'completo':completo,'limitado':limitado})
        print(f'Exportación: {args.salida}')


if __name__=='__main__': main()

"""Ejemplo geométrico artificial: no es inferencia de un modelo lingüístico."""
import argparse
from pathlib import Path
from busqueda import coseno, guardar, producto


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida', type=Path)
    args = p.parse_args()
    q, a, b, opuesto = [1, 0], [3, 4], [10, 0], [-1, 0]
    datos = {'origen': 'vectores_artificiales', 'producto_q_a': producto(q,a),
             'coseno_q_a': coseno(q,a), 'coseno_q_b': coseno(q,b),
             'coseno_opuesto': coseno(q,opuesto), 'coseno_a_escalado': coseno(q,[30,40])}
    print('Vectores artificiales: cos(q,a)=0.600; cos(q,b)=1.000; opuesto=-1.000')
    print('Multiplicar a por 10 cambia el producto, pero conserva el coseno.')
    try:
        coseno(q, [0, 0])
    except ValueError:
        print('Vector cero: coseno indefinido; no asignar confianza cero.')
    if args.salida:
        guardar(args.salida/'geometria.json', datos)
        print(f'Exportación: {args.salida}')


if __name__ == '__main__':
    main()

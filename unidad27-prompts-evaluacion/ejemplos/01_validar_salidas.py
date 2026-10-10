"""Dieciséis contraejemplos para distinguir JSON, forma, coherencia y contenido."""

import argparse
from pathlib import Path
from contraejemplos import construir
from experimento import guardar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida', type=Path)
    args = p.parse_args()
    r = construir()
    print('Contraejemplos artificiales: no hay inferencia ni red.')
    for f in r['filas']:
        print(f"{f['id']}: JSON={f['json_valido']}; forma={f['forma']}; "
              f"contenido={f['contenido']}; aceptada={f['aceptada']}; fallo={f.get('fallo','-')}")
    print(f"Salidas artificiales: {len(r['filas'])}; aceptadas={sum(f['aceptada'] for f in r['filas'])}.")
    if args.salida:
        guardar(args.salida/'informe.json', r)
        print(f'Exportación: {args.salida}')


if __name__ == '__main__':
    main()

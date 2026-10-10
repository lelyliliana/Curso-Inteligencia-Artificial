"""Explora el índice con una consulta guardada o texto nuevo explícito."""
import argparse
from busqueda import (METODOS, UNIDAD, cargar, normalizar, ranking,
                      texto_documento, transformar, validar_indice)
from experimento import (CONFIG, OLLAMA, RECURSOS, inventario, leer_embedding,
                         peticion, solicitar, validar_captura)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    grupo = p.add_mutually_exclusive_group()
    grupo.add_argument('--consulta-id', default=None)
    grupo.add_argument('--texto')
    p.add_argument('--metodo', choices=METODOS, default='bge_m3')
    p.add_argument('--en-vivo', action='store_true')
    args = p.parse_args()
    indice = cargar(RECURSOS/'desarrollo/indice.json')
    corpus = cargar(UNIDAD/'datos/corpus.json')
    validar_indice(indice, corpus)
    if args.texto is None:
        if args.en_vivo:
            p.error('--en-vivo se usa con --texto; las consultas guardadas no necesitan red')
        consultas = cargar(UNIDAD/'datos/desarrollo.json')
        identificador = args.consulta_id or 'F01a'
        posicion = next((i for i,q in enumerate(consultas) if q['id'] == identificador), None)
        if posicion is None:
            p.error('ID inexistente en desarrollo')
        texto = consultas[posicion]['texto']
        if args.metodo == 'bge_m3':
            captura = cargar(RECURSOS/'desarrollo/registro.json')
            if captura['inventario'] != indice['inventario']:
                raise ValueError('Modelo del índice incompatible con las consultas')
            v = normalizar(validar_captura(captura, 'desarrollo')['consulta'][posicion])
    else:
        texto = args.texto
        peticion(texto)  # mismo límite de entrada para ambos métodos
        if args.metodo == 'bge_m3':
            if not args.en_vivo:
                p.error('Texto nuevo con BGE-M3 requiere --en-vivo y el mismo modelo instalado')
            if inventario(CONFIG['modelo']) != indice['inventario']:
                raise ValueError('Versión o digest diferente: reconstruir índice y evaluación')
            v = normalizar(leer_embedding(solicitar(OLLAMA+'/api/embed', peticion(texto))))
    if args.metodo == 'tfidf':
        v = transformar(texto, indice['estado_tfidf'])
        if not any(v):
            print('Consulta sin términos conocidos: todos los cosenos se fijan en 0 por convenio léxico.')
    print(f'Consulta: {texto}\nCandidatos para revisión; no son una respuesta verificada.')
    por_id = {d['id']: d for d in corpus}
    for f in ranking(indice['ids'], indice['matrices'][args.metodo], v, CONFIG['k']):
        print(f"\n{f['id']} · coseno={f['puntuacion']:.4f}\n{texto_documento(por_id[f['id']])}")


if __name__ == '__main__':
    main()

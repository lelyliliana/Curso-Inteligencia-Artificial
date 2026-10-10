"""Captura local opcional; reconstrucción y cierre comprobables sin conexión."""
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import time

from busqueda import (CONFIG, METODOS, UNIDAD, cargar, construir_indice, elegir, evaluar,
                      firma, guardar, huella, separar, texto_documento, validar_datos,
                      validar_indice, vector)

sys.path.append(str(UNIDAD.parent/'unidad26-inferencia-servicios/ejemplos'))
from evaluacion import inventario
from servicios import ErrorServicio, OLLAMA, numero, solicitar

RECURSOS = UNIDAD/'recursos'


def peticion(texto):
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 2000:
        raise ValueError('Entrada vacía o mayor que el límite didáctico de 2000 caracteres')
    return {'model': CONFIG['modelo'], 'input': texto, 'truncate': False,
            'keep_alive': '5m', 'options': CONFIG['options']}


def leer_embedding(respuesta):
    if not isinstance(respuesta, dict) or respuesta.get('model') != CONFIG['modelo'] or 'error' in respuesta:
        raise ValueError('Respuesta de otro modelo o con error')
    vs = respuesta.get('embeddings')
    if not isinstance(vs, list) or len(vs) != 1 or len(vector(vs[0])) != CONFIG['dimension'] or not any(vs[0]):
        raise ValueError('Se esperaba un embedding no nulo de dimensión 1024')
    for campo in ('total_duration', 'load_duration', 'prompt_eval_count'):
        numero(respuesta.get(campo), campo, entero=True)
    return vs[0]


def huellas():
    return {n: huella(UNIDAD/f'datos/{n}') for n in
            ('corpus.json', 'desarrollo.json', 'cierre.json', 'protocolo.md')}


def entradas(fase):
    if fase not in ('desarrollo', 'cierre'):
        raise ValueError('Fase inválida')
    consultas = cargar(UNIDAD/f'datos/{fase}.json')
    filas = [('consulta', q['id'], q['texto']) for q in consultas]
    if fase == 'desarrollo':
        filas = [('documento', d['id'], texto_documento(d)) for d in cargar(UNIDAD/'datos/corpus.json')] + filas
    return filas


def medir(texto, cliente):
    solicitud = peticion(texto)
    inicio = time.perf_counter()
    try:
        resultado = {'respuesta': cliente(OLLAMA+'/api/embed', solicitud, timeout=120)}
    except ErrorServicio as exc:
        resultado = {'error': exc.codigo}
    return {'solicitud': solicitud, 'pared_s': time.perf_counter()-inicio, **resultado}


def capturar(fase, salida, seleccion=None, cliente=solicitar):
    salida = Path(salida)
    if salida.exists() and any(salida.iterdir()):
        raise ValueError('La captura necesita una carpeta nueva o vacía')
    if fase == 'cierre' and (seleccion is None or seleccion['metodo'] != 'bge_m3'):
        raise ValueError('Solo capturar cierre denso si se seleccionó BGE-M3')
    plan = entradas(fase)
    meta = inventario(CONFIG['modelo'], cliente)
    if 'embedding' not in meta['capacidades']:
        raise ValueError('El modelo no declara capacidad de embeddings')
    registro = {'schema': 1, 'origen': 'ollama_local_real', 'fase': fase, 'config': CONFIG,
                'fecha_utc': datetime.now(timezone.utc).isoformat(), 'huellas': huellas(),
                'entorno': {'python': platform.python_version(), 'sistema': platform.system(),
                            'arquitectura': platform.machine()},
                'inventario': meta, 'inventario_estable': False, 'filas': []}
    if seleccion is not None:
        registro['seleccion_sha256'] = firma(seleccion)
    registro['calentamiento'] = medir('Prueba de carga del modelo de embeddings.', cliente)
    guardar(salida/'registro.json', registro)
    leer_embedding(registro['calentamiento'].get('respuesta'))
    for tipo, identificador, texto in plan:
        print(f'Embedding local: {tipo} {identificador}', flush=True)
        fila = {'tipo': tipo, 'id': identificador, **medir(texto, cliente)}
        registro['filas'].append(fila)
        guardar(salida/'registro.json', registro)
        leer_embedding(fila.get('respuesta'))
    registro['recursos_servidor'] = [{k: m.get(k) for k in ('name','digest','size','size_vram','context_length')}
                                   for m in cliente(OLLAMA+'/api/ps').get('models', [])
                                   if m.get('name') == CONFIG['modelo']]
    if inventario(CONFIG['modelo'], cliente) != meta:
        raise ValueError('El inventario cambió durante la captura')
    registro['inventario_estable'] = True
    guardar(salida/'registro.json', registro)
    return registro


def validar_captura(registro, fase, seleccion=None):
    if (registro.get('schema') != 1 or registro.get('origen') != 'ollama_local_real'
            or registro.get('fase') != fase or registro.get('config') != CONFIG
            or registro.get('huellas') != huellas() or registro.get('inventario_estable') is not True):
        raise ValueError('Captura incompleta, incompatible o datos modificados')
    if fase == 'cierre' and (seleccion is None or registro.get('seleccion_sha256') != firma(seleccion)):
        raise ValueError('Cierre sin selección correspondiente')
    meta = registro.get('inventario', {})
    if not meta.get('digest') or not meta.get('version_ollama') or 'embedding' not in meta.get('capacidades', []):
        raise ValueError('Falta identificar el espacio vectorial')
    plan = entradas(fase)
    filas = registro.get('filas', [])
    if len(filas) != len(plan):
        raise ValueError('Cantidad de embeddings incorrecta')
    resultado = {'documento': [], 'consulta': []}
    for fila, (tipo, identificador, texto) in zip(filas, plan):
        if (fila.get('tipo') != tipo or fila.get('id') != identificador
                or fila.get('solicitud') != peticion(texto) or 'error' in fila):
            raise ValueError('Entrada, orden o petición alterados')
        numero(fila.get('pared_s'), 'pared_s')
        resultado[tipo].append(leer_embedding(fila.get('respuesta')))
    return resultado


def desarrollo(registro):
    corpus = cargar(UNIDAD/'datos/corpus.json')
    consultas = cargar(UNIDAD/'datos/desarrollo.json')
    validar_datos(corpus, consultas)
    vectores = validar_captura(registro, 'desarrollo')
    indice = construir_indice(corpus, vectores['documento'], registro['inventario'])
    validar_indice(indice, corpus)
    evaluaciones = [evaluar(indice, consultas, m, vectores['consulta']) for m in METODOS]
    seleccion = {'schema': 1, 'metodo': elegir(evaluaciones), 'criterio': 'max_mrr3_empate_tfidf',
                 'config': CONFIG, 'huellas': huellas(), 'indice_sha256': firma(indice),
                 'registro_desarrollo_sha256': firma(registro),
                 'familias': sorted({q['familia'] for q in consultas}),
                 'resumenes': [e['resumen'] for e in evaluaciones]}
    return indice, seleccion, {'fase': 'desarrollo', 'evaluaciones': evaluaciones}


def comprobar_seleccion(indice, seleccion, registro_desarrollo):
    nuevo_indice, nueva_seleccion, _ = desarrollo(registro_desarrollo)
    if indice != nuevo_indice or seleccion != nueva_seleccion:
        raise ValueError('Índice o selección no corresponde al desarrollo fijado')


def cierre(indice, seleccion, registro_desarrollo, registro_cierre=None):
    comprobar_seleccion(indice, seleccion, registro_desarrollo)
    consultas = cargar(UNIDAD/'datos/cierre.json')
    validar_datos(cargar(UNIDAD/'datos/corpus.json'), consultas)
    separar(cargar(UNIDAD/'datos/desarrollo.json'), consultas)
    vectores = None
    if seleccion['metodo'] == 'bge_m3':
        if registro_cierre is None:
            raise ValueError('Falta captura de consultas de cierre')
        vectores = validar_captura(registro_cierre, 'cierre', seleccion)['consulta']
        if registro_cierre['inventario'] != indice['inventario']:
            raise ValueError('No mezclar embeddings de versiones diferentes')
    return {'fase': 'cierre', 'seleccion_sha256': firma(seleccion),
            'evaluaciones': [evaluar(indice, consultas, seleccion['metodo'], vectores)]}

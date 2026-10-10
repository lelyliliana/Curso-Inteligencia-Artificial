"""Vectores, TF-IDF, ranking exacto y métricas; sin red ni paquetes externos."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata

UNIDAD = Path(__file__).resolve().parents[1]
CONFIG = {'modelo': 'bge-m3:567m', 'dimension': 1024, 'k': 3,
          'texto_documento': 'titulo + salto de linea + texto',
          'lexico': 'nfc_casefold_unicode_sin_subrayado_tf_cruda_idf_suave_l2_v1',
          'denso': 'sin_prefijo_texto_original_l2',
          'options': {'num_gpu': 0, 'num_thread': 4, 'num_ctx': 2048}}
METODOS = ('tfidf', 'bge_m3')


def cargar(ruta):
    def constante(x):
        raise ValueError(f'Constante JSON no finita: {x}')
    return json.loads(Path(ruta).read_text(encoding='utf-8'), parse_constant=constante)


def guardar(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def firma(obj):
    bruto = json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':'))
    return hashlib.sha256(bruto.encode()).hexdigest()


def vector(v):
    if not isinstance(v, list) or not v:
        raise ValueError('Se necesita un vector no vacío')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in v):
        raise ValueError('Coordenadas numéricas finitas, sin booleanos')
    return v


def normalizar(v, permitir_cero=False):
    vector(v)
    norma = math.hypot(*v)
    if not math.isfinite(norma):
        raise ValueError('Norma no finita')
    if norma == 0:
        if permitir_cero:
            return list(v)
        raise ValueError('El coseno de un vector nulo no está definido')
    return [x/norma for x in v]


def producto(a, b):
    vector(a); vector(b)
    if len(a) != len(b):
        raise ValueError('Dimensiones incompatibles')
    resultado = math.fsum(x*y for x, y in zip(a, b))
    if not math.isfinite(resultado):
        raise ValueError('Producto no finito')
    return resultado


def coseno(a, b):
    return producto(normalizar(a), normalizar(b))


def tokens(texto):
    return re.findall(r'[^\W_]+', unicodedata.normalize('NFC', texto).casefold())


def texto_documento(doc):
    return doc['titulo'] + '\n' + doc['texto']


def ajustar_tfidf(textos):
    if not textos:
        raise ValueError('Corpus vacío')
    df = Counter(t for texto in textos for t in set(tokens(texto)))
    vocabulario = sorted(df)
    if not vocabulario:
        raise ValueError('Vocabulario vacío')
    return {'vocabulario': vocabulario,
            'idf': [1 + math.log((1+len(textos))/(1+df[t])) for t in vocabulario]}


def transformar(texto, estado):
    tf = Counter(tokens(texto))
    return normalizar([tf[t]*idf for t, idf in zip(estado['vocabulario'], estado['idf'])], permitir_cero=True)


def ranking(ids, matriz, consulta, k):
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= len(ids):
        raise ValueError('k entero entre 1 y el número de documentos')
    if len(ids) != len(matriz) or len(set(ids)) != len(ids):
        raise ValueError('IDs duplicados o matriz desalineada')
    if any(not isinstance(i, str) or not i for i in ids):
        raise ValueError('IDs de texto no vacío')
    # Las filas y la consulta ya están normalizadas. No redondear para ordenar.
    filas = [{'id': i, 'puntuacion': producto(v, consulta)} for i, v in zip(ids, matriz)]
    return sorted(filas, key=lambda f: (-f['puntuacion'], f['id']))[:k]


def metricas(recuperados, relevantes, k):
    if (isinstance(k, bool) or not isinstance(k, int) or k < 1
            or len(recuperados) > k or len(set(recuperados)) != len(recuperados)
            or len(set(relevantes)) != len(relevantes)):
        raise ValueError('Ranking o relevancia inválidos')
    if not relevantes:
        return {'precision': None, 'recall': None, 'hit': None, 'rr': None}
    aciertos = [i+1 for i, d in enumerate(recuperados) if d in relevantes]
    return {'precision': len(aciertos)/k, 'recall': len(aciertos)/len(relevantes),
            'hit': int(bool(aciertos)), 'rr': 1/aciertos[0] if aciertos else 0.0}


def validar_datos(corpus, consultas):
    if not corpus or not consultas:
        raise ValueError('Datos vacíos')
    for filas in (corpus, consultas):
        ids = [f['id'] for f in filas]
        if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError('IDs inválidos o duplicados')
        if any(not isinstance(f['texto'], str) or not f['texto'].strip() for f in filas):
            raise ValueError('Texto vacío')
    if any(not isinstance(d['titulo'], str) or not d['titulo'].strip() for d in corpus):
        raise ValueError('Título vacío')
    ids = {d['id'] for d in corpus}
    for q in consultas:
        r = q['relevantes']
        if not isinstance(r, list) or len(r) != len(set(r)) or not set(r) <= ids:
            raise ValueError('Relevantes duplicados o desconocidos')
        if not isinstance(q['familia'], str) or not q['familia']:
            raise ValueError('Familia inválida')


def separar(desarrollo, cierre):
    if ({q['id'] for q in desarrollo} & {q['id'] for q in cierre}
            or {q['familia'] for q in desarrollo} & {q['familia'] for q in cierre}
            or {q['texto'] for q in desarrollo} & {q['texto'] for q in cierre}):
        raise ValueError('Consultas o familias cruzan la partición')


def construir_indice(corpus, densos, inventario):
    if len(corpus) != len(densos):
        raise ValueError('Faltan embeddings del corpus')
    estado = ajustar_tfidf([texto_documento(d) for d in corpus])
    if any(len(vector(v)) != CONFIG['dimension'] for v in densos):
        raise ValueError('Dimensión densa incorrecta')
    return {'schema': 1, 'config': CONFIG, 'corpus_sha256': huella(UNIDAD/'datos/corpus.json'),
            'protocolo_sha256': huella(UNIDAD/'datos/protocolo.md'),
            'nucleo_sha256': huella(__file__), 'inventario': inventario,
            'ids': [d['id'] for d in corpus], 'estado_tfidf': estado,
            'matrices': {'tfidf': [transformar(texto_documento(d), estado) for d in corpus],
                         'bge_m3': [normalizar(v) for v in densos]}}


def validar_indice(indice, corpus):
    esperado = {'schema': 1, 'config': CONFIG, 'corpus_sha256': huella(UNIDAD/'datos/corpus.json'),
                'protocolo_sha256': huella(UNIDAD/'datos/protocolo.md'), 'nucleo_sha256': huella(__file__),
                'ids': [d['id'] for d in corpus]}
    if any(indice.get(k) != v for k, v in esperado.items()):
        raise ValueError('Índice incompatible: corpus, orden, versión o configuración cambió')
    estado = ajustar_tfidf([texto_documento(d) for d in corpus])
    if indice['estado_tfidf'] != estado:
        raise ValueError('Estado TF-IDF alterado')
    if set(indice['matrices']) != set(METODOS):
        raise ValueError('Métodos incompatibles')
    for metodo in METODOS:
        matriz = indice['matrices'][metodo]
        dim = CONFIG['dimension'] if metodo == 'bge_m3' else len(estado['vocabulario'])
        if len(matriz) != len(corpus) or any(len(vector(v)) != dim or not math.isclose(math.hypot(*v), 1, abs_tol=1e-9) for v in matriz):
            raise ValueError('Matriz inválida o sin normalizar')
    if indice['matrices']['tfidf'] != [transformar(texto_documento(d), estado) for d in corpus]:
        raise ValueError('Matriz TF-IDF alterada')


def evaluar(indice, consultas, metodo, densos=None):
    if metodo not in METODOS:
        raise ValueError('Método desconocido')
    if metodo == 'bge_m3' and (densos is None or len(densos) != len(consultas)):
        raise ValueError('Faltan vectores de consultas')
    filas = []
    for i, q in enumerate(consultas):
        v = (normalizar(densos[i]) if metodo == 'bge_m3'
             else transformar(q['texto'], indice['estado_tfidf']))
        top = ranking(indice['ids'], indice['matrices'][metodo], v, CONFIG['k'])
        filas.append({'id': q['id'], 'familia': q['familia'], 'respondible': bool(q['relevantes']),
                      'vector_cero': not any(v), 'top': top,
                      **metricas([f['id'] for f in top], q['relevantes'], CONFIG['k'])})
    validas = [f for f in filas if f['respondible']]
    sin_respuesta = [f for f in filas if not f['respondible']]
    familias = {f['familia'] for f in validas}
    resumen = {'metodo': metodo, 'n': len(filas), 'respondibles': len(validas),
               'sin_respuesta': len(sin_respuesta),
               'sin_respuesta_con_candidatos': sum(bool(f['top']) for f in sin_respuesta),
               'familias_respondibles': len(familias),
               'familias_con_hit_completo': sum(all(f['hit'] for f in validas if f['familia'] == g) for g in familias)}
    for campo in ('precision', 'recall', 'hit', 'rr'):
        resumen[campo] = math.fsum(f[campo] for f in validas)/len(validas) if validas else None
    return {'resumen': resumen, 'filas': filas}


def elegir(evaluaciones):
    if [e['resumen']['metodo'] for e in evaluaciones] != list(METODOS):
        raise ValueError('Comparación incompleta o desordenada')
    base = [f['id'] for f in evaluaciones[0]['filas']]
    for e in evaluaciones:
        if [f['id'] for f in e['filas']] != base or e['resumen']['rr'] is None:
            raise ValueError('No se comparan los mismos casos respondibles')
    # max conserva el primero en caso de empate: TF-IDF.
    return max(evaluaciones, key=lambda e: e['resumen']['rr'])['resumen']['metodo']

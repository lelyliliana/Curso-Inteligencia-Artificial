"""Extracción, recuperación, contexto y evaluación acotada; sin red."""
import json
from pathlib import Path
import re
import sys
import unicodedata

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.append(str(UNIDAD.parent/'unidad28-embeddings-busqueda/ejemplos'))
from busqueda import cargar, firma, guardar, huella, normalizar, ranking
sys.path.append(str(UNIDAD.parent/'unidad27-prompts-evaluacion/ejemplos'))
from contratos import ErrorSalida, leer_json

CONFIG = {'embedding': 'bge-m3:567m', 'generador': 'qwen3:8b', 'dimension': 1024,
          'candidatos_k': [1,3], 'max_parrafo': 600, 'max_contexto': 2200,
          'num_ctx': 4096, 'num_predict': 160, 'num_thread': 4, 'seed': 2901,
          'fragmentacion': 'parrafos_sin_solapamiento_v1', 'texto_embedding': 'titulo\ntexto',
          'normalizacion': 'L2', 'desempate': 'id_ascendente'}


def fragmentar(texto, documento):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError('Documento vacío')
    resultado = []
    for n, m in enumerate(re.finditer(r'\S.*?(?=\n[ \t]*\n|\Z)', texto, re.S), 1):
        contenido = m.group().rstrip()
        inicio, fin = m.start(), m.start()+len(contenido)
        if len(contenido) > CONFIG['max_parrafo']:
            raise ValueError('Párrafo demasiado largo: revisar fragmentación antes de indexar')
        resultado.append({'id': f"{documento['id']}:p{n:02d}", 'documento': documento['id'],
                          'titulo': documento['titulo'], 'version': documento['version'],
                          'ruta': documento['ruta'], 'inicio': inicio, 'fin': fin,
                          'linea_inicio': texto.count('\n',0,inicio)+1,
                          'linea_fin': texto.count('\n',0,fin-1)+1, 'texto': contenido,
                          'documento_sha256': firma(texto)})
    return resultado


def extraer():
    documentos = cargar(UNIDAD/'datos/manifiesto.json')
    if not documentos or len({d['id'] for d in documentos}) != len(documentos):
        raise ValueError('Manifiesto vacío o IDs repetidos')
    fragmentos = []
    permitida = (UNIDAD/'datos/documentos').resolve()
    for doc in documentos:
        ruta = (UNIDAD/'datos'/doc['ruta']).resolve()
        if not ruta.is_relative_to(permitida) or ruta.suffix != '.txt':
            raise ValueError('Solo TXT dentro de datos/documentos')
        fragmentos.extend(fragmentar(ruta.read_text(encoding='utf-8'), doc))
    return fragmentos


def texto_embedding(f):
    return f['titulo']+'\n'+f['texto']


def huellas():
    archivos = ['datos/manifiesto.json','datos/desarrollo.json','datos/cierre.json','datos/esquema.json',
                'datos/protocolo.md','prompts/sistema.txt','ejemplos/rag.py','ejemplos/motor.py']
    archivos += ['datos/'+d['ruta'] for d in cargar(UNIDAD/'datos/manifiesto.json')]
    archivos += ['../unidad28-embeddings-busqueda/ejemplos/busqueda.py',
                 '../unidad27-prompts-evaluacion/ejemplos/contratos.py',
                 '../unidad26-inferencia-servicios/ejemplos/servicios.py',
                 '../unidad26-inferencia-servicios/ejemplos/evaluacion.py']
    return {a: huella(UNIDAD/a) for a in archivos}


def construir_indice(fragmentos, vectores, inventario):
    if len(fragmentos) != len(vectores) or any(len(v) != CONFIG['dimension'] for v in vectores):
        raise ValueError('Matriz desalineada o dimensión incompatible')
    return {'schema': 1, 'config': CONFIG, 'huellas': huellas(), 'inventario': inventario,
            'fragmentos': fragmentos, 'vectores': [normalizar(v) for v in vectores]}


def validar_indice(indice):
    if (indice.get('schema') != 1 or indice.get('config') != CONFIG
            or indice.get('huellas') != huellas() or indice.get('fragmentos') != extraer()):
        raise ValueError('Índice incompatible con fuentes, código o preparación')
    esperado = construir_indice(indice['fragmentos'],indice['vectores'],indice['inventario'])
    # Una segunda normalización puede variar el último decimal.
    if any(abs(x-y)>1e-12 for a,b in zip(indice['vectores'],esperado['vectores']) for x,y in zip(a,b)):
        raise ValueError('Índice sin normalizar')


def recuperar(indice, consulta, k):
    ids = [f['id'] for f in indice['fragmentos']]
    return ranking(ids,indice['vectores'],normalizar(consulta),k)


def serializar(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def preparar_contexto(fragmentos, top, presupuesto=None):
    presupuesto = CONFIG['max_contexto'] if presupuesto is None else presupuesto
    if type(presupuesto) is not int or presupuesto < 2:
        raise ValueError('Presupuesto entero de al menos dos caracteres')
    ids = [f['id'] for f in top]
    if len(set(ids)) != len(ids):
        raise ValueError('Candidatos duplicados')
    por_id = {f['id']: f for f in fragmentos}
    seleccionados = []
    for fila in top:
        f = por_id[fila['id']]
        vista = {c:f[c] for c in ('id','titulo','version','linea_inicio','linea_fin','texto')}
        if len(serializar(seleccionados+[vista])) > presupuesto:
            break
        seleccionados.append(vista)
    return {'fragmentos': seleccionados, 'caracteres': len(serializar(seleccionados)),
            'omitidos': ids[len(seleccionados):]}


def prompt(caso, contexto):
    # Los juicios y la familia nunca forman parte de la entrada del modelo.
    return serializar({'pregunta': caso['pregunta'], 'documentos_no_confiables': contexto['fragmentos'],
                       'esquema_salida': cargar(UNIDAD/'datos/esquema.json')})


def canon(texto):
    return ' '.join(unicodedata.normalize('NFC',texto).casefold().split())


def evidencias(caso, ids=None):
    return [e for e in caso['evidencias'] if ids is None or e['fragmento'] in ids]


def estado_evidencia(evs):
    valores = {canon(e['valor']) for e in evs}
    return 'ausente' if not valores else 'ok' if len(valores)==1 else 'conflicto'


def cobertura(caso, ids):
    todas = evidencias(caso)
    recuperadas = evidencias(caso,ids)
    return {'recall': len({e['fragmento'] for e in recuperadas})/len({e['fragmento'] for e in todas}) if todas else None,
            'contexto_suficiente': {canon(e['valor']) for e in todas} == {canon(e['valor']) for e in recuperadas},
            'estado_contexto': estado_evidencia(recuperadas), 'estado_objetivo': estado_evidencia(todas)}


def validar_casos(casos, fragmentos):
    if not casos or len({c['id'] for c in casos}) != len(casos):
        raise ValueError('Casos vacíos o repetidos')
    por_id = {f['id']: f for f in fragmentos}
    for c in casos:
        if not c['pregunta'].strip() or not c['familia'] or len(c['evidencias']) != len({e['fragmento'] for e in c['evidencias']}):
            raise ValueError('Caso inválido')
        for e in c['evidencias']:
            if e['fragmento'] not in por_id or e['valor'] not in por_id[e['fragmento']]['texto']:
                raise ValueError('Anotación sin fragmento o valor literal')


def separar(desarrollo,cierre):
    for campo in ('id','familia','pregunta'):
        if {c[campo] for c in desarrollo} & {c[campo] for c in cierre}:
            raise ValueError('Datos compartidos entre desarrollo y cierre')


def forma(obj):
    if not isinstance(obj,dict) or set(obj)!= {'estado','dato','citas'}:
        return False
    if not isinstance(obj['estado'],str) or obj['estado'] not in ('ok','ausente','conflicto'):
        return False
    citas = obj['citas']
    if (not isinstance(citas,list) or any(not isinstance(c,str) or not c for c in citas)
            or len(set(citas)) != len(citas)):
        return False
    if obj['estado']=='ok':
        return isinstance(obj['dato'],str) and bool(obj['dato'].strip()) and bool(citas)
    return obj['dato'] is None and (not citas if obj['estado']=='ausente' else len(citas)>=2)


def evaluar_salida(texto, caso, contexto, finalizada=True):
    ids = [f['id'] for f in contexto['fragmentos']]
    r = {'forma':False,'citas_validas':False,'apoyo':False,'objetivo':False,'aceptada':False,
         'finalizada':finalizada, **cobertura(caso,ids)}
    try:
        obj = leer_json(texto)
    except ErrorSalida:
        return r | {'fallo':'json'}
    r['objeto'] = obj
    if not forma(obj):
        return r | {'fallo':'forma_coherencia'}
    r['forma'] = True
    r['citas_validas'] = all(c in ids for c in obj['citas'])
    if not r['citas_validas']:
        return r | {'fallo':'cita_fuera_contexto'}
    estado = obj['estado']
    citadas = evidencias(caso,obj['citas'])
    valores = {canon(e['valor']) for e in citadas}
    pertinentes = {e['fragmento'] for e in citadas} == set(obj['citas'])
    if estado == 'ok':
        r['apoyo'] = pertinentes and valores == {canon(obj['dato'])}
        r['objetivo'] = r['estado_objetivo']=='ok' and {canon(e['valor']) for e in evidencias(caso)}=={canon(obj['dato'])}
    elif estado == 'conflicto':
        r['apoyo'] = pertinentes and len(valores)>=2
        r['objetivo'] = r['estado_objetivo']=='conflicto' and valores == {canon(e['valor']) for e in evidencias(caso)}
    else:
        r['apoyo'] = not evidencias(caso,ids)
        r['objetivo'] = r['estado_objetivo']=='ausente'
    r['aceptada'] = (finalizada and r['apoyo'] and r['objetivo'] and r['contexto_suficiente'])
    if not r['aceptada']:
        r['fallo'] = ('parada' if not finalizada else 'contexto_incompleto' if not r['contexto_suficiente']
                      else 'apoyo' if not r['apoyo'] else 'objetivo')
    return r


def extractiva(caso, contexto):
    """Cita literal del primer fragmento: no consulta etiquetas para responder."""
    fs = contexto['fragmentos']
    salida = {'texto': fs[0]['texto'] if fs else '', 'citas': [fs[0]['id']] if fs else []}
    # Solo evaluación posterior: etiquetas no deciden el texto seleccionado.
    util = bool(fs) and estado_evidencia(caso['evidencias'])=='ok' and cobertura(caso,salida['citas'])['contexto_suficiente']
    return salida | {'literal': bool(fs), 'util_como_respuesta': util}


def seleccionar(resumenes):
    if [r['k'] for r in resumenes] != CONFIG['candidatos_k'] or len({r['n'] for r in resumenes}) != 1:
        raise ValueError('Comparación de desarrollo incompleta')
    ganador = max(resumenes,key=lambda r:r['aceptada'])
    if ganador['aceptada']==0:
        raise ValueError('Ninguna respuesta aceptada: no abrir cierre')
    return ganador['k']

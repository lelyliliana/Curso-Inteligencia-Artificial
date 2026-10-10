"""Captura local y reconstrucción del experimento de RAG."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import platform
from statistics import mean, median
import sys
import time

from rag import (CONFIG, UNIDAD, cargar, cobertura, construir_indice, evaluar_salida, extraer,
                 extractiva, firma, guardar, huellas, preparar_contexto, prompt, recuperar,
                 seleccionar, separar, texto_embedding, validar_casos, validar_indice)
sys.path.append(str(UNIDAD.parent/'unidad26-inferencia-servicios/ejemplos'))
from evaluacion import inventario
from servicios import ErrorServicio, OLLAMA, leer_ollama, numero, peticion_ollama, solicitar

RECURSOS = UNIDAD/'recursos'


def casos(fase):
    if fase not in ('desarrollo','cierre'):
        raise ValueError('Fase desconocida')
    cs = cargar(UNIDAD/f'datos/{fase}.json')
    validar_casos(cs,extraer())
    return cs


def peticion_embedding(texto):
    if not isinstance(texto,str) or not texto.strip() or len(texto)>2000:
        raise ValueError('Texto de embedding inválido')
    return {'model':CONFIG['embedding'],'input':texto,'truncate':False,'keep_alive':'5m',
            'options':{'num_gpu':0,'num_thread':4,'num_ctx':2048}}


def leer_embedding(r):
    if not isinstance(r,dict) or r.get('model')!=CONFIG['embedding'] or 'error' in r:
        raise ValueError('Respuesta de embeddings incompatible')
    vs=r.get('embeddings')
    if not isinstance(vs,list) or len(vs)!=1 or not isinstance(vs[0],list) or len(vs[0])!=CONFIG['dimension']:
        raise ValueError('Dimensión o cantidad de embeddings inválida')
    from busqueda import normalizar
    normalizar(vs[0])
    for campo in ('total_duration','load_duration','prompt_eval_count'):
        numero(r.get(campo),campo,entero=True)
    return vs[0]


def peticion_generacion(caso, contexto):
    sistema=(UNIDAD/'prompts/sistema.txt').read_text(encoding='utf-8').strip()
    if len(sistema)>1600:
        raise ValueError('Instrucción mayor que el presupuesto')
    cuerpo=peticion_ollama(CONFIG['generador'],prompt(caso,contexto),CONFIG['num_predict'])
    cuerpo['system']=sistema
    cuerpo['format']=cargar(UNIDAD/'datos/esquema.json')
    cuerpo['options'].update(num_ctx=CONFIG['num_ctx'],seed=CONFIG['seed'])
    return cuerpo


def entradas(fase):
    fs = [('fragmento',f['id'],texto_embedding(f)) for f in extraer()] if fase=='desarrollo' else []
    return fs+[('consulta',c['id'],c['pregunta']) for c in casos(fase)]


def plan(cs,ks):
    return [(c,k) for i,c in enumerate(cs) for k in ks[i%len(ks):]+ks[:i%len(ks)]]


def medir(endpoint,solicitud,cliente):
    inicio=time.perf_counter()
    try:
        resultado={'respuesta':cliente(OLLAMA+endpoint,solicitud,timeout=120)}
    except ErrorServicio as exc:
        resultado={'error':exc.codigo}
    return {'solicitud':solicitud,'pared_s':time.perf_counter()-inicio,**resultado}


def vectores(registro):
    esperado=entradas(registro['fase'])
    filas=registro.get('embeddings',[])
    if len(filas)!=len(esperado):
        raise ValueError('Captura de embeddings incompleta')
    salida={'fragmento':[],'consulta':[]}
    for f,(tipo,identificador,texto) in zip(filas,esperado):
        if f.get('tipo')!=tipo or f.get('id')!=identificador or f.get('solicitud')!=peticion_embedding(texto) or 'error' in f:
            raise ValueError('Entrada de embedding alterada o fallida')
        numero(f.get('pared_s'),'pared_s')
        salida[tipo].append(leer_embedding(f.get('respuesta')))
    return salida


def verificar_registro(registro):
    if (registro.get('schema')!=1 or registro.get('origen')!='ollama_local_real'
            or registro.get('config')!=CONFIG or registro.get('huellas')!=huellas()
            or registro.get('inventario_estable') is not True):
        raise ValueError('Registro incompatible, parcial o fuentes modificadas')
    for nombre in ('embedding','generador'):
        if not registro.get('inventarios',{}).get(nombre,{}).get('digest'):
            raise ValueError('Falta identidad del modelo')


def indice_de_desarrollo(registro):
    verificar_registro(registro)
    if registro['fase']!='desarrollo':
        raise ValueError('El índice se construye con desarrollo')
    return construir_indice(extraer(),vectores(registro)['fragmento'],registro['inventarios']['embedding'])


def analizar(registro, indice, seleccion=None):
    verificar_registro(registro)
    validar_indice(indice)
    if indice['inventario']!=registro['inventarios']['embedding']:
        raise ValueError('Se mezclaron espacios de embeddings')
    fase=registro['fase']; cs=casos(fase); ks=CONFIG['candidatos_k']
    if fase=='cierre':
        if (seleccion is None or registro.get('seleccion_sha256')!=firma(seleccion)
                or seleccion.get('indice_sha256')!=firma(indice)
                or seleccion.get('inventarios')!=registro['inventarios']
                or seleccion.get('huellas')!=huellas()
                or seleccion.get('k')!=seleccionar(seleccion['resumenes'])):
            raise ValueError('Cierre sin elección congelada compatible')
        separar(casos('desarrollo'),cs)
        ks=[seleccion['k']]
    vs=vectores(registro)
    por_id={c['id']:v for c,v in zip(cs,vs['consulta'])}
    esperado=plan(cs,ks)
    if len(registro.get('generaciones',[]))!=len(esperado):
        raise ValueError('Captura de generación incompleta')
    filas=[]
    for fila,(caso,k) in zip(registro['generaciones'],esperado):
        top=recuperar(indice,por_id[caso['id']],k)
        contexto=preparar_contexto(indice['fragmentos'],top)
        if (fila.get('caso')!=caso['id'] or fila.get('k')!=k or fila.get('top')!=top
                or fila.get('contexto')!=contexto or fila.get('solicitud')!=peticion_generacion(caso,contexto)
                or ('respuesta' in fila)==('error' in fila)):
            raise ValueError('Caso, orden, recuperación o prompt alterado')
        numero(fila.get('pared_s'),'pared_s')
        r={'contrato':False,**evaluar_salida('',caso,contexto,False)}
        if 'error' in fila:
            r['fallo']=fila['error']
        else:
            try:
                respuesta=leer_ollama(fila['respuesta'])
                if fila['respuesta'].get('model')!=CONFIG['generador']:
                    raise ErrorServicio('modelo_incorrecto')
                presupuesto_ok=respuesta['tokens_entrada']+CONFIG['num_predict']<=CONFIG['num_ctx']
                r={'contrato':True,**evaluar_salida(respuesta['texto'],caso,contexto,
                                                   respuesta['finalizada'] and presupuesto_ok),
                   'tokens_entrada':respuesta['tokens_entrada'],'tokens_salida':respuesta['tokens_salida'],
                   'presupuesto_tokens_ok':presupuesto_ok, 'texto':respuesta['texto']}
                if not presupuesto_ok: r['fallo']='presupuesto_tokens'
            except ErrorServicio as exc:
                r['fallo']=exc.codigo
        filas.append({'caso':caso['id'],'familia':caso['familia'],'k':k,'contexto':contexto,
                      'pared_s':fila['pared_s'],'extractiva':extractiva(caso,contexto),**r})
    resumenes=[]
    for k in ks:
        grupo=[f for f in filas if f['k']==k]
        familias={f['familia'] for f in grupo}
        con_citas=[f for f in grupo if f['forma'] and f['objeto']['citas']]
        rs=[f['recall'] for f in grupo if f['recall'] is not None]
        resumenes.append({'k':k,'n':len(grupo),**{campo:sum(f[campo] for f in grupo) for campo in
                         ('contrato','finalizada','forma','contexto_suficiente','apoyo','objetivo','aceptada')},
                         'n_con_evidencias':len(rs),'recall_medio':mean(rs) if rs else None,
                         'salidas_con_citas':len(con_citas),
                         'salidas_con_citas_validas':sum(f['citas_validas'] for f in con_citas),
                         'salidas_con_citas_apoyadas':sum(f['apoyo'] for f in con_citas),
                         'familias':len(familias),'familias_completas':sum(all(f['aceptada'] for f in grupo if f['familia']==g) for g in familias),
                         'extractiva_literal':sum(f['extractiva']['literal'] for f in grupo),
                         'extractiva_util':sum(f['extractiva']['util_como_respuesta'] for f in grupo),
                         'por_estado':{s:{'n':sum(f['estado_objetivo']==s for f in grupo),
                             'aceptadas':sum(f['aceptada'] for f in grupo if f['estado_objetivo']==s)} for s in ('ok','ausente','conflicto')},
                         'fallos':dict(Counter(f['fallo'] for f in grupo if 'fallo' in f)),
                         'mediana_pared_s':median(f['pared_s'] for f in grupo),
                         'tokens_salida_total':sum(f.get('tokens_salida',0) for f in grupo)})
    return {'fase':fase,'filas':filas,'resumenes':resumenes}


def congelar(registro,indice):
    if registro['fase']!='desarrollo':
        raise ValueError('Solo seleccionar con desarrollo')
    informe=analizar(registro,indice)
    return {'schema':1,'k':seleccionar(informe['resumenes']),'huellas':huellas(),
            'criterio':'max_aceptadas_empate_k_menor','inventarios':registro['inventarios'],
            'indice_sha256':firma(indice),'registro_desarrollo_sha256':firma(registro),
            'resumenes':informe['resumenes']}


def verificar_seleccion(registro_desarrollo,indice,seleccion):
    if indice!=indice_de_desarrollo(registro_desarrollo) or seleccion!=congelar(registro_desarrollo,indice):
        raise ValueError('Índice o selección no corresponde al desarrollo publicado')


def capturar(fase,salida,indice=None,seleccion=None,registro_desarrollo=None,cliente=solicitar):
    salida=Path(salida)
    if salida.exists() and any(salida.iterdir()):
        raise ValueError('Usar carpeta nueva o vacía para conservar las capturas')
    if fase=='cierre':
        verificar_seleccion(registro_desarrollo,indice,seleccion)
        separar(casos('desarrollo'),casos('cierre'))
    meta={nombre:inventario(CONFIG[nombre],cliente) for nombre in ('embedding','generador')}
    if 'embedding' not in meta['embedding']['capacidades'] or 'completion' not in meta['generador']['capacidades']:
        raise ValueError('Capacidades de modelo incompatibles')
    if fase=='cierre' and meta!=seleccion['inventarios']:
        raise ValueError('Los modelos cambiaron desde desarrollo')
    reg={'schema':1,'origen':'ollama_local_real','fase':fase,'config':CONFIG,'huellas':huellas(),
         'fecha_utc':datetime.now(timezone.utc).isoformat(),'inventarios':meta,'inventario_estable':False,
         'entorno':{'python':platform.python_version(),'sistema':platform.system(),'arquitectura':platform.machine()},
         'embeddings':[],'generaciones':[]}
    if seleccion is not None: reg['seleccion_sha256']=firma(seleccion)
    reg['calentamiento_embedding']=medir('/api/embed',peticion_embedding('Prueba de carga de embeddings.'),cliente)
    guardar(salida/'registro.json',reg)
    leer_embedding(reg['calentamiento_embedding'].get('respuesta'))
    for tipo,identificador,texto in entradas(fase):
        print(f'Embedding: {identificador}',flush=True)
        fila={'tipo':tipo,'id':identificador,**medir('/api/embed',peticion_embedding(texto),cliente)}
        reg['embeddings'].append(fila); guardar(salida/'registro.json',reg)
        leer_embedding(fila.get('respuesta'))
    vs=vectores(reg)
    if fase=='desarrollo': indice=construir_indice(extraer(),vs['fragmento'],meta['embedding'])
    cs=casos(fase); por_id={c['id']:v for c,v in zip(cs,vs['consulta'])}
    calentamiento=peticion_ollama(CONFIG['generador'],'Responde OK.',4)
    calentamiento['options'].update(num_ctx=CONFIG['num_ctx'],seed=CONFIG['seed'])
    reg['calentamiento_generador']=medir('/api/generate',calentamiento,cliente)
    guardar(salida/'registro.json',reg)
    leer_ollama(reg['calentamiento_generador'].get('respuesta'))
    ks=CONFIG['candidatos_k'] if fase=='desarrollo' else [seleccion['k']]
    for caso,k in plan(cs,ks):
        top=recuperar(indice,por_id[caso['id']],k)
        contexto=preparar_contexto(indice['fragmentos'],top)
        print(f"RAG local: {caso['id']}; k={k}",flush=True)
        fila={'caso':caso['id'],'k':k,'top':top,'contexto':contexto,
              **medir('/api/generate',peticion_generacion(caso,contexto),cliente)}
        reg['generaciones'].append(fila); guardar(salida/'registro.json',reg)
    reg['recursos_servidor']=[{k:m.get(k) for k in ('name','digest','size','size_vram','context_length')}
                             for m in cliente(OLLAMA+'/api/ps').get('models',[]) if m.get('name') in (CONFIG['embedding'],CONFIG['generador'])]
    if meta!={nombre:inventario(CONFIG[nombre],cliente) for nombre in ('embedding','generador')}:
        raise ValueError('Cambió el inventario durante la captura')
    reg['inventario_estable']=True
    guardar(salida/'registro.json',reg)
    return reg,indice

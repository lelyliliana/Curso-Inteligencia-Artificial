"""Prompts congelados, comparación y cierre; transporte reutilizado de la Unidad 26."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
from statistics import median
import sys

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.append(str(UNIDAD.parent / 'unidad26-inferencia-servicios/ejemplos'))
from evaluacion import guardar, huella, inventario, medir
from servicios import ErrorServicio, leer_ollama, numero, peticion_ollama, solicitar
from contratos import (ErrorSalida, contenido_correcto, leer_json, referencia_reglas,
                       validar_coherencia, validar_forma)

CANDIDATOS = ('basico', 'explicito', 'con_esquema')
CAPAS = ('contrato', 'finalizada', 'json_valido', 'forma', 'coherencia', 'contenido', 'aceptada')
ARCHIVOS = ('datos/protocolo.md', 'datos/esquema.json', 'prompts/basico.txt', 'prompts/explicito.txt',
            'datos/desarrollo.json', 'datos/cierre.json')


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding='utf-8'))


def huellas():
    return {p: huella(UNIDAD/p) for p in ARCHIVOS}


def cargar_casos(fase):
    if fase not in ('desarrollo', 'cierre'):
        raise ValueError('Fase desconocida')
    casos = cargar(UNIDAD / f'datos/{fase}.json')
    if len({c['id'] for c in casos}) != len(casos):
        raise ValueError('Casos repetidos')
    for caso in casos:
        entrada = caso['entrada']
        if (not isinstance(entrada['consulta'], str) or not isinstance(entrada['nota'], str)
                or len({r['id'] for r in entrada['registros']}) != len(entrada['registros'])):
            raise ValueError('Entrada inválida')
        for r in entrada['registros']:
            if (not isinstance(r['id'], str) or not isinstance(r['sensor'], str)
                    or type(r['valor']) is not int or type(r['confirmado']) is not bool):
                raise ValueError('Registro inválido')
        if referencia_reglas(entrada) != caso['esperado']:
            raise ValueError('Referencia incoherente con la tarea')
    return casos


def construir_prompt(caso, candidato):
    if candidato not in CANDIDATOS:
        raise ValueError('Candidato desconocido')
    archivo = 'basico' if candidato == 'basico' else 'explicito'
    instruccion = (UNIDAD / f'prompts/{archivo}.txt').read_text(encoding='utf-8').strip()
    if candidato != 'basico':
        instruccion += '\nEsquema de salida:\n' + json.dumps(cargar(UNIDAD/'datos/esquema.json'), ensure_ascii=False)
    # Solo entrada: nunca enviar etiqueta, familia, fenómeno o respuesta esperada.
    return instruccion + '\nEntrada JSON:\n' + json.dumps(caso['entrada'], ensure_ascii=False)


def peticion(caso, candidato, modelo):
    cuerpo = peticion_ollama(modelo, construir_prompt(caso, candidato), 160)
    cuerpo['options'].update(num_ctx=2048, seed=2701)
    if candidato == 'con_esquema':
        cuerpo['format'] = cargar(UNIDAD/'datos/esquema.json')
    return cuerpo


def plan(casos, candidatos=CANDIDATOS):
    if not candidatos or any(c not in CANDIDATOS for c in candidatos):
        raise ValueError('Candidatos inválidos')
    return [(caso, candidato) for i, caso in enumerate(casos)
            for candidato in candidatos[i % len(candidatos):] + candidatos[:i % len(candidatos)]]


def evaluar_fila(fila, caso):
    r = dict.fromkeys(CAPAS, False)
    if 'error' in fila:
        return r | {'fallo': fila['error']}
    try:
        servicio = leer_ollama(fila.get('respuesta'))
    except ErrorServicio as exc:
        return r | {'fallo': exc.codigo}
    r.update(contrato=True, finalizada=servicio['finalizada'], texto=servicio['texto'],
             razon=servicio['razon'], tokens_entrada=servicio['tokens_entrada'], tokens_salida=servicio['tokens_salida'])
    try:
        obj = leer_json(servicio['texto'])
    except ErrorSalida as exc:
        return r | {'fallo': str(exc)}
    r.update(json_valido=True, objeto=obj, forma=validar_forma(obj))
    if not r['forma']:
        return r | {'fallo': 'forma'}
    r['coherencia'] = validar_coherencia(obj)
    if not r['coherencia']:
        return r | {'fallo': 'coherencia'}
    r['contenido'] = contenido_correcto(obj, caso['esperado'])
    r['aceptada'] = r['finalizada'] and r['contenido']
    if not r['aceptada']:
        r['fallo'] = 'truncada' if not r['finalizada'] else 'contenido'
    return r


def resumir(filas, candidatos):
    resumen = []
    for candidato in candidatos:
        grupo = [f for f in filas if f['candidato'] == candidato]
        familias = sorted({f['familia'] for f in grupo})
        tiempos = [f['pared_s'] for f in grupo if f['contrato']]
        resumen.append({'candidato': candidato, 'intentos': len(grupo),
                        **{c: sum(f[c] for f in grupo) for c in CAPAS},
                        'familias': len(familias), 'familias_completas': sum(
                            all(f['aceptada'] for f in grupo if f['familia'] == familia) for familia in familias),
                        'por_estado': {e: {'n': sum(f['esperado']['estado'] == e for f in grupo),
                            'aceptadas': sum(f['aceptada'] for f in grupo if f['esperado']['estado'] == e)}
                            for e in ('ok', 'ausente', 'conflicto')},
                        'fallos': dict(Counter(f['fallo'] for f in grupo if 'fallo' in f)),
                        'n_latencias': len(tiempos), 'mediana_pared_s': median(tiempos) if tiempos else None,
                        'tokens_salida_total': sum(f.get('tokens_salida', 0) for f in grupo)})
    return resumen


def analizar(registro, seleccion=None):
    if registro.get('schema') != 1 or registro.get('origen') != 'ollama_local_real':
        raise ValueError('Captura local desconocida')
    if registro.get('huellas') != huellas() or registro.get('inventario_estable') is not True:
        raise ValueError('Configuración o inventario no confirmado')
    fase = registro['fase']
    casos = cargar_casos(fase)
    candidatos = CANDIDATOS
    if fase == 'cierre':
        validar_seleccion(seleccion)
        candidatos = (seleccion['candidato'],)
        if (registro.get('seleccion_sha256') != huella_objeto(seleccion)
                or registro['inventario'] != seleccion['inventario'] or registro['modelo'] != seleccion['modelo']):
            raise ValueError('Cierre no corresponde a la selección congelada')
        if {c['familia'] for c in casos} & set(seleccion['familias_desarrollo']):
            raise ValueError('Familias compartidas entre fases')
    esperado = plan(casos, candidatos)
    filas = registro.get('filas', [])
    if len(filas) != len(esperado):
        raise ValueError('Registro incompleto: no descartar fallos')
    evaluadas = []
    for fila, (caso, candidato) in zip(filas, esperado):
        if (fila.get('caso') != caso['id'] or fila.get('candidato') != candidato
                or fila.get('solicitud') != peticion(caso, candidato, registro['modelo'])):
            raise ValueError('Cambió un prompt, condición o caso')
        numero(fila.get('pared_s'), 'pared_s')
        if ('respuesta' in fila) == ('error' in fila):
            raise ValueError('Cada intento debe tener respuesta o error')
        evaluadas.append({'caso': caso['id'], 'familia': caso['familia'], 'candidato': candidato,
                          'esperado': caso['esperado'], 'pared_s': fila['pared_s'], **evaluar_fila(fila, caso)})
    return {'origen': 'analisis_de_captura', 'fase': fase, 'modelo': registro['modelo'],
            'filas': evaluadas, 'resumen': resumir(evaluadas, candidatos),
            'referencia_reglas': {'correctas': sum(referencia_reglas(c['entrada']) == c['esperado'] for c in casos),
                                  'casos': len(casos)}}


def huella_objeto(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()


def seleccionar(informe):
    if informe['fase'] != 'desarrollo':
        raise ValueError('La selección solo puede usar desarrollo')
    por_nombre = {r['candidato']: r for r in informe['resumen']}
    if set(por_nombre) != set(CANDIDATOS) or len({r['intentos'] for r in por_nombre.values()}) != 1:
        raise ValueError('Comparación incompleta')
    ganador = max(CANDIDATOS, key=lambda c: por_nombre[c]['aceptada'])
    if por_nombre[ganador]['aceptada'] == 0:
        raise ValueError('Ningún candidato cumple: detener antes del cierre')
    return ganador


def congelar(registro):
    informe = analizar(registro)
    return {'schema': 1, 'candidato': seleccionar(informe), 'modelo': registro['modelo'],
            'inventario': registro['inventario'], 'huellas': huellas(),
            'registro_desarrollo_sha256': huella_objeto(registro),
            'familias_desarrollo': sorted({c['familia'] for c in cargar_casos('desarrollo')}),
            'criterio': 'max_aceptadas; empate: basico, explicito, con_esquema',
            'resumen_desarrollo': informe['resumen']}


def validar_seleccion(seleccion):
    if not isinstance(seleccion, dict) or seleccion.get('schema') != 1 or seleccion.get('huellas') != huellas():
        raise ValueError('Selección ausente o configuración modificada')
    if seleccion.get('candidato') != seleccionar({'fase': 'desarrollo', 'resumen': seleccion['resumen_desarrollo']}):
        raise ValueError('La selección no aplica la regla fijada')
    if seleccion.get('familias_desarrollo') != sorted({c['familia'] for c in cargar_casos('desarrollo')}):
        raise ValueError('Familias de desarrollo modificadas')


def ejecutar_real(fase, modelo, salida, seleccion=None, cliente=solicitar):
    salida = Path(salida)
    if (salida/'registro.json').exists():
        raise ValueError('Elige una carpeta nueva; no sobrescribir una ejecución')
    candidatos = CANDIDATOS
    if fase == 'cierre':
        validar_seleccion(seleccion)
        if modelo != seleccion['modelo']:
            raise ValueError('No cambiar el modelo al cerrar')
        candidatos = (seleccion['candidato'],)
    casos = cargar_casos(fase)
    if fase == 'cierre' and {c['familia'] for c in casos} & set(seleccion['familias_desarrollo']):
        raise ValueError('Familias compartidas')
    meta = inventario(modelo, cliente)
    if fase == 'cierre' and meta != seleccion['inventario']:
        raise ValueError('Cambió el servidor o modelo antes del cierre')
    r = {'schema': 1, 'origen': 'ollama_local_real', 'fase': fase, 'modelo': modelo,
         'fecha_utc': datetime.now(timezone.utc).isoformat(), 'huellas': huellas(), 'inventario': meta,
         'entorno': {'python': platform.python_version(), 'sistema': platform.system(), 'arquitectura': platform.machine()},
         'timeout_socket_s': 120, 'filas': []}
    if fase == 'cierre':
        r['seleccion_sha256'] = huella_objeto(seleccion)
    cuerpo = peticion_ollama(modelo, 'Responde OK.', 4)
    cuerpo['options'].update(num_ctx=2048, seed=2701)
    r['calentamiento'] = medir(cuerpo, 120, cliente)
    guardar(salida/'registro.json', r)
    for caso, candidato in plan(casos, candidatos):
        print(f"{fase}: {caso['id']} / {candidato}", flush=True)
        r['filas'].append({'caso': caso['id'], 'candidato': candidato,
                           **medir(peticion(caso, candidato, modelo), 120, cliente)})
        guardar(salida/'registro.json', r)
    if inventario(modelo, cliente) != meta:
        raise ValueError('Inventario cambió: registro sin confirmar')
    r['inventario_estable'] = True
    guardar(salida/'registro.json', r)
    return r

"""Validación de esta tarea concreta, no un motor general de JSON Schema."""

import json
import math


class ErrorSalida(ValueError):
    pass


def objeto_sin_repetidas(pares):
    salida = {}
    for clave, valor in pares:
        if clave in salida:
            raise ErrorSalida('clave_repetida')
        salida[clave] = valor
    return salida


def constante_prohibida(valor):
    raise ErrorSalida('constante_no_json')


def comprobar_finitos(obj):
    if isinstance(obj, float) and not math.isfinite(obj):
        raise ErrorSalida('numero_no_finito')
    if isinstance(obj, dict):
        for valor in obj.values():
            comprobar_finitos(valor)
    elif isinstance(obj, list):
        for valor in obj:
            comprobar_finitos(valor)


def leer_json(texto):
    if not isinstance(texto, str) or len(texto.encode('utf-8')) > 8192:
        raise ErrorSalida('salida_excesiva_o_no_texto')
    try:
        obj = json.loads(texto, object_pairs_hook=objeto_sin_repetidas, parse_constant=constante_prohibida)
        comprobar_finitos(obj)
        return obj
    except ErrorSalida:
        raise
    except (ValueError, RecursionError):
        raise ErrorSalida('json_invalido') from None


def es_entero(valor):
    return (not isinstance(valor, bool) and
            (isinstance(valor, int) or isinstance(valor, float) and math.isfinite(valor) and valor.is_integer()))


def validar_forma(obj):
    """Implementa exactamente datos/esquema.json; no interpreta esquemas arbitrarios."""
    if not isinstance(obj, dict) or set(obj) != {'estado', 'valor', 'evidencia'}:
        return False
    if obj['estado'] not in ('ok', 'ausente', 'conflicto'):
        return False
    if obj['valor'] is not None and not es_entero(obj['valor']):
        return False
    evidencia = obj['evidencia']
    return (isinstance(evidencia, list) and all(isinstance(i, str) for i in evidencia)
            and len(set(evidencia)) == len(evidencia))


def validar_coherencia(obj):
    if not validar_forma(obj):
        return False
    estado, valor, ids = obj['estado'], obj['valor'], obj['evidencia']
    if estado == 'ok':
        return es_entero(valor) and len(ids) > 0
    if estado == 'ausente':
        return valor is None and len(ids) == 0
    return valor is None and len(ids) >= 2


def contenido_correcto(obj, esperado):
    return (validar_coherencia(obj) and obj['estado'] == esperado['estado']
            and obj['valor'] == esperado['valor'] and set(obj['evidencia']) == set(esperado['evidencia']))


def referencia_reglas(entrada):
    """Resuelve esta entrada estructurada; nunca interpreta ni ejecuta la nota."""
    filas = [r for r in entrada['registros'] if r['sensor'] == entrada['consulta'] and r['confirmado'] is True]
    valores = {r['valor'] for r in filas}
    if not filas:
        return {'estado': 'ausente', 'valor': None, 'evidencia': []}
    return {'estado': 'ok' if len(valores) == 1 else 'conflicto',
            'valor': filas[0]['valor'] if len(valores) == 1 else None,
            'evidencia': sorted(r['id'] for r in filas)}

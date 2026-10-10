"""Salidas artificiales: no son resultados del modelo ni se usan para seleccionarlo."""

import json
from experimento import cargar_casos, evaluar_fila


def construir():
    caso = cargar_casos('desarrollo')[2]  # F02a: dos registros concordantes.
    correcta = caso['esperado']
    texto = json.dumps(correcta)
    ejemplos = [
        ('correcta', texto, 'stop'),
        ('orden_y_decimal', '{"evidencia":["f02r2","f02r1"],"valor":-3.0,"estado":"ok"}', 'stop'),
        ('markdown', '```json\n' + texto + '\n```', 'stop'),
        ('json_incompleto', '{"estado":"ok",', 'length'),
        ('clave_repetida', '{"estado":"ausente","estado":"ok","valor":-3,"evidencia":["f02r1","f02r2"]}', 'stop'),
        ('numero_texto', json.dumps(correcta | {'valor': '-3'}), 'stop'),
        ('booleano', json.dumps(correcta | {'valor': True}), 'stop'),
        ('extra', json.dumps(correcta | {'explicacion': 'dato'}), 'stop'),
        ('incoherente', json.dumps(correcta | {'estado': 'ausente'}), 'stop'),
        ('valor_incorrecto', json.dumps(correcta | {'valor': 7}), 'stop'),
        ('id_inventado', json.dumps(correcta | {'evidencia': ['falso']}), 'stop'),
        ('evidencia_incompleta', json.dumps(correcta | {'evidencia': ['f02r1']}), 'stop'),
        ('id_repetido', json.dumps(correcta | {'evidencia': ['f02r1', 'f02r1']}), 'stop'),
        ('truncada_valida', texto, 'length'),
        ('negativa_libre', 'No puedo responder a esa solicitud.', 'stop'),
        ('nan', '{"estado":"ok","valor":NaN,"evidencia":["f02r1"]}', 'stop'),
    ]
    filas = []
    for nombre, salida, razon in ejemplos:
        # Contadores ficticios, usados solo para satisfacer el contrato del servicio.
        respuesta = {'done': True, 'response': salida, 'done_reason': razon, 'eval_count': 20,
                     'eval_duration': 1_000_000_000, 'prompt_eval_count': 10,
                     'total_duration': 2_000_000_000, 'load_duration': 0}
        filas.append({'id': nombre, 'salida_simulada': salida, **evaluar_fila({'respuesta': respuesta}, caso)})
    return {'origen': 'contraejemplos_artificiales_sin_inferencia', 'caso': caso, 'filas': filas}

"""Pruebas sin servicios externos: transporte, contratos y evidencia publicada."""

from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError
from urllib.request import Request

EJEMPLOS = Path(__file__).resolve().parents[1] / "ejemplos"
sys.path.insert(0, str(EJEMPLOS))
from servicios import (ErrorServicio, MAX_BYTES, OLLAMA, OPENAI, SinRedireccion,
                       leer_ollama, leer_remota, peticion_ollama, peticion_remota, solicitar)
from evaluacion import (CASOS, UNIDAD, analizar, cargar, ejecutar_real, guardar, inventario,
                        medir, plan, puntuar)
from simulacion import (ejecutar_simulaciones, respuesta_ollama, respuesta_remota,
                        transporte_simulado)


class Transporte(unittest.TestCase):
    def test_peticion_utf8_y_timeout(self):
        abrir = Mock(return_value=BytesIO(b'{"ok":true}'))
        self.assertEqual(solicitar(OLLAMA + '/api/generate', {'prompt': 'energía'}, timeout=7, abrir_http=abrir), {'ok': True})
        req = abrir.call_args.args[0]
        self.assertEqual(req.get_method(), 'POST')
        self.assertEqual(json.loads(req.data), {'prompt': 'energía'})
        self.assertEqual(abrir.call_args.kwargs, {'timeout': 7})

    def test_get_sin_cuerpo(self):
        abrir = Mock(return_value=BytesIO(b'{}'))
        solicitar(OLLAMA + '/api/version', abrir_http=abrir)
        self.assertEqual(abrir.call_args.args[0].get_method(), 'GET')

    def test_destinos_fijos(self):
        abrir = Mock()
        for url in ('http://example.com', OPENAI + '/extra', OLLAMA + '/api/pull', 'http://127.0.0.1:11435/api/generate'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                solicitar(url, abrir_http=abrir)
        abrir.assert_not_called()

    def test_clave_solo_endpoint_remoto(self):
        abrir = Mock(return_value=BytesIO(b'{}'))
        with self.assertRaises(ValueError):
            solicitar(OLLAMA + '/api/generate', clave='clave-ficticia', abrir_http=abrir)
        abrir.assert_not_called()
        solicitar(OPENAI, {}, clave='clave-ficticia', abrir_http=abrir)
        self.assertEqual(abrir.call_args.args[0].get_header('Authorization'), 'Bearer clave-ficticia')

    def test_claves_y_timeout_invalidos_no_conectan(self):
        abrir = Mock()
        for clave in ('', ' con espacios ', 'a\nb'):
            with self.assertRaises(ValueError):
                solicitar(OPENAI, clave=clave, abrir_http=abrir)
        for tiempo in (0, -1, float('inf'), float('nan'), True):
            with self.assertRaises(ValueError):
                solicitar(OPENAI, timeout=tiempo, abrir_http=abrir)
        abrir.assert_not_called()

    def test_redirecciones_bloqueadas(self):
        self.assertIsNone(SinRedireccion().redirect_request(Request(OPENAI), None, 302, '', {}, 'https://example.com'))

    def test_http_no_reintenta_ni_expone_cuerpo(self):
        abrir = Mock(side_effect=transporte_simulado({'http': 429}))
        with self.assertRaises(ErrorServicio) as ctx:
            solicitar(OPENAI, {}, clave='clave-ficticia', abrir_http=abrir)
        self.assertEqual(str(ctx.exception), 'http_429')
        self.assertEqual(abrir.call_count, 1)

    def test_timeout_directo_y_envuelto(self):
        for error in (TimeoutError('secreto'), URLError(TimeoutError('secreto'))):
            with self.assertRaisesRegex(ErrorServicio, '^timeout$'):
                solicitar(OPENAI, abrir_http=Mock(side_effect=error))

    def test_conexion_sin_exponer_direccion(self):
        with self.assertRaisesRegex(ErrorServicio, '^conexion$'):
            solicitar(OPENAI, abrir_http=Mock(side_effect=URLError('dato privado')))

    def test_cuerpo_acotado(self):
        fuente = Mock()
        fuente.__enter__ = Mock(return_value=fuente)
        fuente.__exit__ = Mock(return_value=False)
        fuente.read.return_value = b' ' * (MAX_BYTES + 1)
        with self.assertRaisesRegex(ErrorServicio, 'demasiado_grande'):
            solicitar(OPENAI, abrir_http=Mock(return_value=fuente))
        fuente.read.assert_called_once_with(MAX_BYTES + 1)

    def test_json_malformado_unicode_y_constantes(self):
        for bruto in (b'<html/>', b'\xff', b'{', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.assertRaisesRegex(ErrorServicio, '^json_invalido$'):
                solicitar(OPENAI, abrir_http=Mock(return_value=BytesIO(bruto)))

    def test_json_no_objeto_y_error_en_200(self):
        for bruto, codigo in ((b'[]', 'contrato_invalido'), (b'{"error":"privado"}', 'error_del_servicio')):
            with self.assertRaisesRegex(ErrorServicio, '^' + codigo + '$'):
                solicitar(OPENAI, abrir_http=Mock(return_value=BytesIO(bruto)))


class Contratos(unittest.TestCase):
    def test_parametros_limitados_y_cpu(self):
        p = peticion_ollama('modelo', 'Hola', 4)
        self.assertFalse(p['stream'])
        self.assertFalse(p['think'])
        self.assertEqual(p['options']['num_gpu'], 0)
        self.assertEqual(p['options']['num_ctx'], 1024)
        for limite in (0, -1, 257, 2.5, True):
            with self.assertRaises(ValueError):
                peticion_ollama('modelo', 'hola', limite)

    def test_prompt_y_modelo_obligatorios(self):
        for modelo, prompt in (('', 'hola'), ('m', ''), ('m', ' '*2), ('m', 'a'*4001)):
            with self.assertRaises(ValueError):
                peticion_ollama(modelo, prompt, 4)

    def test_unidades_velocidad(self):
        r = leer_ollama(respuesta_ollama())
        self.assertEqual(r['tokens_por_segundo'], 10)
        self.assertEqual(r['tokens_salida'], 20)

    def test_duracion_cero_no_divide(self):
        r = leer_ollama({**respuesta_ollama(), 'eval_duration': 0})
        self.assertIsNone(r['tokens_por_segundo'])

    def test_salida_vacia_es_contrato_valido(self):
        r = leer_ollama(respuesta_ollama(''))
        self.assertEqual(r['texto'], '')

    def test_done_falso_y_campos_ausentes(self):
        for cambio in ({'done': False}, {'response': None}, {'done_reason': ''}, {'eval_count': None}):
            with self.assertRaises(ErrorServicio):
                leer_ollama(respuesta_ollama() | cambio)
        with self.assertRaises(ErrorServicio):
            leer_ollama([])

    def test_contadores_y_duraciones_invalidos(self):
        for campo in ('eval_count', 'eval_duration', 'prompt_eval_count', 'load_duration', 'total_duration'):
            for valor in (-1, 0.5, True, float('nan')):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ErrorServicio):
                    leer_ollama(respuesta_ollama() | {campo: valor})

    def test_correcto_truncado_no_aceptado(self):
        r = puntuar({'respuesta': respuesta_ollama('42', 'length')}, {'esperado': '42'})
        self.assertTrue(r['coincide'])
        self.assertFalse(r['aceptada'])

    def test_incorrecto_aunque_finalizado(self):
        r = puntuar({'respuesta': respuesta_ollama('43')}, {'esperado': '42'})
        self.assertTrue(r['finalizada'])
        self.assertFalse(r['aceptada'])

    def test_normalizacion_solo_exterior(self):
        self.assertTrue(puntuar({'respuesta': respuesta_ollama('\n 42 ')}, {'esperado': '42'})['aceptada'])
        for contenido in ('42.', '4 2', 'Respuesta: 42'):
            self.assertFalse(puntuar({'respuesta': respuesta_ollama(contenido)}, {'esperado': '42'})['aceptada'])

    def test_remota_sin_temperatura_y_sin_persistencia(self):
        p = peticion_remota('elegido', 'hola')
        self.assertFalse(p['store'])
        self.assertNotIn('temperature', p)
        self.assertEqual(p['max_output_tokens'], 256)
        for limite in (0, 15, 4097, True):
            with self.assertRaises(ValueError):
                peticion_remota('m', 'hola', limite)

    def test_remota_texto_no_es_primer_item(self):
        self.assertEqual(leer_remota(respuesta_remota())['texto'], '42')

    def test_remota_varios_segmentos(self):
        r = respuesta_remota('cuarenta')
        r['output'][1]['content'].append({'type': 'output_text', 'text': ' y dos'})
        self.assertEqual(leer_remota(r)['texto'], 'cuarenta y dos')

    def test_remota_incompleta_y_fallida(self):
        for estado in ('incomplete', 'failed'):
            self.assertFalse(leer_remota(respuesta_remota(estado=estado))['finalizada'])

    def test_remota_rechazo_no_aceptado(self):
        r = respuesta_remota()
        r['output'][1]['content'].append({'type': 'refusal', 'refusal': 'simulado'})
        self.assertTrue(leer_remota(r)['rechazo'])
        self.assertFalse(leer_remota(r)['finalizada'])

    def test_remota_sin_texto_y_contrato_invalido(self):
        self.assertEqual(leer_remota({'status': 'completed', 'output': []})['texto'], '')
        for r in ({}, {'status': 'running', 'output': []}, {'status': 'completed', 'output': [None]},
                  {'status': 'completed', 'output': [{'type': 'message', 'content': '42'}]}):
            with self.assertRaises(ErrorServicio):
                leer_remota(r)


class Evidencia(unittest.TestCase):
    def setUp(self):
        self.registro = cargar(UNIDAD / 'recursos/local/registro.json')
        self.casos = cargar(CASOS)

    def test_casos_y_orden_alternado(self):
        self.assertEqual(len({c['id'] for c in self.casos}), 4)
        self.assertEqual([l for c, l in plan(self.casos)], [4, 48, 48, 4, 4, 48, 48, 4])

    def test_registro_reproduce_informe(self):
        self.assertEqual(analizar(self.registro), cargar(UNIDAD / 'recursos/local/informe.json'))

    def test_referencia_conteos_y_medianas(self):
        resumen = analizar(self.registro)['resumen']
        self.assertEqual([r['aceptada'] for r in resumen], [2, 4])
        self.assertEqual([r['coincide'] for r in resumen], [3, 4])
        for r in resumen:
            tiempos = sorted(f['pared_s'] for f in self.registro['filas'] if f['limite'] == r['limite'])
            self.assertEqual(r['mediana_pared_s'], (tiempos[1]+tiempos[2])/2)

    def test_error_no_desaparece_del_denominador(self):
        fila = self.registro['filas'][0]
        del fila['respuesta']
        fila['error'] = 'timeout'
        r = analizar(self.registro)['resumen'][0]
        self.assertEqual((r['solicitudes'], r['n_latencias'], r['aceptada']), (4, 3, 1))
        self.assertEqual(r['errores'], {'timeout': 1})

    def test_no_acepta_registro_incompleto(self):
        self.registro['filas'].pop()
        with self.assertRaises(ValueError):
            analizar(self.registro)

    def test_no_acepta_cambio_prompt_condicion_u_orden(self):
        for tipo in ('prompt', 'limite', 'orden'):
            r = deepcopy(self.registro)
            if tipo == 'prompt':
                r['filas'][0]['solicitud']['prompt'] = 'otro'
            elif tipo == 'limite':
                r['filas'][0]['limite'] = 48
            else:
                r['filas'][0], r['filas'][1] = r['filas'][1], r['filas'][0]
            with self.assertRaises(ValueError):
                analizar(r)

    def test_no_acepta_otro_protocolo_o_simulacion(self):
        for campo, valor in (('origen', 'simulado'), ('schema', 2), ('casos_sha256', 'otro'),
                             ('protocolo_sha256', 'otro'), ('inventario_estable', False)):
            with self.assertRaises(ValueError):
                analizar(self.registro | {campo: valor})

    def test_no_acepta_latencia_negativa_o_resultado_ambiguo(self):
        self.registro['filas'][0]['pared_s'] = -1
        with self.assertRaises(ValueError):
            analizar(self.registro)
        self.registro['filas'][0]['pared_s'] = 1
        self.registro['filas'][0]['error'] = 'timeout'
        with self.assertRaises(ValueError):
            analizar(self.registro)

    def test_analisis_y_simulacion_sin_red(self):
        with patch('socket.socket', side_effect=AssertionError('No debe abrir sockets')):
            analizar(self.registro)
            r = ejecutar_simulaciones()
        self.assertEqual(sum(f['aceptada'] for f in r['filas']), 2)
        self.assertEqual(r, cargar(UNIDAD / 'recursos/simulacion/informe.json'))

    def test_inventario_no_descarga_ni_acepta_cloud(self):
        cliente = Mock(side_effect=[{'version':'v'}, {'models':[]}])
        with self.assertRaises(ValueError):
            inventario('m', cliente)
        self.assertEqual(cliente.call_count, 2)
        cliente = Mock(side_effect=[{'version':'v'}, {'models':[{'name':'m','size':1}]}, {'remote_host':'cloud'}])
        with self.assertRaises(ValueError):
            inventario('m', cliente)

    def test_medicion_conserva_fallo_y_no_reintenta(self):
        cliente = Mock(side_effect=ErrorServicio('timeout'))
        r = medir({}, 7, cliente)
        self.assertEqual(r['error'], 'timeout')
        self.assertGreaterEqual(r['pared_s'], 0)
        cliente.assert_called_once_with(OLLAMA + '/api/generate', {}, timeout=7)

    def test_orquestacion_persiste_fallos(self):
        def cliente(url, cuerpo=None, **kw):
            if url.endswith('/api/generate'):
                raise ErrorServicio('timeout')
            return {'models': []}
        with tempfile.TemporaryDirectory() as carpeta, patch('evaluacion.inventario', return_value={'digest':'x'}):
            with patch('builtins.print'):
                r = ejecutar_real('m', carpeta, cliente=cliente)
            self.assertEqual(cargar(Path(carpeta)/'registro.json'), r)
            self.assertEqual([s['solicitudes'] for s in analizar(r)['resumen']], [4, 4])
            self.assertTrue(all('error' in f for f in r['filas']))

    def test_cambio_modelo_no_publica_exito(self):
        cliente = Mock(return_value={'models': []})
        with tempfile.TemporaryDirectory() as carpeta, patch('evaluacion.inventario', side_effect=[{'digest':'a'}, {'digest':'b'}]):
            with patch('builtins.print'), self.assertRaises(ValueError):
                ejecutar_real('m', carpeta, cliente=cliente)
            r = cargar(Path(carpeta)/'registro.json')
            self.assertNotIn('inventario_estable', r)
            self.assertEqual(len(r['filas']), 8)

    def test_guardado_no_admite_nan(self):
        with tempfile.TemporaryDirectory() as carpeta, self.assertRaises(ValueError):
            guardar(Path(carpeta)/'informe.json', {'x': float('nan')})

    def test_cli_remota_sin_clave_falla_antes_de_red(self):
        import os
        env = {k:v for k,v in os.environ.items() if k not in ('OPENAI_MODEL', 'OPENAI_API_KEY')}
        r = subprocess.run([sys.executable, str(EJEMPLOS/'probar_api_remota.py')], env=env,
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 2)
        self.assertIn('no se ha enviado ninguna petición', r.stderr)


if __name__ == '__main__':
    unittest.main()

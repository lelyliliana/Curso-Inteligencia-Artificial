"""Contratos, permisos, bucle, protocolo y recarga; nunca usa Ollama real."""

import asyncio
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock
from urllib import error

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
from herramientas import (CATALOGO, Sesion, cargar, evaluar, final_valido, flujo_fijo,
                          json_estricto, validar_resultado)
from agente import (ErrorServicio, MODELO, URL, chat, ejecutar_agente, leer_respuesta,
                    reproducir, solicitud)
from experimento import analizar, casos_fase, huellas
from servidor_mcp import MAX_LINEA, VERSION, Servidor


def respuesta(contenido="", nombre=None, argumentos=None):
    m = {"role": "assistant", "content": contenido}
    if nombre:
        m["tool_calls"] = [{"function": {"name": nombre, "arguments": argumentos or {"sensor": "S-11"}}}]
    return {"model": MODELO, "done": True, "done_reason": "stop", "message": m,
            "prompt_eval_count": 50, "eval_count": 20, "total_duration": 100,
            "load_duration": 0, "eval_duration": 90}


def rpc(id_, metodo, params=None):
    return {"jsonrpc": "2.0", "id": id_, "method": metodo, "params": {} if params is None else params}


def servidor_listo():
    s = Servidor()
    s.responder(rpc(1, "initialize", {"protocolVersion": VERSION, "capabilities": {},
                                    "clientInfo": {"name": "prueba", "version": "1"}}))
    s.responder({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return s


class HerramientasTest(unittest.TestCase):
    def test_media_manual_y_negativos(self):
        for sensor, media, n in (("S-11", 20, 3), ("S-23", 1, 4)):
            s = Sesion()
            self.assertTrue(s.llamar("consultar_sensor", {"sensor": sensor})["ok"])
            self.assertEqual(s.llamar("calcular_media", {"sensor": sensor})["datos"],
                             {"sensor": sensor, "media_c": media, "cantidad": n})

    def test_escritura_denegada_sin_mutacion(self):
        s = Sesion()
        antes = deepcopy(s.datos)
        self.assertEqual(s.llamar("cambiar_umbral", {"sensor": "S-11", "umbral_c": 99})["codigo"], "denegado")
        self.assertEqual(s.datos, antes)
        self.assertEqual(s.eventos[0]["etapa"], "autorizacion")

    def test_autorizacion_antes_de_buscar_existencia(self):
        s = Sesion()
        for id_ in ("S-14", "S-88"):
            r = s.llamar("consultar_sensor", {"sensor": id_})
            self.assertEqual(r, {"ok": False, "codigo": "denegado", "datos": {}})
        self.assertFalse(s.consultas)

    def test_recurso_ausente_permitido(self):
        self.assertEqual(Sesion().llamar("consultar_sensor", {"sensor": "S-90"})["codigo"], "no_disponible")

    def test_argumentos_hostiles_y_tipos(self):
        for args in (None, [], {"sensor": True}, {"sensor": "../../etc"}, {"sensor": "S-11\n"},
                     {"sensor": "S-11", "permisos": "todos"}, {}, {"sensor": "S-１１"}):
            with self.subTest(args=args):
                self.assertEqual(Sesion().llamar("consultar_sensor", args)["codigo"], "argumentos_invalidos")

    def test_desconocida_no_ejecuta(self):
        for nombre in ("eval", "os.system", [], None):
            self.assertEqual(Sesion().llamar(nombre, {})["codigo"], "desconocida")

    def test_media_exige_consulta_del_mismo_sensor(self):
        s = Sesion()
        s.llamar("consultar_sensor", {"sensor": "S-11"})
        self.assertEqual(s.llamar("calcular_media", {"sensor": "S-13"})["codigo"], "sin_consulta")
        self.assertEqual(Sesion().llamar("calcular_media", {"sensor": "S-11"})["codigo"], "sin_consulta")

    def test_resultado_no_permite_mutar_cache(self):
        s = Sesion()
        r = s.llamar("consultar_sensor", {"sensor": "S-11"})
        r["datos"]["lecturas_c"][0] = 100
        self.assertEqual(s.llamar("calcular_media", {"sensor": "S-11"})["datos"]["media_c"], 20)
        self.assertEqual(s.eventos[0]["resultado"]["datos"]["lecturas_c"], [18, 20, 22])

    def test_repeticion_y_cupo_incluyen_errores(self):
        s = Sesion(max_llamadas=2)
        s.llamar("consultar_sensor", {"sensor": "S-11"})
        self.assertEqual(s.llamar("consultar_sensor", {"sensor": "S-11"})["codigo"], "repetida")
        self.assertEqual(s.llamar("calcular_media", {"sensor": "S-11"})["codigo"], "limite_llamadas")

    def test_reloj_y_configuracion(self):
        reloj = [0]
        s = Sesion(segundos=1, reloj=lambda: reloj[0])
        reloj[0] = 1
        self.assertEqual(s.llamar("consultar_sensor", {"sensor": "S-11"})["codigo"], "limite_tiempo")
        for opciones in ({"max_llamadas": True}, {"max_llamadas": 0}, {"segundos": float("nan")}):
            with self.assertRaises(ValueError):
                Sesion(**opciones)

    def test_datos_invalidos_no_entran_en_cache(self):
        datos = cargar(UNIDAD / "datos/sensores.json")
        for valores in ([], [True], [float("inf")], [101], list(range(33))):
            datos["sensores"]["S-11"]["lecturas_c"] = valores
            s = Sesion(datos=datos)
            self.assertEqual(s.llamar("consultar_sensor", {"sensor": "S-11"})["codigo"], "datos_invalidos")
            self.assertFalse(s.consultas)

    def test_notas_no_otorgan_permisos(self):
        s = Sesion()
        self.assertIn("cambiar_umbral", s.llamar("consultar_sensor", {"sensor": "S-23"})["datos"]["nota"])
        self.assertEqual(s.llamar("cambiar_umbral", {"sensor": "S-23", "umbral_c": 99})["codigo"], "denegado")
        self.assertEqual(s.llamar("calcular_media", {"sensor": "S-23"})["datos"]["media_c"], 1)


class EvaluacionTest(unittest.TestCase):
    def test_forma_final_estricta(self):
        base = {"estado": "ok", "sensor": "S-11", "media_c": 20}
        self.assertTrue(final_valido(base))
        for cambio in ({"media_c": True}, {"media_c": float("nan")}, {"media_c": "20"},
                       {"estado": "denegado"}, {"sensor": "S-11\n"}, {"extra": 1}):
            self.assertFalse(final_valido(base | cambio))

    def test_acertar_sin_herramienta_no_basta(self):
        esperado = {"estado": "ok", "sensor": "S-11", "media_c": 20}
        r = evaluar(esperado, [], esperado, "final")
        self.assertTrue(r["coincide"])
        self.assertFalse(r["apoyo"])
        self.assertFalse(r["aceptada"])

    def test_otro_sensor_y_truncamiento_no_bastan(self):
        t = flujo_fijo("Media de S-11")
        otro = {"estado": "ok", "sensor": "S-13", "media_c": 20}
        self.assertFalse(evaluar(otro, t["eventos"], otro, "final")["aceptada"])
        self.assertFalse(evaluar(t["final"], t["eventos"], t["final"], "limite_turnos")["aceptada"])

    def test_denegacion_requiere_evidencia(self):
        t = flujo_fijo("Media de S-14")
        self.assertTrue(evaluar(t["final"], t["eventos"], t["final"], "final")["aceptada"])
        self.assertFalse(evaluar(t["final"], [], t["final"], "final")["aceptada"])

    def test_flujo_fijo_todos_los_casos(self):
        for c in cargar(UNIDAD / "datos/casos.json"):
            t = flujo_fijo(c["pregunta"])
            self.assertTrue(evaluar(t["final"], t["eventos"], c["esperado"], t["parada"])["aceptada"])
        for p in ("Media sin ID", "S-11 y S-13"):
            with self.assertRaises(ValueError):
                flujo_fijo(p)

    def test_particiones_familias_e_identificadores(self):
        dev, cierre = casos_fase("desarrollo"), casos_fase("cierre")
        self.assertEqual((len(dev), len(cierre)), (8, 8))
        for clave in ("familia", "id"):
            self.assertFalse({c[clave] for c in dev} & {c[clave] for c in cierre})
        self.assertFalse({c["esperado"]["sensor"] for c in dev} & {c["esperado"]["sensor"] for c in cierre})
        for grupo in (dev, cierre):
            for tipo in ("normal", "ausente", "permiso", "inyeccion"):
                self.assertEqual(sum(c["tipo"] == tipo for c in grupo), 2)

    def test_json_rechaza_claves_duplicadas_y_constantes(self):
        for s in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                json_estricto(s)

    def test_resultados_tipados(self):
        for r in ({"ok": True, "codigo": "denegado", "datos": {}},
                  {"ok": False, "codigo": "denegado", "datos": {"lecturas": [1]}},
                  {"ok": True, "codigo": "ok", "datos": {"sensor": "S-11", "media_c": True, "cantidad": 3}}):
            with self.assertRaises(ValueError):
                validar_resultado("calcular_media", r)


class AgenteTest(unittest.TestCase):
    def test_secuencia_y_recarga_sintetica(self):
        respuestas = [respuesta(nombre="consultar_sensor"), respuesta(nombre="calcular_media"),
                      respuesta('{"estado":"ok","sensor":"S-11","media_c":20}')]
        cliente = Mock(side_effect=respuestas)
        t = ejecutar_agente("Media de S-11", cliente=cliente)
        self.assertEqual(t["parada"], "final")
        self.assertEqual(len(t["eventos"]), 2)
        self.assertEqual(reproducir("Media de S-11", t)["final"], t["final"])
        ultimo = cliente.call_args_list[-1].args[0]["messages"]
        self.assertEqual([m["role"] for m in ultimo], ["system", "user", "assistant", "tool", "assistant", "tool"])
        self.assertEqual(ultimo[-1]["tool_name"], "calcular_media")

    def test_no_filtra_referencias(self):
        cliente = Mock(return_value=respuesta('{}'))
        ejecutar_agente("Media de S-11", cliente=cliente)
        cuerpo = cliente.call_args.args[0]
        self.assertEqual(cuerpo["messages"][1], {"role": "user", "content": "Media de S-11"})
        self.assertEqual([t["function"]["name"] for t in cuerpo["tools"]], [t["name"] for t in CATALOGO])
        self.assertNotIn("esperado", json.dumps(cuerpo))
        self.assertFalse(cuerpo["think"])

    def test_repeticion_detiene_bucle(self):
        cliente = Mock(return_value=respuesta(nombre="consultar_sensor"))
        t = ejecutar_agente("S-11", cliente=cliente)
        self.assertEqual(t["parada"], "repetida")
        self.assertEqual(cliente.call_count, 2)

    def test_maximo_cuatro_turnos(self):
        cliente = Mock(side_effect=[respuesta(nombre="desconocida" + str(i)) for i in range(4)])
        t = ejecutar_agente("S-11", cliente=cliente)
        self.assertEqual(t["parada"], "limite_turnos")
        self.assertEqual(cliente.call_count, 4)
        self.assertFalse(any(e["resultado"]["ok"] for e in t["eventos"]))

    def test_tiempo_expirado_no_ejecuta_propuesta(self):
        reloj = [0]
        def cliente(cuerpo, timeout):
            self.assertLessEqual(timeout, 45)
            reloj[0] = 121
            return respuesta(nombre="consultar_sensor")
        t = ejecutar_agente("S-11", cliente=cliente, reloj=lambda: reloj[0])
        self.assertEqual(t["parada"], "limite_tiempo")
        self.assertEqual(t["eventos"], [])
        self.assertEqual(reproducir("S-11", t)["parada"], "limite_tiempo")

    def test_http_error_sin_reintento(self):
        cliente = Mock(side_effect=ErrorServicio("timeout"))
        t = ejecutar_agente("S-11", cliente=cliente)
        self.assertEqual(t["parada"], "timeout")
        self.assertEqual(cliente.call_count, 1)
        self.assertEqual(t["llamadas"][0]["error"], "timeout")

    def test_truncada_no_ejecuta(self):
        r = respuesta(nombre="consultar_sensor")
        r["done_reason"] = "length"
        t = ejecutar_agente("S-11", cliente=Mock(return_value=r))
        self.assertEqual(t["parada"], "salida_truncada")
        self.assertFalse(t["eventos"])

    def test_paralelismo_se_rechaza_completo(self):
        r = respuesta(nombre="consultar_sensor")
        r["message"]["tool_calls"] *= 2
        t = ejecutar_agente("S-11", cliente=Mock(return_value=r))
        self.assertEqual(t["parada"], "paralelismo_no_soportado")
        self.assertFalse(t["eventos"])

    def test_contratos_respuesta_y_contexto(self):
        for cambio, codigo in (({"done": False}, "contrato_invalido"),
                               ({"model": "otro"}, "contrato_invalido"),
                               ({"prompt_eval_count": True}, "contrato_invalido"),
                               ({"prompt_eval_count": 4000}, "limite_contexto")):
            with self.assertRaises(ErrorServicio) as e:
                leer_respuesta(respuesta() | cambio)
            self.assertEqual(e.exception.codigo, codigo)
        with self.assertRaises(ErrorServicio):
            solicitud([{"role": "user", "content": "x" * 16001}])

    def test_llamada_invalida_y_final_invalido(self):
        r = respuesta(nombre="consultar_sensor")
        r["message"]["tool_calls"][0]["function"]["arguments"] = "{}"
        self.assertEqual(ejecutar_agente("S-11", cliente=Mock(return_value=r))["parada"], "llamada_invalida")
        self.assertEqual(ejecutar_agente("S-11", cliente=Mock(return_value=respuesta("hecho")))["parada"], "final_invalido")

    def test_recarga_detecta_alteraciones(self):
        t = ejecutar_agente("S-11", cliente=Mock(return_value=respuesta('{}')))
        for campo in ("final", "eventos", "parada"):
            copia = deepcopy(t)
            copia[campo] = "alterado"
            with self.assertRaises(ValueError):
                reproducir("S-11", copia)
        t["llamadas"][0]["solicitud"]["messages"][1]["content"] = "S-13"
        with self.assertRaises(ValueError):
            reproducir("S-11", t)


class HttpTest(unittest.TestCase):
    def test_destino_fijo_sin_claves(self):
        abrir = Mock(return_value=io.BytesIO(b'{"dato": 1}'))
        self.assertEqual(chat({}, abrir_http=abrir), {"dato": 1})
        req = abrir.call_args.args[0]
        self.assertEqual(req.full_url, URL)
        self.assertNotIn("Authorization", dict(req.header_items()))

    def test_limite_bytes_y_json_invalido(self):
        for bruto, codigo in ((b"x" * 1_048_577, "respuesta_demasiado_grande"),
                              (b'\xff', "json_invalido"), (b'{"x": NaN}', "json_invalido"),
                              (b'[]', "contrato_invalido"), (b'{"error":"detalle"}', "contrato_invalido")):
            with self.assertRaises(ErrorServicio) as e:
                chat({}, abrir_http=Mock(return_value=io.BytesIO(bruto)))
            self.assertEqual(e.exception.codigo, codigo)

    def test_timeout_conexion_y_http_sin_cuerpo(self):
        for exc, codigo in ((TimeoutError(), "timeout"), (error.URLError("detalle"), "conexion"),
                            (error.HTTPError(URL, 503, "secreto", {}, io.BytesIO(b"secreto")), "http_503")):
            with self.assertRaises(ErrorServicio) as e:
                chat({}, abrir_http=Mock(side_effect=exc))
            self.assertEqual(str(e.exception), codigo)

    def test_timeout_fuera_dominio(self):
        for timeout in (0, 46, True, float("inf")):
            with self.assertRaises(ValueError):
                chat({}, timeout=timeout)


class MCPTest(unittest.TestCase):
    def test_handshake_antes_de_operaciones(self):
        s = Servidor()
        self.assertEqual(s.responder(rpc(1, "tools/list"))["error"]["code"], -32002)
        self.assertEqual(servidor_listo().estado, "listo")

    def test_version_negociada_y_capacidades(self):
        s = Servidor()
        r = s.responder(rpc(1, "initialize", {"protocolVersion": "otra", "capabilities": {},
                                             "clientInfo": {"name": "prueba", "version": "1"}}))
        self.assertEqual(r["result"]["protocolVersion"], VERSION)
        self.assertEqual(r["result"]["capabilities"], {"tools": {"listChanged": False}})

    def test_notificaciones_sin_respuesta(self):
        for metodo in ("notifications/initialized", "notifications/ignorada"):
            self.assertIsNone(Servidor().responder({"jsonrpc": "2.0", "method": metodo}))

    def test_catalogo_esquemas_y_anotaciones(self):
        r = servidor_listo().responder(rpc(2, "tools/list"))["result"]["tools"]
        self.assertEqual(r, CATALOGO)
        self.assertEqual(r, cargar(UNIDAD / "datos/esquemas.json")["herramientas_mcp"])
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in r))
        self.assertTrue(all(t["inputSchema"]["additionalProperties"] is False for t in r))

    def test_tool_error_diferente_rpc_error(self):
        s = servidor_listo()
        r = s.responder(rpc(2, "tools/call", {"name": "consultar_sensor", "arguments": {"sensor": "S-14"}}))
        self.assertTrue(r["result"]["isError"])
        self.assertNotIn("error", r)
        r = s.responder(rpc(3, "tools/call", {"name": "shell", "arguments": {}}))
        self.assertEqual(r["error"]["code"], -32602)
        self.assertNotIn("result", r)

    def test_argumentos_incorrectos_como_error_herramienta(self):
        r = servidor_listo().responder(rpc(2, "tools/call", {"name": "consultar_sensor", "arguments": {"sensor": "../x"}}))
        self.assertEqual(r["result"]["structuredContent"]["codigo"], "argumentos_invalidos")
        self.assertTrue(r["result"]["isError"])

    def test_estructura_call_incorrecta(self):
        r = servidor_listo().responder(rpc(2, "tools/call", {"name": "consultar_sensor", "arguments": []}))
        self.assertEqual(r["error"]["code"], -32602)

    def test_metodo_desconocido_e_ids(self):
        s = servidor_listo()
        self.assertEqual(s.responder(rpc(2, "resources/list"))["error"]["code"], -32601)
        self.assertEqual(s.responder(rpc(2, "ping"))["error"]["code"], -32600)
        self.assertEqual(s.responder(rpc(True, "ping"))["error"]["code"], -32600)

    def test_subproceso_parse_error_y_limite_linea(self):
        programa = str(UNIDAD / "ejemplos/servidor_mcp.py")
        for entrada, codigo in ((b'{mal}\n', -32700), (b'x' * (MAX_LINEA + 1), -32600),
                                (b'[]\n', -32600)):
            proc = subprocess.run([sys.executable, programa], input=entrada, capture_output=True, timeout=5, check=True)
            self.assertEqual(json.loads(proc.stdout)["error"]["code"], codigo)
            self.assertEqual(proc.stderr, b"")

    def test_intercambio_real_y_captura_publicada(self):
        spec = importlib.util.spec_from_file_location("cliente_mcp", UNIDAD / "ejemplos/01_probar_mcp.py")
        cliente = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cliente)
        traza = asyncio.run(cliente.intercambio())
        self.assertEqual(traza, cargar(UNIDAD / "recursos/mcp/intercambio.json"))
        self.assertEqual(len(traza["traza"]), 17)


class CapturasTest(unittest.TestCase):
    def test_reconstruccion_y_totales_de_ambas_fases(self):
        for fase in ("desarrollo", "cierre"):
            r = cargar(UNIDAD / f"recursos/{fase}/registro.json")
            informe = analizar(r)
            self.assertEqual(informe, cargar(UNIDAD / f"recursos/{fase}/informe.json"))
            self.assertEqual(informe["resumen"][0]["aceptada"], 8)
            self.assertEqual(informe["resumen"][1]["tareas"], 8)

    def test_huellas_y_ausencia_de_casos(self):
        r = cargar(UNIDAD / "recursos/desarrollo/registro.json")
        self.assertEqual(r["huellas"], huellas())
        for clave, valor in (("huellas", {}), ("tareas", r["tareas"][:-1]), ("inventario_estable", False)):
            with self.assertRaises(ValueError):
                analizar(r | {clave: valor})

    def test_cierre_misma_configuracion(self):
        from herramientas import huella
        dev = cargar(UNIDAD / "recursos/desarrollo/registro.json")
        cierre = cargar(UNIDAD / "recursos/cierre/registro.json")
        self.assertEqual(dev["huellas"], cierre["huellas"])
        self.assertEqual(dev["inventario"], cierre["inventario"])
        self.assertEqual(cierre["desarrollo_sha256"], huella(UNIDAD / "recursos/desarrollo/registro.json"))

    def test_auditoria_separada_del_modelo(self):
        r = cargar(UNIDAD / "recursos/auditoria/auditoria.json")
        self.assertEqual(r["origen"], "propuestas_artificiales_no_generadas_por_modelo")
        self.assertEqual(len(r["escenarios"]), 11)
        for escenario in r["escenarios"]:
            self.assertFalse(any(e["nombre"] == "cambiar_umbral" and e["resultado"]["ok"] for e in escenario["eventos"]))


if __name__ == "__main__":
    unittest.main()

"""Comprobaciones de admisión, métricas, privacidad y recuperación."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
import hashlib
import http.client
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import socket
import sys
import threading
import unittest
from unittest.mock import patch
from contextlib import redirect_stderr

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import laboratorio as lab
from observacion import LIMITES_MS, Observador
from operacion import Config, ErrorEntrada, SHA_MODELO, Servicio, ServicioOperado, categoria, temporal


class ObservacionTest(unittest.TestCase):
    def obs(self, **kwargs):
        return Observador(SHA_MODELO, **kwargs)

    def terminar(self, obs, n, status=200, ms=10, ruta="prediccion", metodo="POST"):
        obs.iniciar()
        obs.terminar(str(n), ruta, metodo, status, "ninguno", ms)

    def test_vacio_no_es_cero_errores(self):
        r = self.obs().resumen()["prediccion_POST"]
        self.assertIsNone(r["tasa_5xx"])
        self.assertIsNone(r["media_ms"])
        self.assertIsNone(r["fraccion_buenas"])

    def test_denominador_excluye_salud(self):
        o = self.obs()
        self.terminar(o, 0, 500)
        for i in range(10):
            self.terminar(o, i+1, ruta="live", metodo="GET")
        self.assertEqual(o.resumen()["terminadas"], 11)
        self.assertEqual(o.resumen()["prediccion_POST"]["tasa_5xx"], 1)

    def test_4xx_no_es_5xx(self):
        o = self.obs()
        self.terminar(o, 0, 422)
        r = o.resumen()["prediccion_POST"]
        self.assertEqual((r["rechazos_4xx"], r["fallos_5xx"], r["exitos_2xx"]), (1,0,0))
        self.assertEqual(r["fraccion_buenas"], 0)

    def test_rapida_con_error_no_es_buena(self):
        o = self.obs(objetivo_ms=20)
        self.terminar(o, 0, 503, 1)
        self.terminar(o, 1, 200, 21)
        self.terminar(o, 2, 200, 20)
        self.assertEqual(o.resumen()["prediccion_POST"]["fraccion_buenas"], 1/3)

    def test_histograma_acumulado_inclusivo(self):
        o = self.obs()
        for i, ms in enumerate((1, 5, 7, 2500)):
            self.terminar(o, i, ms=ms)
        h = o.resumen()["prediccion_POST"]["histograma_acumulado"]
        self.assertEqual([x["n"] for x in h], [1,2,3,3,3,3,4])

    def test_media_usa_todas_predicciones(self):
        o = self.obs()
        self.terminar(o, 0, 200, 10)
        self.terminar(o, 1, 500, 90)
        self.assertEqual(o.resumen()["prediccion_POST"]["media_ms"], 50)

    def test_historial_acotado_contadores_acumulados(self):
        o = self.obs(capacidad=2)
        for i in range(5):
            self.terminar(o, i)
        self.assertEqual([e["solicitud_id"] for e in o.historial()], ["3", "4"])
        self.assertEqual(o.resumen()["terminadas"], 5)

    def test_historial_y_resumen_son_copias(self):
        o = self.obs()
        self.terminar(o, 0)
        o.historial()[0]["status"] = 500
        o.resumen()["por_status"]["200"] = 99
        self.assertEqual(o.historial()[0]["status"], 200)
        self.assertEqual(o.resumen()["por_status"]["200"], 1)

    def test_concurrencia_contadores(self):
        o = self.obs()
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: self.terminar(o, i), range(100)))
        self.assertEqual((o.resumen()["terminadas"], o.resumen()["en_curso"]), (100,0))

    def test_abandono_y_rechazo_conexion_separados(self):
        o = self.obs()
        o.iniciar(); o.abandonar(); o.rechazar_conexion()
        r = o.resumen()
        self.assertEqual(r["abandonadas_sin_respuesta"], 1)
        self.assertEqual(r["conexiones_rechazadas_antes_de_HTTP"], 1)
        self.assertEqual(r["prediccion_POST"]["total"], 0)

    def test_etiquetas_acotadas(self):
        o = self.obs()
        with self.assertRaises(ValueError):
            o.terminar("1", "/ruta-privada", "POST", 200, "ninguno", 1)
        self.assertEqual(categoria("/api/predecir?texto=privado"), "otros")

    def test_valores_invalidos(self):
        for ms in (-1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                self.obs().terminar("1", "prediccion", "POST", 200, "ninguno", ms)
        for kwargs in ({"capacidad":0}, {"capacidad":True}, {"objetivo_ms":0}, {"objetivo_ms":math.nan}):
            with self.assertRaises(ValueError):
                self.obs(**kwargs)

    def test_salida_estructurada(self):
        s = io.StringIO()
        with redirect_stderr(s):
            self.terminar(self.obs(emitir=True), 0)
        r = json.loads(s.getvalue())
        self.assertEqual(set(r), {"evento","solicitud_id","ruta","metodo","status","codigo","duracion_ms","modelo_sha256"})


class AdmisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Servicio()

    def test_config_inmutable(self):
        with self.assertRaises(FrozenInstanceError):
            Config().conexiones = 8

    def test_config_limites(self):
        for d in ({"conexiones":0},{"conexiones":33},{"conexiones":True},{"inferencias":2},
                  {"historial":0},{"espera_socket_s":-1},{"objetivo_ms":math.inf}):
            with self.assertRaises(ValueError):
                Config(**d)

    def test_contrato_igual_a_u32(self):
        o = ServicioOperado(self.base)
        self.assertEqual(o.predecir(lab.entrada()), self.base.predecir(lab.entrada()))

    def test_rechazo_no_degrada(self):
        o = ServicioOperado(self.base)
        with self.assertRaises(ErrorEntrada):
            o.predecir({})
        self.assertEqual(o.disponibilidad(), {"estado":"listo","ocupado":False})

    def test_error_libera_y_degrada(self):
        o = ServicioOperado(self.base)
        with patch.object(self.base, "predecir", side_effect=RuntimeError("fallo")), self.assertRaises(RuntimeError):
            o.predecir(lab.entrada())
        self.assertEqual(o.disponibilidad(), {"estado":"degradado","ocupado":False})

    def test_mantenimiento_no_invoca_modelo(self):
        o = ServicioOperado(self.base)
        o.establecer_estado("mantenimiento")
        with patch.object(self.base, "predecir", side_effect=AssertionError("No inferir")), self.assertRaises(ErrorEntrada) as c:
            o.predecir(lab.entrada())
        self.assertEqual((c.exception.status,c.exception.codigo),(503,"no_disponible"))

    def test_estado_invalido(self):
        with self.assertRaises(ValueError):
            ServicioOperado(self.base).establecer_estado("estado arbitrario")

    def test_no_hay_cola_y_drena_admitida(self):
        b = lab.BaseControlada(self.base)
        b.preparar_bloqueo()
        o = ServicioOperado(b)
        with ThreadPoolExecutor(max_workers=1) as pool:
            pendiente = pool.submit(o.predecir, lab.entrada())
            try:
                self.assertTrue(b.entrada.wait(2))
                with self.assertRaises(ErrorEntrada) as c:
                    o.predecir(lab.entrada())
                self.assertEqual(c.exception.codigo,"ocupado")
                o.establecer_estado("mantenimiento")
            finally:
                b.liberar.set()
            self.assertEqual(pendiente.result(timeout=3)["estado"], "ok")
        self.assertFalse(o.disponibilidad()["ocupado"])
        self.assertEqual(o.disponibilidad()["estado"], "mantenimiento")


class HTTPTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Servicio()
        cls.contexto = temporal(cls.base, Config(espera_socket_s=.15))
        cls.s = cls.contexto.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.contexto.__exit__(None,None,None)

    def test_ids_generados_no_reflejados(self):
        r = lab.pedir(self.s.server_port,obj=lab.entrada(),cabeceras={"X-Request-ID":"mi-secreto"})
        self.assertRegex(r["solicitud_id"], r"^[a-f0-9]{32}$")
        self.assertEqual(self.s.observador.historial()[-1]["solicitud_id"], r["solicitud_id"])
        self.assertNotIn("mi-secreto", json.dumps(self.s.observador.historial()))

    def test_ids_distintos(self):
        ids = [lab.pedir(self.s.server_port,"/live",metodo="GET")["solicitud_id"] for _ in range(3)]
        self.assertEqual(len(set(ids)),3)

    def test_live_ready_mantenimiento(self):
        self.s.servicio.establecer_estado("mantenimiento")
        try:
            self.assertEqual(lab.pedir(self.s.server_port,"/live",metodo="GET")["status"],200)
            self.assertEqual(lab.pedir(self.s.server_port,"/ready",metodo="GET")["status"],503)
            self.assertEqual(lab.pedir(self.s.server_port,"/health",metodo="GET")["status"],503)
        finally:
            self.s.servicio.establecer_estado("listo")

    def test_retry_after_en_rechazo(self):
        self.s.servicio.establecer_estado("mantenimiento")
        try:
            r=lab.pedir(self.s.server_port,obj=lab.entrada())
        finally:
            self.s.servicio.establecer_estado("listo")
        self.assertEqual((r["status"],r["retry_after"]),(503,"1"))
        self.assertNotIn("resultado",r["respuesta"])

    def test_snapshot_excluye_su_respuesta(self):
        r=lab.pedir(self.s.server_port,"/metricas",metodo="GET")["respuesta"]
        despues=self.s.observador.resumen()
        self.assertEqual(despues["terminadas"],r["terminadas"]+1)
        self.assertEqual(r["en_curso"],1)

    def test_origen_y_rutas_no_ampliados(self):
        for ruta in ("/live","/ready","/metricas"):
            self.assertEqual(lab.pedir(self.s.server_port,ruta,metodo="GET",cabeceras={"Origin":"https://ajeno.invalid"})["status"],403)
        self.assertEqual(lab.pedir(self.s.server_port,"/admin/estado",obj={"estado":"listo"})["status"],404)

    def test_metodo_de_sondas(self):
        self.assertEqual(lab.pedir(self.s.server_port,"/ready",obj={})["status"],405)

    def test_privacidad_entrada_ruta_y_excepcion(self):
        lab.pedir(self.s.server_port,obj={"texto":"dato-privado"})
        lab.pedir(self.s.server_port,"/dato-privado?secreto=1",metodo="GET")
        with patch.object(self.base,"predecir",side_effect=RuntimeError("dato-privado")):
            r=lab.pedir(self.s.server_port,obj=lab.entrada())
        self.s.servicio.establecer_estado("listo")
        self.assertEqual(r["status"],500)
        self.assertNotIn("dato-privado",json.dumps(self.s.observador.historial()))
        self.assertNotIn("dato-privado",json.dumps(r))

    def test_timeout_cuerpo_408(self):
        with socket.create_connection(("127.0.0.1",self.s.server_port),timeout=2) as c:
            c.sendall(f"POST /api/predecir HTTP/1.1\r\nHost: 127.0.0.1:{self.s.server_port}\r\nContent-Type: application/json\r\nContent-Length: 9\r\n\r\n{{".encode())
            datos=b""
            while bloque:=c.recv(4096):
                datos+=bloque
        self.assertTrue(datos.startswith(b"HTTP/1.0 408"))
        self.assertIn(b"lectura_agotada",datos)

    def test_socket_sin_cabecera_libera_cupo(self):
        with temporal(self.base,Config(conexiones=1,espera_socket_s=.1)) as s:
            with socket.create_connection(("127.0.0.1",s.server_port),timeout=2) as c:
                c.sendall(b"GET /")
                self.assertEqual(c.recv(4096),b"")
            lab.esperar(lambda:s.permisos._value==1)
            self.assertEqual(lab.pedir(s.server_port,"/live",metodo="GET")["status"],200)

    def test_archivos_ui_iguales(self):
        c=http.client.HTTPConnection("127.0.0.1",self.s.server_port,timeout=2)
        try:
            c.request("GET","/app.js")
            r=c.getresponse()
            self.assertEqual(r.read(),lab.anterior.ESTATICOS["/app.js"][0].read_bytes())
        finally:
            c.close()


class EvidenciaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observacion=lab.observar()
        cls.fallos=lab.fallos()

    def test_ocho_respuestas_correlacionadas(self):
        r=self.observacion
        self.assertEqual(len(r["casos"]),8)
        self.assertEqual({c["solicitud_id"] for c in r["casos"]},{e["solicitud_id"] for e in r["eventos"]})

    def test_observacion_denominadores(self):
        p=self.observacion["resumen"]["prediccion_POST"]
        self.assertEqual((p["total"],p["exitos_2xx"],p["rechazos_4xx"],p["fallos_5xx"]),(4,2,2,0))

    def test_saturacion_sin_bloquear_sondas(self):
        c={x["caso"]:x for x in self.fallos["casos"]}
        self.assertEqual(c["saturacion_inferencia"]["status"],503)
        self.assertEqual(c["ready_ocupado"]["respuesta"],{"version":"1","estado":"listo","ocupado":True})
        self.assertEqual(c["live_ocupado"]["status"],200)

    def test_degradacion_y_recuperacion(self):
        c={x["caso"]:x for x in self.fallos["casos"]}
        self.assertEqual([c[n]["status"] for n in ("fallo_inyectado","ready_degradado","live_degradado","rechazo_degradado","recuperacion_fallo")],[500,503,200,503,200])

    def test_timeout_cliente_no_cancela(self):
        r=self.fallos
        self.assertTrue(r["timeout_cliente"]["servidor_seguia_ocupado"])
        recibidos={x["solicitud_id"] for x in r["casos"]}
        extras=[e for e in r["eventos"] if e["solicitud_id"] not in recibidos]
        self.assertEqual(len(extras),1)
        self.assertEqual(extras[0]["status"],200)

    def test_conexiones_fuera_del_denominador(self):
        r=self.fallos["saturacion_conexiones"]
        self.assertTrue(r["respuesta_sin_solicitud_HTTP"].startswith("HTTP/1.0 503"))
        self.assertNotIn("X-Request-ID",r["respuesta_sin_solicitud_HTTP"])
        self.assertEqual(r["resumen"]["conexiones_rechazadas_antes_de_HTTP"],1)
        self.assertEqual(r["resumen"]["prediccion_POST"]["total"],1)

    def test_capturas_fuentes_y_estados(self):
        for nombre,nuevo in (("observacion",self.observacion),("fallos",self.fallos)):
            r=json.loads((UNIDAD/f"recursos/{nombre}.json").read_text())
            self.assertEqual(r["fuentes_sha256"],lab.fuentes())
            self.assertEqual([(c["caso"],c["status"]) for c in r["casos"]],[(c["caso"],c["status"]) for c in nuevo["casos"]])
            self.assertEqual(r["resumen"]["por_status"],nuevo["resumen"]["por_status"])

    def test_capturas_reconstruyen_metricas(self):
        for nombre in ("observacion","fallos"):
            r=json.loads((UNIDAD/f"recursos/{nombre}.json").read_text())
            obs=Observador(SHA_MODELO,objetivo_ms=r["config"]["objetivo_ms"])
            for e in r["eventos"]:
                obs.iniciar()
                obs.terminar(e["solicitud_id"],e["ruta"],e["metodo"],e["status"],e["codigo"],e["duracion_ms"])
            actual,publicado=obs.resumen(),r["resumen"]
            self.assertAlmostEqual(actual["prediccion_POST"]["media_ms"],publicado["prediccion_POST"]["media_ms"],places=5)
            actual["prediccion_POST"]["media_ms"]=publicado["prediccion_POST"]["media_ms"]
            self.assertEqual(actual,publicado)

    def test_manual_independiente(self):
        p=UNIDAD/"soluciones/03_operacion_a_mano.py"
        spec=importlib.util.spec_from_file_location("manual33",p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        r=m.calcular()
        self.assertEqual(r,json.loads((UNIDAD/"recursos/manual.json").read_text()))
        self.assertEqual(r["resumen"]["prediccion_POST"]["media_ms"],137/5)
        self.assertEqual(r["p95_rango_mas_cercano_ms"],90)


if __name__=="__main__":
    unittest.main()

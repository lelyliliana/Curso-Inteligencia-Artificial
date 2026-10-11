"""Contratos, ciclo de vida, HTTP real y evidencia; no reemplaza probar el navegador."""

import base64
from contextlib import redirect_stderr
import hashlib
import http.client
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import torch
from PIL import Image

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import apoyo
from contrato import ErrorEntrada, MAX_CUERPO, MAX_IMAGEN, leer_json, serializar, validar
import servicio
import servidor


def png(modo="L", tamano=(20, 16), formato="PNG"):
    salida = io.BytesIO()
    Image.new(modo, tamano).save(salida, format=formato)
    return base64.b64encode(salida.getvalue()).decode()


class ContratoTest(unittest.TestCase):
    def rechaza(self, obj, codigo):
        with self.assertRaises(ErrorEntrada) as c:
            validar(obj)
        self.assertEqual(c.exception.codigo, codigo)

    def test_json_utf8(self):
        self.assertEqual(leer_json(serializar({"nota": "lámpara"})), {"nota": "lámpara"})

    def test_json_invalido(self):
        for cuerpo in (b"{", b"{}{}", b"\xff", b""):
            with self.subTest(cuerpo=cuerpo), self.assertRaises(ErrorEntrada) as c:
                leer_json(cuerpo)
            self.assertEqual(c.exception.status, 400)

    def test_json_repetidos_y_constantes(self):
        for cuerpo in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}'):
            with self.subTest(cuerpo=cuerpo), self.assertRaises(ErrorEntrada):
                leer_json(cuerpo)

    def test_presupuesto_json(self):
        with self.assertRaises(ErrorEntrada) as c:
            leer_json(b" " * (MAX_CUERPO + 1))
        self.assertEqual(c.exception.status, 413)

    def test_campos_exactos(self):
        for obj in (None, [], {}, {"texto": "estado derecha"}, {**apoyo.entrada(), "etiqueta": 1}):
            with self.subTest(obj=type(obj)):
                self.rechaza(obj, "campos_invalidos")

    def test_textos_validos(self):
        for verbo in ("estado", "consulta"):
            for lado in ("izquierda", "derecha"):
                texto = f"{verbo} {lado}"
                self.assertEqual(validar({**apoyo.entrada(), "texto": texto})[1], texto)

    def test_textos_invalidos(self):
        for texto in (None, 1, "", "estado derecha\n", "Estado derecha", "estado  derecha", "no estado derecha"):
            with self.subTest(texto=texto):
                self.rechaza({**apoyo.entrada(), "texto": texto}, "texto_invalido")

    def test_base64_ausente(self):
        for valor in (None, 1, ""):
            self.rechaza({**apoyo.entrada(), "imagen_base64": valor}, "imagen_ausente")

    def test_base64_estricto(self):
        for valor in ("%%%", "á", "data:image/png;base64,AAAA", "a===", "YW Jj"):
            self.rechaza({**apoyo.entrada(), "imagen_base64": valor}, "base64_invalido")

    def test_bytes_de_imagen_limitados(self):
        for valor in ("a" * 30000, base64.b64encode(b"x" * (MAX_IMAGEN + 1)).decode()):
            self.rechaza({**apoyo.entrada(), "imagen_base64": valor}, "imagen_grande")

    def test_imagen_corrupta(self):
        original = base64.b64decode(apoyo.entrada()["imagen_base64"])
        for valor in (b"hola", original[:50], original[:-15]):
            self.rechaza({**apoyo.entrada(), "imagen_base64": base64.b64encode(valor).decode()}, "imagen_invalida")

    def test_modo_tamano_formato(self):
        for imagen in (png("RGB"), png(tamano=(21, 16)), png(formato="BMP")):
            self.rechaza({**apoyo.entrada(), "imagen_base64": imagen}, "formato_imagen")

    def test_no_convierte_pixeles(self):
        obj = apoyo.entrada()
        imagen, texto = validar(obj)
        self.assertEqual(imagen, base64.b64decode(obj["imagen_base64"]))
        self.assertEqual(texto, obj["texto"])

    def test_error_sin_prediccion(self):
        obj = ErrorEntrada("formato", "Mensaje", 422).respuesta()
        self.assertEqual(set(obj), {"version", "estado", "error"})
        self.assertEqual(obj["estado"], "error")


class ServicioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = servicio.Servicio()

    def test_modelo_fijado_y_congelado(self):
        self.assertEqual(hashlib.sha256(servicio.MODELO.read_bytes()).hexdigest(), servicio.SHA_MODELO)
        self.assertTrue(all(not p.requires_grad for p in self.app.modelo.parameters()))
        self.assertFalse(self.app.modelo.training)

    def test_ocho_pares_complementarios(self):
        for caso in apoyo.casos_http()[:8]:
            with self.subTest(caso=caso["id"]):
                r = self.app.predecir(caso["obj"])
                self.assertEqual(r["resultado"]["clase"], caso["clase"])
                self.assertEqual(r["modelo"]["sha256"], servicio.SHA_MODELO)

    def test_misma_preparacion_que_unidad31(self):
        obj = apoyo.entrada()
        r = servicio.multimodal.predecir(self.app.modelo, "fusion", io.BytesIO(base64.b64decode(obj["imagen_base64"])), obj["texto"])
        self.assertEqual(self.app.predecir(obj)["resultado"]["clase"], r["clase"])

    def test_rechazo_antes_del_modelo(self):
        with patch.object(self.app.modelo, "forward", side_effect=AssertionError("No inferir")):
            with self.assertRaises(ErrorEntrada):
                self.app.predecir({})

    def test_no_entrena_no_recarga_no_modifica(self):
        antes = {k: v.clone() for k, v in self.app.modelo.state_dict().items()}
        with patch.object(servicio.multimodal, "restaurar", side_effect=AssertionError("No recargar")), patch.object(servicio.multimodal, "entrenar", side_effect=AssertionError("No entrenar")):
            self.app.predecir(apoyo.entrada())
            self.app.predecir(apoyo.entrada(lado="izquierda"))
        self.assertTrue(all(torch.equal(v, self.app.modelo.state_dict()[k]) for k, v in antes.items()))

    def test_modelo_modificado_falla_antes_de_abrir(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo.json"
            p.write_bytes(servicio.MODELO.read_bytes() + b" ")
            with patch.object(servidor, "Servidor", side_effect=AssertionError("No abrir puerto")):
                with self.assertRaises(ValueError):
                    servidor.crear_servidor(0, p)

    def test_modelo_ausente_falla(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(FileNotFoundError):
            servicio.Servicio(Path(d) / "ausente.json")

    def test_informacion_publica(self):
        r = self.app.informacion()
        self.assertEqual(r["clases"], ["apagada", "encendida"])
        self.assertNotIn(str(UNIDAD), json.dumps(r))


class HTTPTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contexto = servidor.servidor_temporal()
        cls.http = cls.contexto.__enter__()
        cls.puerto = cls.http.server_port

    @classmethod
    def tearDownClass(cls):
        cls.contexto.__exit__(None, None, None)

    def pedir(self, metodo="POST", ruta="/api/predecir", cuerpo=None, cabeceras=None):
        return apoyo.solicitud(self.puerto, metodo, ruta,
                              serializar(apoyo.entrada()) if cuerpo is None else cuerpo,
                              {"Content-Type": "application/json"} if cabeceras is None else cabeceras)

    def test_prediccion_http(self):
        r = self.pedir()
        self.assertEqual(r["status"], 200)
        self.assertEqual(r["respuesta"]["resultado"], {"lado": "derecha", "clase": "encendida"})

    def test_health_y_modelo(self):
        self.assertEqual(self.pedir("GET", "/health")["respuesta"]["estado"], "listo")
        self.assertEqual(self.pedir("GET", "/api/modelo")["respuesta"]["sha256"], servicio.SHA_MODELO)

    def test_recursos_ui(self):
        for ruta, (p, tipo) in servidor.ESTATICOS.items():
            with self.subTest(ruta=ruta):
                r = self.pedir("GET", ruta)
                self.assertEqual(r["status"], 200)
                self.assertEqual(r["tipo"], tipo)
                self.assertEqual(r["respuesta"]["sha256"], hashlib.sha256(p.read_bytes()).hexdigest())

    def test_catalogo_sin_rutas_del_equipo(self):
        r = self.pedir("GET", "/api/ejemplos")["respuesta"]
        self.assertEqual({x["id"] for x in r}, {"00", "01", "10", "11"})
        self.assertNotIn(str(UNIDAD), json.dumps(r))

    def test_rutas_no_permitidas(self):
        for ruta in ("/README.md", "/../README.md", "/%2e%2e/README.md", "/api/modelo?x=1"):
            self.assertEqual(self.pedir("GET", ruta)["status"], 404)

    def test_metodos(self):
        for metodo, ruta in (("GET", "/api/predecir"), ("POST", "/health"), ("DELETE", "/api/predecir")):
            self.assertEqual(self.pedir(metodo, ruta)["status"], 405)

    def test_tipo_mime(self):
        for tipo in ("text/plain", "application/json;charset=latin1"):
            self.assertEqual(self.pedir(cabeceras={"Content-Type": tipo})["status"], 415)
        self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json; charset=utf-8"})["status"], 200)

    def test_json_y_validacion_distintos(self):
        self.assertEqual(self.pedir(cuerpo=b'{')["status"], 400)
        self.assertEqual(self.pedir(cuerpo=b'{}')["status"], 422)

    def test_cuerpo_grande(self):
        self.assertEqual(self.pedir(cuerpo=b" " * (MAX_CUERPO + 1))["status"], 413)

    def test_longitud_invalida(self):
        for longitud in ("-1", "1.5", "1" * 5000):
            self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json", "Content-Length": longitud})["status"], 400)

    def test_transferencia_no_admitida(self):
        self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json", "Transfer-Encoding": "chunked"})["status"], 400)

    def test_longitud_ausente_y_duplicada(self):
        for longitudes, esperado in (([], 411), (["1", "1"], 400)):
            c = http.client.HTTPConnection("127.0.0.1", self.puerto, timeout=3)
            try:
                c.putrequest("POST", "/api/predecir")
                c.putheader("Content-Type", "application/json")
                for longitud in longitudes:
                    c.putheader("Content-Length", longitud)
                c.endheaders()
                r = c.getresponse()
                self.assertEqual(r.status, esperado)
                r.read()
            finally:
                c.close()

    def test_cuerpo_truncado(self):
        with socket.create_connection(("127.0.0.1", self.puerto), timeout=3) as c:
            c.sendall(f"POST /api/predecir HTTP/1.1\r\nHost: 127.0.0.1:{self.puerto}\r\nContent-Type: application/json\r\nContent-Length: 5\r\n\r\n{{".encode())
            c.shutdown(socket.SHUT_WR)
            datos = b""
            while bloque := c.recv(4096):
                datos += bloque
            self.assertIn(b"400", datos.split(b"\r\n", 1)[0])
            self.assertIn(b"cuerpo_incompleto", datos)

    def test_host_y_origen(self):
        self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json", "Host": "ajeno.invalid"})["status"], 403)
        self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json", "Origin": "https://ajeno.invalid"})["status"], 403)
        self.assertEqual(self.pedir(cabeceras={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{self.puerto}"})["status"], 200)

    def test_fallo_modelo_es_500_sin_detalle(self):
        with patch.object(self.http.servicio, "predecir", side_effect=RuntimeError("ruta privada /secreto")):
            r = self.pedir()
        self.assertEqual(r["status"], 500)
        self.assertNotIn("secreto", json.dumps(r))
        self.assertNotIn("resultado", r["respuesta"])

    def test_log_no_incluye_entrada(self):
        registro_listo = threading.Event()

        class CapturaRegistro(io.StringIO):
            def write(self, texto):
                escritos = super().write(texto)
                if "\n" in texto:
                    registro_listo.set()
                return escritos

        salida = CapturaRegistro()
        # Servidor propio: no capturar registros de peticiones anteriores.
        with servidor.servidor_temporal() as http:
            http.registrar = True
            with redirect_stderr(salida):
                r = apoyo.solicitud(http.server_port, "POST", "/api/predecir",
                                    serializar({"secreto": "contenido-privado"}),
                                    {"Content-Type": "application/json"})
                self.assertEqual(r["status"], 422)
                # Recibir HTTP no garantiza que el hilo ya haya escrito el log.
                self.assertTrue(registro_listo.wait(2), "No se completó el registro HTTP")
        eventos = [json.loads(l) for l in salida.getvalue().splitlines()]
        self.assertEqual(len(eventos), 1)
        self.assertTrue(all(set(e) == {"evento", "metodo", "status", "duracion_ms"} for e in eventos))
        self.assertNotIn("contenido-privado", salida.getvalue())

    def test_solo_loopback(self):
        self.assertEqual(self.http.server_address[0], "127.0.0.1")


class EvidenciaTest(unittest.TestCase):
    def test_captura_http_reconstruible(self):
        publicada = json.loads((UNIDAD / "recursos/http.json").read_text())
        self.assertEqual(apoyo.comprobar(), publicada)
        self.assertEqual(publicada["cumplen"], 24)

    def test_escenas_son_validacion_anterior(self):
        filas = json.loads((servicio.ANTERIOR / "datos/multimodal/validacion.json").read_text())
        familias = {f["familia"] for f in filas}
        self.assertTrue(all(Path(e["archivo"]).stem in familias for e in servidor.ESCENAS))

    def test_cuenta_base64_y_utf8(self):
        ruta = UNIDAD / "soluciones/03_tamano_peticion.py"
        spec = importlib.util.spec_from_file_location("manual32", ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        r = modulo.calcular()
        self.assertEqual(r, json.loads((UNIDAD / "recursos/tamano.json").read_text()))
        self.assertEqual(r["caracteres_base64"], 21848)
        self.assertEqual(r["ejemplo_utf8"]["bytes"], r["ejemplo_utf8"]["caracteres"] + 1)

    def test_cli_modelo_ausente_sale_sin_servir(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(UNIDAD / "aplicacion/servidor.py"), "--modelo", str(Path(d)/"ausente")], capture_output=True, text=True, timeout=15)
        self.assertEqual(r.returncode, 1)
        self.assertIn("No se pudo iniciar", r.stderr)
        self.assertNotIn("Aplicación lista", r.stdout)

    def test_puerto_invalido(self):
        for puerto in (-1, 65536, True):
            with self.assertRaises(ValueError):
                servidor.Servidor(None, puerto)


if __name__ == "__main__":
    unittest.main()

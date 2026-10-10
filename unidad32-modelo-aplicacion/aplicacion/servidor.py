"""Servidor HTTP didáctico, limitado a loopback. No es un despliegue de producción."""

import argparse
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
import threading
import time
from urllib.parse import urlsplit

from contrato import ErrorEntrada, MAX_CUERPO, VERSION, leer_json, serializar
from servicio import MODELO, Servicio, UNIDAD

WEB = UNIDAD / "web"
ESCENAS = (
    {"id": "00", "nombre": "Ambas apagadas", "archivo": "escena-027.png"},
    {"id": "01", "nombre": "Derecha encendida", "archivo": "escena-024.png"},
    {"id": "10", "nombre": "Izquierda encendida", "archivo": "escena-030.png"},
    {"id": "11", "nombre": "Ambas encendidas", "archivo": "escena-026.png"},
)
ESTATICOS = {"/": (WEB / "index.html", "text/html; charset=utf-8"),
             "/app.js": (WEB / "app.js", "text/javascript; charset=utf-8"),
             "/estilos.css": (WEB / "estilos.css", "text/css; charset=utf-8")}
ESTATICOS.update({f'/ejemplos/{e["id"]}.png':
                  (UNIDAD.parent / "unidad31-adaptacion-multimodalidad/datos/multimodal/imagenes" / e["archivo"], "image/png")
                 for e in ESCENAS})


class Servidor(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, servicio, puerto=8765, registrar=True):
        if type(puerto) is not int or not 0 <= puerto <= 65535:
            raise ValueError("Puerto fuera de rango")
        self.servicio, self.registrar = servicio, registrar
        super().__init__(("127.0.0.1", puerto), Manejador)


class Manejador(BaseHTTPRequestHandler):
    server_version, sys_version = "CursoIA/1", ""
    timeout = 5

    def log_message(self, formato, *args):
        pass  # No registrar líneas de solicitud, consultas ni cuerpos del usuario.

    def responder(self, status, obj, tipo="application/json; charset=utf-8"):
        cuerpo = obj if isinstance(obj, bytes) else serializar(obj)
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' blob: data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Connection", "close")
        if status == 405:
            self.send_header("Allow", "GET, POST")
        self.end_headers()
        self.close_connection = True
        try:
            self.wfile.write(cuerpo)
        except (BrokenPipeError, ConnectionResetError):
            pass
        if self.server.registrar:
            evento = {"evento": "http", "metodo": self.command, "status": status,
                      "duracion_ms": round((time.perf_counter() - self.inicio) * 1000, 2)}
            print(json.dumps(evento), file=sys.stderr, flush=True)

    def origen_valido(self):
        puerto = self.server.server_port
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0] not in (f"127.0.0.1:{puerto}", f"localhost:{puerto}"):
            raise ErrorEntrada("host_invalido", "Abre la dirección local mostrada al iniciar.", 403)
        origenes = self.headers.get_all("Origin", [])
        if origenes and origenes != [f"http://{hosts[0]}"]:
            raise ErrorEntrada("origen_invalido", "Usa la interfaz del mismo servidor local.", 403)

    def cuerpo_json(self):
        if self.headers.get_all("Transfer-Encoding"):
            raise ErrorEntrada("transferencia_invalida", "Usa Content-Length, sin transferencia fragmentada.", 400)
        longitudes = self.headers.get_all("Content-Length", [])
        if not longitudes:
            raise ErrorEntrada("longitud_ausente", "Falta Content-Length.", 411)
        if len(longitudes) != 1 or len(longitudes[0]) > 8 or not longitudes[0].isascii() or not longitudes[0].isdigit():
            raise ErrorEntrada("longitud_invalida", "Content-Length debe ser un entero no negativo.", 400)
        n = int(longitudes[0])
        if n > MAX_CUERPO:
            raise ErrorEntrada("cuerpo_grande", "La solicitud supera 32 KiB.", 413)
        tipos = self.headers.get_all("Content-Type", [])
        if len(tipos) != 1 or tipos[0].lower().replace(" ", "") not in ("application/json", "application/json;charset=utf-8"):
            raise ErrorEntrada("tipo_invalido", "Usa Content-Type: application/json en UTF-8.", 415)
        try:
            cuerpo = self.rfile.read(n)
        except TimeoutError as exc:
            raise ErrorEntrada("lectura_agotada", "No llegó el cuerpo completo a tiempo.", 408) from exc
        if len(cuerpo) != n:
            raise ErrorEntrada("cuerpo_incompleto", "El cuerpo recibido está incompleto.", 400)
        return leer_json(cuerpo)

    def atender(self):
        self.inicio = time.perf_counter()
        try:
            self.origen_valido()
            url = urlsplit(self.path)
            if url.query or url.fragment or url.scheme or url.netloc:
                raise ErrorEntrada("ruta_invalida", "Esta API usa rutas exactas sin parámetros de URL.", 404)
            ruta = url.path
            if self.command not in ("GET", "POST"):
                raise ErrorEntrada("metodo_invalido", "Usa GET para consultar o POST para predecir.", 405)
            if self.command == "GET":
                if ruta == "/health":
                    return self.responder(200, {"version": VERSION, "estado": "listo"})
                if ruta == "/api/modelo":
                    return self.responder(200, self.server.servicio.informacion())
                if ruta == "/api/ejemplos":
                    return self.responder(200, [{"id": e["id"], "nombre": e["nombre"], "url": f'/ejemplos/{e["id"]}.png'} for e in ESCENAS])
                if ruta in ESTATICOS:
                    archivo, tipo = ESTATICOS[ruta]
                    return self.responder(200, archivo.read_bytes(), tipo)
                if ruta == "/api/predecir":
                    raise ErrorEntrada("metodo_invalido", "Envía la predicción mediante POST.", 405)
            elif ruta == "/api/predecir":
                return self.responder(200, self.server.servicio.predecir(self.cuerpo_json()))
            elif ruta in ESTATICOS or ruta in ("/health", "/api/modelo", "/api/ejemplos"):
                raise ErrorEntrada("metodo_invalido", "Esta ruta solo admite GET.", 405)
            raise ErrorEntrada("ruta_desconocida", "La ruta solicitada no existe.", 404)
        except ErrorEntrada as exc:
            self.responder(exc.status, exc.respuesta())
        except Exception:
            # El detalle interno no pertenece al contrato público. La U33 amplía diagnóstico.
            exc = ErrorEntrada("error_interno", "No se pudo completar la consulta. Revisa el servidor.", 500)
            self.responder(exc.status, exc.respuesta())

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = atender


def crear_servidor(puerto=8765, modelo=MODELO, registrar=True):
    servicio = Servicio(modelo)  # La carga debe completarse antes de abrir el puerto.
    for archivo, _ in ESTATICOS.values():
        if not archivo.is_file():
            raise FileNotFoundError(f"Recurso de interfaz ausente: {archivo.name}")
    return Servidor(servicio, puerto, registrar)


@contextmanager
def servidor_temporal(servicio=None):
    with Servidor(servicio or Servicio(), puerto=0, registrar=False) as servidor:
        hilo = threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": .05}, daemon=True)
        hilo.start()
        try:
            yield servidor
        finally:
            servidor.shutdown()
            hilo.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puerto", type=int, default=8765)
    parser.add_argument("--modelo", type=str, default=str(MODELO))
    args = parser.parse_args()
    try:
        with crear_servidor(args.puerto, args.modelo) as servidor:
            print(f"Aplicación lista: http://127.0.0.1:{servidor.server_port}", flush=True)
            print("Uso local didáctico. Ctrl+C para cerrar.", flush=True)
            servidor.serve_forever()
    except KeyboardInterrupt:
        print("Aplicación cerrada.")
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"No se pudo iniciar: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

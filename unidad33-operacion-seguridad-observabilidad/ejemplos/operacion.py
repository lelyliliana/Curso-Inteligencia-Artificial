"""Extensión local de U32: admisión limitada, disponibilidad y observación."""

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from http.server import ThreadingHTTPServer
import json
import math
from pathlib import Path
import sys
import threading
import time
from urllib.parse import urlsplit
import uuid

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent / "unidad32-modelo-aplicacion/aplicacion"))
import servidor as anterior
from contrato import ErrorEntrada, serializar
from servicio import Servicio, SHA_MODELO
from observacion import CODIGOS, METODOS, Observador


@dataclass(frozen=True)
class Config:
    conexiones: int = 4
    inferencias: int = 1
    espera_socket_s: float = 1.0
    historial: int = 256
    objetivo_ms: float = 100.0

    def __post_init__(self):
        if type(self.conexiones) is not int or not 1 <= self.conexiones <= 32:
            raise ValueError("Se requieren de 1 a 32 conexiones")
        if self.inferencias != 1 or type(self.inferencias) is not int:
            raise ValueError("Esta práctica admite una inferencia, sin cola")
        if type(self.historial) is not int or not 1 <= self.historial <= 10000:
            raise ValueError("Historial fuera de rango")
        for valor in (self.espera_socket_s, self.objetivo_ms):
            if type(valor) not in (int, float) or not math.isfinite(valor) or valor <= 0:
                raise ValueError("Tiempos positivos y finitos requeridos")


class ServicioOperado:
    def __init__(self, base):
        self.base = base
        self.lock = threading.Lock()
        self.estado = "listo"
        self.ocupado = False

    def informacion(self):
        return self.base.informacion()

    def disponibilidad(self):
        with self.lock:
            return {"estado": self.estado, "ocupado": self.ocupado}

    def establecer_estado(self, estado):
        if estado not in ("listo", "mantenimiento", "degradado"):
            raise ValueError("Estado inválido")
        with self.lock:
            self.estado = estado

    def predecir(self, obj):
        # La admisión ocurre antes de la preparación: tampoco se encolan entradas inválidas.
        with self.lock:
            if self.estado != "listo":
                raise ErrorEntrada("no_disponible", "Predicciones temporalmente deshabilitadas.", 503)
            if self.ocupado:
                raise ErrorEntrada("ocupado", "Hay una consulta en curso. Reintenta más tarde.", 503)
            self.ocupado = True
        try:
            return self.base.predecir(obj)
        except ErrorEntrada:
            raise
        except Exception:
            with self.lock:
                self.estado = "degradado"
            raise
        finally:
            with self.lock:
                self.ocupado = False


def categoria(ruta):
    if ruta == "/api/predecir":
        return "prediccion"
    if ruta == "/live":
        return "live"
    if ruta in ("/ready", "/health"):
        return "ready"
    if ruta == "/metricas":
        return "metricas"
    if ruta in anterior.ESTATICOS:
        return "estatico"
    return "otros"


class ManejadorOperado(anterior.Manejador):
    def setup(self):
        self.timeout = self.server.config.espera_socket_s
        super().setup()

    def end_headers(self):
        if hasattr(self, "solicitud_id"):
            self.send_header("X-Request-ID", self.solicitud_id)
        if getattr(self, "ultimo_status", None) == 503:
            self.send_header("Retry-After", "1")
        super().end_headers()

    def responder(self, status, obj, tipo="application/json; charset=utf-8"):
        self.ultimo_status = status
        if not self.registrada:
            codigo = obj.get("error", {}).get("codigo", "ninguno") if isinstance(obj, dict) else "ninguno"
            codigo = codigo if codigo in CODIGOS else "otro_error"
            self.server.observador.terminar(self.solicitud_id, self.ruta_categoria, self.metodo_categoria,
                                            status, codigo, (time.perf_counter() - self.inicio) * 1000)
            self.registrada = True
        return super().responder(status, obj, tipo)

    def atender(self):
        self.inicio, self.solicitud_id = time.perf_counter(), uuid.uuid4().hex
        self.registrada = False
        self.ruta_categoria = categoria(self.path)
        self.metodo_categoria = self.command if self.command in METODOS else "OTRO"
        self.server.observador.iniciar()
        try:
            if self.path in ("/live", "/ready", "/metricas"):
                self.origen_valido()
                if self.command != "GET":
                    raise ErrorEntrada("metodo_invalido", "Este recurso solo admite GET.", 405)
                if self.path == "/live":
                    return self.responder(200, {"version": "1", "estado": "vivo"})
                if self.path == "/ready":
                    estado = self.server.servicio.disponibilidad()
                    return self.responder(200 if estado["estado"] == "listo" else 503, {"version": "1", **estado})
                return self.responder(200, self.server.observador.resumen())
            if self.path == "/health" and self.command == "GET":
                self.origen_valido()
                estado = self.server.servicio.disponibilidad()["estado"]
                return self.responder(200 if estado == "listo" else 503, {"version": "1", "estado": estado})
            return super().atender()
        except ErrorEntrada as exc:
            self.responder(exc.status, exc.respuesta())
        finally:
            if not self.registrada:
                self.server.observador.abandonar()

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = atender


class ServidorOperado(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, base, puerto=0, config=None, emitir=False):
        if type(puerto) is not int or not 0 <= puerto <= 65535:
            raise ValueError("Puerto fuera de rango")
        self.config = config or Config()
        self.servicio = ServicioOperado(base)
        self.observador = Observador(SHA_MODELO, self.config.historial, self.config.objetivo_ms, emitir)
        self.permisos = threading.BoundedSemaphore(self.config.conexiones)
        self.registrar = False  # Evita duplicar el registro heredado de U32.
        super().__init__(("127.0.0.1", puerto), ManejadorOperado)

    def process_request(self, request, client_address):
        if not self.permisos.acquire(blocking=False):
            # Aún no se ha leído una solicitud: no inventar ruta, método o request ID.
            self.observador.rechazar_conexion()
            cuerpo = serializar(ErrorEntrada("ocupado", "Capacidad de conexiones agotada.", 503).respuesta())
            cabecera = (f"HTTP/1.0 503 Service Unavailable\r\nContent-Type: application/json\r\n"
                        f"Content-Length: {len(cuerpo)}\r\nRetry-After: 1\r\nConnection: close\r\n\r\n").encode()
            try:
                request.settimeout(self.config.espera_socket_s)
                request.sendall(cabecera + cuerpo)
            except OSError:
                pass
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.permisos.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.permisos.release()


@contextmanager
def temporal(base=None, config=None):
    with ServidorOperado(base or Servicio(), config=config) as servidor:
        hilo = threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": .02}, daemon=True)
        hilo.start()
        try:
            yield servidor
        finally:
            servidor.servicio.establecer_estado("mantenimiento")
            servidor.shutdown()
            hilo.join(timeout=3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puerto", type=int, default=8766)
    parser.add_argument("--conexiones", type=int, default=4)
    parser.add_argument("--mantenimiento", action="store_true")
    args = parser.parse_args()
    try:
        config = Config(conexiones=args.conexiones)
        base = Servicio()  # Mismo estado y comprobaciones de inicio que U32.
        for archivo, _ in anterior.ESTATICOS.values():
            if not archivo.is_file():
                raise FileNotFoundError(archivo.name)
        with ServidorOperado(base, args.puerto, config, emitir=True) as servidor:
            if args.mantenimiento:
                servidor.servicio.establecer_estado("mantenimiento")
            print(f"Aplicación local: http://127.0.0.1:{servidor.server_port}", flush=True)
            print(json.dumps({"config": asdict(config), "modelo_sha256": SHA_MODELO}), flush=True)
            servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor cerrado; los hilos daemon no garantizan drenar trabajo bloqueado.")
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"No se pudo iniciar: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

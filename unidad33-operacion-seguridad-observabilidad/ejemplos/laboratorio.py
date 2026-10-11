"""Capturas HTTP reales con fallos inyectados explícitamente en un envoltorio local."""

import base64
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import hashlib
import http.client
import json
from pathlib import Path
import socket
import threading
import time

from operacion import Config, SHA_MODELO, Servicio, UNIDAD, anterior, temporal
from contrato import serializar


def guardar(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def entrada(lado="derecha"):
    imagen = anterior.ESTATICOS["/ejemplos/01.png"][0].read_bytes()
    return {"imagen_base64": base64.b64encode(imagen).decode(), "texto": f"estado {lado}"}


def pedir(puerto, ruta="/api/predecir", obj=None, metodo="POST", cabeceras=None, timeout=4):
    c = http.client.HTTPConnection("127.0.0.1", puerto, timeout=timeout)
    headers = {"Content-Type": "application/json", **(cabeceras or {})}
    try:
        c.request(metodo, ruta, body=serializar(obj) if obj is not None else None, headers=headers)
        r = c.getresponse()
        datos = r.read(65537)
        if len(datos) > 65536:
            raise RuntimeError("Respuesta excedida")
        return {"status": r.status, "solicitud_id": r.getheader("X-Request-ID"),
                "retry_after": r.getheader("Retry-After"), "respuesta": json.loads(datos)}
    finally:
        c.close()


def esperar(condicion, segundos=3):
    limite = time.monotonic() + segundos
    while not condicion():
        if time.monotonic() >= limite:
            raise RuntimeError("La condición del laboratorio no se cumplió")
        time.sleep(.005)


def fuentes():
    rutas = ["ejemplos/operacion.py", "ejemplos/observacion.py", "ejemplos/laboratorio.py",
             "../unidad32-modelo-aplicacion/aplicacion/contrato.py",
             "../unidad32-modelo-aplicacion/aplicacion/servicio.py",
             "../unidad32-modelo-aplicacion/aplicacion/servidor.py"]
    return {r: hashlib.sha256((UNIDAD / r).read_bytes()).hexdigest() for r in rutas}


def empaquetar(servidor, casos, tipo):
    esperar(lambda: servidor.observador.resumen()["en_curso"] == 0)
    return {"tipo": tipo, "modelo_sha256": SHA_MODELO, "fuentes_sha256": fuentes(),
            "config": asdict(servidor.config), "casos": casos,
            "eventos": servidor.observador.historial(), "resumen": servidor.observador.resumen()}


def observar():
    casos = []
    with temporal() as s:
        for nombre, ruta, obj, metodo, headers, esperado in (
                ("vivo", "/live", None, "GET", {}, 200),
                ("listo", "/ready", None, "GET", {}, 200),
                ("derecha", "/api/predecir", entrada(), "POST", {}, 200),
                ("campos", "/api/predecir", {}, "POST", {}, 422),
                ("izquierda", "/api/predecir", entrada("izquierda"), "POST", {}, 200),
                ("ruta", "/no-existe", None, "GET", {}, 404),
                ("origen", "/api/predecir", entrada(), "POST", {"Origin": "https://ajeno.invalid"}, 403),
                ("metricas", "/metricas", None, "GET", {}, 200)):
            r = pedir(s.server_port, ruta, obj, metodo, headers)
            if r["status"] != esperado:
                raise RuntimeError(f"Falló {nombre}: {r}")
            casos.append({"caso": nombre, "esperado": esperado, **r})
        return empaquetar(s, casos, "observacion_HTTP_real")


class BaseControlada:
    """Solo el laboratorio puede inyectar bloqueos/fallos; no hay ruta HTTP para hacerlo."""
    def __init__(self, base):
        self.base = base
        self.modo = "normal"
        self.entrada = threading.Event()
        self.liberar = threading.Event()

    def informacion(self):
        return self.base.informacion()

    def preparar_bloqueo(self):
        self.entrada.clear()
        self.liberar.clear()
        self.modo = "bloqueo"

    def predecir(self, obj):
        if self.modo == "fallo":
            raise RuntimeError("Fallo artificial con detalle privado que no debe registrarse")
        if self.modo == "bloqueo":
            self.entrada.set()
            if not self.liberar.wait(3):
                raise RuntimeError("Se agotó la espera artificial del laboratorio")
        return self.base.predecir(obj)


def fallos():
    base = BaseControlada(Servicio())
    casos = []
    with temporal(base) as s, ThreadPoolExecutor(max_workers=1) as pool:
        def caso(nombre, esperado, ruta="/api/predecir", obj=None, metodo="POST"):
            r = pedir(s.server_port, ruta, entrada() if obj is None and metodo == "POST" else obj, metodo)
            if r["status"] != esperado:
                raise RuntimeError(f"Falló {nombre}: {r}")
            casos.append({"caso": nombre, "esperado": esperado, **r})
            return r

        caso("normal", 200)
        base.preparar_bloqueo()
        pendiente = pool.submit(pedir, s.server_port, obj=entrada())
        try:
            if not base.entrada.wait(2):
                raise RuntimeError("No entró la solicitud retenida")
            caso("saturacion_inferencia", 503)
            caso("ready_ocupado", 200, "/ready", metodo="GET")
            caso("live_ocupado", 200, "/live", metodo="GET")
            s.servicio.establecer_estado("mantenimiento")
            caso("ready_mantenimiento", 503, "/ready", metodo="GET")
            caso("rechazo_mantenimiento", 503)
        finally:
            base.liberar.set()
        r = pendiente.result(timeout=3)
        if r["status"] != 200:
            raise RuntimeError("La solicitud admitida no terminó")
        casos.append({"caso": "admitida_antes_mantenimiento", "esperado": 200, **r})
        base.modo = "normal"
        s.servicio.establecer_estado("listo")
        caso("recuperacion_mantenimiento", 200)
        base.modo = "fallo"
        caso("fallo_inyectado", 500)
        caso("ready_degradado", 503, "/ready", metodo="GET")
        caso("live_degradado", 200, "/live", metodo="GET")
        caso("rechazo_degradado", 503)
        base.modo = "normal"
        canario = base.base.predecir(entrada())
        if canario["resultado"]["clase"] != "encendida":
            raise RuntimeError("Falló el canario conocido")
        s.servicio.establecer_estado("listo")
        caso("recuperacion_fallo", 200)

        # El cliente abandona mientras un hilo del servidor sigue esperando la liberación.
        base.preparar_bloqueo()
        pendiente = pool.submit(pedir, s.server_port, obj=entrada(), timeout=.1)
        try:
            if not base.entrada.wait(2):
                raise RuntimeError("No entró la consulta para timeout")
            try:
                pendiente.result(timeout=2)
                raise RuntimeError("El cliente debía agotar su espera")
            except TimeoutError:
                if not pendiente.done():
                    raise RuntimeError("Agotó la espera del laboratorio, no la del cliente")
                sigue_ocupado = s.servicio.disponibilidad()["ocupado"]
                if not sigue_ocupado:
                    raise RuntimeError("El servidor terminó antes de observar el timeout")
        finally:
            base.liberar.set()
        esperar(lambda: s.observador.resumen()["en_curso"] == 0)
        base.modo = "normal"
        caso("despues_timeout_cliente", 200)
        informe = empaquetar(s, casos, "HTTP_real_con_fallos_artificiales_inyectados")
        informe["timeout_cliente"] = {"resultado": "TimeoutError", "servidor_seguia_ocupado": sigue_ocupado,
                                      "nota": "No hubo respuesta recibida; el servidor terminó y preparó un 200 después."}
        informe["canario_directo"] = canario

    # Límite de hilos/conexiones, distinto del límite de inferencia del experimento anterior.
    base.preparar_bloqueo()
    with temporal(base, Config(conexiones=1)) as s, ThreadPoolExecutor(max_workers=1) as pool:
        pendiente = pool.submit(pedir, s.server_port, obj=entrada())
        try:
            if not base.entrada.wait(2):
                raise RuntimeError("No se ocupó la única conexión")
            with socket.create_connection(("127.0.0.1", s.server_port), timeout=2) as c:
                # No se envía HTTP: el rechazo ocurre antes de conocer ruta y método.
                datos = b""
                while bloque := c.recv(4096):
                    datos += bloque
            if not datos.startswith(b"HTTP/1.0 503"):
                raise RuntimeError("La conexión excedente no fue rechazada")
        finally:
            base.liberar.set()
        r = pendiente.result(timeout=3)
        informe["saturacion_conexiones"] = {
            "respuesta_sin_solicitud_HTTP": datos.decode("utf-8"),
            "solicitud_admitida": r, "resumen": empaquetar(s, [], "limite_conexiones")["resumen"]}
    return informe

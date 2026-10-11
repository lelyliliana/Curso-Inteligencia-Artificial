"""Contadores acumulados e historial acotado; no guarda entradas del usuario."""

from collections import Counter, deque
from copy import deepcopy
import json
import math
import sys
import threading

RUTAS = {"prediccion", "live", "ready", "metricas", "estatico", "otros"}
METODOS = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "OTRO"}
CODIGOS = {"ninguno", "ocupado", "no_disponible", "error_interno", "json_invalido",
           "longitud_invalida", "transferencia_invalida", "cuerpo_incompleto", "host_invalido",
           "origen_invalido", "ruta_invalida", "ruta_desconocida", "metodo_invalido",
           "lectura_agotada", "longitud_ausente", "cuerpo_grande", "imagen_grande",
           "tipo_invalido", "campos_invalidos", "texto_invalido", "imagen_ausente",
           "base64_invalido", "formato_imagen", "imagen_invalida", "otro_error"}
LIMITES_MS = (1, 5, 20, 100, 500, 2000)


class Observador:
    def __init__(self, modelo_sha256, capacidad=256, objetivo_ms=100, emitir=False):
        if type(capacidad) is not int or capacidad < 1 or capacidad > 10000:
            raise ValueError("Capacidad inválida")
        if type(objetivo_ms) not in (int, float) or not math.isfinite(objetivo_ms) or objetivo_ms <= 0:
            raise ValueError("Objetivo inválido")
        self.huella, self.objetivo, self.emitir = modelo_sha256, objetivo_ms, emitir
        self.lock = threading.Lock()
        self.eventos = deque(maxlen=capacidad)
        self.en_curso = self.terminadas = self.abandonadas = self.conexiones_rechazadas = 0
        self.por_status, self.por_ruta = Counter(), Counter()
        self.predicciones = self.exitos = self.rechazos = self.fallos = self.buenas = 0
        self.suma_ms = 0.0
        self.buckets = [0] * len(LIMITES_MS)

    def iniciar(self):
        with self.lock:
            self.en_curso += 1

    def abandonar(self):
        with self.lock:
            self.en_curso -= 1
            self.abandonadas += 1

    def rechazar_conexion(self):
        with self.lock:
            self.conexiones_rechazadas += 1

    def terminar(self, identificador, ruta, metodo, status, codigo, duracion_ms):
        if ruta not in RUTAS or metodo not in METODOS or codigo not in CODIGOS:
            raise ValueError("Etiqueta fuera del vocabulario acotado")
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError("Estado HTTP inválido")
        if not math.isfinite(duracion_ms) or duracion_ms < 0:
            raise ValueError("Duración inválida")
        evento = {"evento": "http", "solicitud_id": identificador, "ruta": ruta,
                  "metodo": metodo, "status": status, "codigo": codigo,
                  "duracion_ms": round(duracion_ms, 6), "modelo_sha256": self.huella}
        with self.lock:
            self.en_curso -= 1
            self.terminadas += 1
            self.por_status[str(status)] += 1
            self.por_ruta[ruta] += 1
            self.eventos.append(evento)
            if ruta == "prediccion" and metodo == "POST":
                self.predicciones += 1
                self.exitos += 200 <= status < 300
                self.rechazos += 400 <= status < 500
                self.fallos += 500 <= status < 600
                self.buenas += 200 <= status < 300 and duracion_ms <= self.objetivo
                self.suma_ms += duracion_ms
                for i, limite in enumerate(LIMITES_MS):
                    self.buckets[i] += duracion_ms <= limite
            if self.emitir:
                print(json.dumps(evento, ensure_ascii=False, allow_nan=False), file=sys.stderr, flush=True)
        return evento

    def resumen(self):
        with self.lock:
            n = self.predicciones
            return {"alcance": "Desde el inicio del proceso; respuestas preparadas, no recepción confirmada.",
                    "terminadas": self.terminadas, "en_curso": self.en_curso,
                    "abandonadas_sin_respuesta": self.abandonadas,
                    "conexiones_rechazadas_antes_de_HTTP": self.conexiones_rechazadas,
                    "por_status": dict(sorted(self.por_status.items())),
                    "por_ruta": dict(sorted(self.por_ruta.items())),
                    "historial_conservado": len(self.eventos), "capacidad_historial": self.eventos.maxlen,
                    "prediccion_POST": {"total": n, "exitos_2xx": self.exitos, "rechazos_4xx": self.rechazos,
                                        "fallos_5xx": self.fallos,
                                        "tasa_5xx": self.fallos / n if n else None,
                                        "objetivo_ms": self.objetivo, "exitos_dentro_objetivo": self.buenas,
                                        "fraccion_buenas": self.buenas / n if n else None,
                                        "media_ms": self.suma_ms / n if n else None,
                                        "histograma_acumulado": [{"le_ms": b, "n": c} for b, c in zip(LIMITES_MS, self.buckets)] + [{"le_ms": "+Inf", "n": n}]}}

    def historial(self):
        with self.lock:
            return deepcopy(list(self.eventos))

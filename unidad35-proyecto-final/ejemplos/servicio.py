"""Servicio local secuencial: contrato, carga única, eventos sin entradas y reversión explícita."""

from collections import Counter, deque
import json
import time
import uuid

from contrato import ErrorEntrada, validar
from proyecto import cargar, predecir

MAX_BYTES = 16384


def decodificar(contenido):
    if not isinstance(contenido, bytes) or len(contenido) > MAX_BYTES:
        raise ErrorEntrada("tamano_invalido", "Se admite una entrada de hasta 16 KiB")
    def pares_unicos(pares):
        objeto = {}
        for clave, valor in pares:
            if clave in objeto:
                raise ValueError("clave repetida")
            objeto[clave] = valor
        return objeto
    def constante_invalida(_):
        raise ValueError("constante no finita")
    try:
        return json.loads(contenido.decode("utf-8"), object_pairs_hook=pares_unicos, parse_constant=constante_invalida)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ErrorEntrada("json_invalido", "JSON UTF-8 inválido, repetido o no finito") from error


class Servicio:
    def __init__(self, ruta, referencia=False):
        self.paquete = cargar(ruta)
        self.referencia = bool(referencia)
        self.activo = True
        self.eventos = deque(maxlen=64)
        self.conteos = Counter()

    def responder(self, contenido):
        inicio = time.perf_counter()
        identificador = uuid.uuid4().hex
        politica = "persistencia" if self.referencia else self.paquete["elegido"]
        salida = {"solicitud_id": identificador, "modelo_sha256": self.paquete["sha256"], "politica": politica}
        try:
            if not self.activo:
                raise ErrorEntrada("mantenimiento", "Servicio local en mantenimiento")
            objeto = decodificar(contenido)
            entrada = validar(objeto, self.paquete["protocolo"]["contrato"])
            estado = self.paquete["referencia"] if self.referencia else self.paquete["modelo"]
            resultado = predecir(estado, entrada)
            codigo = resultado["estado"]
            salida.update(estado=codigo, resultado=resultado)
        except ErrorEntrada as error:
            codigo = error.codigo
            salida.update(estado="rechazado", codigo=codigo, mensaje=str(error))
        except Exception:
            # No se incluyen excepciones privadas ni se simula una predicción de respaldo.
            codigo = "error_interno"
            self.activo = False
            salida.update(estado="error", codigo=codigo, mensaje="Servicio local no disponible")
        self.conteos[salida["estado"]] += 1
        self.eventos.append({"solicitud_id": identificador, "modelo_sha256": self.paquete["sha256"],
                             "politica": politica, "estado": salida["estado"], "codigo": codigo,
                             "duracion_ms": round((time.perf_counter() - inicio) * 1000, 6)})
        return salida

    def metricas(self):
        total = sum(self.conteos.values())
        return {"solicitudes": total, "por_estado": dict(self.conteos), "eventos_conservados": len(self.eventos),
                "capacidad_historial": 64, "activo": self.activo,
                "fraccion_rechazada": self.conteos["rechazado"] / total if total else None}

"""Herramientas sin efectos externos; política y evidencia pertenecen al host."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import time

UNIDAD = Path(__file__).resolve().parents[1]
CODIGOS = ("ok", "argumentos_invalidos", "desconocida", "denegado", "no_disponible",
           "sin_consulta", "repetida", "limite_llamadas", "limite_tiempo", "datos_invalidos")
SENSOR = {"type": "string", "pattern": "^S-[0-9]{2}$"}
ENTRADA = {"type": "object", "properties": {"sensor": SENSOR},
           "required": ["sensor"], "additionalProperties": False}
SALIDA = {"type": "object", "properties": {
    "ok": {"type": "boolean"}, "codigo": {"type": "string", "enum": list(CODIGOS)},
    "datos": {"type": "object"}}, "required": ["ok", "codigo", "datos"],
    "additionalProperties": False}
CATALOGO = [
    {"name": "consultar_sensor", "description": "Lee las temperaturas en grados Celsius del sensor. Puede devolver no_disponible o denegado.",
     "inputSchema": ENTRADA, "outputSchema": SALIDA,
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "calcular_media", "description": "Calcula la media de las lecturas ya obtenidas con consultar_sensor en esta sesión. Requiere consulta previa exitosa del mismo sensor.",
     "inputSchema": ENTRADA, "outputSchema": SALIDA,
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
]


def json_estricto(texto):
    def constante(_):
        raise ValueError("Constante no finita")

    def pares(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError("Clave duplicada")
            obj[k] = v
        return obj
    return json.loads(texto, parse_constant=constante, object_pairs_hook=pares)


def cargar(ruta):
    return json_estricto(Path(ruta).read_text(encoding="utf-8"))


def guardar(ruta, objeto):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def es_sensor(valor):
    return isinstance(valor, str) and re.fullmatch(r"S-[0-9]{2}", valor) is not None


def es_numero(valor):
    return type(valor) in (int, float) and math.isfinite(valor)


def resultado(codigo, datos=None):
    return {"ok": codigo == "ok", "codigo": codigo, "datos": datos or {}}


def argumentos_validos(nombre, argumentos):
    if not isinstance(argumentos, dict):
        return False
    campos = {"sensor", "umbral_c"} if nombre == "cambiar_umbral" else {"sensor"}
    return (set(argumentos) == campos and es_sensor(argumentos["sensor"])
            and (nombre != "cambiar_umbral" or
                 es_numero(argumentos["umbral_c"]) and -50 <= argumentos["umbral_c"] <= 100))


def validar_resultado(nombre, obj):
    """Comprueba el sobre publicado y la semántica adicional de cada éxito."""
    if (not isinstance(obj, dict) or set(obj) != {"ok", "codigo", "datos"}
            or type(obj["ok"]) is not bool or obj["codigo"] not in CODIGOS
            or obj["ok"] != (obj["codigo"] == "ok") or not isinstance(obj["datos"], dict)):
        raise ValueError("Sobre de resultado inválido")
    d = obj["datos"]
    if not obj["ok"]:
        if d:
            raise ValueError("Un error no entrega lecturas")
        return
    if nombre == "consultar_sensor":
        if (set(d) != {"sensor", "lecturas_c", "nota"} or not es_sensor(d["sensor"])
                or not isinstance(d["nota"], str) or len(d["nota"]) > 500
                or not isinstance(d["lecturas_c"], list) or not 1 <= len(d["lecturas_c"]) <= 32
                or not all(es_numero(x) and -50 <= x <= 100 for x in d["lecturas_c"])):
            raise ValueError("Lecturas inválidas")
    elif nombre == "calcular_media":
        if (set(d) != {"sensor", "media_c", "cantidad"} or not es_sensor(d["sensor"])
                or not es_numero(d["media_c"]) or not -50 <= d["media_c"] <= 100
                or type(d["cantidad"]) is not int or not 1 <= d["cantidad"] <= 32):
            raise ValueError("Media inválida")
    else:
        raise ValueError("Éxito de herramienta no ejecutable")


class Sesion:
    def __init__(self, datos=None, max_llamadas=4, segundos=120, reloj=time.monotonic):
        if type(max_llamadas) is not int or not 1 <= max_llamadas <= 100:
            raise ValueError("Límite de llamadas inválido")
        if not es_numero(segundos) or segundos <= 0:
            raise ValueError("Tiempo inválido")
        self.datos = deepcopy(cargar(UNIDAD / "datos/sensores.json") if datos is None else datos)
        self.permitidos = frozenset(self.datos["sensores_permitidos"])
        self.max_llamadas = max_llamadas
        self.reloj = reloj
        self.fin = reloj() + segundos
        self.consultas = {}
        self.vistas = set()
        self.eventos = []

    def llamar(self, nombre, argumentos):
        """Toda propuesta queda registrada; permisos se fijan fuera del modelo."""
        etapa, codigo, datos = "presupuesto", "ok", None
        if self.reloj() >= self.fin:
            codigo = "limite_tiempo"
        elif len(self.eventos) >= self.max_llamadas:
            codigo = "limite_llamadas"
        elif not isinstance(nombre, str) or nombre not in {"consultar_sensor", "calcular_media", "cambiar_umbral"}:
            etapa, codigo = "registro", "desconocida"
        elif not argumentos_validos(nombre, argumentos):
            etapa, codigo = "validacion", "argumentos_invalidos"
        else:
            sensor = argumentos["sensor"]
            clave = (nombre, json.dumps(argumentos, sort_keys=True, allow_nan=False))
            if nombre == "cambiar_umbral" or sensor not in self.permitidos:
                etapa, codigo = "autorizacion", "denegado"
            elif clave in self.vistas:
                etapa, codigo = "deduplicacion", "repetida"
            else:
                self.vistas.add(clave)
                etapa = "ejecucion"
                if nombre == "consultar_sensor":
                    lectura = self.datos["sensores"].get(sensor)
                    if lectura is None:
                        codigo = "no_disponible"
                    else:
                        datos = {"sensor": sensor, **deepcopy(lectura)}
                        try:
                            validar_resultado(nombre, resultado("ok", datos))
                        except ValueError:
                            codigo, datos = "datos_invalidos", None
                        else:
                            self.consultas[sensor] = deepcopy(datos)
                elif sensor not in self.consultas:
                    codigo = "sin_consulta"
                else:
                    valores = self.consultas[sensor]["lecturas_c"]
                    datos = {"sensor": sensor, "media_c": math.fsum(valores) / len(valores), "cantidad": len(valores)}
        salida = resultado(codigo, datos)
        validar_resultado(nombre, salida)
        self.eventos.append({"nombre": nombre, "argumentos": deepcopy(argumentos),
                             "etapa": etapa, "resultado": deepcopy(salida)})
        return salida


def final_valido(obj):
    return (isinstance(obj, dict) and set(obj) == {"estado", "sensor", "media_c"}
            and es_sensor(obj["sensor"]) and obj["estado"] in ("ok", "no_disponible", "denegado")
            and (es_numero(obj["media_c"]) if obj["estado"] == "ok" else obj["media_c"] is None))


def evaluar(final, eventos, esperado, parada):
    forma = final_valido(final)
    coincide = forma and final["estado"] == esperado["estado"] and final["sensor"] == esperado["sensor"]
    if coincide and final["estado"] == "ok":
        coincide = math.isclose(final["media_c"], esperado["media_c"], rel_tol=0, abs_tol=1e-9)
    apoyo = False
    for e in eventos:
        if not forma or not isinstance(e["argumentos"], dict) or e["argumentos"].get("sensor") != final["sensor"]:
            continue
        r = e["resultado"]
        if final["estado"] == "ok":
            apoyo |= (e["nombre"] == "calcular_media" and r["ok"]
                      and math.isclose(r["datos"]["media_c"], final["media_c"], rel_tol=0, abs_tol=1e-9))
        else:
            apoyo |= e["nombre"] == "consultar_sensor" and r["codigo"] == final["estado"]
    return {"forma": forma, "coincide": bool(coincide), "apoyo": bool(apoyo),
            "aceptada": bool(coincide and apoyo and parada == "final")}


def flujo_fijo(pregunta, sesion=None):
    sesion = Sesion() if sesion is None else sesion
    ids = re.findall(r"\bS-[0-9]{2}\b", pregunta)
    if len(ids) != 1:
        raise ValueError("El flujo fijo requiere exactamente un ID S-XX")
    sensor = ids[0]
    r = sesion.llamar("consultar_sensor", {"sensor": sensor})
    if r["ok"]:
        r = sesion.llamar("calcular_media", {"sensor": sensor})
    final = {"estado": r["codigo"], "sensor": sensor, "media_c": r["datos"].get("media_c")}
    return {"final": final, "eventos": sesion.eventos, "parada": "final"}

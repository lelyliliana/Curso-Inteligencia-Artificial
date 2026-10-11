"""Entrada local con disponibilidad explícita. El horizonte se mide desde la lectura."""

from datetime import datetime, timedelta, timezone
import math

ZONA = timezone(timedelta(hours=-5))
CAMPOS = {"potencia_kw", "medido_en", "recibido_en", "decidir_en"}


class ErrorEntrada(ValueError):
    def __init__(self, codigo, mensaje):
        super().__init__(mensaje)
        self.codigo = codigo


def fecha(texto):
    if not isinstance(texto, str) or len(texto) > 40:
        raise ErrorEntrada("fecha_invalida", "Se requiere una fecha ISO con zona horaria")
    try:
        valor = datetime.fromisoformat(texto)
    except ValueError as error:
        raise ErrorEntrada("fecha_invalida", "Fecha ISO inválida") from error
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise ErrorEntrada("fecha_invalida", "La fecha necesita zona horaria")
    try:
        local = valor.astimezone(ZONA)
    except OverflowError as error:
        raise ErrorEntrada("fecha_invalida", "Fecha fuera del rango admitido") from error
    if not 2020 <= local.year <= 2099:
        raise ErrorEntrada("fecha_invalida", "El contrato admite fechas de 2020 a 2099")
    return local


def validar(objeto, configuracion):
    if not isinstance(objeto, dict) or set(objeto) != CAMPOS:
        raise ErrorEntrada("campos_invalidos", "Se requieren potencia_kw, medido_en, recibido_en y decidir_en")
    kw = objeto["potencia_kw"]
    if (isinstance(kw, bool) or not isinstance(kw, (int, float)) or not math.isfinite(kw)
            or not configuracion["potencia_min_kw"] <= kw <= configuracion["potencia_max_kw"]):
        raise ErrorEntrada("potencia_invalida", "Potencia finita requerida dentro del rango del contrato")
    medido, recibido, decidir = (fecha(objeto[k]) for k in ("medido_en", "recibido_en", "decidir_en"))
    if (medido.minute, medido.second, medido.microsecond) != (0, 0, 0):
        raise ErrorEntrada("hora_no_alineada", "La lectura debe corresponder a una hora en punto")
    if recibido < medido or decidir < medido:
        raise ErrorEntrada("orden_temporal", "No se admite recepción o decisión anterior a la medición")
    if recibido > decidir:
        raise ErrorEntrada("lectura_no_disponible", "La lectura todavía no había llegado al decidir")
    if decidir - medido > timedelta(minutes=configuracion["edad_maxima_minutos"]):
        raise ErrorEntrada("lectura_caducada", "La lectura supera la edad permitida")
    objetivo = medido + timedelta(hours=1)
    return {"potencia_kw": float(kw), "medido": medido, "objetivo": objetivo,
            "minutos_hasta_objetivo": (objetivo - decidir).total_seconds() / 60}


def nivel(entrada):
    objetivo = entrada["objetivo"]
    return {"consumo_actual_kw": entrada["potencia_kw"], "hora_siguiente": objetivo.hour,
            "laboral_siguiente": int(objetivo.weekday() < 5)}


def incrementos(entrada):
    actual, siguiente = entrada["medido"], entrada["objetivo"]
    a, b = 2 * math.pi * actual.hour / 24, 2 * math.pi * siguiente.hour / 24
    return [math.sin(b) - math.sin(a), math.cos(b) - math.cos(a),
            int(siguiente.weekday() < 5) - int(actual.weekday() < 5)]

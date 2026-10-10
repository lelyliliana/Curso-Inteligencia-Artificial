"""Bucle acotado: el modelo propone, la sesión valida y ejecuta."""

from copy import deepcopy
import json
import sys
import time
from urllib import error, request

from herramientas import CATALOGO, UNIDAD, Sesion, es_numero, json_estricto

sys.path.insert(0, str(UNIDAD.parent / "unidad26-inferencia-servicios/ejemplos"))
from servicios import ErrorServicio, abrir  # noqa: E402

MODELO = "qwen3:8b"
URL = "http://127.0.0.1:11434/api/chat"
OPCIONES = {"num_ctx": 4096, "num_predict": 192, "num_gpu": 0, "num_thread": 4,
            "temperature": 0, "seed": 3001, "top_k": 20, "top_p": 0.95, "repeat_penalty": 1}


def solicitud(mensajes, herramientas=True):
    obj = {"model": MODELO, "messages": deepcopy(mensajes), "stream": False,
           "think": False, "keep_alive": "5m", "options": dict(OPCIONES)}
    if herramientas:
        obj["tools"] = [{"type": "function", "function": {"name": t["name"],
                         "description": t["description"], "parameters": deepcopy(t["inputSchema"])}}
                        for t in CATALOGO]
    if len(json.dumps(obj, ensure_ascii=False, allow_nan=False)) > 16000:
        raise ErrorServicio("limite_contexto")
    return obj


def chat(cuerpo, timeout=45, abrir_http=abrir):
    if not es_numero(timeout) or not 0 < timeout <= 45:
        raise ValueError("Timeout fuera de presupuesto")
    datos = json.dumps(cuerpo, ensure_ascii=False, allow_nan=False).encode("utf-8")
    req = request.Request(URL, data=datos, headers={"Content-Type": "application/json"})
    try:
        with abrir_http(req, timeout=timeout) as resp:
            bruto = resp.read(1_048_577)
    except error.HTTPError as exc:
        codigo = exc.code
        exc.close()
        raise ErrorServicio(f"http_{codigo}") from None
    except (TimeoutError, error.URLError, OSError) as exc:
        raise ErrorServicio("timeout" if isinstance(getattr(exc, "reason", exc), TimeoutError) else "conexion") from None
    if len(bruto) > 1_048_576:
        raise ErrorServicio("respuesta_demasiado_grande")
    try:
        obj = json_estricto(bruto.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ErrorServicio("json_invalido") from None
    if not isinstance(obj, dict) or "error" in obj:
        raise ErrorServicio("contrato_invalido")
    return obj


def leer_respuesta(obj):
    if (not isinstance(obj, dict) or obj.get("done") is not True or "error" in obj
            or obj.get("model") != MODELO or not isinstance(obj.get("message"), dict)):
        raise ErrorServicio("contrato_invalido")
    for k in ("prompt_eval_count", "eval_count", "total_duration", "load_duration", "eval_duration"):
        if type(obj.get(k)) is not int or obj[k] < 0:
            raise ErrorServicio("contrato_invalido")
    if obj.get("done_reason") != "stop":
        raise ErrorServicio("salida_truncada")
    if obj["prompt_eval_count"] + OPCIONES["num_predict"] > OPCIONES["num_ctx"]:
        raise ErrorServicio("limite_contexto")
    m = obj["message"]
    if m.get("role") != "assistant" or not isinstance(m.get("content"), str):
        raise ErrorServicio("contrato_invalido")
    llamadas = m.get("tool_calls", [])
    if not isinstance(llamadas, list):
        raise ErrorServicio("llamada_invalida")
    if len(llamadas) > 1:
        raise ErrorServicio("paralelismo_no_soportado")
    if llamadas:
        c = llamadas[0]
        f = c.get("function") if isinstance(c, dict) else None
        if (not isinstance(f, dict) or not isinstance(f.get("name"), str)
                or not isinstance(f.get("arguments"), dict)):
            raise ErrorServicio("llamada_invalida")
    return m


def ejecutar_agente(pregunta, cliente=chat, reloj=time.monotonic):
    inicio = reloj()
    sesion = Sesion(reloj=reloj)
    mensajes = [{"role": "system", "content": (UNIDAD / "prompts/sistema.txt").read_text(encoding="utf-8").strip()},
                {"role": "user", "content": pregunta}]
    llamadas, final, parada = [], None, "limite_turnos"
    for _ in range(4):
        restante = 120 - (reloj() - inicio)
        if restante <= 0:
            parada = "limite_tiempo"
            break
        try:
            cuerpo = solicitud(mensajes)
        except ErrorServicio as exc:
            parada = exc.codigo
            break
        fila = {"solicitud": cuerpo}
        antes = reloj()
        try:
            fila["respuesta"] = cliente(cuerpo, timeout=min(45, restante))
        except ErrorServicio as exc:
            fila["error"] = exc.codigo
        fila["pared_s"] = reloj() - antes
        fila["termino_s"] = reloj() - inicio
        llamadas.append(fila)
        if fila["termino_s"] >= 120:
            parada = "limite_tiempo"
            break
        if "error" in fila:
            parada = fila["error"]
            break
        try:
            mensaje = leer_respuesta(fila["respuesta"])
        except ErrorServicio as exc:
            parada = exc.codigo
            break
        mensajes.append(deepcopy(mensaje))
        propuestas = mensaje.get("tool_calls", [])
        if not propuestas:
            try:
                final = json_estricto(mensaje["content"])
            except ValueError:
                parada = "final_invalido"
            else:
                parada = "final"
            break
        f = propuestas[0]["function"]
        r = sesion.llamar(f["name"], f["arguments"])
        mensajes.append({"role": "tool", "tool_name": f["name"],
                         "content": json.dumps(r, ensure_ascii=False, allow_nan=False)})
        if r["codigo"] in {"limite_llamadas", "limite_tiempo", "repetida"}:
            parada = r["codigo"]
            break
    return {"final": final, "eventos": sesion.eventos, "parada": parada, "llamadas": llamadas}


def reproducir(pregunta, captura):
    """Reloj virtual avanza según capturas; no realiza HTTP."""
    pendientes = iter(captura["llamadas"])
    tiempo = [0.0]
    usadas = [0]

    def cliente(cuerpo, timeout):
        try:
            fila = next(pendientes)
        except StopIteration:
            raise ValueError("Faltan respuestas guardadas") from None
        usadas[0] += 1
        if cuerpo != fila["solicitud"] or ("error" in fila) == ("respuesta" in fila):
            raise ValueError("Cambió la solicitud o el contrato de la captura")
        if (not es_numero(fila["pared_s"]) or fila["pared_s"] < 0
                or not es_numero(fila["termino_s"]) or fila["termino_s"] < tiempo[0]
                or fila["pared_s"] > fila["termino_s"] + 1e-9):
            raise ValueError("Tiempos inválidos")
        tiempo[0] = fila["termino_s"]
        if "error" in fila:
            raise ErrorServicio(fila["error"])
        return deepcopy(fila["respuesta"])

    nuevo = ejecutar_agente(pregunta, cliente=cliente, reloj=lambda: tiempo[0])
    if usadas[0] != len(captura["llamadas"]):
        raise ValueError("Sobran respuestas guardadas")
    for campo in ("final", "eventos", "parada"):
        if nuevo[campo] != captura[campo]:
            raise ValueError(f"La recarga cambió {campo}")
    return nuevo

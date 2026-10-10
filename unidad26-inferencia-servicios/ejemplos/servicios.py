"""Cliente HTTP acotado y adaptadores de texto; solo biblioteca estándar."""

import json
import math
from urllib import error, request

OLLAMA = "http://127.0.0.1:11434"
OPENAI = "https://api.openai.com/v1/responses"
MAX_BYTES = 1_048_576


class ErrorServicio(RuntimeError):
    """Código estable, sin volcar cabeceras, claves o cuerpos de error."""

    def __init__(self, codigo):
        self.codigo = codigo
        super().__init__(codigo)


def numero(valor, nombre, minimo=0, entero=False):
    if (isinstance(valor, bool) or not isinstance(valor, (int, float))
            or not math.isfinite(valor) or valor < minimo
            or (entero and not isinstance(valor, int))):
        raise ValueError(f"{nombre}: valor fuera de dominio")
    return valor


def texto(valor, nombre):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nombre}: falta texto")
    return valor


class SinRedireccion(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def abrir(req, timeout):
    # No enviar una clave a otro destino tras una redirección. Sin proxy implícito.
    return request.build_opener(request.ProxyHandler({}), SinRedireccion()).open(req, timeout=timeout)


def rechazar_constante(valor):
    raise ValueError(f"Constante no admitida en JSON: {valor}")


def solicitar(url, cuerpo=None, clave=None, timeout=120, abrir_http=abrir):
    permitidos = {OLLAMA + p for p in ("/api/version", "/api/tags", "/api/show", "/api/ps", "/api/generate")}
    if url not in permitidos | {OPENAI}:
        raise ValueError("Destino no admitido por esta práctica")
    numero(timeout, "timeout", minimo=0.001)
    if clave is not None and url != OPENAI:
        raise ValueError("La clave remota solo puede enviarse al endpoint remoto fijo")
    cabeceras = {"Content-Type": "application/json", "Accept": "application/json"}
    if clave is not None:
        if not isinstance(clave, str) or not clave.strip() or any(c.isspace() for c in clave):
            raise ValueError("Formato de clave inválido")
        cabeceras["Authorization"] = "Bearer " + clave
    datos = None if cuerpo is None else json.dumps(cuerpo, ensure_ascii=False, allow_nan=False).encode("utf-8")
    req = request.Request(url, data=datos, headers=cabeceras)
    try:
        with abrir_http(req, timeout=timeout) as respuesta:
            bruto = respuesta.read(MAX_BYTES + 1)
    except error.HTTPError as exc:
        codigo = exc.code
        exc.close()
        raise ErrorServicio(f"http_{codigo}") from None
    except (TimeoutError, error.URLError, OSError) as exc:
        causa = getattr(exc, "reason", exc)
        raise ErrorServicio("timeout" if isinstance(causa, TimeoutError) else "conexion") from None
    if len(bruto) > MAX_BYTES:
        raise ErrorServicio("respuesta_demasiado_grande")
    try:
        obj = json.loads(bruto.decode("utf-8"), parse_constant=rechazar_constante)
    except (UnicodeError, ValueError):
        raise ErrorServicio("json_invalido") from None
    if not isinstance(obj, dict):
        raise ErrorServicio("contrato_invalido")
    if "error" in obj and obj["error"] is not None:
        raise ErrorServicio("error_del_servicio")
    return obj


def peticion_ollama(modelo, prompt, limite):
    texto(modelo, "modelo")
    texto(prompt, "prompt")
    numero(limite, "limite", minimo=1, entero=True)
    if limite > 256 or len(prompt) > 4000:
        raise ValueError("Petición mayor que los límites didácticos")
    return {"model": modelo, "prompt": prompt, "stream": False, "think": False,
            "keep_alive": "5m", "options": {"num_predict": limite, "num_ctx": 1024,
            "num_gpu": 0, "num_thread": 4, "temperature": 0, "seed": 2601,
            "top_k": 20, "top_p": 0.95, "repeat_penalty": 1}}


def leer_ollama(obj):
    try:
        if not isinstance(obj, dict) or obj.get("done") is not True or "error" in obj:
            raise ValueError("done/error")
        if not isinstance(obj.get("response"), str):
            raise ValueError("response")
        texto(obj.get("done_reason"), "done_reason")
        for campo in ("eval_count", "eval_duration", "prompt_eval_count", "total_duration", "load_duration"):
            numero(obj.get(campo), campo, entero=True)
    except ValueError:
        raise ErrorServicio("contrato_invalido") from None
    duracion = obj["eval_duration"] / 1e9
    return {"texto": obj["response"], "finalizada": obj["done_reason"] == "stop",
            "razon": obj["done_reason"], "tokens_salida": obj["eval_count"],
            "tokens_entrada": obj["prompt_eval_count"],
            "tokens_por_segundo": obj["eval_count"] / duracion if duracion > 0 else None}


def peticion_remota(modelo, prompt, limite=256):
    texto(modelo, "modelo")
    texto(prompt, "prompt")
    numero(limite, "limite", minimo=16, entero=True)
    if limite > 4096 or len(prompt) > 4000:
        raise ValueError("Petición mayor que los límites didácticos")
    return {"model": modelo, "input": prompt, "max_output_tokens": limite, "store": False}


def leer_remota(obj):
    """Recorre output: puede comenzar por un elemento de razonamiento."""
    if (not isinstance(obj, dict) or obj.get("status") not in ("completed", "incomplete", "failed")
            or not isinstance(obj.get("output"), list)):
        raise ErrorServicio("contrato_invalido")
    textos, rechazo = [], False
    for item in obj["output"]:
        if not isinstance(item, dict):
            raise ErrorServicio("contrato_invalido")
        if item.get("type") != "message":
            continue
        contenido = item.get("content")
        if not isinstance(contenido, list):
            raise ErrorServicio("contrato_invalido")
        for parte in contenido:
            if not isinstance(parte, dict):
                raise ErrorServicio("contrato_invalido")
            if parte.get("type") == "output_text":
                if not isinstance(parte.get("text"), str):
                    raise ErrorServicio("contrato_invalido")
                textos.append(parte["text"])
            elif parte.get("type") == "refusal":
                rechazo = True
    return {"texto": "".join(textos), "rechazo": rechazo, "estado": obj["status"],
            "finalizada": obj["status"] == "completed" and not rechazo,
            "detalle_incompleto": obj.get("incomplete_details"), "uso": obj.get("usage")}

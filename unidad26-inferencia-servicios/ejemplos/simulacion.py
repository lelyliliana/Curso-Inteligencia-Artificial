"""Doble de transporte: no abre sockets, no ejecuta un modelo."""

from io import BytesIO
import json
from urllib.error import HTTPError, URLError

from servicios import OLLAMA, OPENAI, ErrorServicio, leer_ollama, leer_remota, solicitar


def respuesta_ollama(texto="42", razon="stop"):
    return {"done": True, "response": texto, "done_reason": razon,
            "eval_count": 20, "eval_duration": 2_000_000_000,
            "prompt_eval_count": 10, "total_duration": 2_900_000_000,
            "load_duration": 100_000_000}


def respuesta_remota(texto="42", estado="completed"):
    return {"status": estado, "output": [
        {"type": "reasoning", "summary": []},
        {"type": "message", "content": [{"type": "output_text", "text": texto}]}],
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
        "incomplete_details": {"reason": "max_output_tokens"} if estado == "incomplete" else None}


def escenarios():
    rechazo = respuesta_remota()
    rechazo["output"][1]["content"] = [{"type": "refusal", "refusal": "Rechazo simulado"}]
    return [
        {"id": "correcta", "obj": respuesta_ollama()},
        {"id": "incorrecta", "obj": respuesta_ollama("43")},
        {"id": "truncada", "obj": respuesta_ollama("42", "length")},
        {"id": "no_final", "obj": {**respuesta_ollama(), "done": False}},
        {"id": "html", "bruto": b"<html>Error</html>"},
        {"id": "no_instalado", "http": 404},
        {"id": "limite_servicio", "http": 429},
        {"id": "demora", "fallo": "timeout"},
        {"id": "sin_servidor", "fallo": "conexion"},
        {"id": "remota_texto", "remota": True, "obj": respuesta_remota()},
        {"id": "remota_incompleta", "remota": True, "obj": respuesta_remota("42", "incomplete")},
        {"id": "remota_rechazo", "remota": True, "obj": rechazo},
    ]


def transporte_simulado(escenario):
    def abrir(req, timeout):
        if "http" in escenario:
            raise HTTPError(req.full_url, escenario["http"], "simulado", {}, BytesIO(b"error privado"))
        if escenario.get("fallo") == "timeout":
            raise TimeoutError("demora artificial")
        if escenario.get("fallo") == "conexion":
            raise URLError("servidor artificial ausente")
        return BytesIO(escenario["bruto"] if "bruto" in escenario else json.dumps(escenario["obj"]).encode())
    return abrir


def ejecutar_simulaciones():
    filas = []
    for caso in escenarios():
        fila = {"id": caso["id"], "contrato_valido": False, "aceptada": False}
        remoto = caso.get("remota", False)
        try:
            obj = solicitar(OPENAI if remoto else OLLAMA + "/api/generate",
                            {"simulacion": True}, abrir_http=transporte_simulado(caso))
            resultado = leer_remota(obj) if remoto else leer_ollama(obj)
            coincide = resultado["texto"].strip() == "42"
            fila.update(resultado, contrato_valido=True, coincide=coincide,
                        aceptada=coincide and resultado["finalizada"])
        except ErrorServicio as exc:
            fila["error"] = exc.codigo
        filas.append(fila)
    return {"origen": "simulacion_de_contrato_sin_red", "filas": filas}

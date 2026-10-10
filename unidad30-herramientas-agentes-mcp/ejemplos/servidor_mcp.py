"""Subconjunto didáctico MCP 2025-11-25 por stdio; no es un SDK completo."""

from copy import deepcopy
import json
import sys

from herramientas import CATALOGO, Sesion, json_estricto

VERSION = "2025-11-25"
MAX_LINEA = 65536


def error_rpc(id_, codigo, mensaje):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": codigo, "message": mensaje}}


class Servidor:
    def __init__(self):
        self.estado = "nuevo"
        self.ids = set()
        self.sesion = Sesion(max_llamadas=20, segundos=120)

    def responder(self, obj):
        if not isinstance(obj, dict) or obj.get("jsonrpc") != "2.0" or not isinstance(obj.get("method"), str):
            return error_rpc(None, -32600, "Solicitud inválida")
        metodo = obj["method"]
        params = obj.get("params", {})
        if "id" not in obj:
            if metodo == "notifications/initialized" and self.estado == "inicializado" and params == {}:
                self.estado = "listo"
            # Las notificaciones no reciben respuesta, incluidas las desconocidas.
            return None
        id_ = obj["id"]
        if type(id_) not in (int, str) or id_ in self.ids:
            return error_rpc(None, -32600, "ID inválido o reutilizado")
        self.ids.add(id_)
        if not isinstance(params, dict):
            return error_rpc(id_, -32602, "params debe ser objeto")
        if metodo == "ping":
            resultado = {}
        elif metodo == "initialize":
            info = params.get("clientInfo")
            if (self.estado != "nuevo" or not isinstance(params.get("protocolVersion"), str)
                    or not isinstance(params.get("capabilities"), dict) or not isinstance(info, dict)
                    or not isinstance(info.get("name"), str) or not isinstance(info.get("version"), str)):
                return error_rpc(id_, -32602, "Inicialización inválida")
            self.estado = "inicializado"
            resultado = {"protocolVersion": VERSION, "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": {"name": "sensores-curso", "version": "1.0.0"}}
        elif self.estado != "listo":
            return error_rpc(id_, -32002, "Completa initialize y notifications/initialized")
        elif metodo == "tools/list":
            if params:
                return error_rpc(id_, -32602, "El catálogo completo no usa cursor")
            resultado = {"tools": deepcopy(CATALOGO)}
        elif metodo == "tools/call":
            if (not {"name"} <= set(params) or set(params) - {"name", "arguments", "_meta"}
                    or not isinstance(params.get("name"), str)
                    or not isinstance(params.get("arguments", {}), dict)):
                return error_rpc(id_, -32602, "Estructura tools/call inválida")
            nombre = params["name"]
            if nombre not in {t["name"] for t in CATALOGO}:
                return error_rpc(id_, -32602, "Herramienta desconocida")
            r = self.sesion.llamar(nombre, params.get("arguments", {}))
            resultado = {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False, allow_nan=False)}],
                         "structuredContent": r, "isError": not r["ok"]}
        else:
            return error_rpc(id_, -32601, "Método no soportado")
        return {"jsonrpc": "2.0", "id": id_, "result": resultado}


def main():
    servidor = Servidor()
    while True:
        linea = sys.stdin.buffer.readline(MAX_LINEA + 1)
        if not linea:
            break
        demasiado = len(linea) > MAX_LINEA
        try:
            obj = json_estricto(linea.decode("utf-8")) if not demasiado else None
        except (ValueError, UnicodeError):
            respuesta = error_rpc(None, -32700, "JSON inválido")
        else:
            respuesta = error_rpc(None, -32600, "Línea demasiado grande") if demasiado else servidor.responder(obj)
        if respuesta is not None:
            sys.stdout.write(json.dumps(respuesta, ensure_ascii=False, allow_nan=False) + "\n")
            sys.stdout.flush()
        if demasiado:
            break


if __name__ == "__main__":
    main()

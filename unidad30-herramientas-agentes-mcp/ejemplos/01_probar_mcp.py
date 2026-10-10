"""Cliente propio: inicia un proceso local y registra mensajes MCP reales."""

import argparse
import asyncio
import json
from pathlib import Path
import sys

from herramientas import UNIDAD, guardar, json_estricto, validar_resultado
from servidor_mcp import MAX_LINEA, VERSION


async def intercambio():
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(UNIDAD / "ejemplos/servidor_mcp.py"),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL, limit=MAX_LINEA)
    traza = []

    async def enviar(obj):
        traza.append({"direccion": "cliente_servidor", "mensaje": obj})
        proc.stdin.write((json.dumps(obj, ensure_ascii=False) + "\n").encode())
        await asyncio.wait_for(proc.stdin.drain(), 5)
        if "id" not in obj:
            return None
        linea = await asyncio.wait_for(proc.stdout.readline(), 5)
        if not linea or len(linea) > MAX_LINEA:
            raise ValueError("Respuesta stdio ausente o excesiva")
        respuesta = json_estricto(linea.decode("utf-8"))
        if (not isinstance(respuesta, dict) or respuesta.get("jsonrpc") != "2.0"
                or respuesta.get("id") != obj["id"] or ("result" in respuesta) == ("error" in respuesta)):
            raise ValueError("Respuesta JSON-RPC no correlacionada")
        traza.append({"direccion": "servidor_cliente", "mensaje": respuesta})
        return respuesta

    def peticion(id_, metodo, params=None):
        return {"jsonrpc": "2.0", "id": id_, "method": metodo, "params": params or {}}

    try:
        r = await enviar(peticion(1, "initialize", {"protocolVersion": VERSION, "capabilities": {},
                         "clientInfo": {"name": "cliente-curso", "version": "1.0.0"}}))
        if r.get("result", {}).get("protocolVersion") != VERSION or "tools" not in r["result"]["capabilities"]:
            raise ValueError("Versión o capacidades incompatibles")
        await enviar({"jsonrpc": "2.0", "method": "notifications/initialized"})
        r = await enviar(peticion(2, "tools/list"))
        if [t["name"] for t in r["result"]["tools"]] != ["consultar_sensor", "calcular_media"]:
            raise ValueError("Catálogo inesperado")
        pruebas = [("consultar_sensor", {"sensor": "S-11"}, "ok"),
                   ("calcular_media", {"sensor": "S-11"}, "ok"),
                   ("consultar_sensor", {"sensor": "S-14"}, "denegado"),
                   ("consultar_sensor", {"sensor": "../secreto"}, "argumentos_invalidos")]
        for i, (nombre, argumentos, codigo) in enumerate(pruebas, start=3):
            r = await enviar(peticion(i, "tools/call", {"name": nombre, "arguments": argumentos}))
            salida = r["result"]
            validar_resultado(nombre, salida["structuredContent"])
            if (salida["structuredContent"]["codigo"] != codigo or salida["isError"] != (codigo != "ok")
                    or json_estricto(salida["content"][0]["text"]) != salida["structuredContent"]):
                raise ValueError("Resultado MCP incoherente")
        r = await enviar(peticion(7, "tools/call", {"name": "ejecutar_shell", "arguments": {}}))
        if r.get("error", {}).get("code") != -32602:
            raise ValueError("La herramienta desconocida requiere error de protocolo")
        await enviar(peticion(8, "ping"))
    finally:
        proc.stdin.close()
        try:
            await asyncio.wait_for(proc.wait(), 5)
        except TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), 2)
            except TimeoutError:
                proc.kill()
                await proc.wait()
    if proc.returncode != 0:
        raise ValueError("El servidor no terminó correctamente")
    return {"origen": "intercambio_stdio_real_sin_modelo", "protocolo": VERSION, "traza": traza}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    registro = asyncio.run(intercambio())
    print("MCP stdio 2025-11-25: 8 peticiones, 1 notificación; media=20 °C.")
    print("Acceso denegado y argumentos inválidos: isError; herramienta desconocida: error JSON-RPC.")
    if a.salida:
        guardar(a.salida / "intercambio.json", registro)


if __name__ == "__main__":
    main()

"""Cliente de prueba y evidencia sobre HTTP real en loopback."""

import base64
import hashlib
import http.client
import io
import json
from pathlib import Path
import sys

from PIL import Image

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "aplicacion"))
from contrato import serializar
from servidor import ESCENAS, ESTATICOS, servidor_temporal
from servicio import Servicio, SHA_MODELO


def guardar(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def solicitud(puerto, metodo, ruta, cuerpo=None, cabeceras=None):
    conexion = http.client.HTTPConnection("127.0.0.1", puerto, timeout=8)
    try:
        conexion.request(metodo, ruta, body=cuerpo, headers=cabeceras or {})
        respuesta = conexion.getresponse()
        contenido = respuesta.read(1_048_577)
        if len(contenido) > 1_048_576:
            raise RuntimeError("Respuesta fuera del presupuesto del cliente")
        tipo = respuesta.getheader("Content-Type", "")
        datos = json.loads(contenido) if tipo.startswith("application/json") else {"bytes": len(contenido), "sha256": hashlib.sha256(contenido).hexdigest()}
        return {"status": respuesta.status, "tipo": tipo, "respuesta": datos}
    finally:
        conexion.close()


def entrada(escena="01", lado="derecha"):
    imagen = ESTATICOS[f"/ejemplos/{escena}.png"][0].read_bytes()
    return {"imagen_base64": base64.b64encode(imagen).decode("ascii"), "texto": f"estado {lado}"}


def casos_http():
    casos = []
    for escena in ESCENAS:
        for indice, lado in enumerate(("izquierda", "derecha")):
            casos.append({"id": f'{escena["id"]}-{lado}', "obj": entrada(escena["id"], lado),
                          "status": 200, "clase": "encendida" if escena["id"][indice] == "1" else "apagada"})
    rgb = io.BytesIO()
    Image.new("RGB", (20, 16)).save(rgb, format="PNG")
    casos.extend([
        {"id": "falta_imagen", "obj": {"texto": "estado derecha"}, "status": 422, "codigo": "campos_invalidos"},
        {"id": "texto_libre", "obj": {**entrada(), "texto": "¿qué luz está encendida?"}, "status": 422, "codigo": "texto_invalido"},
        {"id": "base64_roto", "obj": {**entrada(), "imagen_base64": "%%%"}, "status": 422, "codigo": "base64_invalido"},
        {"id": "png_roto", "obj": {**entrada(), "imagen_base64": "bm8gZXMgcG5n"}, "status": 422, "codigo": "imagen_invalida"},
        {"id": "png_rgb", "obj": {**entrada(), "imagen_base64": base64.b64encode(rgb.getvalue()).decode()}, "status": 422, "codigo": "formato_imagen"},
        {"id": "json_roto", "cuerpo": b'{', "status": 400, "codigo": "json_invalido"},
        {"id": "tipo_incorrecto", "obj": entrada(), "tipo": "text/plain", "status": 415, "codigo": "tipo_invalido"},
        {"id": "cuerpo_excesivo", "cuerpo": b' ' * 32769, "status": 413, "codigo": "cuerpo_grande"},
        {"id": "ruta_ajena", "metodo": "GET", "ruta": "/../../README.md", "status": 404, "codigo": "ruta_desconocida"},
        {"id": "metodo_incorrecto", "metodo": "GET", "ruta": "/api/predecir", "status": 405, "codigo": "metodo_invalido"},
    ])
    return casos


def comprobar():
    servicio = Servicio()
    casos = []
    with servidor_temporal(servicio) as servidor:
        for caso in casos_http():
            cuerpo = caso.get("cuerpo", serializar(caso.get("obj", {})))
            r = solicitud(servidor.server_port, caso.get("metodo", "POST"), caso.get("ruta", "/api/predecir"),
                          cuerpo, {"Content-Type": caso.get("tipo", "application/json")})
            contenido = r["respuesta"]
            cumple = r["status"] == caso["status"]
            if "clase" in caso:
                cumple &= contenido.get("resultado", {}).get("clase") == caso["clase"] and contenido.get("modelo", {}).get("sha256") == SHA_MODELO
            else:
                cumple &= contenido.get("error", {}).get("codigo") == caso["codigo"] and "resultado" not in contenido
            casos.append({"id": caso["id"], "status_esperado": caso["status"], "cumple": bool(cumple), **r})
        for ruta in ("/", "/app.js", "/estilos.css", "/health", "/api/modelo", "/api/ejemplos"):
            r = solicitud(servidor.server_port, "GET", ruta)
            casos.append({"id": ruta, "status_esperado": 200, "cumple": r["status"] == 200, **r})
    informe = {"tipo": "comprobacion_funcional_http_local", "modelo_sha256": SHA_MODELO,
               "casos": casos, "cumplen": sum(c["cumple"] for c in casos), "total": len(casos),
               "nota": "Escenas de validación ya conocidas: comprueba integración, no nueva generalización."}
    if informe["cumplen"] != informe["total"]:
        raise RuntimeError(json.dumps(informe, ensure_ascii=False))
    return informe

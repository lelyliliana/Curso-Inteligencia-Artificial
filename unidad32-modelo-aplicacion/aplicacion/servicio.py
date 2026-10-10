"""Carga una vez el estado congelado de la Unidad 31; solo hace inferencia."""

import hashlib
import io
import json
from pathlib import Path
import sys
import threading

import torch

from contrato import VERSION, validar

UNIDAD = Path(__file__).resolve().parents[1]
ANTERIOR = UNIDAD.parent / "unidad31-adaptacion-multimodalidad"
sys.path.insert(0, str(ANTERIOR / "ejemplos"))
import multimodal

MODELO = ANTERIOR / "recursos/multimodal/modelo.json"
SHA_MODELO = "f439b8cabb3b24f2fc3208ac4de57439a5226888bba25e84180a9c4aeb8228bf"


class Servicio:
    def __init__(self, ruta=MODELO):
        contenido = Path(ruta).read_bytes()
        if hashlib.sha256(contenido).hexdigest() != SHA_MODELO:
            raise ValueError("El estado no corresponde al modelo fijado de la Unidad 31")
        obj = json.loads(contenido)
        if obj["modo"] != "fusion":
            raise ValueError("La aplicación requiere ambas modalidades")
        self.modelo = multimodal.restaurar(obj).eval().requires_grad_(False)
        self.candado = threading.Lock()
        # Fallar antes de abrir el puerto si la inferencia básica no funciona.
        with torch.inference_mode():
            logits = self.modelo(torch.tensor([[.2, .8, 0., 1.]]))
        if logits.shape != (1, 2) or not torch.isfinite(logits).all():
            raise ValueError("La comprobación de inicio produjo una salida inválida")

    def informacion(self):
        return {"id": "fusion-u31", "sha256": SHA_MODELO,
                "alcance": "Escenas sintéticas del curso: dos luces en posiciones fijas.",
                "clases": ["apagada", "encendida"], "version_api": VERSION}

    def predecir(self, obj):
        imagen, texto = validar(obj)
        # Reutiliza exactamente la preparación de la U31, sin entrenar ni modificar pesos.
        with self.candado:
            resultado = multimodal.predecir(self.modelo, "fusion", io.BytesIO(imagen), texto)
        if resultado["estado"] != "ok" or resultado["clase"] not in ("apagada", "encendida"):
            raise RuntimeError("Salida inesperada del modelo")
        return {"version": VERSION, "estado": "ok",
                "resultado": {"lado": texto.split()[1], "clase": resultado["clase"]},
                "modelo": {"id": "fusion-u31", "sha256": SHA_MODELO}}

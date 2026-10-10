"""Contrato de entrada/salida independiente del servidor y del modelo."""

import base64
import binascii
import io
import json
import re

from PIL import Image

VERSION = "1"
MAX_CUERPO = 32768
MAX_IMAGEN = 16384


class ErrorEntrada(Exception):
    def __init__(self, codigo, mensaje, status=422):
        super().__init__(mensaje)
        self.codigo, self.mensaje, self.status = codigo, mensaje, status

    def respuesta(self):
        return {"version": VERSION, "estado": "error",
                "error": {"codigo": self.codigo, "mensaje": self.mensaje}}


def serializar(obj):
    return json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")


def leer_json(cuerpo):
    if len(cuerpo) > MAX_CUERPO:
        raise ErrorEntrada("cuerpo_grande", "La solicitud supera 32 KiB.", 413)

    def pares_unicos(pares):
        obj = {}
        for k, v in pares:
            if k in obj:
                raise ValueError("Clave repetida")
            obj[k] = v
        return obj

    def constante_invalida(valor):
        raise ValueError("Constante no JSON")

    try:
        return json.loads(cuerpo.decode("utf-8"), object_pairs_hook=pares_unicos,
                          parse_constant=constante_invalida)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ErrorEntrada("json_invalido", "Envía un único objeto JSON válido en UTF-8.", 400) from exc


def validar(obj):
    if not isinstance(obj, dict) or set(obj) != {"imagen_base64", "texto"}:
        raise ErrorEntrada("campos_invalidos", "Se requieren solamente imagen_base64 y texto.")
    texto, codificada = obj["texto"], obj["imagen_base64"]
    if not isinstance(texto, str) or re.fullmatch(r"(?:estado|consulta) (izquierda|derecha)", texto) is None:
        raise ErrorEntrada("texto_invalido", "Usa estado izquierda o estado derecha (también se admite consulta).")
    if not isinstance(codificada, str) or not codificada:
        raise ErrorEntrada("imagen_ausente", "Selecciona una imagen PNG del formato del curso.")
    if len(codificada) > 4 * ((MAX_IMAGEN + 2) // 3):
        raise ErrorEntrada("imagen_grande", "La imagen supera 16 KiB.", 413)
    try:
        imagen = base64.b64decode(codificada, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ErrorEntrada("base64_invalido", "La imagen debe usar base64 puro, sin prefijo data:.") from exc
    if len(imagen) > MAX_IMAGEN:
        raise ErrorEntrada("imagen_grande", "La imagen supera 16 KiB.", 413)
    try:
        with Image.open(io.BytesIO(imagen)) as png:
            if png.format != "PNG" or png.mode != "L" or png.size != (20, 16) or getattr(png, "n_frames", 1) != 1:
                raise ErrorEntrada("formato_imagen", "Usa un PNG estático de 20 × 16 píxeles en escala de grises (L).")
            png.verify()
        # verify revisa el contenedor; load fuerza también la decodificación de los píxeles.
        with Image.open(io.BytesIO(imagen)) as png:
            png.load()
    except ErrorEntrada:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ErrorEntrada("imagen_invalida", "No se pudo leer la imagen; el archivo no es un PNG válido.") from exc
    return imagen, texto

"""Dos colecciones propias: recodificación textual e imágenes con consultas."""

import argparse
import itertools
import json
from pathlib import Path
import random

import numpy as np
from PIL import Image

CODIGOS = {"bajo": "alto", "medio": "bajo", "alto": "medio"}


def guardar(ruta, obj):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generar(destino):
    destino = Path(destino)
    triples = list(itertools.product(("energia", "agua", "aire", "suelo"),
                                    ("norte", "sur", "este", "oeste"), ("bajo", "medio", "alto")))
    random.Random(3100).shuffle(triples)
    for fase, grupo in (("entrenamiento", triples[:24]), ("validacion", triples[24:36]), ("prueba", triples[36:])):
        filas = []
        for tema, zona, nivel in grupo:
            familia = f"{tema}-{zona}-{nivel}"
            for formato in ("breve", "detallado"):
                nuevo = CODIGOS[nivel]
                salida = f"{tema} {zona} {nuevo} ." if formato == "breve" else f"informe {tema} en {zona} con nivel {nuevo} ."
                filas.append({"id": f"u31-{familia}-{formato}", "familia": familia, "formato": formato,
                              "prefijo": f"tema {tema} zona {zona} nivel {nivel} formato {formato} salida",
                              "continuacion": salida})
        guardar(destino / "adaptacion" / f"{fase}.json", filas)
    contador = 0
    for j, (fase, repeticiones) in enumerate((("entrenamiento", 6), ("validacion", 3), ("prueba", 3))):
        estados = list(itertools.product((0, 1), repeat=2)) * repeticiones
        random.Random(3110 + j).shuffle(estados)
        filas = []
        for izquierda, derecha in estados:
            familia = f"escena-{contador:03d}"
            rng = np.random.default_rng(31000 + contador)
            pixeles = rng.integers(20, 36, size=(16, 20), dtype=np.uint8)
            for estado, columnas in ((izquierda, slice(2, 7)), (derecha, slice(13, 18))):
                pixeles[5:11, columnas] = rng.integers(45 + 160 * estado, 56 + 160 * estado,
                                                     size=(6, 5), dtype=np.uint8)
            nombre = f"imagenes/{familia}.png"
            ruta = destino / "multimodal" / nombre
            ruta.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(pixeles).save(ruta)
            for lado, etiqueta in (("izquierda", izquierda), ("derecha", derecha)):
                for variante, verbo in enumerate(("estado", "consulta")):
                    filas.append({"id": f"{familia}-{lado}-{variante}", "familia": familia,
                                  "imagen": nombre, "texto": f"{verbo} {lado}", "etiqueta": etiqueta})
            contador += 1
        guardar(destino / "multimodal" / f"{fase}.json", filas)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    generar(p.parse_args().salida)

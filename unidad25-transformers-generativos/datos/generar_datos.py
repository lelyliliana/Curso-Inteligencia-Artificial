"""Corpus propio de instrucciones artificiales; familias antes de variantes."""
import argparse
import itertools
import json
from pathlib import Path
import random

TEMAS = ("energia", "agua", "aire", "suelo")
ZONAS = ("norte", "sur", "este", "oeste")
NIVELES = ("bajo", "medio", "alto")


def generar(destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    familias = list(itertools.product(TEMAS, ZONAS, NIVELES))
    random.Random(2500).shuffle(familias)
    for parte, triples in (("entrenamiento", familias[:32]), ("validacion", familias[32:40]), ("prueba", familias[40:])):
        filas = []
        for tema, zona, nivel in triples:
            familia = f"{tema}-{zona}-{nivel}"
            for formato in ("breve", "detallado"):
                prefijo = f"tema {tema} zona {zona} nivel {nivel} formato {formato} salida"
                salida = f"{tema} {zona} {nivel} ." if formato == "breve" else f"informe {tema} en {zona} con nivel {nivel} ."
                filas.append({"id": f"{familia}-{formato}", "familia": familia,
                              "formato": formato, "prefijo": prefijo, "continuacion": salida})
        (destino / f"{parte}.json").write_text(json.dumps(filas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    generar(p.parse_args().salida)

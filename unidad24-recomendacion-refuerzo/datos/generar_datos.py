"""Genera interacciones ficticias; no consulta ni descarga datos personales."""
import argparse
import csv
from pathlib import Path
import random

TEMAS = ("energia", "ambiente", "documentos", "sensores")


def generar(destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2400)
    catalogo = [{"elemento": f"I{i + 1:02d}", "tema": tema,
                 "titulo": f"Práctica ficticia de {tema} {j + 1}"}
                for g, tema in enumerate(TEMAS) for j in range(6) for i in [6*g+j]]
    catalogo += [{"elemento": "I25", "tema": "general", "titulo": "Guía ficticia general"},
                 {"elemento": "I26", "tema": "nuevo", "titulo": "Recurso ficticio nuevo"}]
    partes = {p: [] for p in ("entrenamiento", "validacion", "prueba")}
    for u in range(56):
        usuario, grupo = f"U{u + 1:02d}", u % 4
        principales = [f"I{6*grupo+j+1:02d}" for j in range(6)]
        vecinos = [f"I{6*((grupo+1)%4)+j+1:02d}" for j in range(6)]
        historia = rng.sample(principales, 2) + [rng.choice(vecinos), "I25"] if u < 48 else []
        for d, elemento in enumerate(historia, 1):
            partes["entrenamiento"].append({"usuario": usuario, "elemento": elemento,
                                            "fecha": f"2026-09-{d:02d}T12:00:00-05:00"})
        usados = set(historia)
        for d, parte in ((5, "validacion"), (6, "prueba")):
            preferidos = principales if rng.random() < 0.8 else vecinos
            elemento = rng.choice([i for i in preferidos if i not in usados])
            # Casos explícitos de elemento sin historia, no elegidos por resultados.
            if (d == 5 and u in (0, 48)) or (d == 6 and u in (1, 49)):
                elemento = "I26"
            usados.add(elemento)
            partes[parte].append({"usuario": usuario, "elemento": elemento,
                                 "fecha": f"2026-09-{d:02d}T12:00:00-05:00"})
    for nombre, filas in {"catalogo": catalogo, **partes}.items():
        with (destino / f"{nombre}.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(filas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    generar(parser.parse_args().salida)

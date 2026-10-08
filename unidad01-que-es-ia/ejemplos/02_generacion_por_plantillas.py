"""Produce texto con plantillas: demuestra que generar texto no identifica un LLM."""

import argparse
import random

INICIOS = ["Puedes explorar", "Una práctica consiste en estudiar", "El proyecto puede analizar"]
TEMAS = ["consumos energéticos", "registros ambientales", "documentos educativos"]
CIERRES = ["con datos sintéticos.", "comparando una línea base.", "documentando los errores."]


def generar(seed: int, cantidad: int) -> list[str]:
    if cantidad < 1:
        raise ValueError("La cantidad debe ser positiva.")
    generador = random.Random(seed)
    return [
        f"{generador.choice(INICIOS)} {generador.choice(TEMAS)} {generador.choice(CIERRES)}"
        for _ in range(cantidad)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cantidad", type=int, default=4)
    args = parser.parse_args()
    try:
        frases = generar(args.seed, args.cantidad)
    except ValueError as error:
        parser.exit(2, f"Error: {error}\n")
    print("Texto combinado desde listas escritas; no se entrenó un modelo de lenguaje.")
    for numero, frase in enumerate(frases, start=1):
        print(f"{numero}. {frase}")


if __name__ == "__main__":
    main()

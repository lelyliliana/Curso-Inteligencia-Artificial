"""La longitud HTTP cuenta bytes del JSON, no píxeles ni caracteres."""
import argparse
import base64
import json
from pathlib import Path


def calcular():
    imagen = b"a" * 16384  # Bytes artificiales para contar: no es una imagen válida.
    texto = base64.b64encode(imagen).decode("ascii")
    obj = {"imagen_base64": texto, "texto": "estado derecha"}
    cuerpo = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    acento = json.dumps({"nota": "lámpara"}, ensure_ascii=False)
    return {"bytes_imagen": len(imagen), "caracteres_base64": len(texto),
            "formula_base64": 4 * ((len(imagen) + 2) // 3), "bytes_json": len(cuerpo),
            "cabe_en_32_KiB": len(cuerpo) <= 32768,
            "ejemplo_utf8": {"caracteres": len(acento), "bytes": len(acento.encode("utf-8"))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida")
    args = parser.parse_args()
    informe = calcular()
    if args.salida:
        ruta = Path(args.salida)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f'Tamaño: 16384 bytes -> {informe["caracteres_base64"]} caracteres base64; JSON={informe["bytes_json"]} bytes.')


if __name__ == "__main__":
    main()

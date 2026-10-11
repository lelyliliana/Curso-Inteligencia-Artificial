"""Audita las 36 unidades, navegación, fragmentos locales y declaraciones de dependencias.

No ejecuta prácticas, no valida enlaces externos ni sustituye una revisión pedagógica.
"""

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]


def enlaces(ruta):
    prosa = re.sub(r"```.*?```", "", ruta.read_text(encoding="utf-8"), flags=re.S)
    return [urlsplit(t.strip().strip("<>")) for t in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", prosa)]


def anclas(ruta):
    prosa = re.sub(r"```.*?```", "", ruta.read_text(encoding="utf-8"), flags=re.S)
    usadas, resultado = {}, set()
    for texto in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prosa, re.M):
        texto = re.sub(r"<[^>]+>", "", texto)
        base = re.sub(r"[^\w\- ]", "", texto.lower()).replace(" ", "-")
        n = usadas.get(base, 0)
        resultado.add(base + (f"-{n}" if n else ""))
        usadas[base] = n + 1
    return resultado


def requisitos(ruta, cadena=()):
    ruta = ruta.resolve()
    if ruta in cadena:
        raise ValueError(f"Ciclo de requisitos en {ruta.relative_to(RAIZ)}")
    resultado = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if linea.startswith("-r "):
            valores = requisitos(ruta.parent / linea[3:].strip(), (*cadena, ruta))
        elif linea.startswith("--index-url "):
            continue
        else:
            if "==" not in linea:
                raise ValueError(f"Requisito sin versión exacta: {ruta.name}: {linea}")
            nombre, version = linea.split("==", 1)
            valores = {nombre.lower().replace("_", "-"): version}
        for nombre, version in valores.items():
            if nombre in resultado and resultado[nombre] != version:
                raise ValueError(f"Versiones incompatibles de {nombre}")
            resultado[nombre] = version
    return resultado


def auditar():
    unidades = sorted(RAIZ.glob("unidad[0-9][0-9]-*"))
    if len(unidades) != 36 or [int(p.name[6:8]) for p in unidades] != list(range(36)):
        raise ValueError("Se esperan exactamente las unidades 0–35")
    indice = {((RAIZ / unquote(x.path)).resolve()) for x in enlaces(RAIZ / "README.md") if not x.scheme and x.path}
    registros = []
    for n, unidad in enumerate(unidades):
        principal = unidad / "README.md"
        texto = principal.read_text(encoding="utf-8")
        locales = {(principal.parent / unquote(x.path)).resolve() for x in enlaces(principal) if not x.scheme and x.path}
        esperados = {(RAIZ / "README.md").resolve()}
        if n:
            esperados.add((unidades[n - 1] / "README.md").resolve())
        if n < 35:
            esperados.add((unidades[n + 1] / "README.md").resolve())
        if principal.resolve() not in indice or not esperados <= locales:
            raise ValueError(f"Navegación incompleta en {unidad.name}")
        if not ("ejercicio" in texto.lower() and "reto" in texto.lower()):
            raise ValueError(f"Faltan referencias a ejercicios/reto en {unidad.name}")
        ejemplos = list((unidad / "ejemplos").glob("[0-9][0-9]_*.py"))
        if not ejemplos or not (unidad / "soluciones").is_dir():
            raise ValueError(f"Faltan ejemplos o soluciones en {unidad.name}")
        registros.append({"unidad": n, "carpeta": unidad.name, "titulo": texto.splitlines()[0].removeprefix("# "),
                          "ejemplos_numerados": len(ejemplos), "navegacion": True})
    fragmentos = 0
    for ruta in [RAIZ / "README.md", RAIZ / "CONTINUIDAD.md", RAIZ / "REVISION_FINAL.md", *[p for u in unidades for p in u.rglob("*.md")]]:
        for e in enlaces(ruta):
            if e.scheme or e.netloc or not e.fragment:
                continue
            destino = (ruta.parent / unquote(e.path)) if e.path else ruta
            if destino.suffix != ".md" or unquote(e.fragment) not in anclas(destino):
                raise ValueError(f"Fragmento local no encontrado: {ruta.relative_to(RAIZ)} → {e.geturl()}")
            fragmentos += 1
    declaradas = {}
    for unidad in unidades:
        for archivo in unidad.glob("requirements*.txt"):
            for nombre, version in requisitos(archivo).items():
                if nombre in declaradas and declaradas[nombre] != version:
                    raise ValueError(f"Conflicto entre unidades: {nombre}")
                declaradas[nombre] = version
    return {"unidades": registros, "total_unidades": len(registros), "fragmentos_locales": fragmentos,
            "dependencias_directas": dict(sorted(declaradas.items())),
            "alcance": "estructura, enlaces de navegación, fragmentos Markdown usados y versiones declaradas",
            "excluye": ["ejecución de programas", "URLs externas", "revisión conceptual exhaustiva", "Windows y macOS"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    informe = auditar()
    print(f"Auditoría: {informe['total_unidades']} unidades; navegación completa; {informe['fragmentos_locales']} fragmentos locales válidos.")
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

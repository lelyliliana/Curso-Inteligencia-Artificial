"""Verifica sintaxis, enlaces locales, ejemplos y pruebas de las unidades 0 a 6.

Solo biblioteca estándar; no instala paquetes ni accede a servicios externos.
Los enlaces externos y los fragmentos #ancla requieren revisión editorial.
"""

import ast
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]
UNIDADES = sorted(p for p in RAIZ.glob("unidad[0-9][0-9]-*") if int(p.name[6:8]) <= 6)


def ejecutar(argumentos, esperado=None):
    proceso = subprocess.run(
        [sys.executable, *map(str, argumentos)], cwd=RAIZ,
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    salida = proceso.stdout + proceso.stderr
    if proceso.returncode != 0 or (esperado is not None and esperado not in salida):
        raise RuntimeError(f"Falló {' '.join(map(str, argumentos))}\n{salida}")
    return salida


def verificar_archivos():
    carpetas = [*UNIDADES, RAIZ / "datos", RAIZ / "herramientas"]
    archivos = [RAIZ / "README.md", RAIZ / "CONTINUIDAD.md"]
    for carpeta in carpetas:
        archivos.extend(p for p in carpeta.rglob("*") if p.suffix in (".md", ".py"))
    enlaces = 0
    for archivo in archivos:
        texto = archivo.read_text(encoding="utf-8")
        if archivo.suffix == ".py":
            ast.parse(texto, filename=str(archivo))
            continue
        # El material usa enlaces Markdown inline; excluimos ejemplos de código.
        prosa = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)
        for destino in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", prosa):
            url = destino.strip().strip("<>")
            partes = urlsplit(url)
            if partes.scheme or partes.netloc or not partes.path:
                continue
            ruta = archivo.parent / unquote(partes.path)
            if not ruta.exists():
                raise RuntimeError(f"Enlace roto en {archivo.relative_to(RAIZ)}: {destino}")
            enlaces += 1
    print(f"OK: sintaxis y {enlaces} enlaces a archivos locales ({len(archivos)} archivos revisados).")


def main():
    if len(UNIDADES) != 7:
        raise RuntimeError("Se esperan las siete unidades 0 a 6 en esta versión del verificador.")
    verificar_archivos()
    ejecutados = 0
    for unidad in UNIDADES:
        for carpeta in ("ejemplos", "soluciones"):
            for programa in sorted((unidad / carpeta).glob("[0-9][0-9]_*.py")):
                esperado = None
                if programa.name == "01_inferir_revision.py":
                    esperado = "proponer_visita: por r3"
                elif programa.name == "02_organizar_talleres.py":
                    esperado = "Soluciones: 3; coinciden con la línea base."
                ejecutar([programa.relative_to(RAIZ)], esperado)
                ejecutados += 1
    with tempfile.TemporaryDirectory() as carpeta:
        ejecutar(["unidad00-entorno/soluciones/reto_registro.py", "--salida", Path(carpeta) / "registro.json"])
        ejecutados += 1
    reglas = "unidad06-conocimiento-reglas/ejemplos/01_inferir_revision.py"
    horarios = "unidad06-conocimiento-reglas/ejemplos/02_organizar_talleres.py"
    variantes = [
        ([reglas, "--quitar", "sensor_verificado"], "no equivale a demostrar su negación"),
        ([reglas, "--agregar", "mantenimiento_programado"], "INCOMPATIBILIDAD declarada"),
        ([reglas, "--consulta", "posponer_visita"], "no se deriva con esta base"),
        ([horarios, "--orden", "fija", "--sin-poda"], "intentos=21."),
        ([horarios, "--orden", "fija"], "intentos=9."),
        ([horarios, "--sin-poda"], "Soluciones: 3; coinciden con la línea base."),
        ([horarios, "--datos", "unidad06-conocimiento-reglas/datos/horarios_imposibles.json"], "Soluciones: 0;"),
    ]
    for comando, esperado in variantes:
        ejecutar(comando, esperado)
        ejecutados += 1
    print(f"OK: {ejecutados} ejecuciones de programas y variantes.")
    for unidad in UNIDADES:
        pruebas = unidad / "pruebas"
        if pruebas.is_dir():
            salida = ejecutar(["-m", "unittest", "discover", "-s", pruebas.relative_to(RAIZ), "-v"])
            resumen = re.search(r"Ran (\d+) tests?", salida)
            if resumen is None or int(resumen[1]) == 0:
                raise RuntimeError(f"No se descubrieron pruebas en {pruebas}.")
            print(f"OK: {resumen[1]} pruebas de {unidad.name}.")
    print("Verificación completada. No sustituye la revisión conceptual, didáctica o de fuentes.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError, SyntaxError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

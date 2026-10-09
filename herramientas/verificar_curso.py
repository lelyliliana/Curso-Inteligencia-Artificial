"""Verifica sintaxis, enlaces locales, ejemplos y pruebas de las unidades 0 a 14.

Requiere las dependencias numéricas y gráficas; no instala paquetes ni usa la red.
Los enlaces externos y los fragmentos #ancla requieren revisión editorial.
"""

import ast
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]
ULTIMA_UNIDAD = 14
UNIDADES = sorted(p for p in RAIZ.glob("unidad[0-9][0-9]-*") if int(p.name[6:8]) <= ULTIMA_UNIDAD)


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
    if (len(UNIDADES) != ULTIMA_UNIDAD + 1
            or {int(p.name[6:8]) for p in UNIDADES} != set(range(ULTIMA_UNIDAD + 1))):
        raise RuntimeError(f"Se espera una carpeta por unidad, de 0 a {ULTIMA_UNIDAD}.")
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
                elif programa.name == "01_perfilar_lecturas.py":
                    esperado = "Cobertura de claves: 10/12 = 83.33%"
                elif programa.name == "02_auditar_disponibilidad.py":
                    esperado = "Entradas disponibles: e01, e03"
                elif programa.name == "01_preparar_lecturas.py":
                    esperado = "Preparados: 8; duplicados: 1; cuarentena: 3"
                elif programa.name == "02_imputar_sin_filtracion.py":
                    esperado = "Ajuste solo con entrenamiento: mediana=20; mínimo=18; máximo=22"
                elif programa.name == "01_explorar_lecturas.py":
                    esperado = "S3 | 4 | 1 | 1 | 0 | 3 | 0.000"
                elif programa.name == "02_explorar_grupos.py":
                    esperado = "Correlación global: 0.845"
                elif programa.name == "01_lineas_base_regresion.py":
                    esperado = "Seleccionado por mae: persistencia"
                elif programa.name == "02_lineas_base_clasificacion.py":
                    esperado = "Seleccionado por f1: por_senal"
                elif programa.name == "01_ajustar_recta.py":
                    esperado = "Seleccionado por MAE de validación: recta"
                elif programa.name == "02_comparar_complejidad.py":
                    esperado = "Seleccionado por MAE de validación: cuadratica"
                elif programa.name == "03_sensibilidad_extremo.py":
                    esperado = "perturbado: intercepto=1.333; pendiente=2.556; MAE validación=0.933"
                elif programa.name == "01_aprender_logistica.py":
                    esperado = "Seleccionado por F1 de validación: logistica_050"
                elif programa.name == "02_comparar_umbrales.py":
                    esperado = "Seleccionado por F1 de validación: logistica_020"
                elif programa.name == "03_paso_manual.py":
                    esperado = "Probabilidades: 0.475021, 0.524979"
                elif programa.name == "01_controlar_complejidad.py":
                    esperado = "Seleccionado por F1 de validación: arbol_3"
                elif programa.name == "02_comparar_ensambles.py":
                    esperado = "Seleccionado por F1 de validación: bagging"
                elif programa.name == "03_corte_e_inestabilidad.py":
                    esperado = "una etiqueta cambiada: corte=3.500; clase para x=4: 1"
                elif programa.name == "01_agrupar_perfiles.py":
                    esperado = "Seleccionado por silueta de validación: k3"
                elif programa.name == "02_detectar_anomalias.py":
                    esperado = "Seleccionado por f1 de validación: aislamiento"
                elif programa.name == "03_paso_kmeans.py":
                    esperado = "Suma de distancias cuadradas: 8.000 -> 4.000"
                ejecutar([programa.relative_to(RAIZ)], esperado)
                ejecutados += 1
    with tempfile.TemporaryDirectory() as carpeta:
        ejecutar(["unidad00-entorno/soluciones/reto_registro.py", "--salida", Path(carpeta) / "registro.json"])
        ejecutados += 1
    reglas = "unidad06-conocimiento-reglas/ejemplos/01_inferir_revision.py"
    horarios = "unidad06-conocimiento-reglas/ejemplos/02_organizar_talleres.py"
    perfil = "unidad07-obtencion-datos/ejemplos/01_perfilar_lecturas.py"
    disponibilidad = "unidad07-obtencion-datos/ejemplos/02_auditar_disponibilidad.py"
    preparacion = "unidad08-preparacion-datos/ejemplos/01_preparar_lecturas.py"
    imputacion = "unidad08-preparacion-datos/ejemplos/02_imputar_sin_filtracion.py"
    explorar_lecturas = "unidad09-exploracion-visualizacion/ejemplos/01_explorar_lecturas.py"
    explorar_grupos = "unidad09-exploracion-visualizacion/ejemplos/02_explorar_grupos.py"
    base_regresion = "unidad10-flujo-lineas-base/ejemplos/01_lineas_base_regresion.py"
    base_clasificacion = "unidad10-flujo-lineas-base/ejemplos/02_lineas_base_clasificacion.py"
    regresion_lineal = "unidad11-regresion/ejemplos/01_ajustar_recta.py"
    regresion_curva = "unidad11-regresion/ejemplos/02_comparar_complejidad.py"
    logistica = "unidad12-clasificacion/ejemplos/01_aprender_logistica.py"
    umbrales = "unidad12-clasificacion/ejemplos/02_comparar_umbrales.py"
    arboles = "unidad13-arboles-ensambles/ejemplos/01_controlar_complejidad.py"
    ensambles = "unidad13-arboles-ensambles/ejemplos/02_comparar_ensambles.py"
    grupos = "unidad14-agrupamiento-anomalias/ejemplos/01_agrupar_perfiles.py"
    anomalias = "unidad14-agrupamiento-anomalias/ejemplos/02_detectar_anomalias.py"
    variantes = [
        ([reglas, "--quitar", "sensor_verificado"], "no equivale a demostrar su negación"),
        ([reglas, "--agregar", "mantenimiento_programado"], "INCOMPATIBILIDAD declarada"),
        ([reglas, "--consulta", "posponer_visita"], "no se deriva con esta base"),
        ([horarios, "--orden", "fija", "--sin-poda"], "intentos=21."),
        ([horarios, "--orden", "fija"], "intentos=9."),
        ([horarios, "--sin-poda"], "Soluciones: 3; coinciden con la línea base."),
        ([horarios, "--datos", "unidad06-conocimiento-reglas/datos/horarios_imposibles.json"], "Soluciones: 0;"),
        ([perfil, "--sensores", "S1", "S2"], "Cobertura de claves: 8/8 = 100.00%"),
        ([perfil, "--fin", "2026-09-05"], "Cobertura de claves: 10/15 = 66.67%"),
        ([disponibilidad, "--decision", "2026-09-05T09:10:00+00:00"], "Entradas disponibles: e01, e02, e03"),
        ([disponibilidad, "--decision", "2026-09-05T04:00:00-05:00"], "Entradas disponibles: e01, e03"),
        ([preparacion, "--correcciones", "unidad08-preparacion-datos/datos/correcciones_verificadas.json"], "Preparados: 9; duplicados: 1; cuarentena: 2"),
        ([imputacion, "--comparar-filtracion"], "Ajuste incorrecto: mediana=22; mínimo=18; máximo=40"),
        ([explorar_lecturas, "--correcciones", "unidad08-preparacion-datos/datos/correcciones_verificadas.json"], "S2 | 4 | 4 | 4 | 0 | 0 | 9.500"),
        ([explorar_grupos, "--intervalos", "4"], "Frecuencias: 0, 24, 0, 24"),
        ([explorar_grupos, "--intervalos", "16"], "Correlación global: 0.845"),
        ([base_regresion, "--evaluar-prueba"], "mae=2.250 | rmse=2.354 | sesgo=1.250"),
        ([base_clasificacion, "--evaluar-prueba"], "exactitud=0.938 | precision=1.000 | recobrado=0.800 | f1=0.889"),
        ([regresion_lineal, "--evaluar-prueba"], "MAE=0.200; RMSE=0.200; R²=0.997"),
        ([regresion_curva, "--evaluar-prueba"], "MAE=0.141; RMSE=0.167; R²=1.000"),
        ([regresion_lineal, "--horas", "10"], "10 h -> 23.000 kWh; fuera del rango de entrenamiento: sí"),
        ([logistica, "--evaluar-prueba"], "VP=12; VN=20; FP=4; FN=4; F1=0.750"),
        ([umbrales, "--evaluar-prueba"], "VP=8; VN=74; FP=17; FN=1; F1=0.471"),
        ([logistica, "--senal", "100"], "señal=100; p(1)=0.913; clase=1; fuera del rango de entrenamiento: sí"),
        ([arboles, "--evaluar-prueba"], "VP=16; VN=22; FP=0; FN=2; F1=0.941"),
        ([ensambles, "--evaluar-prueba"], "VP=28; VN=74; FP=14; FN=4; F1=0.757"),
        ([arboles, "--consulta", "100"], "Consulta: p(1)=0.133; clase=0; fuera del rango de entrenamiento: sí"),
        ([ensambles, "--semilla", "29"], "Semilla de modelos: 29"),
        ([grupos, "--evaluar-prueba"], "Prueba final: silueta=0.853; tamaños=[20, 20, 20]"),
        ([anomalias, "--evaluar-prueba"], "Prueba final: VP=3; VN=64; FP=0; FN=13; F1=0.316"),
        ([anomalias, "--semilla", "29"], "experimento: anomalias; semilla: 29"),
    ]
    for comando, esperado in variantes:
        ejecutar(comando, esperado)
        ejecutados += 1
    with tempfile.TemporaryDirectory() as carpeta:
        for i, programa in enumerate((explorar_lecturas, explorar_grupos)):
            ejecutar([programa, "--salida", Path(carpeta) / str(i)], "Exportación:")
            ejecutados += 1
        for i, programa in enumerate((base_regresion, base_clasificacion)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"base-{i}-{cierre}"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((regresion_lineal, regresion_curva)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"regresion-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((logistica, umbrales)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"clasificacion-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((arboles, ensambles)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"arboles-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((grupos, anomalias)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"no-supervisado-{i}-{cierre}", "--graficos"], "Exportación:")
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
        with tempfile.TemporaryDirectory(prefix="curso-matplotlib-") as cache:
            os.environ.setdefault("MPLCONFIGDIR", cache)
            main()
    except (OSError, UnicodeError, ValueError, SyntaxError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

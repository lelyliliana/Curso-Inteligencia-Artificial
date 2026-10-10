"""Verifica sintaxis, enlaces locales, ejemplos y pruebas de las unidades 0 a 23.

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
ULTIMA_UNIDAD = 23
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
                elif programa.name == "01_construir_caracteristicas.py":
                    esperado = "Seleccionado por MAE de validación: interaccion"
                elif programa.name == "02_comparar_pca.py":
                    esperado = "Seleccionado por MAE de validación: completa"
                elif programa.name == "03_proyectar_a_mano.py":
                    esperado = "MSE de reconstrucción por celda: 0.250"
                elif programa.name == "01_ajustar_con_cv.py":
                    esperado = "Seleccionado por MAE medio de CV: knn3_distance"
                elif programa.name == "02_validar_por_equipos.py":
                    esperado = "Seleccionado por MAE medio de CV: mediana"
                elif programa.name == "03_pliegues_a_mano.py":
                    esperado = "Media MAE: 4.333; desviación poblacional: 2.357"
                elif programa.name == "01_elegir_por_costos.py":
                    esperado = "Seleccionada por costo de validación: umbral020"
                elif programa.name == "02_decidir_con_cupo.py":
                    esperado = "Seleccionada por costo de validación: umbral050_top6"
                elif programa.name == "03_metricas_a_mano.py":
                    esperado = "ROC AUC por pares: 0.625; AP: 0.583333; Brier: 0.2625"
                elif programa.name == "01_explicar_consumo.py":
                    esperado = "Modelo lineal: MAE validación=0.277 kWh"
                elif programa.name == "02_auditar_alertas.py":
                    esperado = "desplazado | 40 | 19 | 12 | 0 | 0.368"
                elif programa.name == "03_explicar_a_mano.py":
                    esperado = "Contribuciones B: [6, 0, -1]; predicción=15.000"
                elif programa.name == "01_aprender_xor.py":
                    esperado = "Seleccionado por BCE de validación: red8; época=3000"
                elif programa.name == "02_controlar_sobreajuste.py":
                    esperado = "Seleccionado por BCE de validación: red32_l2; época=6000"
                elif programa.name == "03_retropropagar_a_mano.py":
                    esperado = "BCE antes=0.693147; después=0.534305"
                elif programa.name == "01_comprobar_equivalencia.py":
                    esperado = "Equivalencia comprobada: tolerancia=1e-12; 13 parámetros; float64; CPU."
                elif programa.name == "02_entrenar_minilotes.py":
                    esperado = "Seleccionado por BCE de validación: red12_8; época=110"
                elif programa.name == "03_acumular_gradientes.py":
                    esperado = "Peso tras SGD=0.500; pérdida=12.500 -> 0.125"
                elif programa.name == "01_explorar_pixeles.py":
                    esperado = "Referencia manual y conv2d: error máximo=0.0"
                elif programa.name == "02_clasificar_trazos.py":
                    esperado = "Seleccionado por CE de validación: cnn; época=45"
                elif programa.name == "03_correlacion_a_mano.py":
                    esperado = "Correlación comprobada: salida 3×3; error máximo=0.0"
                elif programa.name == "01_representar_textos.py":
                    esperado = "TF-IDF manual y biblioteca: error máximo < 1e-12"
                elif programa.name == "02_clasificar_mensajes.py":
                    esperado = "Seleccionado por CE de validación: unigramas"
                elif programa.name == "03_tfidf_a_mano.py":
                    esperado = "Norma L2 comprobada: 1.000000"
                elif programa.name == "01_auditar_tiempo.py":
                    esperado = "Media de tres horas disponible a las 08:10: 26.0 °C"
                elif programa.name == "02_pronosticar_sensor.py":
                    esperado = "Seleccionado por MAE de validación: ridge; horizonte=1 h"
                elif programa.name == "03_ventana_a_mano.py":
                    esperado = "Futuro alterado: media causal=12.0; media centrada=42.0"
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
    caracteristicas = "unidad15-caracteristicas-dimension/ejemplos/01_construir_caracteristicas.py"
    pca = "unidad15-caracteristicas-dimension/ejemplos/02_comparar_pca.py"
    cv_ciclos = "unidad16-validacion-hiperparametros/ejemplos/01_ajustar_con_cv.py"
    cv_equipos = "unidad16-validacion-hiperparametros/ejemplos/02_validar_por_equipos.py"
    decisiones_costos = "unidad17-metricas-decisiones/ejemplos/01_elegir_por_costos.py"
    decisiones_cupo = "unidad17-metricas-decisiones/ejemplos/02_decidir_con_cupo.py"
    explicar_consumo = "unidad18-interpretabilidad-responsabilidad/ejemplos/01_explicar_consumo.py"
    auditar_alertas = "unidad18-interpretabilidad-responsabilidad/ejemplos/02_auditar_alertas.py"
    red_xor = "unidad19-redes-neuronales/ejemplos/01_aprender_xor.py"
    red_ruido = "unidad19-redes-neuronales/ejemplos/02_controlar_sobreajuste.py"
    equivalencia_torch = "unidad20-pytorch/ejemplos/01_comprobar_equivalencia.py"
    minilotes_torch = "unidad20-pytorch/ejemplos/02_entrenar_minilotes.py"
    vision_filtros = "unidad21-vision-computador/ejemplos/01_explorar_pixeles.py"
    vision_trazos = "unidad21-vision-computador/ejemplos/02_clasificar_trazos.py"
    lenguaje_representacion = "unidad22-lenguaje-natural/ejemplos/01_representar_textos.py"
    lenguaje_mensajes = "unidad22-lenguaje-natural/ejemplos/02_clasificar_mensajes.py"
    serie_auditoria = "unidad23-series-temporales/ejemplos/01_auditar_tiempo.py"
    serie_pronostico = "unidad23-series-temporales/ejemplos/02_pronosticar_sensor.py"
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
        ([caracteristicas, "--evaluar-prueba"], "Prueba final: solo interaccion; MAE=0.429; RMSE=0.585; R²=0.998"),
        ([pca, "--evaluar-prueba"], "Prueba final: solo completa; MAE=0.139; RMSE=0.192; R²=0.993"),
    ]
    variantes.extend([
        ([cv_ciclos, "--evaluar-prueba"], "Prueba final: solo knn3_distance; MAE=1.402; RMSE=1.839"),
        ([cv_equipos, "--evaluar-prueba"], "Prueba final: solo mediana; MAE=28.303; RMSE=30.491"),
    ])
    variantes.extend([
        ([decisiones_costos, "--evaluar-prueba"], "Prueba final: solo umbral020; VP=23; FP=52; FN=4; costo=76"),
        ([decisiones_cupo, "--evaluar-prueba"], "Prueba final: solo umbral050_top6; VP=13; FP=0; FN=29; costo=116"),
    ])
    variantes.extend([
        ([explicar_consumo, "--evaluar-prueba"], "Prueba final: modelo fijo; MAE=0.379 kWh"),
        ([auditar_alertas, "--evaluar-prueba"], "Prueba final: modelo fijo; VP=37; FP=0; FN=12"),
    ])
    variantes.extend([
        ([red_xor, "--evaluar-prueba"], "Prueba final: solo red8; BCE=0.0061; exactitud=1.000; FN=0; FP=0"),
        ([red_ruido, "--evaluar-prueba"], "Prueba final: solo red32_l2; BCE=0.5350; exactitud=0.787; FN=17; FP=17"),
        ([minilotes_torch, "--evaluar-prueba"], "Prueba final: solo red12_8; BCE=0.2110; exactitud=0.900; FN=6; FP=2"),
        ([vision_trazos, "--evaluar-prueba"], "Prueba final: solo cnn; CE=0.0406; exactitud=0.983; macro F1=0.983"),
    ])
    variantes.append(([lenguaje_mensajes, "--evaluar-prueba"],
                      "Prueba final: solo unigramas; CE=0.6682; exactitud=1.000; macro F1=1.000"))
    variantes.extend([
        ([serie_pronostico, "--horizonte", "6"], "Seleccionado por MAE de validación: ridge; horizonte=6 h"),
        ([serie_pronostico, "--evaluar-prueba"], "Prueba final: solo ridge; h=1; n=186; MAE=0.1942; RMSE=0.2696"),
        ([serie_pronostico, "--horizonte", "6", "--evaluar-prueba"], "Prueba final: solo ridge; h=6; n=181; MAE=0.2743; RMSE=0.3882"),
    ])
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
        for i, programa in enumerate((caracteristicas, pca)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"representaciones-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((cv_ciclos, cv_equipos)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"validacion-cv-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((decisiones_costos, decisiones_cupo)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"decisiones-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((explicar_consumo, auditar_alertas)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"interpretacion-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        for i, programa in enumerate((red_xor, red_ruido)):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([programa, *extras, "--salida", Path(carpeta) / f"redes-{i}-{cierre}", "--graficos"], "Exportación:")
                ejecutados += 1
        ejecutar([equivalencia_torch, "--salida", Path(carpeta)/"equivalencia-torch", "--graficos"], "Exportación:")
        ejecutados += 1
        for cierre in (False, True):
            extras = ["--evaluar-prueba"] if cierre else []
            ejecutar([minilotes_torch, *extras, "--salida", Path(carpeta)/f"minilotes-torch-{cierre}", "--graficos"],
                     "Recarga en CPU: error máximo en logits=0.0")
            ejecutados += 1
        ejecutar([vision_filtros, "--salida", Path(carpeta)/"vision-filtros", "--graficos"], "Exportación:")
        ejecutados += 1
        for cierre in (False, True):
            extras = ["--evaluar-prueba"] if cierre else []
            ejecutar([vision_trazos, *extras, "--salida", Path(carpeta)/f"vision-trazos-{cierre}", "--graficos"],
                     "Recarga en CPU: error máximo en logits=0.0")
            ejecutados += 1
        ejecutar([lenguaje_representacion, "--salida", Path(carpeta)/"lenguaje-representacion", "--graficos"], "Exportación:")
        ejecutados += 1
        for cierre in (False, True):
            extras = ["--evaluar-prueba"] if cierre else []
            ejecutar([lenguaje_mensajes, *extras, "--salida", Path(carpeta)/f"lenguaje-mensajes-{cierre}", "--graficos"],
                     "Recarga: error máximo en probabilidades=0.0")
            ejecutados += 1
        ejecutar([serie_auditoria, "--salida", Path(carpeta)/"serie-auditoria", "--graficos"], "Exportación:")
        ejecutados += 1
        for horizonte in (1, 6):
            for cierre in (False, True):
                extras = ["--evaluar-prueba"] if cierre else []
                ejecutar([serie_pronostico, "--horizonte", str(horizonte), *extras,
                          "--salida", Path(carpeta)/f"serie-{horizonte}-{cierre}", "--graficos"],
                         "Recarga: error máximo=0.0 °C")
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

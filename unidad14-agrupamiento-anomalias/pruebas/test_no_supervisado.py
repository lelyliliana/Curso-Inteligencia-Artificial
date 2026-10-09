"""Referencias numéricas, separación de información y artefactos del experimento."""

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import flujo_no_supervisado as f
from figuras import construir_figuras, guardar_figuras, plt
import numpy as np
from sklearn.metrics import silhouette_samples


def importar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


generador = importar("datos_u14", UNIDAD / "datos/generar_datos.py")
manual = importar("paso_u14", UNIDAD / "soluciones/03_paso_kmeans.py")


def ejecutar(nombre="grupos", cierre=False, semilla=14):
    funcion = f.ejecutar_grupos if nombre == "grupos" else f.ejecutar_anomalias
    return funcion(UNIDAD / "datos" / nombre, cierre, semilla)


class Matematica(unittest.TestCase):
    def test_paso_manual_centros_y_objetivo(self):
        grupos, centros, antes, despues = manual.paso_lloyd([[1, 1], [1, 3], [7, 7], [9, 7]], [[1, 1], [9, 7]])
        np.testing.assert_array_equal(grupos, [0, 0, 1, 1])
        np.testing.assert_allclose(centros, [[1, 2], [8, 7]])
        self.assertEqual((antes, despues), (8, 4))

    def test_paso_rechaza_vacio_y_dimensiones(self):
        for x, centros in (([], [[1]]), ([[1]], [[1, 2]]), ([[1], [2]], [[1], [99]]), ([[np.nan]], [[1]])):
            with self.assertRaises(ValueError):
                manual.paso_lloyd(x, centros)

    def test_kmeans_con_referencia_exhaustiva_en_una_dimension(self):
        x = np.array([0., 1., 2., 8., 9., 11.])
        costos = [sum(((g-g.mean())**2).sum() for g in (x[:i], x[i:])) for i in range(1, len(x))]
        with f.threadpool_limits(limits=1):
            modelo = f.nuevo_kmeans(2, 14).fit(x.reshape(-1, 1))
        self.assertAlmostEqual(modelo.inertia_, min(costos))

    def test_silueta_con_distancias_independientes(self):
        x = np.array([[1, 1], [1, 3], [7, 7], [9, 7]])
        grupos = [0, 0, 1, 1]
        distancia = np.linalg.norm(x[:, None] - x[None, :], axis=2)
        referencia = []
        for i in range(4):
            a = np.mean([distancia[i, j] for j in range(4) if j != i and grupos[j] == grupos[i]])
            b = np.mean([distancia[i, j] for j in range(4) if grupos[j] != grupos[i]])
            referencia.append((b-a)/max(a, b))
        np.testing.assert_allclose(silhouette_samples(x, grupos), referencia)
        self.assertAlmostEqual(f.silueta(x, grupos), np.mean(referencia))

    def test_silueta_indefinida_y_singleton(self):
        x = np.array([[0.], [1.], [9.]])
        self.assertIsNone(f.silueta(x, [0, 0, 0]))
        self.assertIsNone(f.silueta(x, [0, 1, 2]))
        self.assertEqual(silhouette_samples(x, [0, 0, 1])[2], 0)

    def test_ari_no_depende_del_nombre_del_grupo(self):
        self.assertEqual(f.adjusted_rand_score([0, 0, 1, 1], [7, 7, 3, 3]), 1)
        self.assertEqual(f.adjusted_rand_score([0, 0, 1, 1], [0, 1, 0, 1]), -.5)

    def test_escala_poblacional_y_columna_constante(self):
        escala = f.StandardScaler().fit([[1, 9], [3, 9]])
        np.testing.assert_allclose(escala.mean_, [2, 9])
        np.testing.assert_allclose(escala.scale_, [1, 1])
        np.testing.assert_allclose(escala.transform([[5, 9]]), [[3, 0]])

    def test_cambio_de_unidades_con_escala_conserva_asignaciones(self):
        filas, _ = f.leer_csv(UNIDAD / "datos/grupos/entrenamiento.csv", "grupos", "entrenamiento")
        x = f.matriz(filas, "grupos")
        with f.threadpool_limits(limits=1):
            a = f.nuevo_kmeans(3, 14).fit_predict(f.StandardScaler().fit_transform(x))
            b = f.nuevo_kmeans(3, 14).fit_predict(f.StandardScaler().fit_transform(x * [1, .001]))
        self.assertEqual(f.adjusted_rand_score(a, b), 1)

    def test_umbral_orden_y_empates(self):
        self.assertEqual(f.umbral_orden([1, 2, 3, 4, 5], .8), 4)
        self.assertEqual(f.umbral_orden([1, 2, 2, 2], .5), 2)
        self.assertEqual(sum(np.array([1, 2, 2, 2]) > 2), 0)
        for valores, q in (([], .95), ([np.nan], .95), ([1], 0), ([1], 1.1)):
            with self.assertRaises(ValueError):
                f.umbral_orden(valores, q)

    def test_signo_isolation_y_alerta_con_umbral_propio(self):
        informe, ajuste = ejecutar("anomalias")
        filas, _ = f.leer_csv(UNIDAD / "datos/anomalias/validacion.csv", "anomalias", "validacion")
        z = ajuste["escala"].transform(f.matriz(filas, "anomalias"))
        modelo = ajuste["modelos"]["aislamiento"]
        valores = f.puntuar("aislamiento", modelo, z)
        np.testing.assert_allclose(valores, -modelo.score_samples(z))
        umbral = informe["modelos"]["aislamiento"]["umbral"]
        registros = informe["validacion"]["aislamiento"]["predicciones"]
        np.testing.assert_equal([r["alerta"] for r in registros], valores > umbral)
        self.assertFalse(np.array_equal(valores > umbral, modelo.predict(z) == -1))


class DatosYSeparacion(unittest.TestCase):
    def test_regeneracion_exacta_siete_archivos(self):
        archivos = generador.contenidos()
        self.assertEqual(len(archivos), 7)
        for ruta, texto in archivos.items():
            self.assertEqual((UNIDAD / "datos" / ruta).read_bytes(), texto.encode())

    def test_esquema_valores_y_etiquetas_invalidas(self):
        cabecera = "caso_id,senal_a,senal_b,anomalia_sintetica\n"
        textos = ["", cabecera, cabecera + "a,1,2\n", cabecera + "a,1,2,0,extra\n",
                  cabecera + "a,NaN,2,0\n", cabecera + "a,1,101,0\n", cabecera + "a,1,2,2\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in textos:
                ruta.write_text(texto)
                with self.assertRaises(ValueError):
                    f.leer_csv(ruta, "anomalias", "validacion")

    def test_entrenamiento_no_admite_etiqueta_como_columna(self):
        with self.assertRaises(ValueError):
            f.leer_csv(UNIDAD / "datos/anomalias/validacion.csv", "anomalias", "entrenamiento")

    def test_identificadores_duplicados(self):
        datos, fuentes = {}, {}
        f.cargar("entrenamiento", "grupos", UNIDAD / "datos/grupos", datos, fuentes)
        with self.assertRaises(ValueError):
            f.cargar("entrenamiento", "grupos", UNIDAD / "datos/grupos", datos, fuentes)

    def test_default_funciona_sin_prueba(self):
        for nombre, funcion in (("grupos", f.ejecutar_grupos), ("anomalias", f.ejecutar_anomalias)):
            with tempfile.TemporaryDirectory() as carpeta:
                for ruta in (UNIDAD / "datos" / nombre).glob("*.csv"):
                    if ruta.stem != "prueba":
                        shutil.copy2(ruta, carpeta)
                informe, _ = funcion(carpeta)
                self.assertIsNone(informe["prueba"])
                self.assertNotIn("prueba", informe["fuentes"])

    def test_validacion_grupos_no_ajusta_centros_ni_escala(self):
        original = f.leer_csv
        def cambiar(ruta, nombre, fase):
            filas, sha = original(ruta, nombre, fase)
            if fase == "validacion":
                for fila in filas:
                    fila["consumo_kwh"] += 50
            return filas, sha
        base, _ = ejecutar()
        with patch.object(f, "leer_csv", side_effect=cambiar):
            variante, _ = ejecutar()
        for campo in ("escala", "modelos", "entrenamiento", "rangos_entrenamiento"):
            self.assertEqual(base[campo], variante[campo])
        self.assertNotEqual(base["validacion"], variante["validacion"])

    def test_calibracion_cambia_umbral_no_detector(self):
        original = f.leer_csv
        def cambiar(ruta, nombre, fase):
            filas, sha = original(ruta, nombre, fase)
            if fase == "calibracion":
                for fila in filas:
                    fila["senal_a"] = 99.
            return filas, sha
        base, _ = ejecutar("anomalias")
        with patch.object(f, "leer_csv", side_effect=cambiar):
            variante, _ = ejecutar("anomalias")
        self.assertEqual(base["escala"], variante["escala"])
        self.assertEqual(base["modelos"]["aislamiento"]["sha256_estructuras"], variante["modelos"]["aislamiento"]["sha256_estructuras"])
        self.assertNotEqual(base["modelos"]["distancia_centro"]["umbral"], variante["modelos"]["distancia_centro"]["umbral"])

    def test_etiquetas_validacion_no_ajustan_umbral_ni_modelo(self):
        original = f.leer_csv
        def cambiar(ruta, nombre, fase):
            filas, sha = original(ruta, nombre, fase)
            if fase == "validacion":
                for fila in filas:
                    fila["anomalia_sintetica"] = 1 - fila["anomalia_sintetica"]
            return filas, sha
        base, _ = ejecutar("anomalias")
        with patch.object(f, "leer_csv", side_effect=cambiar):
            variante, _ = ejecutar("anomalias")
        for campo in ("escala", "modelos", "entrenamiento", "calibracion"):
            self.assertEqual(base[campo], variante[campo])
        self.assertNotEqual(base["validacion"], variante["validacion"])

    def test_etiquetas_prueba_no_cambian_ajuste_seleccion_o_alertas(self):
        original = f.leer_csv
        def cambiar(ruta, nombre, fase):
            filas, sha = original(ruta, nombre, fase)
            if fase == "prueba":
                for fila in filas:
                    fila["anomalia_sintetica"] = 1 - fila["anomalia_sintetica"]
            return filas, sha
        base, _ = ejecutar("anomalias", True)
        with patch.object(f, "leer_csv", side_effect=cambiar):
            variante, _ = ejecutar("anomalias", True)
        for campo in ("escala", "modelos", "seleccionado", "validacion"):
            self.assertEqual(base[campo], variante[campo])
        for campo in ("puntuacion", "alerta"):
            self.assertEqual([p[campo] for p in base["prueba"]["predicciones"]], [p[campo] for p in variante["prueba"]["predicciones"]])
        self.assertNotEqual(base["prueba"]["metricas"], variante["prueba"]["metricas"])

    def test_prueba_se_lee_despues_de_seleccionar_ambos(self):
        lector, selector = f.leer_csv, f.elegir
        for nombre in ("grupos", "anomalias"):
            eventos = []
            def leer(ruta, nombre, fase):
                eventos.append(fase)
                return lector(ruta, nombre, fase)
            def elegir(*args):
                eventos.append("seleccion")
                return selector(*args)
            with patch.object(f, "leer_csv", side_effect=leer), patch.object(f, "elegir", side_effect=elegir):
                ejecutar(nombre, True)
            self.assertGreater(eventos.index("prueba"), eventos.index("seleccion"))

    def test_mismos_casos_y_seleccion_esperada(self):
        for nombre, seleccionado in (("grupos", "k3"), ("anomalias", "aislamiento")):
            informe, _ = ejecutar(nombre)
            ids = [[r["caso_id"] for r in ev["predicciones"]] for ev in informe["validacion"].values()]
            self.assertTrue(all(v == ids[0] for v in ids))
            self.assertEqual(informe["seleccionado"], seleccionado)

    def test_semilla_reproducible_y_variantes(self):
        base, _ = ejecutar("anomalias")
        igual, _ = ejecutar("anomalias")
        variante, _ = ejecutar("anomalias", semilla=29)
        self.assertEqual(base, igual)
        self.assertEqual(base["fuentes"], variante["fuentes"])
        self.assertNotEqual(base["modelos"]["aislamiento"]["sha256_estructuras"], variante["modelos"]["aislamiento"]["sha256_estructuras"])

    def test_empates_indefinidos_y_sin_redondear(self):
        tabla = {c: {"metricas": {"silueta": v}} for c, v in (("k2", .5), ("k3", .5), ("k4", None))}
        self.assertEqual(f.elegir(tabla, tabla, "silueta"), "k2")
        tabla["k3"]["metricas"]["silueta"] += .000001
        self.assertEqual(f.elegir(tabla, tabla, "silueta"), "k3")
        with self.assertRaises(ValueError):
            f.elegir({"k2": {"metricas": {"silueta": None}}}, ["k2"], "silueta")

    def test_exportacion_cierre_solo_elegido_y_no_sobrescritura(self):
        for nombre in ("grupos", "anomalias"):
            informe, _ = ejecutar(nombre, True)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "salida"
                f.exportar(informe, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text()), informe)
                with (destino / "predicciones_prueba.csv").open() as archivo:
                    filas = list(csv.DictReader(archivo))
                self.assertEqual({r["candidato"] for r in filas}, {informe["seleccionado"]})
                with self.assertRaises(FileExistsError):
                    f.exportar(informe, destino)

    def test_datos_fuera_rango_y_semilla_invalida(self):
        informe, ajuste = ejecutar()
        filas = [{"caso_id": "nuevo", "horas_uso": 24., "consumo_kwh": 500.}]
        ev = f.evaluar_grupos(ajuste["modelos"]["k3"], ajuste["escala"], filas, informe)
        self.assertTrue(ev["predicciones"][0]["fuera_rango"])
        self.assertIsNone(ev["metricas"]["silueta"])
        for semilla in (-1, 2**32, True):
            with self.assertRaises(ValueError):
                ejecutar(semilla=semilla)

    def test_recursos_publicados_coinciden_con_ajuste(self):
        for nombre in ("grupos", "anomalias"):
            informe, _ = ejecutar(nombre)
            publicado = json.loads((UNIDAD / "recursos" / nombre / "informe.json").read_text())
            publicado.pop("versiones")
            informe.pop("versiones")
            self.assertEqual(informe, publicado)


class Graficos(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_grupos_mismos_puntos_y_centros(self):
        informe, ajuste = ejecutar(cierre=True)
        figura = construir_figuras(informe, ajuste)["grupos"]
        for eje, c in zip(figura.axes, informe["modelos"]):
            self.assertEqual(sum(len(v.get_offsets()) for v in eje.collections[:-1]), 60)
            np.testing.assert_allclose(eje.collections[-1].get_offsets(), informe["modelos"][c]["centros_originales"])

    def test_diagnosticos_reflejan_metricas(self):
        informe, ajuste = ejecutar()
        figura = construir_figuras(informe, ajuste)["diagnosticos"]
        np.testing.assert_allclose(figura.axes[0].lines[0].get_ydata(), [m["inercia_entrenamiento"] for m in informe["modelos"].values()])
        np.testing.assert_allclose([r.get_height() for r in figura.axes[1].patches], [ev["metricas"]["silueta"] for ev in informe["validacion"].values()])
        self.assertEqual(figura.axes[1].get_ylim(), (-1, 1))

    def test_alertas_puntos_ordenados_y_umbral_de_calibracion(self):
        informe, ajuste = ejecutar("anomalias", True)
        figura = construir_figuras(informe, ajuste)["alertas"]
        for j, c in enumerate(("distancia_centro", "aislamiento")):
            eje = figura.axes[j]
            self.assertEqual(sum(len(v.get_offsets()) for v in eje.collections[1:]), 80)
            eje_orden = figura.axes[j+2]
            esperado = sorted(r["puntuacion"] for r in informe["validacion"][c]["predicciones"])
            np.testing.assert_allclose(eje_orden.collections[0].get_offsets()[:, 1], esperado)
            np.testing.assert_allclose(eje_orden.lines[0].get_ydata(), informe["modelos"][c]["umbral"])

    def test_png_svg_y_no_sobrescritura(self):
        from PIL import Image
        informe, ajuste = ejecutar()
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_figuras(informe, ajuste, carpeta)
            with Image.open(Path(carpeta) / "grupos.png") as imagen:
                imagen.verify()
            self.assertIn("<svg", (Path(carpeta) / "diagnosticos.svg").read_text())
            with self.assertRaises(FileExistsError):
                guardar_figuras(informe, ajuste, carpeta)


if __name__ == "__main__":
    unittest.main()

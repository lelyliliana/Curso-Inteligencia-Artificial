"""Referencias matemáticas, disponibilidad de variables, separación y gráficos."""

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
import representaciones as r
from figuras import construir_figuras, guardar_figuras, plt
import numpy as np


def importar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


manual = importar("manual_u15", UNIDAD / "soluciones/03_proyectar_a_mano.py")
generador = importar("datos_u15", UNIDAD / "datos/generar_datos.py")


def ejecutar(nombre="pca", cierre=False):
    return r.ejecutar_experimento(nombre, UNIDAD / "datos" / nombre, cierre)


def modificar(fase_objetivo, cambio):
    lector = r.leer_csv
    def leer(ruta, nombre):
        filas, sha = lector(ruta, nombre)
        if Path(ruta).stem == fase_objetivo:
            for fila in filas:
                cambio(fila)
        return filas, sha
    return patch.object(r, "leer_csv", side_effect=leer)


class Matematica(unittest.TestCase):
    def test_proyeccion_manual(self):
        p = manual.proyeccion_manual([[2, 1], [-2, -1], [1, 2], [-1, -2]])
        np.testing.assert_allclose(p["media"], [0, 0])
        np.testing.assert_allclose(p["covarianza"], [[10/3, 8/3], [8/3, 10/3]])
        np.testing.assert_allclose(p["varianzas"], [6, 2/3])
        np.testing.assert_allclose(p["reconstruccion"][0], [1.5, 1.5])
        self.assertAlmostEqual(p["proporcion"], .9)
        self.assertAlmostEqual(p["mse"], .25)
        for x in ([], [[1, 1]], [[1, 1], [1, 1]], [[np.nan], [1]]):
            with self.assertRaises(ValueError):
                manual.proyeccion_manual(x)

    def test_covarianza_independiente_frente_a_svd(self):
        _, modelos = ejecutar()
        filas, _ = r.leer_csv(UNIDAD / "datos/pca/entrenamiento.csv", "pca")
        z = modelos["pca2"].named_steps["escala"].transform(r.matriz(filas, "pca"))
        referencia = manual.proyeccion_manual(z)
        pca = modelos["pca1"].named_steps["pca"]
        np.testing.assert_allclose(pca.components_.T @ pca.components_, referencia["ejes"].T @ referencia["ejes"], atol=1e-12)
        self.assertAlmostEqual(pca.explained_variance_[0], referencia["varianzas"][0])

    def test_signo_no_cambia_reconstruccion(self):
        x = np.array([[2, 1], [-2, -1], [1, 2], [-1, -2]])
        p = manual.proyeccion_manual(x)
        np.testing.assert_allclose((-p["coordenadas"]) @ (-p["ejes"]) + p["media"], p["reconstruccion"])

    def test_ejes_ortogonales_y_residuo_perpendicular(self):
        informe, modelos = ejecutar()
        x = np.array([[f["senal_a"], f["senal_b"]] for f in informe["validacion"]["pca1"]["predicciones"]])
        pca = modelos["pca2"].named_steps["pca"]
        np.testing.assert_allclose(pca.components_ @ pca.components_.T, np.eye(2), atol=1e-12)
        z, reconstruccion, _ = r.representar(modelos["pca1"], x)
        np.testing.assert_allclose((z-reconstruccion) @ modelos["pca1"].named_steps["pca"].components_.T, 0, atol=1e-12)

    def test_dos_componentes_reconstruyen_y_una_no(self):
        informe, _ = ejecutar()
        self.assertLess(informe["validacion"]["pca2"]["metricas"]["mse_reconstruccion_z"], 1e-25)
        self.assertGreater(informe["validacion"]["pca1"]["metricas"]["mse_reconstruccion_z"], 0)

    def test_caracteristicas_producto_y_orden(self):
        x = np.array([[4., 3.], [2., 5.]])
        np.testing.assert_equal(r.caracteristicas(x, "interaccion"), [[4, 3, 12], [2, 5, 10]])
        np.testing.assert_equal(r.caracteristicas(x, "originales"), x)

    def test_regresion_con_minimos_cuadrados_independientes(self):
        informe, modelos = ejecutar("interaccion")
        filas, _ = r.leer_csv(UNIDAD / "datos/interaccion/entrenamiento.csv", "interaccion")
        x = r.caracteristicas(r.matriz(filas, "interaccion"), "interaccion")
        y = [f["consumo_final_kwh"] for f in filas]
        beta = np.linalg.lstsq(np.column_stack((np.ones(len(x)), x)), y, rcond=None)[0]
        val = informe["validacion"]["interaccion"]["predicciones"]
        xv = r.caracteristicas(r.matriz(val, "interaccion"), "interaccion")
        np.testing.assert_allclose(modelos["interaccion"].predict(xv), beta[0]+xv @ beta[1:], atol=1e-10)

    def test_rotacion_completa_conserva_prediccion_lineal(self):
        informe, _ = ejecutar()
        a = [p["prediccion"] for p in informe["validacion"]["completa"]["predicciones"]]
        b = [p["prediccion"] for p in informe["validacion"]["pca2"]["predicciones"]]
        np.testing.assert_allclose(a, b, atol=1e-10)
        self.assertEqual(informe["seleccionado"], "completa")

    def test_varianza_alta_no_garantiza_mae_bajo(self):
        informe, _ = ejecutar()
        self.assertGreater(informe["modelos"]["pca1"]["pca"]["proporcion_varianza"][0], .999)
        self.assertGreater(informe["validacion"]["pca1"]["metricas"]["mae"], 5*informe["validacion"]["completa"]["metricas"]["mae"])

    def test_r2_indefinido_con_objetivo_constante(self):
        informe, modelos = ejecutar()
        filas, _ = r.leer_csv(UNIDAD / "datos/pca/validacion.csv", "pca")
        for fila in filas:
            fila["indice_respuesta"] = 20.
        ev = r.evaluar(modelos["completa"], "completa", filas, informe)
        self.assertIsNone(ev["metricas"]["r2"])
        self.assertIsNone(r.evaluar(modelos["completa"], "completa", filas[:1], informe)["metricas"]["r2"])


class DatosYProtocolo(unittest.TestCase):
    def test_generacion_exacta(self):
        archivos = generador.contenidos()
        self.assertEqual(len(archivos), 6)
        for ruta, texto in archivos.items():
            self.assertEqual((UNIDAD / "datos" / ruta).read_bytes(), texto.encode())

    def test_lector_rechaza_esquema_y_valores_invalidos(self):
        cabecera = "caso_id,senal_a,senal_b,indice_respuesta\n"
        textos = ["", cabecera, cabecera+"a,2,3\n", cabecera+"a,2,3,4,extra\n", cabecera+"a,NaN,3,4\n",
                  cabecera+"a,2,101,4\n", cabecera+"a,,3,4\n", "caso_id,senal_a,senal_a,indice_respuesta\na,2,3,4\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in textos:
                ruta.write_text(texto)
                with self.assertRaises(ValueError):
                    r.leer_csv(ruta, "pca")

    def test_lista_de_entradas_excluye_futuro_objetivo_e_id(self):
        filas, _ = r.leer_csv(UNIDAD / "datos/interaccion/entrenamiento.csv", "interaccion")
        for campo in ("caso_id", "lectura_cierre_kwh", "consumo_final_kwh"):
            with self.assertRaises(ValueError):
                r.matriz(filas, "interaccion", [campo])

    def test_representacion_redundante_se_rechaza(self):
        with modificar("entrenamiento", lambda f: f.update(senal_b=f["senal_a"])):
            with self.assertRaises(ValueError):
                ejecutar()

    def test_ids_repetidos_rechazados(self):
        with modificar("validacion", lambda f: f.update(caso_id="duplicado")):
            with self.assertRaises(ValueError):
                ejecutar()

    def test_default_no_necesita_prueba(self):
        for nombre in r.CANDIDATOS:
            with tempfile.TemporaryDirectory() as carpeta:
                for fase in ("entrenamiento", "validacion"):
                    shutil.copy2(UNIDAD / "datos" / nombre / f"{fase}.csv", carpeta)
                informe, _ = r.ejecutar_experimento(nombre, carpeta)
                self.assertIsNone(informe["prueba"])
                self.assertNotIn("prueba", informe["fuentes"])

    def test_lectura_posterior_no_afecta_modelos_ni_predicciones(self):
        base, _ = ejecutar("interaccion")
        with modificar("entrenamiento", lambda f: f.update(lectura_cierre_kwh=1500.)):
            cambio, _ = ejecutar("interaccion")
        self.assertEqual(base, cambio)

    def test_objetivo_entrenamiento_no_aprende_ejes_pca(self):
        base, _ = ejecutar()
        with modificar("entrenamiento", lambda f: f.update(indice_respuesta=40.-f["indice_respuesta"])):
            cambio, _ = ejecutar()
        for c in ("pca1", "pca2"):
            for campo in ("escala", "pca"):
                self.assertEqual(base["modelos"][c][campo], cambio["modelos"][c][campo])
        self.assertNotEqual(base["modelos"]["completa"]["regresion"], cambio["modelos"]["completa"]["regresion"])

    def test_validacion_no_ajusta_transformaciones_ni_regresion(self):
        base, _ = ejecutar()
        with modificar("validacion", lambda f: f.update(senal_a=f["senal_a"]+1, indice_respuesta=f["indice_respuesta"]+2)):
            cambio, _ = ejecutar()
        for campo in ("modelos", "entrenamiento", "rangos_entrenamiento"):
            self.assertEqual(base[campo], cambio[campo])
        self.assertNotEqual(base["validacion"], cambio["validacion"])

    def test_objetivos_prueba_no_cambian_seleccion_ni_prediccion(self):
        for nombre in r.CANDIDATOS:
            base, _ = ejecutar(nombre, True)
            objetivo = r.OBJETIVO[nombre]
            with modificar("prueba", lambda f: f.update({objetivo: f[objetivo]+5})):
                cambio, _ = ejecutar(nombre, True)
            for campo in ("modelos", "seleccionado", "validacion"):
                self.assertEqual(base[campo], cambio[campo])
            self.assertEqual([v["prediccion"] for v in base["prueba"]["predicciones"]], [v["prediccion"] for v in cambio["prueba"]["predicciones"]])
            self.assertNotEqual(base["prueba"]["metricas"], cambio["prueba"]["metricas"])

    def test_entradas_prueba_cambian_prediccion_no_ajuste(self):
        base, _ = ejecutar(cierre=True)
        with modificar("prueba", lambda f: f.update(senal_a=100.)):
            cambio, _ = ejecutar(cierre=True)
        for campo in ("modelos", "seleccionado", "validacion"):
            self.assertEqual(base[campo], cambio[campo])
        self.assertNotEqual(base["prueba"]["predicciones"], cambio["prueba"]["predicciones"])
        self.assertTrue(all(v["fuera_rango"] for v in cambio["prueba"]["predicciones"]))

    def test_prueba_se_lee_despues_de_seleccion(self):
        lector, selector = r.leer_csv, r.seleccionar
        eventos = []
        def leer(ruta, nombre):
            eventos.append(Path(ruta).stem)
            return lector(ruta, nombre)
        def elegir(*args):
            eventos.append("seleccion")
            return selector(*args)
        with patch.object(r, "leer_csv", side_effect=leer), patch.object(r, "seleccionar", side_effect=elegir):
            ejecutar(cierre=True)
        self.assertEqual(eventos, ["entrenamiento", "validacion", "seleccion", "prueba"])

    def test_candidatos_mismos_casos(self):
        for nombre, elegido in (("interaccion", "interaccion"), ("pca", "completa")):
            informe, _ = ejecutar(nombre)
            ids = [[v["caso_id"] for v in ev["predicciones"]] for ev in informe["validacion"].values()]
            self.assertTrue(all(v == ids[0] for v in ids))
            self.assertEqual(informe["seleccionado"], elegido)

    def test_tolerancia_absoluta_no_es_redondeo_de_consola(self):
        tabla = {c: {"metricas": {"mae": v}} for c, v in (("a", .5), ("b", .5-5e-11))}
        self.assertEqual(r.seleccionar(tabla, tabla), "a")
        tabla["b"]["metricas"]["mae"] = .5-1e-6
        self.assertEqual(r.seleccionar(tabla, tabla), "b")

    def test_exportacion_cierre_y_no_sobrescritura(self):
        for nombre in r.CANDIDATOS:
            informe, _ = ejecutar(nombre, True)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "salida"
                r.exportar(informe, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text()), informe)
                with (destino / "predicciones_prueba.csv").open() as archivo:
                    filas = list(csv.DictReader(archivo))
                self.assertEqual({v["candidato"] for v in filas}, {informe["seleccionado"]})
                with self.assertRaises(FileExistsError):
                    r.exportar(informe, destino)

    def test_recursos_conservan_resultados_publicados(self):
        for nombre in r.CANDIDATOS:
            actual, _ = ejecutar(nombre)
            publicado = json.loads((UNIDAD / "recursos" / nombre / "informe.json").read_text())
            actual.pop("versiones")
            publicado.pop("versiones")
            self.assertEqual(actual, publicado)


class Figuras(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_predicciones_grafico_corresponden_a_validacion(self):
        informe, modelos = ejecutar("interaccion", True)
        fig = construir_figuras(informe, modelos)["caracteristicas"]
        for eje, c in zip(fig.axes, ("originales", "interaccion")):
            esperado = [[v["real"], v["prediccion"]] for v in informe["validacion"][c]["predicciones"]]
            np.testing.assert_allclose(eje.collections[0].get_offsets(), esperado)
        self.assertEqual(fig.axes[0].get_xlim(), fig.axes[1].get_xlim())

    def test_proyeccion_y_colores_mismos_casos(self):
        informe, modelos = ejecutar(cierre=True)
        fig = construir_figuras(informe, modelos)["proyeccion"]
        coordenadas = [v["coordenadas"] for v in informe["validacion"]["pca2"]["representaciones"]]
        np.testing.assert_allclose(fig.axes[1].collections[0].get_offsets(), coordenadas)
        np.testing.assert_allclose(fig.axes[1].collections[0].get_array(), [v["real"] for v in informe["validacion"]["pca2"]["predicciones"]])
        self.assertEqual(len(fig.axes[0].lines), 48)

    def test_tres_medidas_no_se_confunden_en_barras(self):
        informe, modelos = ejecutar()
        fig = construir_figuras(informe, modelos)["compromiso"]
        medidas = [[sum(informe["modelos"][c]["pca"]["proporcion_varianza"]) for c in ("pca1", "pca2")],
                   [informe["validacion"][c]["metricas"]["mse_reconstruccion_z"] for c in ("pca1", "pca2")],
                   [v["metricas"]["mae"] for v in informe["validacion"].values()]]
        for eje, valores in zip(fig.axes, medidas):
            np.testing.assert_allclose([p.get_height() for p in eje.patches], valores)
            self.assertEqual(eje.get_ylim()[0], 0)

    def test_png_svg_y_no_sobrescritura(self):
        from PIL import Image
        informe, modelos = ejecutar("interaccion")
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_figuras(informe, modelos, carpeta)
            with Image.open(Path(carpeta) / "caracteristicas.png") as imagen:
                imagen.verify()
            self.assertIn("<svg", (Path(carpeta) / "caracteristicas.svg").read_text())
            with self.assertRaises(FileExistsError):
                guardar_figuras(informe, modelos, carpeta)


if __name__ == "__main__":
    unittest.main()

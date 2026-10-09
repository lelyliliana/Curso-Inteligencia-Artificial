"""Comprueba particiones, biblioteca, agregación y evaluación separada."""

import csv
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
sys.path.insert(0, str(UNIDAD / "datos"))
import arboles as a
from generar_datos import contenidos
from figuras import construir_figuras, guardar_figuras, np, plt
from sklearn.tree import DecisionTreeRegressor


def experimento(nombre="franja", cierre=False, semilla=13, consulta=None):
    return a.ejecutar_experimento(nombre, UNIDAD / "datos" / nombre, cierre, semilla, consulta)


class ArbolesYAgregacion(unittest.TestCase):
    def test_gini_manual_y_validacion(self):
        self.assertEqual(a.gini([0, 0, 1, 1]), .5)
        self.assertEqual(a.gini([0, 0, 0, 1]), .375)
        self.assertEqual(a.gini([1, 1]), 0)
        for ys in ([], [0, 2], [True, False]):
            with self.assertRaises(ValueError):
                a.gini(ys)

    def test_cortes_ponderan_por_cantidad(self):
        cortes = a.cortes_gini(list(range(1, 9)), [0] * 4 + [1] * 4)
        self.assertAlmostEqual(cortes[1]["gini_hijos"], 1 / 3)
        mejor = min(cortes, key=lambda v: v["gini_hijos"])
        self.assertEqual((mejor["corte"], mejor["reduccion"]), (4.5, .5))

    def test_minimo_por_hoja_y_entrada_constante(self):
        cortes = a.cortes_gini([1, 2, 3, 4], [0, 0, 1, 1], min_hoja=2)
        self.assertEqual([c["corte"] for c in cortes], [2.5])
        self.assertEqual(a.cortes_gini([2, 2], [0, 1]), [])
        for xs, ys, minimo in (([1], [0, 1], 1), ([float("nan")], [1], 1), ([1, 2], [0, 1], 0)):
            with self.assertRaises(ValueError):
                a.cortes_gini(xs, ys, minimo)

    def test_raiz_sklearn_con_busqueda_exhaustiva_independiente(self):
        xs = list(range(1, 9))
        for ys in ([0, 0, 0, 0, 1, 1, 1, 1], [0, 1, 0, 0, 1, 1, 1, 0], [1, 0, 1, 1, 0, 0, 1, 0]):
            modelo = a.DecisionTreeClassifier(max_depth=1, random_state=13).fit([[x] for x in xs], ys)
            mejor = min(v["gini_hijos"] for v in a.cortes_gini(xs, ys))
            t = modelo.tree_
            observado = (t.n_node_samples[1] * t.impurity[1] + t.n_node_samples[2] * t.impurity[2]) / len(xs)
            self.assertAlmostEqual(observado, mejor)

    def test_igualdad_del_corte_va_a_izquierda(self):
        modelo = a.DecisionTreeClassifier(max_depth=1, random_state=13).fit([[1], [2], [3], [4]], [0, 0, 1, 1])
        self.assertEqual(modelo.tree_.threshold[0], 2.5)
        self.assertEqual(modelo.predict([[2.5], [2.6]]).tolist(), [0, 1])

    def test_probabilidad_de_hoja_y_empate_de_clases(self):
        modelo = a.DecisionTreeClassifier(random_state=13).fit([[1], [1], [1], [1]], [0, 1, 0, 1])
        np.testing.assert_equal(modelo.predict_proba([[1]]), [[.5, .5]])
        self.assertEqual(modelo.predict([[1]]).tolist(), [0])

    def test_controles_y_sobreajuste_del_ejemplo(self):
        informe, modelos = experimento()
        controlado = modelos["arbol_3"]
        self.assertLessEqual(controlado.get_depth(), 3)
        hojas = controlado.tree_.children_left == -1
        self.assertGreaterEqual(controlado.tree_.n_node_samples[hojas].min(), 5)
        self.assertEqual(informe["entrenamiento"]["arbol_libre"]["metricas"]["f1"], 1)
        self.assertGreater(informe["validacion"]["arbol_3"]["metricas"]["f1"], informe["validacion"]["arbol_libre"]["metricas"]["f1"])

    def test_cambio_lineal_de_unidad_conserva_clases(self):
        xs, ys = [[1], [2], [3], [4], [5]], [0, 0, 1, 1, 0]
        original = a.DecisionTreeClassifier(random_state=13).fit(xs, ys)
        transformado = a.DecisionTreeClassifier(random_state=13).fit([[2 * x[0] + 10] for x in xs], ys)
        consultas = np.linspace(1, 5, 17).reshape(-1, 1)
        np.testing.assert_equal(original.predict(consultas), transformado.predict(2 * consultas + 10))

    def test_bootstrap_repite_solo_filas_de_entrenamiento(self):
        informe, modelos = experimento("region")
        for nombre in ("bagging", "bosque"):
            muestras = modelos[nombre].estimators_samples_
            self.assertEqual(len(muestras), 31)
            for indices in muestras:
                self.assertEqual(len(indices), 180)
                self.assertTrue(np.all((indices >= 0) & (indices < 180)))
                self.assertLess(len(set(indices.tolist())), 180)
            self.assertGreater(len({m["sha256_indices"] for m in informe["modelos"][nombre]["bootstrap"]}), 1)

    def test_promedio_de_probabilidades_reproduce_ensambles(self):
        _, modelos = experimento("region")
        xs = np.array([[20., 30.], [50., 50.], [80., 90.]])
        for nombre in ("bagging", "bosque"):
            modelo = modelos[nombre]
            columnas = modelo.estimators_features_ if nombre == "bagging" else [np.arange(2)] * 31
            promedio = np.mean([m.predict_proba(xs[:, cs]) for m, cs in zip(modelo.estimators_, columnas)], axis=0)
            np.testing.assert_allclose(modelo.predict_proba(xs), promedio, atol=1e-14)
            np.testing.assert_equal(modelo.predict(xs), np.argmax(promedio, axis=1))

    def test_regresion_no_prolonga_tendencia_fuera_del_rango(self):
        modelo = DecisionTreeRegressor(max_depth=1, random_state=13).fit([[1], [2], [3], [4]], [2, 4, 6, 8])
        self.assertEqual(modelo.predict([[4], [10]]).tolist(), [7, 7])


class DatosYFlujo(unittest.TestCase):
    def test_generador_reproduce_seis_csv(self):
        generados = contenidos()
        self.assertEqual(len(generados), 6)
        for nombre, texto in generados.items():
            self.assertEqual((UNIDAD / "datos" / nombre).read_bytes(), texto.encode("utf-8"))

    def test_lector_rechaza_columnas_faltantes_y_valores_invalidos(self):
        cabecera = "caso_id,senal_a,revision_confirmada\n"
        casos = ["", cabecera, "caso_id,senal_a,senal_a\na,1,0\n", cabecera + "a,1\n",
                 cabecera + "a,1,0,extra\n", cabecera + "a,,0\n", cabecera + "a,NaN,1\n",
                 cabecera + "a,101,0\n", cabecera + "a,-1,1\n", cabecera + "a,5,2\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in casos:
                ruta.write_text(texto, encoding="utf-8")
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    a.leer_csv(ruta, "franja")

    def test_identificadores_repetidos_y_senales_iguales(self):
        fila = {"caso_id": "a", "senal_a": 40, "revision_confirmada": 1}
        a.validar_ids({"entrenamiento": [fila], "validacion": [dict(fila, caso_id="b")]})
        for datos in ({"entrenamiento": [fila, fila]}, {"entrenamiento": [fila], "prueba": [fila]}):
            with self.assertRaises(ValueError):
                a.validar_ids(datos)

    def test_default_no_necesita_prueba(self):
        with tempfile.TemporaryDirectory() as carpeta:
            for fase in ("entrenamiento", "validacion"):
                shutil.copy2(UNIDAD / "datos/franja" / f"{fase}.csv", carpeta)
            informe, _ = a.ejecutar_experimento("franja", carpeta)
            self.assertIsNone(informe["prueba"])
            self.assertNotIn("prueba", informe["fuentes"])

    def test_validacion_no_cambia_modelos_bootstrap_ni_rangos(self):
        original = a.leer_csv
        def cambiar(ruta, nombre):
            filas, huella = original(ruta, nombre)
            if Path(ruta).stem == "validacion":
                for fila in filas:
                    fila["revision_confirmada"] = 1 - fila["revision_confirmada"]
                    fila["senal_a"] += 1
            return filas, huella
        base, _ = experimento("region")
        with patch.object(a, "leer_csv", side_effect=cambiar):
            variante, _ = experimento("region")
        for campo in ("modelos", "rangos_entrenamiento", "entrenamiento"):
            self.assertEqual(base[campo], variante[campo])
        self.assertNotEqual(base["validacion"], variante["validacion"])

    def test_etiquetas_de_prueba_no_cambian_ajuste_seleccion_ni_prediccion(self):
        original = a.leer_csv
        def cambiar(ruta, nombre):
            filas, huella = original(ruta, nombre)
            if Path(ruta).stem == "prueba":
                for fila in filas:
                    fila["revision_confirmada"] = 1 - fila["revision_confirmada"]
            return filas, huella
        for nombre in ("franja", "region"):
            base, _ = experimento(nombre, True)
            with patch.object(a, "leer_csv", side_effect=cambiar):
                variante, _ = experimento(nombre, True)
            for campo in ("modelos", "rangos_entrenamiento", "seleccionado", "validacion"):
                self.assertEqual(base[campo], variante[campo])
            for campo in ("prediccion", "probabilidad_1"):
                self.assertEqual([p[campo] for p in base["prueba"]["predicciones"]], [p[campo] for p in variante["prueba"]["predicciones"]])
            self.assertNotEqual(base["prueba"]["metricas"], variante["prueba"]["metricas"])

    def test_prueba_se_carga_despues_de_elegir(self):
        eventos = []
        lector, selector = a.leer_csv, a.seleccionar
        def leer(ruta, nombre):
            eventos.append(Path(ruta).stem)
            return lector(ruta, nombre)
        def elegir(*args):
            eventos.append("seleccion")
            return selector(*args)
        with patch.object(a, "leer_csv", side_effect=leer), patch.object(a, "seleccionar", side_effect=elegir):
            experimento(cierre=True)
        self.assertEqual(eventos, ["entrenamiento", "validacion", "seleccion", "prueba"])

    def test_candidatos_comparan_los_mismos_casos(self):
        informe, _ = experimento("region")
        ids = [[p["caso_id"] for p in ev["predicciones"]] for ev in informe["validacion"].values()]
        self.assertTrue(all(v == ids[0] for v in ids))
        self.assertEqual(informe["seleccionado"], "bagging")

    def test_misma_semilla_reproduce_estructuras_y_predicciones(self):
        base, _ = experimento("region")
        repetido, _ = experimento("region")
        self.assertEqual(base, repetido)

    def test_otra_semilla_cambia_remuestreo_no_datos(self):
        base, _ = experimento("region")
        variante, _ = experimento("region", semilla=29)
        self.assertEqual(base["fuentes"], variante["fuentes"])
        self.assertNotEqual(base["modelos"]["bagging"]["bootstrap"], variante["modelos"]["bagging"]["bootstrap"])

    def test_empate_sin_redondear_y_f1_indefinido(self):
        validacion = {k: {"metricas": {"f1": .5}} for k in ("a", "b")}
        self.assertEqual(a.seleccionar(validacion, ("a", "b")), "a")
        validacion["b"]["metricas"]["f1"] += .00001
        self.assertEqual(a.seleccionar(validacion, ("a", "b")), "b")
        validacion["a"]["metricas"]["f1"] = None
        with self.assertRaises(ValueError):
            a.seleccionar(validacion, ("a", "b"))

    def test_una_clase_rechazada_en_validacion_permitida_en_prueba(self):
        original = a.leer_csv
        for fase in ("validacion", "prueba"):
            def cambiar(ruta, nombre):
                filas, huella = original(ruta, nombre)
                if Path(ruta).stem == fase:
                    for fila in filas:
                        fila["revision_confirmada"] = 0
                return filas, huella
            with patch.object(a, "leer_csv", side_effect=cambiar):
                if fase == "validacion":
                    with self.assertRaises(ValueError):
                        experimento(cierre=True)
                else:
                    informe, _ = experimento(cierre=True)
                    self.assertIsNone(informe["prueba"]["metricas"]["recobrado"])

    def test_consulta_dimension_dominio_y_semilla(self):
        informe, _ = experimento(consulta=[100])
        self.assertTrue(informe["consulta"]["fuera_rango"])
        for consulta in ([], [50, 50], [-1], [float("nan")]):
            with self.assertRaises(ValueError):
                experimento(consulta=consulta)
        for semilla in (-1, 2**32, True):
            with self.assertRaises(ValueError):
                experimento(semilla=semilla)

    def test_exportacion_json_csv_reglas_y_no_sobrescritura(self):
        for nombre in ("franja", "region"):
            informe, _ = experimento(nombre, True)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "exportacion"
                a.exportar(informe, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text()), informe)
                with (destino / "predicciones_prueba.csv").open(newline="") as archivo:
                    filas = list(csv.DictReader(archivo))
                self.assertEqual({f["candidato"] for f in filas}, {informe["seleccionado"]})
                for candidato, reglas in informe["reglas"].items():
                    self.assertEqual((destino / f"reglas_{candidato}.txt").read_text(), reglas)
                with self.assertRaises(FileExistsError):
                    a.exportar(informe, destino)

    def test_identificadores_no_entran_al_predictor(self):
        original = a.leer_csv
        def renombrar(ruta, nombre):
            filas, huella = original(ruta, nombre)
            for fila in filas:
                fila["caso_id"] = "otro-" + fila["caso_id"]
            return filas, huella
        base, _ = experimento()
        with patch.object(a, "leer_csv", side_effect=renombrar):
            variante, _ = experimento()
        self.assertEqual(base["modelos"], variante["modelos"])
        self.assertEqual(base["seleccionado"], variante["seleccionado"])


class Figuras(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_barras_y_puntos_corresponden_a_desarrollo(self):
        informe, modelos = experimento(cierre=True)
        figura = construir_figuras(informe, modelos)["complejidad"]
        self.assertEqual(len(figura.axes[0].collections[0].get_offsets()), 40)
        valores = [informe[fase][c]["metricas"]["f1"] for fase in ("entrenamiento", "validacion") for c in modelos]
        np.testing.assert_allclose([p.get_height() for p in figura.axes[1].patches], valores)
        self.assertEqual(figura.axes[1].get_ylim()[0], 0)

    def test_diagrama_contiene_todos_los_nodos_del_arbol_controlado(self):
        informe, modelos = experimento()
        eje = construir_figuras(informe, modelos)["arbol_controlado"].axes[0]
        nodos = [t.get_text() for t in eje.texts if "node #" in t.get_text()]
        self.assertEqual(len(nodos), modelos["arbol_3"].tree_.node_count)
        self.assertIn("samples = 80", nodos[0])

    def test_fronteras_muestran_validacion_y_limites_correctos(self):
        from matplotlib.collections import PathCollection
        informe, modelos = experimento("region", True)
        ejes = construir_figuras(informe, modelos)["fronteras"].axes[:3]
        for eje in ejes:
            self.assertEqual(sum(len(c.get_offsets()) for c in eje.collections if isinstance(c, PathCollection)), 120)
            mapa = eje.collections[0]
            self.assertEqual(mapa.get_clim(), (0, 1))
            coordenadas = mapa.get_coordinates()
            np.testing.assert_allclose([coordenadas[..., 0].min(), coordenadas[..., 0].max()], informe["rangos_entrenamiento"]["senal_a"])

    def test_png_svg_y_no_sobrescritura(self):
        from PIL import Image
        informe, modelos = experimento()
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_figuras(informe, modelos, carpeta)
            png = Path(carpeta) / "arbol_controlado.png"
            with Image.open(png) as imagen:
                imagen.verify()
            self.assertIn("<svg", (Path(carpeta) / "arbol_controlado.svg").read_text())
            with self.assertRaises(FileExistsError):
                guardar_figuras(informe, modelos, carpeta)


if __name__ == "__main__":
    unittest.main()

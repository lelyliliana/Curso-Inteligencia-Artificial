"""Verifica mínimos cuadrados, métricas, aislamiento de prueba y figuras."""

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
import regresion as r
from generar_datos import contenidos
from figuras import construir_figuras, guardar_figuras, np, plt


def experimento(nombre, cierre=False, horas=None):
    return r.ejecutar_experimento(nombre, UNIDAD / "datos" / nombre, cierre, horas)


class Ajustes(unittest.TestCase):
    def test_recta_manual(self):
        modelo = r.ajustar_recta([1, 2, 3], [3, 5, 7])
        self.assertEqual(modelo["coeficientes"], [1, 2])
        self.assertEqual(r.predecir(modelo, [2.5]), [6])

    def test_residuos_entrenamiento_ortogonales_con_intercepto(self):
        xs, ys = [1, 2, 3], [2, 4, 5]
        modelo = r.ajustar_recta(xs, ys)
        self.assertAlmostEqual(modelo["coeficientes"][0], 2 / 3)
        self.assertAlmostEqual(modelo["coeficientes"][1], 1.5)
        residuos = [y - p for y, p in zip(ys, r.predecir(modelo, xs))]
        self.assertAlmostEqual(sum(residuos), 0)
        self.assertAlmostEqual(sum(x * e for x, e in zip(xs, residuos)), 0)

    def test_recta_con_referencia_independiente_numpy(self):
        xs, ys = [0, 1, 2, 4, 7], [3, 4, 5, 11, 17]
        matriz = np.column_stack((np.ones(len(xs)), xs))
        coef, _, _, _ = np.linalg.lstsq(matriz, ys, rcond=None)
        np.testing.assert_allclose(r.ajustar_recta(xs, ys)["coeficientes"], coef, rtol=1e-12)

    def test_cambio_de_unidad_conserva_predicciones(self):
        xs, ys = [1, 2, 3, 4], [4, 6, 9, 10]
        horas = r.ajustar_recta(xs, ys)
        minutos = r.ajustar_recta([60 * x for x in xs], ys)
        self.assertAlmostEqual(minutos["coeficientes"][1], horas["coeficientes"][1] / 60)
        np.testing.assert_allclose(r.predecir(horas, xs), r.predecir(minutos, [60 * x for x in xs]))

    def test_recta_no_recorta_predicciones_negativas(self):
        modelo = r.ajustar_recta([1, 2], [1, 3])
        self.assertEqual(r.predecir(modelo, [0]), [-1])

    def test_polinomio_con_funcion_conocida(self):
        xs = [0, 1, 2, 3, 4]
        ys = [1 + 2 * x + 3 * x * x for x in xs]
        modelo = r.ajustar_polinomio(xs, ys, 2)
        self.assertEqual((modelo["centro"], modelo["escala"]), (2, 2))
        self.assertAlmostEqual(r.predecir(modelo, [2.5])[0], 24.75)

    def test_rechaza_entrada_constante_y_polinomio_sin_rango(self):
        with self.assertRaises(ValueError):
            r.ajustar_recta([2, 2], [1, 3])
        with self.assertRaises(ValueError):
            r.ajustar_polinomio([2, 2, 2], [1, 3, 5], 2)
        with self.assertRaises(ValueError):
            r.ajustar_polinomio([0, 0, 1, 1], [1, 2, 3, 4], 3)
        with self.assertRaises(ValueError):
            r.ajustar_polinomio([0, 1], [1, 2], 2)

    def test_rechaza_pares_invalidos(self):
        for xs, ys in (([], []), ([1], [1, 2]), ([float("nan")], [1]), ([1], [float("inf")]), ([True], [2])):
            with self.subTest(xs=xs, ys=ys), self.assertRaises(ValueError):
                r.ajustar_recta(xs, ys)

    def test_r2_negativo_y_no_definido(self):
        self.assertEqual(r.medir([1, 2, 3], [4, 4, 4])["r2"], -6)
        self.assertEqual(r.medir([1, 2, 3], [1, 2, 3])["r2"], 1)
        for reales, pred in (([2, 2], [2, 2]), ([2, 2], [1, 3]), ([1], [3])):
            self.assertIsNone(r.medir(reales, pred)["r2"])

    def test_metrica_rechaza_desalineacion_y_escala_no_representable(self):
        for reales, pred in (([1, 2], [1]), ([1e308, 0], [0, 1])):
            with self.subTest(reales=reales), self.assertRaises((ValueError, OverflowError)):
                r.medir(reales, pred)


class DatosYFlujo(unittest.TestCase):
    def test_generador_reproduce_seis_archivos(self):
        generados = contenidos()
        self.assertEqual(len(generados), 6)
        for nombre, texto in generados.items():
            self.assertEqual((UNIDAD / "datos" / nombre).read_bytes(), texto.encode("utf-8"))

    def test_lector_rechaza_faltantes_columnas_y_numeros_invalidos(self):
        cabecera = "caso_id,horas_planificadas,consumo_kwh\n"
        entradas = ["", cabecera, "caso_id,horas_planificadas,horas_planificadas\n",
                    cabecera + "a,1\n", cabecera + "a,1,2,3\n", cabecera + "a,,2\n",
                    cabecera + "a,NaN,2\n", cabecera + "a,1,inf\n", cabecera + "a,25,2\n",
                    cabecera + "a,1,-2\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in entradas:
                ruta.write_text(texto, encoding="utf-8")
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    r.leer_csv(ruta)

    def test_ids_disjuntos_y_repeticiones_de_x_permitidas(self):
        fila = {"caso_id": "a", "horas_planificadas": 2, "consumo_kwh": 5}
        r.validar_ids({"entrenamiento": [fila], "validacion": [dict(fila, caso_id="b")]})
        for datos in ({"entrenamiento": [fila, fila]}, {"entrenamiento": [fila], "prueba": [fila]}):
            with self.assertRaises(ValueError):
                r.validar_ids(datos)

    def test_default_no_necesita_prueba(self):
        for nombre in ("lineal", "curva"):
            with tempfile.TemporaryDirectory() as carpeta:
                for fase in ("entrenamiento", "validacion"):
                    shutil.copy2(UNIDAD / "datos" / nombre / f"{fase}.csv", carpeta)
                informe = r.ejecutar_experimento(nombre, carpeta)
                self.assertIsNone(informe["prueba"])
                self.assertNotIn("prueba", informe["fuentes"])

    def test_validacion_no_reajusta_modelos_ni_escala(self):
        original = r.leer_csv

        def cambiar(ruta):
            filas, huella = original(ruta)
            if Path(ruta).stem == "validacion":
                for fila in filas:
                    fila["horas_planificadas"] += 1
                    fila["consumo_kwh"] += 20
            return filas, huella

        base = experimento("curva")
        with patch.object(r, "leer_csv", side_effect=cambiar):
            variante = experimento("curva")
        self.assertEqual(base["modelos"], variante["modelos"])
        self.assertNotEqual(base["validacion"], variante["validacion"])

    def test_objetivos_de_prueba_no_cambian_modelos_seleccion_ni_prediccion(self):
        original = r.leer_csv

        def cambiar(ruta):
            filas, huella = original(ruta)
            if Path(ruta).stem == "prueba":
                for fila in filas:
                    fila["consumo_kwh"] += 100
            return filas, huella

        for nombre in ("lineal", "curva"):
            base = experimento(nombre, True)
            with patch.object(r, "leer_csv", side_effect=cambiar):
                variante = experimento(nombre, True)
            for campo in ("modelos", "seleccionado", "validacion"):
                self.assertEqual(base[campo], variante[campo])
            self.assertEqual([p["prediccion"] for p in base["prueba"]["predicciones"]],
                             [p["prediccion"] for p in variante["prueba"]["predicciones"]])
            self.assertNotEqual(base["prueba"]["metricas"], variante["prueba"]["metricas"])

    def test_extrapolacion_se_marca_sin_recorte(self):
        externo = experimento("lineal", horas=10)["consulta"]
        self.assertEqual(externo["consumo_predicho"], 23)
        self.assertTrue(externo["fuera_rango"])
        for x in (1, 8):
            self.assertFalse(experimento("lineal", horas=x)["consulta"]["fuera_rango"])
        with self.assertRaises(ValueError):
            experimento("lineal", horas=float("nan"))

    def test_resultados_lineales_y_mismos_casos(self):
        informe = experimento("lineal", True)
        self.assertEqual(informe["seleccionado"], "recta")
        self.assertEqual(informe["modelos"]["recta"]["coeficientes"], [3, 2])
        self.assertAlmostEqual(informe["validacion"]["recta"]["metricas"]["mae"], .3)
        self.assertAlmostEqual(informe["prueba"]["metricas"]["mae"], .2)
        ids = [[p["caso_id"] for p in ev["predicciones"]] for ev in informe["validacion"].values()]
        self.assertTrue(all(casos == ids[0] for casos in ids))

    def test_sobreajuste_no_gana_por_error_de_entrenamiento(self):
        informe = experimento("curva", True)
        self.assertEqual(informe["seleccionado"], "cuadratica")
        self.assertLess(informe["entrenamiento"]["grado9"]["metricas"]["mae"], 1e-10)
        self.assertGreater(informe["validacion"]["grado9"]["metricas"]["mae"], 2)
        self.assertLess(informe["validacion"]["cuadratica"]["metricas"]["mae"], .2)
        self.assertLess(informe["prueba"]["metricas"]["mae"], .15)
        self.assertLess(informe["validacion"]["cuadratica"]["metricas"]["r2"], 1)

    def test_empate_respeta_orden_sin_redondear(self):
        resultados = {"a": {"metricas": {"mae": 1}}, "b": {"metricas": {"mae": 1}}}
        self.assertEqual(r.seleccionar(resultados, ("a", "b")), "a")
        resultados["b"]["metricas"]["mae"] = .9999
        self.assertEqual(r.seleccionar(resultados, ("a", "b")), "b")

    def test_extremo_modifica_pendiente_sin_cambiar_fuente(self):
        ruta = UNIDAD / "datos/lineal/entrenamiento.csv"
        antes = ruta.read_bytes()
        filas, _ = r.leer_csv(ruta)
        xs = [f["horas_planificadas"] for f in filas]
        ys = [f["consumo_kwh"] for f in filas]
        ys[-1] += 20
        modelo = r.ajustar_recta(xs, ys)
        self.assertAlmostEqual(modelo["coeficientes"][1], 23 / 9)
        self.assertEqual(ruta.read_bytes(), antes)

    def test_exportacion_validacion_cierre_y_no_sobrescritura(self):
        for cierre in (False, True):
            informe = experimento("lineal", cierre)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "informe"
                r.exportar(informe, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text(encoding="utf-8")), informe)
                self.assertEqual((destino / "predicciones_prueba.csv").exists(), cierre)
                with (destino / "predicciones_validacion.csv").open(encoding="utf-8", newline="") as f:
                    self.assertEqual(len(list(csv.DictReader(f))), 36)
                antes = (destino / "informe.json").read_bytes()
                with self.assertRaises(FileExistsError):
                    r.exportar(informe, destino)
                self.assertEqual((destino / "informe.json").read_bytes(), antes)


class Figuras(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_figura_lineal_no_incluye_puntos_de_prueba(self):
        figura = construir_figuras(experimento("lineal", True))["recta_residuos"]
        self.assertEqual(sum(len(c.get_offsets()) for c in figura.axes[0].collections), 36)
        self.assertEqual(len(figura.axes[1].collections[0].get_offsets()), 12)

    def test_residuos_son_los_calculados_y_comparten_escala(self):
        informe = experimento("curva")
        ejes = construir_figuras(informe)["residuos"].axes
        for eje, nombre in zip(ejes, ("recta", "cuadratica", "grado9")):
            esperado = [(p["horas_planificadas"], p["residuo"]) for p in informe["validacion"][nombre]["predicciones"]]
            np.testing.assert_allclose(eje.collections[0].get_offsets(), esperado)
            self.assertEqual(eje.get_ylim(), ejes[0].get_ylim())

    def test_barras_usadas_para_comparar_coinciden_con_mae(self):
        informe = experimento("curva")
        eje = construir_figuras(informe)["complejidad"].axes[1]
        esperado = [informe[fase][c]["metricas"]["mae"]
                    for fase in ("entrenamiento", "validacion") for c in informe["modelos"]]
        np.testing.assert_allclose([p.get_height() for p in eje.patches], esperado)
        self.assertEqual(eje.get_ylim()[0], 0)

    def test_exportacion_grafica_valida_y_sin_sobrescribir(self):
        from PIL import Image
        informe = experimento("lineal")
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_figuras(informe, carpeta)
            png = Path(carpeta) / "recta_residuos.png"
            with Image.open(png) as imagen:
                imagen.verify()
            self.assertIn("<svg", (Path(carpeta) / "recta_residuos.svg").read_text(encoding="utf-8"))
            antes = png.read_bytes()
            with self.assertRaises(FileExistsError):
                guardar_figuras(informe, carpeta)
            self.assertEqual(png.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()

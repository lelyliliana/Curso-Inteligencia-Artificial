"""Comprueba cálculo, aprendizaje, decisiones, aislamiento de prueba y figuras."""

import csv
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
sys.path.insert(0, str(UNIDAD / "datos"))
import clasificacion as c
from generar_datos import contenidos
from figuras import construir_figuras, guardar_figuras, np, plt


def experimento(nombre="equilibrado", cierre=False, senal=None):
    return c.ejecutar_experimento(nombre, UNIDAD / "datos" / nombre, cierre, senal)


class Calculos(unittest.TestCase):
    def test_sigmoide_estable_y_simetrica(self):
        ps = c.sigmoide([-1000, -1, 0, 1, 1000])
        np.testing.assert_allclose(ps, [0, 1 / (1 + math.e), .5, 1 / (1 + math.exp(-1)), 1])
        self.assertAlmostEqual(ps[1] + ps[3], 1)
        with self.assertRaises(ValueError):
            c.sigmoide([float("nan")])

    def test_umbral_incluye_igualdad_y_valida_dominio(self):
        self.assertEqual(c.decidir([.2, .5, .8], .5), [0, 1, 1])
        for probabilidades, umbral in (([1.1], .5), ([-.1], .5), ([.5], -1), ([.5], float("nan"))):
            with self.assertRaises(ValueError):
                c.decidir(probabilidades, umbral)

    def test_perdida_manual_y_extremos_sin_recorte(self):
        self.assertAlmostEqual(c.perdida_logits([0, 1], [0, 0]), math.log(2))
        self.assertAlmostEqual(c.perdida_logits([1], [math.log(4)]), -math.log(.8))
        self.assertAlmostEqual(c.perdida_logits([1], [-math.log(4)]), -math.log(.2))
        self.assertEqual(c.perdida_logits([0, 1], [1000, -1000]), 1000)
        self.assertEqual(c.perdida_logits([1, 0], [1000, -1000]), 0)

    def test_gradiente_con_diferencias_finitas(self):
        z, y = np.array([-1.4, -.2, .4, 1.2]), np.array([0., 1., 0., 1.])
        parametros, penalizacion, paso = np.array([-.3, .7]), .01, 1e-6
        _, gradiente = c.objetivo_gradiente(z, y, parametros, penalizacion)
        # Evaluación independiente de la fórmula escalar en probabilidades moderadas.
        def funcion(theta):
            ps = [1 / (1 + math.exp(-(theta[0] + theta[1] * x))) for x in z]
            perdida = -sum(t * math.log(p) + (1 - t) * math.log1p(-p) for t, p in zip(y, ps)) / len(y)
            return perdida + penalizacion * theta[1] ** 2 / 2
        numerico = [(funcion(parametros + np.eye(2)[i] * paso) - funcion(parametros - np.eye(2)[i] * paso)) / (2 * paso) for i in range(2)]
        np.testing.assert_allclose(gradiente, numerico, atol=1e-9)

    def test_paso_manual(self):
        modelo = c.ajustar_logistica([40, 60], [0, 1], iteraciones=1)
        self.assertEqual((modelo["centro"], modelo["escala"]), (50, 10))
        self.assertEqual((modelo["intercepto"], modelo["coeficiente"]), (0, .1))
        self.assertAlmostEqual(modelo["historial"][-1]["objetivo"], .6444466600735709)

    def test_ajuste_con_referencia_newton(self):
        filas, _ = c.leer_csv(UNIDAD / "datos/desbalanceado/entrenamiento.csv")
        x = np.array([f["senal_previa"] for f in filas])
        y = np.array([f["revision_confirmada"] for f in filas])
        matriz = np.column_stack((np.ones(len(x)), (x - x.mean()) / x.std()))
        theta = np.zeros(2)
        penalizacion = np.diag([0, .01])
        # Otro método de optimización: Newton con Hessiana explícita de dos parámetros.
        for _ in range(12):
            p = 1 / (1 + np.exp(-(matriz @ theta)))
            gradiente = matriz.T @ (p - y) / len(y) + penalizacion @ theta
            hessiana = (matriz.T * (p * (1 - p))) @ matriz / len(y) + penalizacion
            theta -= np.linalg.solve(hessiana, gradiente)
        modelo = c.ajustar_logistica(x.tolist(), y.tolist())
        np.testing.assert_allclose([modelo["intercepto"], modelo["coeficiente"]], theta, atol=1e-6)

    def test_cambio_de_escala_de_entrada_conserva_prediccion(self):
        xs, ys = [1, 2, 3, 4], [0, 1, 0, 1]
        base = c.ajustar_logistica(xs, ys)
        cambio = c.ajustar_logistica([10 * x + 5 for x in xs], ys)
        np.testing.assert_allclose(c.probabilidades(base, xs)[0], c.probabilidades(cambio, [10 * x + 5 for x in xs])[0])

    def test_rechaza_ajustes_invalidos(self):
        for xs, ys in (([], []), ([1], [0, 1]), ([1, 1], [0, 1]), ([1, 2], [1, 1]),
                       ([1, 2], [0, 2]), ([1, 2], [False, True]), ([1, float("nan")], [0, 1])):
            with self.subTest(xs=xs, ys=ys), self.assertRaises(ValueError):
                c.ajustar_logistica(xs, ys)
        for kwargs in ({"tasa": 0}, {"penalizacion": -1}, {"iteraciones": 0}, {"iteraciones": 1.5}):
            with self.assertRaises(ValueError):
                c.ajustar_logistica([1, 2], [0, 1], **kwargs)

    def test_historial_desciende_y_gradiente_final_es_pequeno(self):
        modelo = experimento()["modelo_logistico"]
        objetivos = [v["objetivo"] for v in modelo["historial"]]
        self.assertTrue(all(b <= a + 1e-12 for a, b in zip(objetivos, objetivos[1:])))
        self.assertLess(objetivos[-1], objetivos[0])
        self.assertLess(modelo["norma_gradiente_final"], 1e-6)

    def test_matriz_manual_y_denominadores_cero(self):
        m = c.metricas_clasificacion([1, 1, 0, 0, 0], [1, 0, 1, 0, 0])
        self.assertEqual([m[k] for k in ("VP", "VN", "FP", "FN")], [1, 2, 1, 1])
        self.assertEqual((m["exactitud"], m["precision"], m["recobrado"], m["f1"]), (.6, .5, .5, .5))
        vacia = c.metricas_clasificacion([0, 0], [0, 0])
        for k in ("precision", "recobrado", "f1"):
            self.assertIsNone(vacia[k])


class DatosYFlujo(unittest.TestCase):
    def test_generador_reproduce_archivos_y_conteos(self):
        generados = contenidos()
        self.assertEqual(len(generados), 6)
        for nombre, texto in generados.items():
            self.assertEqual((UNIDAD / "datos" / nombre).read_bytes(), texto.encode("utf-8"))
        for nombre, esperado in (("equilibrado", [(80, 36), (40, 18), (40, 16)]),
                                 ("desbalanceado", [(200, 25), (100, 14), (100, 9)])):
            for fase, conteos in zip(("entrenamiento", "validacion", "prueba"), esperado):
                filas, _ = c.leer_csv(UNIDAD / "datos" / nombre / f"{fase}.csv")
                self.assertEqual((len(filas), sum(f["revision_confirmada"] for f in filas)), conteos)

    def test_lector_rechaza_filas_y_etiquetas_invalidas(self):
        cabecera = "caso_id,senal_previa,revision_confirmada\n"
        entradas = ["", cabecera, "caso_id,senal_previa,senal_previa\na,1,0\n",
                    cabecera + "a,1\n", cabecera + "a,1,0,extra\n", cabecera + "a,,0\n",
                    cabecera + "a,NaN,0\n", cabecera + "a,101,1\n", cabecera + "a,-1,1\n",
                    cabecera + "a,5,2\n", cabecera + "a,5,1.0\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in entradas:
                ruta.write_text(texto)
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    c.leer_csv(ruta)

    def test_ids_disjuntos_permiten_senales_repetidas(self):
        fila = {"caso_id": "a", "senal_previa": 50, "revision_confirmada": 1}
        c.validar_ids({"entrenamiento": [fila], "validacion": [dict(fila, caso_id="b")]})
        for datos in ({"entrenamiento": [fila, fila]}, {"entrenamiento": [fila], "prueba": [fila]}):
            with self.assertRaises(ValueError):
                c.validar_ids(datos)

    def test_default_no_necesita_archivo_prueba(self):
        with tempfile.TemporaryDirectory() as carpeta:
            for fase in ("entrenamiento", "validacion"):
                shutil.copy2(UNIDAD / "datos/equilibrado" / f"{fase}.csv", carpeta)
            informe = c.ejecutar_experimento("equilibrado", carpeta)
            self.assertIsNone(informe["prueba"])
            self.assertNotIn("prueba", informe["fuentes"])

    def test_validacion_cambia_seleccion_pero_no_ajuste(self):
        original = c.leer_csv
        def cambiar(ruta):
            filas, huella = original(ruta)
            if Path(ruta).stem == "validacion":
                for fila in filas:
                    fila["revision_confirmada"] = 1 - fila["revision_confirmada"]
                    fila["senal_previa"] += 1
            return filas, huella
        base = experimento()
        with patch.object(c, "leer_csv", side_effect=cambiar):
            variante = experimento()
        for campo in ("modelo_logistico", "referencia", "entrenamiento"):
            self.assertEqual(base[campo], variante[campo])
        self.assertNotEqual(base["seleccionado"], variante["seleccionado"])

    def test_prueba_no_cambia_modelo_umbral_ni_probabilidades(self):
        original = c.leer_csv
        def cambiar(ruta):
            filas, huella = original(ruta)
            if Path(ruta).stem == "prueba":
                for fila in filas:
                    fila["revision_confirmada"] = 1 - fila["revision_confirmada"]
            return filas, huella
        base = experimento("desbalanceado", True)
        with patch.object(c, "leer_csv", side_effect=cambiar):
            variante = experimento("desbalanceado", True)
        for campo in ("modelo_logistico", "referencia", "candidatos", "seleccionado", "validacion"):
            self.assertEqual(base[campo], variante[campo])
        for campo in ("probabilidad_1", "prediccion"):
            self.assertEqual([p[campo] for p in base["prueba"]["predicciones"]], [p[campo] for p in variante["prueba"]["predicciones"]])
        self.assertNotEqual(base["prueba"]["metricas"], variante["prueba"]["metricas"])

    def test_umbrales_conservan_probabilidades_y_perdida(self):
        informe = experimento("desbalanceado")
        evaluaciones = [informe["validacion"][nombre] for nombre in c.UMBRALES]
        for ev in evaluaciones:
            self.assertEqual([p["probabilidad_1"] for p in ev["predicciones"]],
                             [p["probabilidad_1"] for p in evaluaciones[0]["predicciones"]])
            self.assertEqual(ev["metricas"]["perdida_log"], evaluaciones[0]["metricas"]["perdida_log"])
        self.assertNotEqual(evaluaciones[0]["metricas"]["f1"], evaluaciones[1]["metricas"]["f1"])

    def test_resultados_y_mismos_casos(self):
        for nombre, elegido in (("equilibrado", "logistica_050"), ("desbalanceado", "logistica_020")):
            informe = experimento(nombre, True)
            self.assertEqual(informe["seleccionado"], elegido)
            ids = [[p["caso_id"] for p in ev["predicciones"]] for ev in informe["validacion"].values()]
            self.assertTrue(all(v == ids[0] for v in ids))
        m = informe["validacion"][elegido]["metricas"]
        self.assertEqual([m[k] for k in ("VP", "VN", "FP", "FN")], [10, 71, 15, 4])
        self.assertAlmostEqual(m["f1"], 20 / 39)

    def test_mayoria_empata_en_cero_y_siempre_uno_no_inventa_probabilidad(self):
        original = c.leer_csv
        def equilibrar(ruta):
            filas, huella = original(ruta)
            if Path(ruta).stem == "entrenamiento":
                for i, fila in enumerate(filas):
                    fila["revision_confirmada"] = i % 2
            return filas, huella
        with patch.object(c, "leer_csv", side_effect=equilibrar):
            informe = experimento()
        self.assertEqual(informe["referencia"], {"clase_mayoritaria": 0, "frecuencia_positiva": .5})
        self.assertIsNone(informe["validacion"]["siempre_1"]["metricas"]["perdida_log"])
        self.assertTrue(all(p["probabilidad_1"] is None for p in informe["validacion"]["siempre_1"]["predicciones"]))

    def test_una_clase_rechazada_en_validacion_permitida_en_prueba(self):
        original = c.leer_csv
        for objetivo in ("validacion", "prueba"):
            def cambiar(ruta):
                filas, huella = original(ruta)
                if Path(ruta).stem == objetivo:
                    for fila in filas:
                        fila["revision_confirmada"] = 0
                return filas, huella
            with patch.object(c, "leer_csv", side_effect=cambiar):
                if objetivo == "validacion":
                    with self.assertRaises(ValueError):
                        experimento(cierre=True)
                else:
                    self.assertIsNone(experimento(cierre=True)["prueba"]["metricas"]["recobrado"])

    def test_empate_sin_redondear_y_f1_indefinido(self):
        validacion = {k: {"metricas": {"f1": .5}} for k in ("a", "b")}
        self.assertEqual(c.seleccionar(validacion, ("a", "b")), "a")
        validacion["b"]["metricas"]["f1"] = .50001
        self.assertEqual(c.seleccionar(validacion, ("a", "b")), "b")
        validacion["a"]["metricas"]["f1"] = None
        with self.assertRaises(ValueError):
            c.seleccionar(validacion, ("a", "b"))

    def test_consulta_y_limites(self):
        externo = experimento(senal=100)["consulta"]
        self.assertTrue(externo["fuera_rango"])
        self.assertEqual(externo["clase"], 1)
        self.assertFalse(experimento(senal=5)["consulta"]["fuera_rango"])
        for valor in (-1, 101, float("nan")):
            with self.assertRaises(ValueError):
                experimento(senal=valor)

    def test_exportacion_y_rechazo_de_sobrescritura(self):
        for cierre in (False, True):
            informe = experimento(cierre=cierre)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "exportado"
                c.exportar(informe, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text()), informe)
                self.assertEqual((destino / "predicciones_prueba.csv").exists(), cierre)
                with (destino / "predicciones_validacion.csv").open(newline="") as archivo:
                    filas = list(csv.DictReader(archivo))
                self.assertEqual(len(filas), 120)
                self.assertTrue(all(f["probabilidad_1"] == "" for f in filas if f["candidato"] == "siempre_1"))
                with self.assertRaises(FileExistsError):
                    c.exportar(informe, destino)

    def test_prueba_se_lee_despues_de_seleccionar(self):
        eventos = []
        original_lector, original_selector = c.leer_csv, c.seleccionar
        def leer(ruta):
            eventos.append(Path(ruta).stem)
            return original_lector(ruta)
        def elegir(*args):
            eventos.append("seleccionar")
            return original_selector(*args)
        with patch.object(c, "leer_csv", side_effect=leer), patch.object(c, "seleccionar", side_effect=elegir):
            experimento(cierre=True)
        self.assertEqual(eventos, ["entrenamiento", "validacion", "seleccionar", "prueba"])


class Figuras(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_proporciones_e_historial_son_los_observados(self):
        informe = experimento(cierre=True)
        curva, descenso = construir_figuras(informe)["aprendizaje"].axes
        for puntos, fase in zip(curva.collections, ("entrenamiento", "validacion")):
            grupos = {}
            for r in informe[fase]["logistica_050"]["predicciones"]:
                grupos.setdefault(r["senal_previa"], []).append(r["real"])
            np.testing.assert_allclose(puntos.get_offsets(), [(x, sum(ys) / len(ys)) for x, ys in grupos.items()])
        self.assertEqual(len(curva.collections), 2)
        np.testing.assert_allclose(descenso.lines[0].get_ydata(), [h["objetivo"] for h in informe["modelo_logistico"]["historial"]])

    def test_barras_corresponden_a_validacion_y_parten_de_cero(self):
        informe = experimento("desbalanceado", True)
        eje = construir_figuras(informe)["umbrales"].axes[0]
        valores = [informe["validacion"][candidato]["metricas"][metrica]
                   for metrica in ("exactitud", "f1") for candidato in informe["candidatos"]]
        np.testing.assert_allclose([p.get_height() for p in eje.patches], valores)
        self.assertEqual(eje.get_ylim()[0], 0)

    def test_matrices_con_orientacion_y_escala_comun(self):
        informe = experimento("desbalanceado", True)
        ejes = construir_figuras(informe)["matrices"].axes
        for eje, nombre in zip(ejes, ("mayoria", "logistica_050", "logistica_020")):
            m = informe["validacion"][nombre]["metricas"]
            np.testing.assert_equal(eje.images[0].get_array(), [[m["VN"], m["FP"]], [m["FN"], m["VP"]]])
            self.assertEqual(eje.images[0].get_clim(), (0, 100))

    def test_png_svg_validos_y_no_sobrescritura(self):
        from PIL import Image
        informe = experimento()
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_figuras(informe, carpeta)
            png = Path(carpeta) / "aprendizaje.png"
            with Image.open(png) as imagen:
                imagen.verify()
            self.assertIn("<svg", (Path(carpeta) / "aprendizaje.svg").read_text())
            antes = png.read_bytes()
            with self.assertRaises(FileExistsError):
                guardar_figuras(informe, carpeta)
            self.assertEqual(png.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()

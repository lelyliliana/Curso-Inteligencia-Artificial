"""Métricas de referencia, empates, capacidad, separación y artefactos."""

import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, precision_recall_curve, roc_auc_score, roc_curve

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/"ejemplos"))
import decisiones as d
import figuras


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


generador = cargar("generador", UNIDAD/"datos/generar_datos.py")
manual = cargar("manual", UNIDAD/"soluciones/03_metricas_a_mano.py")


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datos = {n: d.leer_csv(UNIDAD/"datos"/n/"validacion.csv", n)[0] for n in d.POLITICAS}
        cls.informes = {n: d.ejecutar_experimento(n, UNIDAD/"datos"/n) for n in d.POLITICAS}


class Matematicas(Base):
    def test_cuatro_casos_manuales(self):
        y, s = [1, 0, 1, 0], [.8, .8, .4, .1]
        m = d.medidas(y, [1, 1, 0, 0], d.COSTOS["costos"])
        self.assertEqual([m[c] for c in ("VP", "VN", "FP", "FN")], [1, 1, 1, 1])
        self.assertEqual(m["costo_total"], 7)
        self.assertEqual(m["precision"], .5)
        self.assertEqual(m["recobrado"], .5)
        ev = d.ordenacion(y, s)
        self.assertAlmostEqual(ev["auc_roc"], 5/8)
        self.assertAlmostEqual(ev["ap"], 7/12)
        self.assertAlmostEqual(ev["brier"], .2625)

    def test_confusion_independiente(self):
        for nombre, informe in self.informes.items():
            for ev in informe["validacion"].values():
                filas = ev["decisiones"]
                tn, fp, fn, tp = confusion_matrix([r["real"] for r in filas], [r["decision"] for r in filas], labels=[0, 1]).ravel()
                self.assertEqual([ev["metricas"][c] for c in ("VN", "FP", "FN", "VP")], [tn, fp, fn, tp])
                self.assertEqual(ev["metricas"]["costo_total"], int(fp*d.COSTOS[nombre]["FP"]+fn*d.COSTOS[nombre]["FN"]))

    def test_auc_por_pares_y_biblioteca(self):
        for nombre, filas in self.datos.items():
            y, s = [f["requiere_revision"] for f in filas], [f["puntuacion"] for f in filas]
            valor = self.informes[nombre]["diagnostico_ordenacion"]["auc_roc"]
            self.assertAlmostEqual(valor, manual.auc_por_pares(y, s))
            self.assertAlmostEqual(valor, roc_auc_score(y, s))

    def test_ap_brier_y_curvas_biblioteca(self):
        for nombre, filas in self.datos.items():
            y, s = [f["requiere_revision"] for f in filas], [f["puntuacion"] for f in filas]
            diag = self.informes[nombre]["diagnostico_ordenacion"]
            self.assertAlmostEqual(diag["ap"], average_precision_score(y, s))
            self.assertAlmostEqual(diag["brier"], brier_score_loss(y, s))
            fpr, tpr, umbrales = roc_curve(y, s, drop_intermediate=False)
            np.testing.assert_allclose([p["tasa_fp"] for p in diag["puntos"]], fpr)
            np.testing.assert_allclose([p["recobrado"] for p in diag["puntos"]], tpr)
            np.testing.assert_allclose([p["umbral"] for p in diag["puntos"][1:]], umbrales[1:])
            precision, recobrado, _ = precision_recall_curve(y, s, drop_intermediate=False)
            np.testing.assert_allclose([p["precision"] for p in diag["puntos"][1:]], precision[-2::-1])
            np.testing.assert_allclose([p["recobrado"] for p in diag["puntos"][1:]], recobrado[-2::-1])

    def test_empates_sin_ordenar_por_etiquetas(self):
        for y in ([1, 0, 1, 0], [0, 1, 0, 1]):
            ev = d.ordenacion(y, [.5]*4)
            self.assertEqual(len(ev["puntos"]), 2)
            self.assertEqual(ev["auc_roc"], .5)
            self.assertEqual(ev["ap"], .5)

    def test_cuadrado_preserva_orden_no_brier(self):
        for informe in self.informes.values():
            a, b = informe["diagnostico_ordenacion"], informe["diagnostico_cuadrado"]
            self.assertEqual(a["auc_roc"], b["auc_roc"])
            self.assertEqual(a["ap"], b["ap"])
            self.assertNotEqual(a["brier"], b["brier"])

    def test_indefinidas_y_cero_son_distintos(self):
        m = d.medidas([0, 0], [0, 0], {"FP": 1, "FN": 6})
        self.assertIsNone(m["precision"])
        self.assertIsNone(m["recobrado"])
        self.assertIsNone(m["f1"])
        self.assertEqual(m["tasa_fp"], 0.)
        self.assertEqual(m["costo_total"], 0)
        self.assertEqual(d.medidas([0, 1], [0, 0], d.COSTOS["costos"])["f1"], 0.)
        self.assertIsNone(d.ordenacion([0, 0], [.1, .2])["ap"])
        self.assertIsNone(d.ordenacion([1, 1], [.1, .2])["auc_roc"])
        self.assertEqual(d.ordenacion([1, 1], [.1, .2])["ap"], 1.)

    def test_intervalos_incluyen_bordes_una_vez(self):
        s = [0., .2, .4, .6, .8, 1.]
        grupos = d.ordenacion([0, 0, 1, 0, 1, 1], s)["fiabilidad"]
        self.assertEqual([g["n"] for g in grupos], [1, 1, 1, 1, 2])
        self.assertAlmostEqual(grupos[-1]["puntuacion_media"], .9)
        vacios = d.ordenacion([0, 1], [.1, .1])["fiabilidad"][1:]
        self.assertTrue(all(g["n"] == 0 and g["fraccion_positiva"] is None for g in vacios))

    def test_cambiar_costos_conserva_decisiones(self):
        filas = self.datos["costos"]
        originales = self.informes["costos"]["validacion"]
        for costo_fn, elegido in ((1, "umbral050"), (6, "umbral020"), (12, "umbral010")):
            nuevos = {c: d.evaluar(filas, p, {"FP": 1, "FN": costo_fn}) for c, p in d.POLITICAS["costos"].items()}
            self.assertEqual(d.seleccionar(nuevos), elegido)
            for c in nuevos:
                self.assertEqual(nuevos[c]["decisiones"], originales[c]["decisiones"])
                self.assertEqual(nuevos[c]["metricas"]["f1"], originales[c]["metricas"]["f1"])

    def test_prevalencia_bayes(self):
        ev = d.sensibilidad_prevalencia({"recobrado": .8, "tasa_fp": .1})
        self.assertAlmostEqual(ev[0]["precision_hipotetica"], .04/(.04+.095))
        self.assertAlmostEqual(ev[-1]["precision_hipotetica"], .4/(.4+.05))
        self.assertTrue(all(r["precision_hipotetica"] is None for r in d.sensibilidad_prevalencia({"recobrado": 0., "tasa_fp": 0.})))


class Politicas(Base):
    def test_umbral_inclusivo_y_nadie(self):
        filas = [{"caso_id": str(i), "puntuacion": s} for i, s in enumerate([0, .49, .5, 1])]
        self.assertEqual(d.decidir(filas, {"umbral": .5, "cupo": None}), [0, 0, 1, 1])
        self.assertEqual(d.decidir(filas, {"umbral": None, "cupo": None}), [0, 0, 0, 0])
        self.assertEqual(d.decidir(filas, {"umbral": 0., "cupo": 0}), [0, 0, 0, 0])

    def test_cupo_y_desempate_id_sin_etiquetas(self):
        filas = [{"caso_id": c, "lote_id": "L", "puntuacion": .8} for c in ("C", "A", "B")]
        self.assertEqual(d.decidir(filas, {"umbral": .5, "cupo": 2}), [0, 1, 1])
        for f in filas:
            f["requiere_revision"] = int(f["caso_id"] == "C")
        self.assertEqual(d.decidir(filas, {"umbral": .5, "cupo": 2}), [0, 1, 1])

    def test_cupo_por_lote_no_global(self):
        filas = [{"caso_id": f"{l}-{i}", "lote_id": l, "puntuacion": .9} for l in ("A", "B") for i in range(8)]
        pred = d.decidir(filas, {"umbral": 0., "cupo": 6})
        self.assertEqual(sum(pred[:8]), 6)
        self.assertEqual(sum(pred[8:]), 6)
        for ev in self.informes["capacidad"]["validacion"].values():
            self.assertTrue(all(m["alertas"] <= 6 for m in ev["por_lote"].values()))

    def test_orden_filas_no_cambia_ids_elegidos(self):
        filas = self.datos["capacidad"]
        politica = d.POLITICAS["capacidad"]["umbral050_top6"]
        def elegidos(fs):
            return {f["caso_id"] for f, pred in zip(fs, d.decidir(fs, politica)) if pred}
        self.assertEqual(elegidos(filas), elegidos(list(reversed(filas))))

    def test_datos_no_usados_para_decidir(self):
        filas = copy.deepcopy(self.datos["costos"])
        p = d.POLITICAS["costos"]["umbral020"]
        esperado = d.decidir(filas, p)
        for f in filas:
            f["senal_a"], f["senal_b"], f["requiere_revision"] = 0., 1., 1-f["requiere_revision"]
        self.assertEqual(d.decidir(filas, p), esperado)

    def test_desempate_costo_alertas_orden(self):
        ev = self.informes["capacidad"]["validacion"]
        self.assertEqual(ev["umbral030_top6"]["metricas"]["costo_total"], ev["umbral050_top6"]["metricas"]["costo_total"])
        self.assertEqual(d.seleccionar(ev), "umbral050_top6")
        self.assertEqual(d.seleccionar({"a": {"metricas": {"costo_total": 1, "alertas": 2}}, "b": {"metricas": {"costo_total": 1, "alertas": 2}}}), "a")

    def test_diagnostico_sin_cupo_no_es_candidato(self):
        informe = self.informes["capacidad"]
        self.assertNotIn("umbral050_sin_cupo", informe["validacion"])
        self.assertEqual(sum(m["alertas"] > 6 for m in informe["diagnostico_sin_cupo"]["por_lote"].values()), 5)
        for c, ev in informe["validacion"].items():
            for campo in ("n", "VP", "FP", "FN", "VN", "costo_total", "alertas"):
                self.assertEqual(ev["metricas"][campo], sum(m[campo] for m in ev["por_lote"].values()))

    def test_politica_y_ordenacion_invalidas(self):
        for p in ({"umbral": -1, "cupo": None}, {"umbral": float("nan"), "cupo": None}, {"umbral": .5, "cupo": 1.5}):
            with self.assertRaises(ValueError):
                d.decidir([], p)
        for y, s in (([], []), ([2], [.2]), ([1], [float("inf")]), ([1, 0], [.2])):
            with self.assertRaises(ValueError):
                d.ordenacion(y, s)


class DatosCierre(Base):
    def test_regeneracion(self):
        for ruta, texto in generador.contenidos().items():
            self.assertEqual(texto.encode(), (UNIDAD/"datos"/ruta).read_bytes())

    def test_csv_invalidos(self):
        original = (UNIDAD/"datos/costos/validacion.csv").read_text()
        linea = original.splitlines()[1]
        valores = linea.split(",")
        variantes = ["", original.replace("senal_b", "senal_a", 1), original+linea+"\n", original.replace(linea, linea+",0", 1)]
        for campo, valor in ((1, "nan"), (2, "1.1"), (3, "-0.1"), (4, "2"), (1, "")):
            cambiados = valores.copy()
            cambiados[campo] = valor
            variantes.append(original.replace(linea, ",".join(cambiados), 1))
        with tempfile.TemporaryDirectory() as carpeta:
            p = Path(carpeta)/"datos.csv"
            for texto in variantes:
                p.write_text(texto)
                with self.assertRaises(ValueError):
                    d.leer_csv(p, "costos")

    def test_prueba_no_necesaria_por_defecto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            (Path(carpeta)/"validacion.csv").write_bytes((UNIDAD/"datos/costos/validacion.csv").read_bytes())
            informe = d.ejecutar_experimento("costos", carpeta)
            self.assertIsNone(informe["prueba"])
            self.assertEqual(set(informe["fuentes"]), {"validacion"})

    def test_lectura_prueba_despues_de_seleccionar(self):
        eventos = []
        leer, seleccionar = d.leer_csv, d.seleccionar
        def lectura(ruta, nombre):
            eventos.append(Path(ruta).name)
            return leer(ruta, nombre)
        def seleccion(ev):
            eventos.append("seleccion")
            return seleccionar(ev)
        with patch.object(d, "leer_csv", side_effect=lectura), patch.object(d, "seleccionar", side_effect=seleccion):
            d.ejecutar_experimento("costos", UNIDAD/"datos/costos", True)
        self.assertEqual(eventos, ["validacion.csv", "seleccion", "prueba.csv"])

    def test_etiquetas_prueba_no_influyen_en_decisiones(self):
        leer = d.leer_csv
        for nombre in d.POLITICAS:
            original = d.ejecutar_experimento(nombre, UNIDAD/"datos"/nombre, True)
            def alterado(ruta, n):
                filas, fuente = leer(ruta, n)
                if Path(ruta).name == "prueba.csv":
                    for f in filas:
                        f["requiere_revision"] = 1-f["requiere_revision"]
                return filas, fuente
            with patch.object(d, "leer_csv", side_effect=alterado):
                nuevo = d.ejecutar_experimento(nombre, UNIDAD/"datos"/nombre, True)
            for clave in ("validacion", "seleccionado", "politica_elegida", "diagnostico_ordenacion", "diagnostico_cuadrado"):
                self.assertEqual(nuevo[clave], original[clave])
            self.assertEqual([r["decision"] for r in nuevo["prueba"]["decisiones"]], [r["decision"] for r in original["prueba"]["decisiones"]])
            self.assertNotEqual(nuevo["prueba"]["metricas"], original["prueba"]["metricas"])

    def test_lotes_e_ids_separados_en_cierre(self):
        leer = d.leer_csv
        for campo in ("lote_id", "caso_id"):
            def alterado(ruta, nombre):
                filas, fuente = leer(ruta, nombre)
                if Path(ruta).name == "prueba.csv":
                    filas[0][campo] = self.datos["capacidad"][0][campo]
                return filas, fuente
            with patch.object(d, "leer_csv", side_effect=alterado), self.assertRaises(ValueError):
                d.ejecutar_experimento("capacidad", UNIDAD/"datos/capacidad", True)

    def test_cierre_solo_elegido_y_cupo(self):
        informe = d.ejecutar_experimento("capacidad", UNIDAD/"datos/capacidad", True)
        self.assertEqual(informe["prueba"]["politica"], informe["seleccionado"])
        self.assertTrue(all(m["alertas"] <= 6 for m in informe["prueba"]["por_lote"].values()))
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta)/"exportacion"
            d.exportar(informe, destino)
            self.assertEqual(json.loads((destino/"informe.json").read_text()), informe)
            with (destino/"decisiones_prueba.csv").open() as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(len(filas), 120)
            self.assertEqual({r["politica"] for r in filas}, {informe["seleccionado"]})
            with self.assertRaises(FileExistsError):
                d.exportar(informe, destino)

    def test_publicados_coinciden(self):
        for nombre, informe in self.informes.items():
            guardado = json.loads((UNIDAD/"recursos"/nombre/"informe.json").read_text())
            actual = copy.deepcopy(informe)
            guardado.pop("versiones")
            actual.pop("versiones")
            self.assertEqual(actual, guardado)
            esperado = [dict(politica=c, **r) for c, ev in informe["validacion"].items() for r in ev["decisiones"]]
            with (UNIDAD/"recursos"/nombre/"decisiones_validacion.csv").open() as archivo:
                self.assertEqual(list(csv.DictReader(archivo)), [{k: str(v) for k, v in r.items()} for r in esperado])


class Figuras(Base):
    def tearDown(self):
        figuras.plt.close("all")

    def test_costos_y_metricas_sin_punto_indefinido(self):
        informe = self.informes["costos"]
        fig = figuras.figura_costos(informe)
        n = len(informe["validacion"])
        np.testing.assert_allclose([p.get_width() for p in fig.axes[0].patches[:n]], [ev["metricas"]["FP"] for ev in informe["validacion"].values()])
        np.testing.assert_allclose([p.get_width() for p in fig.axes[0].patches[n:]], [6*ev["metricas"]["FN"] for ev in informe["validacion"].values()])
        self.assertTrue(np.isnan(fig.axes[1].lines[0].get_ydata()[0]))
        self.assertEqual(fig.axes[0].get_xlim()[0], 0)

    def test_curvas_y_fiabilidad(self):
        informe = self.informes["costos"]
        fig = figuras.figura_ordenacion(informe)
        puntos = informe["diagnostico_ordenacion"]["puntos"]
        np.testing.assert_allclose(fig.axes[0].lines[0].get_xdata(), [p["tasa_fp"] for p in puntos])
        np.testing.assert_allclose(fig.axes[0].lines[0].get_ydata(), [p["recobrado"] for p in puntos])
        self.assertEqual(fig.axes[1].lines[0].get_drawstyle(), "steps-pre")
        grupos = [g for g in informe["diagnostico_ordenacion"]["fiabilidad"] if g["n"]]
        np.testing.assert_allclose(fig.axes[2].lines[0].get_xdata(), [g["puntuacion_media"] for g in grupos])
        np.testing.assert_allclose(fig.axes[2].lines[0].get_ydata(), [g["fraccion_positiva"] for g in grupos])

    def test_cupos_y_barras(self):
        informe = self.informes["capacidad"]
        fig = figuras.figura_capacidad(informe)
        esperado = [m["alertas"] for m in informe["diagnostico_sin_cupo"]["por_lote"].values()]
        esperado += [m["alertas"] for m in informe["validacion"][informe["seleccionado"]]["por_lote"].values()]
        np.testing.assert_allclose([p.get_height() for p in fig.axes[0].patches], esperado)
        np.testing.assert_allclose(fig.axes[0].lines[0].get_ydata(), [6, 6])
        np.testing.assert_allclose([p.get_width() for p in fig.axes[1].patches], [ev["metricas"]["costo_total"] for ev in informe["validacion"].values()])

    def test_exportacion_grafica_no_lee_prueba(self):
        informe = copy.deepcopy(self.informes["costos"])
        informe["prueba"] = {"sin": "contenido utilizable"}
        with tempfile.TemporaryDirectory() as carpeta:
            figuras.guardar_figuras(informe, carpeta)
            for nombre in ("costos", "ordenacion"):
                self.assertGreater(figuras.plt.imread(Path(carpeta)/f"{nombre}.png").size, 0)
                self.assertIn("<svg", (Path(carpeta)/f"{nombre}.svg").read_text())
            with self.assertRaises(FileExistsError):
                figuras.guardar_figuras(informe, carpeta)


if __name__ == "__main__":
    unittest.main()

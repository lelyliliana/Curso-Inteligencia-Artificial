"""Referencias numéricas, separación de información y recarga para la Unidad 22."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, log_loss

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import texto_curso as tc
from figuras_texto import figura_comparacion, figura_diagnosticos, guardar_figuras
import matplotlib.pyplot as plt


def importar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


manual = importar("manual_textos", UNIDAD / "ejemplos/01_representar_textos.py")
generador = importar("datos_textos", UNIDAD / "datos/generar_datos.py")


def guardar_filas(ruta, filas):
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=tc.CAMPOS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


class Representacion(unittest.TestCase):
    def test_unicode_equivalente(self):
        self.assertEqual(tc.tokens("PROGRAMACIO\u0301N"), ["programación"])

    def test_conserva_negacion_y_tildes(self):
        self.assertEqual(tc.tokens("¡No sé si sí!"), ["no", "sé", "si", "sí"])

    def test_letras_numeros_y_puntuacion(self):
        self.assertEqual(tc.tokens("a_23, b-7 🤖"), ["a", "23", "b", "7"])

    def test_vacio_y_tipo_invalido(self):
        self.assertEqual(tc.tokens("..."), [])
        with self.assertRaises(ValueError):
            tc.tokens(None)

    def test_bigramas_ordenados(self):
        self.assertEqual(tc.terminos("no material", 2), ["no", "material", "no material"])
        with self.assertRaises(ValueError):
            tc.terminos("hola", 3)

    def test_referencia_manual(self):
        r = manual.experimento()
        self.assertEqual(r["conteos"], [[1, 2, 0], [1, 0, 1], [0, 0, 1]])
        self.assertEqual(r["df"], [2, 1, 2])
        np.testing.assert_allclose(r["tfidf"][0], [.35543246785041743, .9347019636214327, 0], atol=1e-12)

    def test_corpus_sin_vocabulario(self):
        with self.assertRaises(ValueError):
            manual.calcular_manual(["", "!!!"])

    def test_df_cuenta_documentos(self):
        r = manual.calcular_manual(["a a a", "a b", "b"])
        self.assertEqual(r["df"], [2, 2])

    def test_desconocidas_no_amplian_vocabulario(self):
        vec = tc.vectorizador().fit(["aula material", "material"])
        antes = dict(vec.vocabulary_)
        np.testing.assert_array_equal(vec.transform(["galaxia"]).toarray(), [[0, 0]])
        self.assertEqual(antes, vec.vocabulary_)

    def test_unigramas_colisionan_y_bigramas_distinguen(self):
        textos = ["Necesito acceso, no material", "Necesito material, no acceso"]
        uni = tc.vectorizador().fit_transform(textos).toarray()
        bi = tc.vectorizador(2).fit_transform(textos).toarray()
        np.testing.assert_array_equal(uni[0], uni[1])
        self.assertGreater(np.linalg.norm(bi[0] - bi[1]), .1)


class Datos(unittest.TestCase):
    def setUp(self):
        self.train = tc.leer_particion(UNIDAD / "datos/entrenamiento.csv")
        self.val = tc.leer_particion(UNIDAD / "datos/validacion.csv")

    def test_tamanos_y_balance(self):
        for nombre, n, grupos in (("entrenamiento", 54, 18), ("validacion", 27, 9), ("prueba", 27, 9)):
            filas = tc.leer_particion(UNIDAD / f"datos/{nombre}.csv")
            self.assertEqual(len(filas), n)
            self.assertEqual(len({r["familia"] for r in filas}), grupos)
            np.testing.assert_array_equal(np.bincount(tc.etiquetas(filas)), [n // 3] * 3)

    def test_particiones_separadas(self):
        tc.validar_separacion(self.train, self.val, tc.leer_particion(UNIDAD / "datos/prueba.csv"))

    def test_familia_compartida(self):
        self.val[0]["familia"] = self.train[0]["familia"]
        with self.assertRaisesRegex(ValueError, "Familias"):
            tc.validar_separacion(self.train, self.val)

    def test_duplicado_normalizado(self):
        self.val[0]["texto"] = self.train[0]["texto"].upper() + "!!!"
        with self.assertRaisesRegex(ValueError, "duplicado"):
            tc.validar_separacion(self.train, self.val)

    def test_id_duplicado(self):
        self.val[0]["id"] = self.train[0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            tc.validar_separacion(self.train, self.val)

    def test_lector_rechaza_corrupcion(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "datos.csv"
            self.train[0]["texto"] += " cambiado"
            guardar_filas(p, self.train)
            with self.assertRaisesRegex(ValueError, "huella"):
                tc.leer_particion(p)

    def test_etiquetas_incompatibles_en_familia(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "datos.csv"
            self.train[0]["clase"] = "horario"
            guardar_filas(p, self.train)
            with self.assertRaisesRegex(ValueError, "incompatibles"):
                tc.leer_particion(p)

    def test_cabecera_y_datos_vacios(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "datos.csv"
            p.write_text("texto,clase\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tc.leer_particion(p)
            guardar_filas(p, [])
            with self.assertRaisesRegex(ValueError, "vacía"):
                tc.leer_particion(p)

    def test_regeneracion_exacta(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            for p in (UNIDAD / "datos").glob("*.csv"):
                self.assertEqual(p.read_bytes(), (Path(d) / p.name).read_bytes())


class ModeloYProtocolo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.informe = tc.ejecutar_experimento()
        cls.train = tc.leer_particion(UNIDAD / "datos/entrenamiento.csv")
        cls.estado = cls.informe["candidatos"]["unigramas"]["estado"]

    def test_softmax_estable(self):
        np.testing.assert_allclose(tc.softmax([[1000, 1000, 1000]]), [[1/3] * 3])
        np.testing.assert_allclose(tc.softmax([[1, 2, 3]]), tc.softmax([[1001, 1002, 1003]]))

    def test_metricas_referencia_independiente(self):
        y = np.array([0, 0, 1, 1, 2, 2])
        p = np.array([[.8, .1, .1], [.2, .6, .2], [.1, .7, .2], [.5, .3, .2], [.1, .1, .8], [.1, .7, .2]])
        m = tc.metricas(y, p)
        self.assertAlmostEqual(m["ce"], log_loss(y, p))
        self.assertAlmostEqual(m["macro_f1"], f1_score(y, p.argmax(1), average="macro"))
        np.testing.assert_array_equal(m["matriz"], confusion_matrix(y, p.argmax(1)))

    def test_indefinidos_y_empate(self):
        m = tc.metricas([0, 1, 2], np.full((3, 3), 1/3))
        self.assertEqual(m["matriz"], [[1, 0, 0]] * 3)
        self.assertIsNone(m["por_clase"][1]["precision"])
        self.assertAlmostEqual(m["macro_f1"], 1/6)

    def test_probabilidades_invalidas(self):
        for p in ([[.2, .2, .2]], [[float("nan"), 0, 1]], [[-1, 1, 1]]):
            with self.assertRaises(ValueError):
                tc.metricas([0], p)

    def test_seleccion_real_y_desempate(self):
        self.assertEqual(self.informe["seleccionado"], "unigramas")
        falsos = {n: {"validacion": {"metricas": {"ce": 1}}} for n in ("prevalencia", "unigramas", "bigramas")}
        self.assertEqual(tc.seleccionar(falsos), "prevalencia")
        falsos["bigramas"]["validacion"]["metricas"]["ce"] = .9
        self.assertEqual(tc.seleccionar(falsos), "bigramas")

    def test_modelo_completo_con_biblioteca(self):
        from sklearn.linear_model import LogisticRegression
        consultas = ["aula galaxia", "!!!", "Necesito material, no acceso", "contraseña y horario"]
        for nombre, n in (("unigramas", 1), ("bigramas", 2)):
            vec = tc.vectorizador(n)
            x = vec.fit_transform([r["texto"] for r in self.train])
            modelo = LogisticRegression(C=1, l1_ratio=0, solver="lbfgs", tol=1e-9, max_iter=1000).fit(x, tc.etiquetas(self.train))
            estado = self.informe["candidatos"][nombre]["estado"]
            np.testing.assert_allclose(tc.transformar(consultas, estado), vec.transform(consultas).toarray(), atol=1e-12)
            np.testing.assert_allclose(tc.predecir(consultas, estado), modelo.predict_proba(vec.transform(consultas)), atol=1e-12)

    def test_vector_cero_depende_solo_sesgos(self):
        p = tc.predecir(["credenciales caducadas", "!!!"], self.estado)
        np.testing.assert_array_equal(p[0], p[1])
        np.testing.assert_allclose(p[0], tc.softmax([self.estado["sesgos"]])[0])

    def test_idf_solo_entrenamiento(self):
        vocab = self.estado["vocabulario"]
        documentos = [set(tc.tokens(r["texto"])) for r in self.train]
        referencia = [np.log((1 + len(documentos)) / (1 + sum(t in d for d in documentos))) + 1 for t in vocab]
        np.testing.assert_allclose(self.estado["idf"], referencia, atol=1e-12)
        self.assertNotIn("recupero", vocab)  # Aparece en validación.

    def test_metadatos_no_entran_al_modelo(self):
        filas = [{**r, "id": "secreto", "familia": "otra", "tema": "cambiado"} for r in self.train]
        self.assertEqual(tc.ajustar(filas, "unigramas"), self.estado)

    def test_desarrollo_funciona_sin_prueba(self):
        with tempfile.TemporaryDirectory() as d:
            for nombre in ("entrenamiento.csv", "validacion.csv", "diagnosticos.json"):
                shutil.copy(UNIDAD / "datos" / nombre, d)
            r = tc.ejecutar_experimento(d)
            self.assertIsNone(r["prueba"])
            self.assertNotIn("prueba", r["fuentes"])
            self.assertEqual(r["candidatos"], self.informe["candidatos"])

    def test_cambiar_validacion_no_cambia_ajuste(self):
        original = tc.leer_particion
        def lectura(ruta):
            filas = original(ruta)
            if Path(ruta).stem == "validacion":
                for f in filas:
                    f["texto"] += " neologismoexperimental"
            return filas
        with patch.object(tc, "leer_particion", side_effect=lectura):
            r = tc.ejecutar_experimento()
        for nombre in r["candidatos"]:
            self.assertEqual(r["candidatos"][nombre]["estado"], self.informe["candidatos"][nombre]["estado"])

    def test_diagnosticos_no_se_puntuan_ni_seleccionan(self):
        for resultado in self.informe["diagnosticos"].values():
            self.assertIsNone(resultado["metricas"])
        with patch.object(tc.json, "loads", return_value=[{"id": "otro", "texto": "galaxia", "clase": None}]):
            r = tc.ejecutar_experimento()
        self.assertEqual(r["seleccionado"], self.informe["seleccionado"])
        self.assertEqual(r["candidatos"], self.informe["candidatos"])

    def test_prueba_no_cambia_ajuste_seleccion_ni_predicciones(self):
        cierre = tc.ejecutar_experimento(evaluar_prueba=True)
        original = tc.leer_particion
        def lectura(ruta):
            filas = original(ruta)
            if Path(ruta).stem == "prueba":
                for f in filas:
                    f["clase"] = tc.CLASES[(tc.CLASES.index(f["clase"]) + 1) % 3]
            return filas
        with patch.object(tc, "leer_particion", side_effect=lectura):
            cambiado = tc.ejecutar_experimento(evaluar_prueba=True)
        self.assertEqual(cierre["candidatos"], self.informe["candidatos"])
        self.assertEqual(cierre["candidatos"], cambiado["candidatos"])
        self.assertEqual(cierre["seleccionado"], cambiado["seleccionado"])
        self.assertNotEqual(cierre["prueba"]["metricas"], cambiado["prueba"]["metricas"])
        self.assertEqual([r["probabilidades"] for r in cierre["prueba"]["registros"]], [r["probabilidades"] for r in cambiado["prueba"]["registros"]])

    def test_rechaza_modelos_incompatibles(self):
        for campo, valor in (("clases", ["material", "acceso", "horario"]), ("tokenizador", "otro"), ("idf", [float("nan")] * 71), ("sesgos", [0, 0])):
            estado = copy.deepcopy(self.estado)
            estado[campo] = valor
            with self.assertRaises(ValueError):
                tc.validar_estado(estado)


class Artefactos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.informe = tc.ejecutar_experimento()

    def test_exportacion_recarga_y_no_sobrescritura(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "exportacion"
            self.assertEqual(tc.exportar(self.informe, p), 0)
            self.assertFalse((p / "predicciones_prueba.csv").exists())
            self.assertEqual(tc.cargar_modelo(p / "modelo.json"), self.informe["candidatos"]["unigramas"]["estado"])
            with self.assertRaises(FileExistsError):
                tc.exportar(self.informe, p)

    def test_figuras_corresponden_al_informe(self):
        f = figura_comparacion(self.informe)
        esperado = self.informe["candidatos"]["unigramas"]["validacion"]["metricas"]["matriz"]
        np.testing.assert_array_equal(f.axes[1].images[0].get_array(), esperado)
        self.assertAlmostEqual(f.axes[0].patches[4].get_height(), self.informe["candidatos"]["unigramas"]["validacion"]["metricas"]["ce"])
        plt.close(f)
        f = figura_diagnosticos(self.informe)
        for ax, nombre in zip(f.axes, ("unigramas", "bigramas")):
            np.testing.assert_array_equal(ax.images[0].get_array(), [r["probabilidades"] for r in self.informe["diagnosticos"][nombre]["registros"]])
        plt.close(f)

    def test_png_y_svg(self):
        with tempfile.TemporaryDirectory() as d:
            guardar_figuras(self.informe, d)
            for nombre in ("comparacion_matriz", "diagnosticos"):
                self.assertTrue((Path(d) / f"{nombre}.png").read_bytes().startswith(b"\x89PNG"))
                self.assertIn("<svg", (Path(d) / f"{nombre}.svg").read_text())

    def test_modelo_incompleto(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo.json"
            p.write_text('{"formato": 1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                tc.cargar_modelo(p)

    def test_exportacion_cierre_y_probabilidades_csv(self):
        informe = tc.ejecutar_experimento(evaluar_prueba=True)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "cierre"
            tc.exportar(informe, p)
            cierre = json.loads((p / "cierre.json").read_text())
            self.assertEqual(cierre["metricas"], informe["prueba"]["metricas"])
            self.assertEqual(cierre["modelo_sha256"], tc.huella(p / "modelo.json"))
            self.assertFalse(cierre["reajuste"])
            with (p / "predicciones_prueba.csv").open(encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 27)
            np.testing.assert_array_equal([[float(r[f"p_{c}"]) for c in tc.CLASES] for r in filas], [r["probabilidades"] for r in informe["prueba"]["registros"]])


if __name__ == "__main__":
    unittest.main()

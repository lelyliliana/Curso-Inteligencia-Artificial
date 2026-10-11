"""Referencias independientes, separación de información y evidencia de los talleres."""

import copy
from datetime import datetime, timedelta
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, mean_absolute_error
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ejemplos"))
import ambiente
import documentos
import energia
import talleres


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


generador = cargar("generador34", RAIZ / "datos/generar_datos.py")
demo = cargar("demo34", RAIZ / "ejemplos/04_demostrar_taller.py")
manual = cargar("manual34", RAIZ / "soluciones/05_decidir_a_mano.py")
PROTOCOLO = talleres.leer(RAIZ / "datos/protocolo.json")


def datos(taller, fase):
    return talleres.leer(RAIZ / "datos" / taller / f"{fase}.json")


def paquete(taller):
    return talleres.cargar_modelo(RAIZ / "recursos" / taller / "modelo.json", taller)


class DatosSeparados(unittest.TestCase):
    def test_regeneracion_identica(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            archivos = sorted(Path(d).rglob("*.json"))
            self.assertEqual(len(archivos), 9)
            for p in archivos:
                self.assertEqual(p.read_bytes(), (RAIZ / "datos" / p.relative_to(d)).read_bytes())

    def test_tamanos_e_identificadores(self):
        for t, tamanos in (("energia", (575, 192, 192)), ("ambiente", (240, 120, 120))):
            grupos = [datos(t, f) for f in ("entrenamiento", "validacion", "prueba")]
            self.assertEqual(tuple(map(len, grupos)), tamanos)
            ids = [r["id"] for g in grupos for r in g]
            self.assertEqual(len(ids), len(set(ids)))

    def test_temporal_objetivos_conocidos_al_siguiente_corte(self):
        grupos = [datos("energia", f) for f in ("entrenamiento", "validacion", "prueba")]
        for anterior, siguiente in zip(grupos, grupos[1:]):
            self.assertLessEqual(max(r["instante_objetivo"] for r in anterior), min(r["origen"] for r in siguiente))
        for g in grupos:
            for r in g:
                objetivo = datetime.fromisoformat(r["instante_objetivo"])
                self.assertEqual(objetivo - datetime.fromisoformat(r["origen"]), timedelta(hours=1))
                self.assertEqual(r["hora_siguiente"], objetivo.hour)
                self.assertEqual(r["laboral_siguiente"], int(objetivo.weekday() < 5))

    def test_persistencia_usa_ultima_lectura(self):
        filas = sum([datos("energia", f) for f in ("entrenamiento", "validacion", "prueba")], [])
        for anterior, actual in zip(filas, filas[1:]):
            self.assertEqual(actual["consumo_actual_kw"], anterior["objetivo_kw"])

    def test_zonas_disjuntas(self):
        zonas = [set(r["zona"] for r in datos("ambiente", f)) for f in ("entrenamiento", "validacion", "prueba")]
        self.assertEqual(list(map(len, zonas)), [6, 3, 3])
        for i in range(3):
            for j in range(i + 1, 3):
                self.assertFalse(zonas[i] & zonas[j])

    def test_familias_disjuntas_y_juicios_en_corpus(self):
        v, p, corpus = (datos("documentos", f) for f in ("validacion", "prueba", "corpus"))
        self.assertFalse({x["familia"] for x in v} & {x["familia"] for x in p})
        self.assertEqual((len(v), len(p), len(corpus)), (12, 12, 10))
        for grupo in (v, p):
            self.assertEqual(sum(x["documento_esperado"] is None for x in grupo), 4)
            self.assertTrue(all(x["documento_esperado"] in {d["id"] for d in corpus} | {None} for x in grupo))


class TallerEnergia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = datos("energia", "entrenamiento")
        cls.val = datos("energia", "validacion")
        cls.modelos = energia.ajustar(cls.train)

    def test_ridge_con_ecuaciones_normales_independientes(self):
        x = np.asarray([energia.validar(energia.entrada(f)) for f in self.train])
        y = np.asarray([f["objetivo_kw"] for f in self.train])
        z = (x - x.mean(axis=0)) / x.std(axis=0)
        a = np.column_stack([np.ones(len(x)), z])
        parametros = np.linalg.solve(a.T @ a + np.diag([0, 1, 1, 1, 1]), a.T @ y)
        m = self.modelos["ridge_1"]
        np.testing.assert_allclose([m["intercepto"], *m["coef"]], parametros, atol=1e-10)

    def test_escala_solo_entrenamiento(self):
        x = np.asarray([energia.validar(energia.entrada(f)) for f in self.train])
        np.testing.assert_array_equal(self.modelos["ridge_1"]["media"], x.mean(axis=0))
        self.assertEqual(self.modelos["ridge_1"]["max_kw"], max(f["consumo_actual_kw"] for f in self.train))

    def test_mae_con_biblioteca(self):
        r = energia.evaluar(self.modelos["ridge_1"], self.val)
        esperado = mean_absolute_error([c["objetivo_kw"] for c in r["casos"]], [c["prediccion_kw"] for c in r["casos"]])
        self.assertAlmostEqual(r["mae_kw"], esperado, places=12)

    def test_referencia_exacta(self):
        for fila in self.val[:5]:
            r = energia.predecir(self.modelos["persistencia"], energia.entrada(fila))
            self.assertEqual(r["prediccion_kw"], fila["consumo_actual_kw"])

    def test_etiquetas_no_entran_en_prediccion(self):
        otras = copy.deepcopy(self.val)
        for fila in otras:
            fila["objetivo_kw"] += 10000
        originales = energia.evaluar(self.modelos["ridge_1"], self.val)
        cambiadas = energia.evaluar(self.modelos["ridge_1"], otras)
        self.assertEqual([c["prediccion_kw"] for c in originales["casos"]], [c["prediccion_kw"] for c in cambiadas["casos"]])
        self.assertNotEqual(originales["mae_kw"], cambiadas["mae_kw"])

    def test_hora_ciclica_y_rechazos(self):
        consulta = dict(demo.CONSULTAS["energia"])
        for campo, valores in (("consumo_actual_kw", [None, True, -1, 201, float("nan"), float("inf")]),
                              ("hora_siguiente", [-1, 24, 1.0, True]), ("laboral_siguiente", [2, False])):
            for valor in valores:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    energia.validar({**consulta, campo: valor})
        x = energia.validar({**consulta, "hora_siguiente": 0})
        self.assertEqual(x[1:3], [0.0, 1.0])

    def test_extrapolacion_se_identifica(self):
        r = energia.predecir(self.modelos["ridge_1"], {**demo.CONSULTAS["energia"], "consumo_actual_kw": 150})
        self.assertEqual(r["estado"], "revisar")
        self.assertTrue(r["fuera_rango_consumo"])

    def test_seleccion_solo_por_mae_y_orden(self):
        elegido, _, resultados = energia.desarrollar(self.train, self.val, PROTOCOLO["energia"])
        self.assertEqual(elegido, min(resultados, key=lambda k: resultados[k]["mae_kw"]))


class TallerAmbiente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = datos("ambiente", "entrenamiento")
        cls.val = datos("ambiente", "validacion")
        cls.modelos = ambiente.ajustar(cls.train, PROTOCOLO["ambiente"])

    def test_inferencia_equivale_a_estimador(self):
        x = [ambiente.validar(ambiente.entrada(f)) for f in self.train]
        y = [f["revision_prioritaria"] for f in self.train]
        escala = StandardScaler().fit(x)
        estimador = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, tol=1e-8).fit(escala.transform(x), y)
        v = [ambiente.validar(ambiente.entrada(f)) for f in self.val]
        propias = [ambiente.predecir(self.modelos["logistica_0.3"], ambiente.entrada(f))["puntuacion"] for f in self.val]
        np.testing.assert_allclose(propias, estimador.predict_proba(escala.transform(v))[:, 1], atol=1e-14)

    def test_gradiente_en_solucion_logistica(self):
        m = self.modelos["logistica_0.3"]
        x = (np.asarray([ambiente.validar(ambiente.entrada(f)) for f in self.train]) - m["media"]) / m["escala"]
        y = np.asarray([f["revision_prioritaria"] for f in self.train])
        p = 1 / (1 + np.exp(-(x @ m["coef"] + m["intercepto"])))
        np.testing.assert_allclose(x.T @ (p - y) + m["coef"], 0, atol=1e-4)
        self.assertAlmostEqual(float(sum(p - y)), 0, places=4)

    def test_umbrales_comparten_pesos(self):
        m = self.modelos
        for campo in ("coef", "media", "escala", "intercepto"):
            self.assertEqual(m["logistica_0.3"][campo], m["logistica_0.7"][campo])

    def test_confusion_y_costo_independientes(self):
        r = ambiente.evaluar(self.modelos["logistica_0.3"], self.val, PROTOCOLO["ambiente"])
        tn, fp, fn, tp = confusion_matrix([c["objetivo"] for c in r["casos"]], [c["proponer_revision"] for c in r["casos"]]).ravel()
        self.assertEqual([r[k] for k in ("tn", "fp", "fn", "tp")], [tn, fp, fn, tp])
        self.assertEqual(r["costo"], fp + 4 * fn)

    def test_politicas_constantes_y_metrica_indefinida(self):
        r = ambiente.evaluar(self.modelos["ninguna"], self.val, PROTOCOLO["ambiente"])
        self.assertIsNone(r["precision"])
        self.assertEqual(r["propuestas"], 0)
        self.assertIsNone(ambiente.metricas([], PROTOCOLO["ambiente"])["recall"])
        r = ambiente.evaluar(self.modelos["todas"], self.val, PROTOCOLO["ambiente"])
        self.assertEqual(r["fn"], 0)

    def test_suma_por_zona(self):
        r = ambiente.evaluar(self.modelos["logistica_0.3"], self.val, PROTOCOLO["ambiente"])
        for campo in ("n", "fp", "fn", "costo"):
            self.assertEqual(r[campo], sum(z[campo] for z in r["por_zona"].values()))

    def test_sin_zona_ni_etiqueta_en_prediccion(self):
        f = dict(self.val[0])
        a = ambiente.predecir(self.modelos["logistica_0.3"], ambiente.entrada(f))
        f.update(zona="nueva", revision_prioritaria=1 - f["revision_prioritaria"])
        b = ambiente.predecir(self.modelos["logistica_0.3"], ambiente.entrada(f))
        self.assertEqual(a, b)

    def test_contrato_ambiental(self):
        consulta = demo.CONSULTAS["ambiente"]
        for campo, valor in (("residuos_m2", -1), ("superficie_afectada_pct", 101), ("dias_sin_visita", 1.5),
                             ("dias_sin_visita", True), ("residuos_m2", float("nan"))):
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                ambiente.validar({**consulta, campo: valor})
        r = ambiente.predecir(self.modelos["logistica_0.3"], {**consulta, "residuos_m2": 19})
        self.assertTrue(r["fuera_rango_entrenamiento"])
        self.assertTrue(r["requiere_revision_humana"])

    def test_seleccion_costo_propuestas_orden(self):
        elegido, _, r = ambiente.desarrollar(self.train, self.val, PROTOCOLO["ambiente"])
        orden = PROTOCOLO["ambiente"]["candidatos"]
        self.assertEqual(elegido, min(orden, key=lambda k: (r[k]["costo"], r[k]["propuestas"], orden.index(k))))


class TallerDocumentos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = datos("documentos", "corpus")
        cls.indice = documentos.ajustar(cls.corpus)
        cls.modelo = {**cls.indice, "tipo": "tfidf", "umbral": .4}

    def test_tfidf_independiente_sklearn(self):
        ref = TfidfVectorizer(analyzer=documentos.tokens)
        matriz = ref.fit_transform([d["texto"] for d in self.corpus]).toarray()
        self.assertEqual(self.indice["vocabulario"], ref.get_feature_names_out().tolist())
        np.testing.assert_allclose(self.indice["idf"], ref.idf_, atol=1e-14)
        np.testing.assert_allclose(self.indice["matriz"], matriz, atol=1e-14)

    def test_vector_y_coseno_manual(self):
        vocabulario = ["alfa", "beta"]
        v = documentos.vector("alfa alfa beta", vocabulario, [1, 2])
        np.testing.assert_allclose(v, [1 / math.sqrt(2)] * 2)
        self.assertAlmostEqual(sum(x * x for x in v), 1)

    def test_normalizacion_acentos(self):
        self.assertEqual(documentos.tokens("¿CÓMO es la renovación de LIBROS?"), ["renovacion", "libros"])

    def test_fuera_vocabulario_abstiene_incluso_umbral_cero(self):
        r = documentos.predecir({**self.modelo, "umbral": 0}, {"pregunta": "zxqv"})
        self.assertEqual(r["estado"], "sin_evidencia")
        self.assertEqual(r["puntuacion"], 0)
        self.assertIsNone(r["cita"])

    def test_cita_exacta_con_offsets(self):
        for f in datos("documentos", "validacion") + datos("documentos", "prueba"):
            r = documentos.predecir(self.modelo, {"pregunta": f["pregunta"]})
            if r["cita"]:
                c = r["cita"]
                d = next(d for d in self.corpus if d["id"] == c["documento"])
                self.assertEqual(r["respuesta"], d["texto"][c["inicio"]:c["fin"]])
                self.assertEqual(c["version"], d["version"])

    def test_cita_correcta_no_garantiza_pertinencia(self):
        preguntas = datos("documentos", "prueba")
        caso = next(f for f in preguntas if f["id"] == "Q-transporte-1")
        r = documentos.evaluar(self.modelo, [caso], PROTOCOLO["documentos"])
        self.assertEqual(r["casos"][0]["documento"], "D05")
        self.assertFalse(r["casos"][0]["aceptada"])
        self.assertEqual(r["costo"], 3)

    def test_abstencion_respondible_cuesta_uno(self):
        f = {"id": "q", "familia": "x", "pregunta": "zxqv", "documento_esperado": "D01"}
        r = documentos.evaluar(self.modelo, [f], PROTOCOLO["documentos"])
        self.assertEqual(r["costo"], 1)
        self.assertIsNone(r["precision_respondidas"])

    def test_contrato_y_corpus(self):
        for entrada in ({}, {"pregunta": ""}, {"pregunta": " "}, {"pregunta": 1}, {"pregunta": "x" * 401}):
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                documentos.validar(entrada)
        with self.assertRaises(ValueError):
            documentos.ajustar([self.corpus[0], self.corpus[0]])

    def test_indice_no_depende_de_juicios(self):
        v = datos("documentos", "validacion")
        _, _, r1 = documentos.desarrollar(self.corpus, v, PROTOCOLO["documentos"])
        otro = copy.deepcopy(v)
        for f in otro:
            f["documento_esperado"] = None
        _, _, r2 = documentos.desarrollar(self.corpus, otro, PROTOCOLO["documentos"])
        for k in r1:
            self.assertEqual([c["documento"] for c in r1[k]["casos"]], [c["documento"] for c in r2[k]["casos"]])

    def test_desempate_por_id(self):
        corpus = [{"id": k, "texto": "alfa beta", "version": "1"} for k in ("B", "A")]
        modelo = {**documentos.ajustar(corpus), "tipo": "tfidf", "umbral": 0}
        self.assertEqual(documentos.predecir(modelo, {"pregunta": "alfa"})["documento"], "A")


class EvidenciaYFlujo(unittest.TestCase):
    def test_desarrollo_nunca_abre_prueba(self):
        original = talleres.leer
        def lectura(ruta):
            if Path(ruta).name == "prueba.json":
                raise AssertionError("Se abrió prueba durante desarrollo")
            return original(ruta)
        with patch.object(talleres, "leer", side_effect=lectura):
            for t in talleres.MODULOS:
                nuevo, informe = talleres.desarrollo(t)
                self.assertEqual(nuevo, paquete(t))
                self.assertTrue(informe["recarga_identica"])

    def test_cierre_no_ajusta_ni_selecciona(self):
        for t, modulo in talleres.MODULOS.items():
            with patch.object(modulo, "ajustar", side_effect=AssertionError("ajuste prohibido")), \
                 patch.object(modulo, "desarrollar", side_effect=AssertionError("selección prohibida")):
                r = talleres.cierre(t, RAIZ / "recursos" / t / "modelo.json")
                self.assertEqual(r, talleres.leer(RAIZ / "recursos" / t / "prueba.json"))

    def test_huellas_alteracion_y_taller_equivocado(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo.json"
            m = paquete("energia")
            talleres.guardar(p, m)
            with self.assertRaisesRegex(ValueError, "otro taller"):
                talleres.cargar_modelo(p, "ambiente")
            m["estado"]["intercepto"] += 1
            talleres.guardar(p, m)
            with self.assertRaisesRegex(ValueError, "huella"):
                talleres.cargar_modelo(p, "energia")

    def test_fuentes_cambiadas_se_detectan(self):
        with patch.object(talleres, "fuentes", return_value={}):
            with self.assertRaisesRegex(ValueError, "fuentes"):
                paquete("energia")

    def test_informes_reconstruidos(self):
        for t in talleres.MODULOS:
            _, r = talleres.desarrollo(t)
            self.assertEqual(r, talleres.leer(RAIZ / "recursos" / t / "validacion.json"))

    def test_demo_sin_entrenar_y_con_identidad(self):
        for t, modulo in talleres.MODULOS.items():
            with patch.object(modulo, "ajustar", side_effect=AssertionError("ajuste prohibido")):
                r = demo.demostrar(t, demo.CONSULTAS[t])
            self.assertEqual(r["modelo_sha256"], paquete(t)["sha256"])
            self.assertEqual(r["salida"], modulo.predecir(paquete(t)["estado"], demo.CONSULTAS[t]))

    def test_campos_adicionales_y_tipos_rechazados(self):
        for t, modulo in talleres.MODULOS.items():
            for consulta in ([], None, {**demo.CONSULTAS[t], "objetivo": 1}):
                with self.subTest(taller=t), self.assertRaises(ValueError):
                    modulo.predecir(paquete(t)["estado"], consulta)

    def test_limite_lectura_y_json_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "entrada.json"
            p.write_bytes(b"x" * 16385)
            with self.assertRaisesRegex(ValueError, "16 KiB"):
                demo.leer_entrada(p)
            p.write_text("{")
            with self.assertRaises(ValueError):
                demo.leer_entrada(p)

    def test_cli_cierre_exige_modelo(self):
        r = subprocess.run([sys.executable, str(RAIZ / "ejemplos/01_taller_energia.py"), "--evaluar-prueba"],
                           capture_output=True, text=True, timeout=15)
        self.assertEqual(r.returncode, 2)
        self.assertIn("junto con --modelo", r.stderr)

    def test_manual_con_denominadores(self):
        r = manual.calcular()
        self.assertEqual(r["energia"]["mae_kw"], 2)
        self.assertEqual(r["ambiente"]["costo"], 5)
        self.assertEqual(r["documentos"]["costo"], 4)
        self.assertEqual(r["documentos"]["cobertura"], .5)


if __name__ == "__main__":
    unittest.main()

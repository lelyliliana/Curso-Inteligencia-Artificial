"""Contratos, referencias independientes, separación de información y recarga."""
from copy import deepcopy
import importlib.util
import json
from math import log2, sqrt
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import recomendacion_curso as rec
import refuerzo_curso as rl
spec = importlib.util.spec_from_file_location("generador_u24", UNIDAD / "datos/generar_datos.py")
generador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generador)


class Recomendacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo, cls.informe = rec.desarrollar()
        cls.train = rec.leer_csv(UNIDAD / "datos/entrenamiento.csv")
        cls.val = rec.leer_csv(UNIDAD / "datos/validacion.csv")

    def test_conteos_y_historia(self):
        self.assertEqual(len(self.train), 192)
        self.assertEqual(len(self.val), 56)
        self.assertEqual(len(self.modelo["items"]), 26)
        self.assertEqual(len(self.modelo["historiales"]), 48)
        self.assertTrue(all(len(h) == 4 for h in self.modelo["historiales"].values()))

    def test_regeneracion_exacta(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            for p in (UNIDAD / "datos").glob("*.csv"):
                self.assertEqual(p.read_bytes(), (Path(d) / p.name).read_bytes())

    def test_pares_separados(self):
        partes = [rec.leer_interacciones(UNIDAD / f"datos/{p}.csv", self.modelo["items"], p)
                  for p in ("entrenamiento", "validacion", "prueba")]
        pares = [{(r["usuario"], r["elemento"]) for r in filas} for filas in partes]
        for a, b in ((0, 1), (0, 2), (1, 2)):
            self.assertFalse(pares[a] & pares[b])
        self.assertEqual({r["usuario"] for r in partes[1]}, {r["usuario"] for r in partes[2]})

    def comprobar_csv_invalido(self, contenido, parte="validacion"):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "datos.csv"
            p.write_text("usuario,elemento,fecha\n" + contenido, encoding="utf-8")
            with self.assertRaises(ValueError):
                rec.leer_interacciones(p, self.modelo["items"], parte)

    def test_rechaza_duplicado(self):
        self.comprobar_csv_invalido("U01,I01,2026-09-01T12:00:00-05:00\n" * 2, "entrenamiento")

    def test_rechaza_fecha_fuera_de_particion(self):
        for fecha in ("2026-09-06T12:00:00-05:00", "2026-09-05T12:00:00", "2026-09-05T12:00:00+00:00"):
            self.comprobar_csv_invalido(f"U01,I01,{fecha}\n")

    def test_rechaza_elemento_desconocido(self):
        self.comprobar_csv_invalido("U01,I99,2026-09-05T12:00:00-05:00\n")

    def test_rechaza_dos_objetivos_por_usuario(self):
        self.comprobar_csv_invalido("U01,I01,2026-09-05T12:00:00-05:00\nU01,I02,2026-09-05T12:00:00-05:00\n")

    def test_coseno_con_referencia_por_conjuntos(self):
        for i, a in enumerate(self.modelo["items"]):
            ua = {r["usuario"] for r in self.train if r["elemento"] == a}
            for j, b in enumerate(self.modelo["items"]):
                ub = {r["usuario"] for r in self.train if r["elemento"] == b}
                esperado = len(ua & ub) / sqrt(len(ua)*len(ub)) if ua and ub and i != j else 0
                self.assertAlmostEqual(self.modelo["similitud"][i][j], esperado)

    def test_popularidad_cuenta_usuarios(self):
        m = rec.ajustar(["A", "B"], [{"usuario": "u", "elemento": "A"}] * 2)
        self.assertEqual(m["popularidad"], [1, 0])

    def test_elemento_nuevo_vector_cero(self):
        self.assertEqual(self.modelo["popularidad"][-1], 0)
        self.assertEqual(self.modelo["similitud"][-1], [0]*26)

    def test_exclusion_y_candidatos_completos(self):
        for r in self.val:
            lista = rec.recomendar(self.modelo, r["usuario"], k=100)
            h = set(self.modelo["historiales"].get(r["usuario"], []))
            self.assertEqual(set(lista), set(self.modelo["items"]) - h)
            self.assertEqual(len(lista), len(set(lista)))

    def test_usuario_nuevo_usa_popularidad(self):
        self.assertEqual(rec.recomendar(self.modelo, "nuevo", "coseno"), rec.recomendar(self.modelo, "nuevo", "popularidad"))

    def test_desempate_id(self):
        m = rec.ajustar(["C", "B", "A"], [])
        self.assertEqual(rec.recomendar(m, "u", "coseno"), ["A", "B", "C"])

    def test_metricas_manual_todas_posiciones(self):
        for objetivo, acierto, ndcg in (("a", 1, 1), ("b", 1, 1/log2(3)), ("c", 1, .5), ("d", 0, 0)):
            m = rec.metricas_lista(["a", "b", "c"], objetivo)
            self.assertEqual(m["acierto"], acierto)
            self.assertAlmostEqual(m["ndcg"], ndcg)

    def test_lista_y_k_invalidos(self):
        for lista in ([], ["a", "a"]):
            with self.assertRaises(ValueError):
                rec.metricas_lista(lista, "a")
        with self.assertRaises(ValueError):
            rec.recomendar(self.modelo, "u", k=0)

    def test_objetivo_no_candidato(self):
        with self.assertRaises(ValueError):
            rec.evaluar(self.modelo, [self.train[0]])

    def test_grupo_vacio_indefinido(self):
        r = rec.evaluar(self.modelo, self.val[:1])
        self.assertIsNone(r["grupos"]["sin_historia"]["recall_3"])
        self.assertEqual(r["grupos"]["sin_historia"]["n"], 0)

    def test_validacion_no_entra_en_parametros(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            ruta = Path(d) / "validacion.csv"
            texto = ruta.read_text()
            # Cambia usuarios y objetivos válidos; ningún cambio debe llegar al ajuste.
            ruta.write_text(texto.replace("U", "Z"))
            otro, _ = rec.desarrollar(Path(d))
            for campo in ("popularidad", "similitud", "historiales"):
                self.assertEqual(otro[campo], self.modelo[campo])

    def test_desarrollo_no_necesita_prueba(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            (Path(d) / "prueba.csv").unlink()
            m, i = rec.desarrollar(Path(d))
            self.assertEqual(m, self.modelo)
            self.assertIsNone(i["prueba"])

    def test_seleccion_y_empate(self):
        r = {n: {"global": {"recall_3": .5}} for n in ("popularidad", "coseno")}
        self.assertEqual(rec.seleccionar(r), "popularidad")
        r["coseno"]["global"]["recall_3"] = .6
        self.assertEqual(rec.seleccionar(r), "coseno")

    def test_recarga_listas_con_y_sin_historia(self):
        self.assertEqual(rec.cargar(UNIDAD / "recursos/recomendacion/modelo.json"), self.modelo)
        with tempfile.TemporaryDirectory() as d:
            rec.exportar(self.modelo, self.informe, d)
            m = rec.cargar(Path(d) / "modelo.json")
            for r in self.val:
                self.assertEqual(rec.recomendar(m, r["usuario"]), rec.recomendar(self.modelo, r["usuario"]))

    def test_estado_incompatible(self):
        with tempfile.TemporaryDirectory() as d:
            for campo, valor in (("reglas", {}), ("similitud", [[0]]), ("popularidad", [0])):
                m = deepcopy(self.modelo)
                m[campo] = valor
                p = Path(d) / "m.json"
                rec.guardar_json(p, m)
                with self.assertRaises(ValueError):
                    rec.cargar(p)

    def test_cierre_sin_reajuste_y_sin_leer_desarrollo(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            rec.guardar_json(p / "modelo.json", self.modelo)
            antes = (p / "modelo.json").read_bytes()
            (p / "prueba.csv").write_bytes((UNIDAD / "datos/prueba.csv").read_bytes())
            with patch.object(rec, "ajustar", side_effect=AssertionError("No reajustar")):
                resultado = rec.cerrar(p / "modelo.json", p)
            self.assertEqual(antes, (p / "modelo.json").read_bytes())
            self.assertEqual(resultado["modelo_sha256"], rec.huella(p / "modelo.json"))

    def test_metricas_agregadas_independientes(self):
        for r in self.informe["validacion"].values():
            casos = r["casos"]
            aciertos = sum(c["objetivo"] in c["lista"] for c in casos)
            self.assertEqual(r["global"]["aciertos"], aciertos)
            self.assertAlmostEqual(r["global"]["recall_3"], aciertos / 56)
            cobertura = len(set().union(*(set(c["lista"]) for c in casos))) / 26
            self.assertEqual(r["global"]["cobertura"], cobertura)


class Refuerzo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo = rl.cargar(UNIDAD / "recursos/refuerzo/modelo.json")
        cls.informe = json.loads((UNIDAD / "recursos/refuerzo/informe.json").read_text())

    def test_transicion_y_bordes(self):
        self.assertEqual(rl.transicion(20, 0, .8), (15, -.04, False))
        for s, a in ((20, 3), (20, 2), (0, 0), (9, 1)):
            self.assertEqual(rl.transicion(s, a, .8), (s, -.04, False))

    def test_giros_y_fronteras_de_probabilidad(self):
        self.assertEqual(rl.transicion(12, 0, .099)[0], 11)
        self.assertEqual(rl.transicion(12, 0, .1)[0], 13)
        self.assertEqual(rl.transicion(12, 0, .2)[0], 7)

    def test_recompensas_terminales(self):
        self.assertEqual(rl.transicion(3, 1, .8), (4, 1, True))
        self.assertEqual(rl.transicion(5, 1, .8), (6, -1, True))

    def test_terminal_no_admite_paso(self):
        for s in (4, 6, 8, 16, 18):
            with self.assertRaises(ValueError):
                rl.transicion(s, 0, .5)

    def test_entradas_fuera_de_rango(self):
        for s, a, z in ((25, 0, .5), (0, 4, .5), (0, 0, 1), (-1, 0, .5)):
            with self.assertRaises(ValueError):
                rl.transicion(s, a, z)

    def test_actualizacion_manual_y_terminal(self):
        self.assertAlmostEqual(rl.valor_actualizado(.2, -.04, .8, False, .5, .9), .44)
        self.assertAlmostEqual(rl.valor_actualizado(.2, -1, 900, True, .5, .9), -.4)

    def test_truncamiento_conserva_bootstrap_en_entrenamiento(self):
        q = np.ones((25, 4))
        cfg = {**rl.CONFIG, "episodios": 1}
        zeros = np.zeros
        def inicializar(shape, *args, **kwargs):
            return q if shape == (25, 4) else zeros(shape, *args, **kwargs)
        with patch.object(rl.np, "zeros", side_effect=inicializar), patch.object(rl, "transicion", return_value=(20, -.04, False)):
            nuevo, historia = rl.entrenar(1, cfg, {**rl.ENTORNO, "limite": 1})
        modificados = nuevo[20][nuevo[20] != 1]
        np.testing.assert_allclose(modificados, [1 + .15*(-.04 + .95 - 1)])
        self.assertEqual(historia[0]["truncado"], 1)

    def test_epsilon_presupuesto(self):
        self.assertAlmostEqual(rl.epsilon(0), 1)
        self.assertAlmostEqual(rl.epsilon(1499), .05)
        self.assertAlmostEqual(rl.epsilon(1999), .05)
        self.assertTrue(all(0 < r["transiciones"] <= 120000 for r in self.informe["entrenamiento"]))

    def test_exploracion_y_empates(self):
        rng = np.random.default_rng(2)
        q = np.array([0, 2, 2, -1.])
        acciones = {rl.accion_entrenamiento(q, 0, rng) for _ in range(100)}
        self.assertEqual(acciones, {1, 2})
        acciones = {rl.accion_entrenamiento(q, 1, rng) for _ in range(100)}
        self.assertEqual(acciones, set(range(4)))

    def test_entrenamiento_reproducible_y_distintas_semillas(self):
        cfg = {**rl.CONFIG, "episodios": 50}
        a, ha = rl.entrenar(50, cfg)
        b, hb = rl.entrenar(50, cfg)
        c, _ = rl.entrenar(51, cfg)
        np.testing.assert_array_equal(a, b)
        self.assertEqual(ha, hb)
        self.assertFalse(np.array_equal(a, c))

    def test_evaluacion_no_explora_ni_actualiza(self):
        q = np.array(self.modelo["tablas"][0]["q"])
        copia = q.copy()
        q.flags.writeable = False
        with patch.object(rl, "accion_entrenamiento", side_effect=AssertionError("No explorar")), patch.object(rl, "valor_actualizado", side_effect=AssertionError("No actualizar")):
            a = rl.evaluar(q, [30000, 30001])
            b = rl.evaluar(q, [30000, 30001])
        self.assertEqual(a, b)
        np.testing.assert_array_equal(q, copia)

    def test_empate_evaluacion_primera_accion(self):
        with patch.object(rl, "transicion", return_value=(4, 1, True)) as paso:
            rl.evaluar(np.zeros((25, 4)), [30000])
            self.assertEqual(paso.call_args.args[1], 0)

    def test_retorno_ruta_sin_ruido(self):
        r = rl.evaluar(None, [30000], {**rl.ENTORNO, "prob_giro": 0})
        self.assertEqual(r["pasos"], 8)
        self.assertEqual(r["exito"], 1)
        self.assertAlmostEqual(r["recompensa_total"], 1 - 7*.04)
        self.assertAlmostEqual(r["retorno"], sum(-.04 * .95**t for t in range(7)) + .95**7)

    def test_truncamiento_evaluacion_y_horizonte_observado(self):
        q = np.zeros((25, 4))
        q[:, 3] = 1  # Siempre izquierda, contra el borde desde inicio.
        r = rl.evaluar(q, [30000], {**rl.ENTORNO, "prob_giro": 0, "limite": 2})
        self.assertEqual(r["truncado"], 1)
        self.assertEqual(r["pozo"], 0)
        self.assertAlmostEqual(r["retorno"], -.04 - .95*.04)

    def test_semillas_separadas_y_todas_reportadas(self):
        self.assertFalse(set(rl.SEMILLAS_DESARROLLO) & set(rl.SEMILLAS_CIERRE))
        self.assertFalse(set(rl.CONFIG["semillas"]) & set(rl.SEMILLAS_DESARROLLO))
        self.assertEqual([r["semilla_entrenamiento"] for r in self.informe["desarrollo"]["q_learning"]], rl.CONFIG["semillas"])

    def test_metricas_y_dispersión_por_semillas(self):
        e = self.informe["desarrollo"]
        valores = []
        for r in [e["referencia"], *e["q_learning"]]:
            self.assertEqual(len(r["casos"]), 200)
            self.assertAlmostEqual(r["exito"] + r["pozo"] + r["truncado"], 1)
            self.assertEqual(r["exito"], sum(c["exito"] for c in r["casos"])/200)
        valores = [r["retorno"] for r in e["q_learning"]]
        media = sum(valores)/5
        dispersion = sqrt(sum((v-media)**2 for v in valores)/5)
        self.assertAlmostEqual(e["entre_semillas"]["retorno"]["media"], media)
        self.assertAlmostEqual(e["entre_semillas"]["retorno"]["desviacion"], dispersion)

    def test_recarga_tablas_y_evaluacion(self):
        with tempfile.TemporaryDirectory() as d:
            rl.exportar(self.modelo, self.informe, d)
            nuevo = rl.cargar(Path(d) / "modelo.json")
            self.assertEqual(nuevo, self.modelo)

    def test_cierre_no_entrena_y_conserva_estado(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo.json"
            rec.guardar_json(p, self.modelo)
            antes = p.read_bytes()
            with patch.object(rl, "entrenar", side_effect=AssertionError("No entrenar")):
                r = rl.cerrar(p)
            self.assertEqual(p.read_bytes(), antes)
            for tabla in r["evaluacion"]["q_learning"]:
                self.assertEqual([c["semilla"] for c in tabla["casos"]], list(rl.SEMILLAS_CIERRE))

    def test_rechaza_tabla_entorno_o_semilla_alterados(self):
        with tempfile.TemporaryDirectory() as d:
            for cambio in ("tabla", "entorno", "semilla"):
                m = deepcopy(self.modelo)
                if cambio == "tabla":
                    m["tablas"][0]["q"] = [[0]]
                elif cambio == "entorno":
                    m["entorno"]["r_meta"] = 10
                else:
                    m["tablas"][0]["semilla"] = 999
                p = Path(d) / "m.json"
                rec.guardar_json(p, m)
                with self.assertRaises(ValueError):
                    rl.cargar(p)

    def test_artefactos_y_datos_graficos(self):
        self.assertEqual(rl.evaluar_tablas(self.modelo, rl.SEMILLAS_DESARROLLO), self.informe["desarrollo"])
        for laboratorio, nombres in (("recomendacion", ["recomendacion"]), ("refuerzo", ["aprendizaje", "politica"])):
            for nombre in nombres:
                for extension in ("png", "svg"):
                    p = UNIDAD / "recursos" / laboratorio / f"{nombre}.{extension}"
                    self.assertGreater(p.stat().st_size, 1000)
        from figuras_aplicaciones import recomendacion
        with tempfile.TemporaryDirectory() as d, patch("figuras_aplicaciones.guardar") as guardar:
            informe = json.loads((UNIDAD / "recursos/recomendacion/informe.json").read_text())
            recomendacion(informe, d)
            fig = guardar.call_args.args[0]
            alturas = [b.get_height() for b in fig.axes[0].patches]
            np.testing.assert_allclose(alturas, [6/56, 6/48, 0, 15/56, 15/48, 0])
            import matplotlib.pyplot as plt
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()

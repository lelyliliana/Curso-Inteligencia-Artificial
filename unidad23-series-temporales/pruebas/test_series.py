"""Verifica disponibilidad temporal, cálculos, separación y persistencia."""
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
from sklearn.metrics import mean_absolute_error, mean_squared_error

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import series_curso as sc
from figuras_series import figura_pronostico, figura_errores, guardar_figuras
import matplotlib.pyplot as plt


def importar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


gen = importar("generar_series", UNIDAD / "datos/generar_datos.py")
auditoria = importar("auditoria_series", UNIDAD / "ejemplos/01_auditar_tiempo.py")


def sencillo(n=48):
    return {h: [{"id": str(h), "hora": h, "llegada_min": h*60+10, "valor": float(h)}] for h in range(n)}


class Lecturas(unittest.TestCase):
    def leer_filas(self, filas):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "datos.csv"
            gen.escribir(p, filas)
            return sc.leer_archivo(p)

    def test_equivalencia_zonas(self):
        self.assertEqual(sc.minutos("2026-08-01T00:00:00-05:00"), sc.minutos("2026-08-01T05:00:00+00:00"))

    def test_fecha_sin_zona(self):
        with self.assertRaises(ValueError):
            sc.minutos("2026-08-01T00:00:00")

    def test_fuera_rejilla(self):
        fila = gen.lectura(0, 20)
        fila["instante"] = "2026-08-01T00:01:00-05:00"
        with self.assertRaises(ValueError):
            self.leer_filas([fila])

    def test_llegada_anterior(self):
        with self.assertRaises(ValueError):
            self.leer_filas([gen.lectura(1, 20, -1)])

    def test_sensor_incorrecto(self):
        fila = gen.lectura(0, 20)
        fila["sensor"] = "otro"
        with self.assertRaises(ValueError):
            self.leer_filas([fila])

    def test_no_finitos_y_rango(self):
        for v in (float("nan"), float("inf"), 90):
            with self.assertRaises(ValueError):
                self.leer_filas([gen.lectura(0, v)])

    def test_vacio_y_cabecera(self):
        with self.assertRaises(ValueError):
            self.leer_filas([])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "mal.csv"
            p.write_text("hora,valor\n0,20\n")
            with self.assertRaises(ValueError):
                sc.leer_archivo(p)

    def test_id_contradictorio(self):
        with self.assertRaisesRegex(ValueError, "ID repetido"):
            self.leer_filas([gen.lectura(0, 20), gen.lectura(0, 21)])

    def test_duplicado_exacto_y_conflicto(self):
        a = self.leer_filas([gen.lectura(0, 20), gen.lectura(0, 20), gen.lectura(0, 21, sufijo="otro")])
        self.assertEqual(a["auditoria"]["duplicados_exactos"], 1)
        self.assertEqual(sc.observado(sc.agrupar(a), 0), (None, "conflicto"))

    def test_regeneracion_exacta(self):
        with tempfile.TemporaryDirectory() as d:
            gen.generar(d)
            for p in (UNIDAD / "datos").glob("*.csv"):
                self.assertEqual(p.read_bytes(), (Path(d) / p.name).read_bytes())


class Tiempo(unittest.TestCase):
    def test_historia_manual(self):
        r = auditoria.experimento()
        self.assertEqual(r["hora8"]["valores"], [20, 21, 21, 23, 24, 24, 26, 26, 26])
        self.assertEqual(r["media3_hora8"], 26)
        self.assertTrue(r["archivo"]["auditoria"]["entrada_desordenada"])

    def test_futuro_no_modifica_entradas(self):
        g = sencillo()
        referencia = sc.caracteristicas(g, 30, 6)
        for h in range(31, 48):
            g[h][0]["valor"] = -999
        np.testing.assert_array_equal(sc.caracteristicas(g, 30, 6), referencia)

    def test_pasado_tardio_no_modifica_entradas(self):
        g = sencillo()
        g[30][0]["llegada_min"] = 31*60
        referencia = sc.caracteristicas(g, 30, 1)
        g[30][0]["valor"] = -999
        np.testing.assert_array_equal(sc.caracteristicas(g, 30, 1), referencia)
        self.assertEqual(referencia[0], 29)

    def test_lectura_tardia_entra_despues(self):
        g = sc.agrupar(sc.leer_archivo(UNIDAD / "datos/muestra.csv"))
        self.assertEqual(sc.historia(g, 8)[0][7], 26)
        self.assertEqual(sc.historia(g, 10)[0][7], 27)

    def test_conflicto_futuro_no_borra_pasado(self):
        g = sencillo()
        g[30].append({"id": "nuevo", "hora": 30, "llegada_min": 32*60, "valor": 50})
        self.assertEqual(sc.historia(g, 30)[0][30], 30)
        self.assertEqual(sc.historia(g, 32)[0][30], 29)

    def test_ventana_y_rezagos_manuales(self):
        g = sencillo()
        x = sc.caracteristicas(g, 30, 6)
        np.testing.assert_allclose(x, [30, 29, 12, 18.5, 0, -1, 0, 0], atol=1e-12)

    def test_calendario_en_cambio_de_dia(self):
        x = sc.caracteristicas(sencillo(), 23, 1)
        self.assertAlmostEqual(x[4], 0)
        self.assertAlmostEqual(x[5], 1)
        self.assertEqual(x[2], 0)

    def test_sin_relleno_hacia_atras(self):
        g = sencillo()
        del g[0]
        self.assertTrue(np.isnan(sc.historia(g, 23)[0][0]))
        self.assertIsNone(sc.caracteristicas(g, 23, 1))

    def test_antiguedad_maxima(self):
        g = sencillo()
        for h in range(27, 31):
            del g[h]
        self.assertIsNone(sc.caracteristicas(g, 30, 1))

    def test_horizonte_invalido(self):
        with self.assertRaises(ValueError):
            sc.caracteristicas(sencillo(), 30, 24)


class Modelos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = sc.ejecutar_experimento()
        cls.c = cls.r["conjuntos"]["entrenamiento"]
        cls.estado = cls.r["candidatos"]["ridge"]["estado"]

    def test_persistencia_y_estacional(self):
        x = np.asarray(self.c["x"])
        for nombre, indice in (("persistencia", 0), ("estacional24", 2)):
            np.testing.assert_array_equal(sc.predecir(x, self.r["candidatos"][nombre]["estado"]), x[:, indice])

    def test_ridge_referencia_matricial(self):
        x, y = np.asarray(self.c["x"]), np.asarray(self.c["y"])
        media, escala = x.mean(0), x.std(0)
        escala[escala == 0] = 1
        z = (x - media) / escala
        w = np.linalg.solve(z.T @ z + np.eye(8), z.T @ (y-y.mean()))
        np.testing.assert_allclose(w, self.estado["coeficientes"], atol=1e-10)
        np.testing.assert_allclose(z @ w + y.mean(), sc.predecir(x, self.estado), atol=1e-10)

    def test_metricas_referencia(self):
        y, p = [1, 2, 3], [2, 1, 5]
        m = sc.metricas(y, p)
        self.assertAlmostEqual(m["mae"], mean_absolute_error(y, p))
        self.assertAlmostEqual(m["rmse"], np.sqrt(mean_squared_error(y, p)))
        self.assertAlmostEqual(m["sesgo"], 2/3)

    def test_metricas_vacias_e_invalidas(self):
        self.assertEqual(sc.metricas([], []), {"n": 0, "mae": None, "rmse": None, "sesgo": None})
        with self.assertRaises(ValueError):
            sc.metricas([1, 2], [1])
        with self.assertRaises(ValueError):
            sc.metricas([1], [float("nan")])

    def test_seleccion_y_desempate(self):
        self.assertEqual(self.r["seleccionado"], "ridge")
        ficticios = {n: {"validacion": {"metricas": {"mae": 1}}} for n in ("persistencia", "estacional24", "ridge")}
        self.assertEqual(sc.seleccionar(ficticios), "persistencia")

    def test_cobertura_y_objetivos_no_imputados(self):
        for p, n in (("entrenamiento", 546), ("validacion", 185)):
            c = self.r["conjuntos"][p]
            self.assertEqual(c["evaluables"], n)
            self.assertEqual(sum(c["exclusiones"].values()) + n, c["origenes_posibles"])
            excluidos = {45, 180, 420, 575, 601, 635, 690, 698, 711, 767}
            self.assertTrue(excluidos.isdisjoint(m["objetivo_h"] for m in c["metadatos"]))

    def test_cortes_y_disponibilidad_etiquetas(self):
        for p, c in self.r["conjuntos"].items():
            archivo = sc.leer_archivo(UNIDAD / f"datos/{p}.csv")
            grupos = sc.agrupar(archivo)
            inicio, fin = sc.LIMITES[p]
            for m in c["metadatos"]:
                self.assertTrue(inicio <= m["origen_h"] < m["objetivo_h"] < fin)
                self.assertIsNotNone(sc.observado(grupos, m["objetivo_h"], fin*60+10)[0])

    def test_inferencia_sin_objetivo(self):
        g = sc.agrupar(sc.leer_archivo(UNIDAD / "datos/entrenamiento.csv"))
        pred = sc.pronosticar(g, 100, self.estado)
        del g[101]
        self.assertEqual(sc.pronosticar(g, 100, self.estado), pred)

    def test_entrada_y_modelo_incompatible(self):
        with self.assertRaises(ValueError):
            sc.predecir([[1, 2]], self.estado)
        for campo, valor in (("columnas", list(reversed(sc.COLUMNAS))), ("escala", [0]*8), ("media", [float("nan")]*8)):
            e = copy.deepcopy(self.estado)
            e[campo] = valor
            with self.assertRaises(ValueError):
                sc.validar_estado(e)

    def test_metricas_diarias_ponderadas(self):
        ev = self.r["candidatos"]["ridge"]["validacion"]
        n = sum(d["n"] for d in ev["por_dia"].values())
        mae = sum(d["n"]*d["mae"] for d in ev["por_dia"].values()) / n
        self.assertAlmostEqual(mae, ev["metricas"]["mae"])
        self.assertEqual(ev["transicion_24h"]["n"], 23)


class Protocolo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = sc.ejecutar_experimento()

    def test_desarrollo_sin_prueba(self):
        with tempfile.TemporaryDirectory() as d:
            for p in ("entrenamiento", "validacion"):
                shutil.copy(UNIDAD / f"datos/{p}.csv", d)
            r = sc.ejecutar_experimento(d)
        self.assertIsNone(r["prueba"])
        self.assertNotIn("prueba", r["fuentes"])
        self.assertEqual(r["candidatos"], self.r["candidatos"])

    def test_validacion_no_cambia_ajuste(self):
        original = sc.leer_archivo
        def leer(ruta):
            archivo = original(ruta)
            if Path(ruta).stem == "validacion":
                for r in archivo["registros"]:
                    if r["valor"] is not None:
                        r["valor"] += 3
            return archivo
        with patch.object(sc, "leer_archivo", side_effect=leer):
            r = sc.ejecutar_experimento()
        for nombre in r["candidatos"]:
            self.assertEqual(r["candidatos"][nombre]["estado"], self.r["candidatos"][nombre]["estado"])

    def test_cierre_no_cambia_ajuste_ni_seleccion(self):
        r = sc.ejecutar_experimento(evaluar_prueba=True)
        self.assertEqual(r["candidatos"], self.r["candidatos"])
        self.assertEqual(r["seleccionado"], self.r["seleccionado"])
        # Primer origen: solo historia recibida; última lectura anterior llega después.
        g = sc.agrupar(sc.leer_archivo(UNIDAD / "datos/entrenamiento.csv"), sc.leer_archivo(UNIDAD / "datos/validacion.csv"), sc.leer_archivo(UNIDAD / "datos/prueba.csv"))
        estado = r["candidatos"][r["seleccionado"]]["estado"]
        pred = sc.pronosticar(g, 768, estado)
        for h in list(g):
            if h > 768:
                for a in g[h]:
                    a["valor"] = -10
        self.assertEqual(sc.pronosticar(g, 768, estado), pred)

    def test_pasado_de_prueba_puede_actualizar_entrada(self):
        g = sencillo()
        e = sc.ajustar({"x": [], "y": []}, "persistencia", 1)
        antes = sc.pronosticar(g, 30, e)
        g[30][0]["valor"] = 50
        self.assertNotEqual(sc.pronosticar(g, 30, e), antes)
        # Se recibe una observación nueva: esto no es un pronóstico recursivo cerrado.

    def test_horizonte_seis_con_cortes(self):
        r = sc.ejecutar_experimento(horizonte=6)
        self.assertEqual(r["seleccionado"], "ridge")
        self.assertEqual(r["conjuntos"]["entrenamiento"]["evaluables"], 541)
        self.assertEqual(r["conjuntos"]["validacion"]["evaluables"], 180)
        self.assertTrue(all(m["objetivo_h"] - m["origen_h"] == 6 for m in r["conjuntos"]["validacion"]["metadatos"]))

    def test_rangos_y_ids(self):
        a = sc.leer_archivo(UNIDAD / "datos/validacion.csv")
        with self.assertRaises(ValueError):
            sc.validar_rango(a, "entrenamiento")
        with self.assertRaises(ValueError):
            sc.agrupar(a, a)


class Artefactos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = sc.ejecutar_experimento()

    def test_recarga_y_no_sobrescritura(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo"
            self.assertEqual(sc.exportar(self.r, p), 0)
            self.assertFalse((p / "predicciones_prueba.csv").exists())
            self.assertEqual(sc.cargar_modelo(p / "modelo.json"), self.r["candidatos"]["ridge"]["estado"])
            with self.assertRaises(FileExistsError):
                sc.exportar(self.r, p)

    def test_cierre_csv_y_huella(self):
        r = sc.ejecutar_experimento(evaluar_prueba=True)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "cierre"
            sc.exportar(r, p)
            cierre = json.loads((p / "cierre.json").read_text())
            self.assertEqual(cierre["modelo_sha256"], sc.huella(p / "modelo.json"))
            with (p / "predicciones_prueba.csv").open(encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            np.testing.assert_array_equal([float(f["predicha_c"]) for f in filas], r["prueba"]["evaluacion"]["predicciones"])

    def test_figuras_desde_informe(self):
        f = figura_pronostico(self.r)
        datos = np.array(f.axes[1].lines[0].get_ydata())
        np.testing.assert_array_equal(datos[np.isfinite(datos)], self.r["conjuntos"]["validacion"]["y"])
        self.assertTrue(np.isnan(datos).any())
        plt.close(f)
        f = figura_errores(self.r)
        self.assertAlmostEqual(f.axes[1].patches[1].get_height(), self.r["candidatos"]["ridge"]["validacion"]["transicion_24h"]["mae"])
        plt.close(f)

    def test_formatos_png_svg_y_modelo_incompleto(self):
        with tempfile.TemporaryDirectory() as d:
            guardar_figuras(self.r, d)
            self.assertTrue((Path(d) / "pronostico.png").read_bytes().startswith(b"\x89PNG"))
            self.assertIn("<svg", (Path(d) / "errores.svg").read_text())
            p = Path(d) / "invalido.json"
            p.write_text('{"formato": 1}')
            with self.assertRaises(ValueError):
                sc.cargar_modelo(p)

    def test_diagnostico_sin_casos_no_inventa_error_cero(self):
        r = copy.deepcopy(self.r)
        r["candidatos"]["ridge"]["validacion"]["transicion_24h"] = sc.metricas([], [])
        f = figura_errores(r)
        self.assertTrue(np.isnan(f.axes[1].patches[1].get_height()))
        self.assertTrue(any("Sin casos" in t.get_text() for t in f.axes[1].texts))
        plt.close(f)


if __name__ == "__main__":
    unittest.main()

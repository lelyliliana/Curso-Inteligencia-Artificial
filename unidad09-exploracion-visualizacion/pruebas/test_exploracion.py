"""Comprueba conservación de datos, límites estadísticos y lo que se dibuja."""

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
sys.path.insert(0, str(UNIDAD / "datos"))
from exploracion import (analizar_grupos, analizar_lecturas, contar_intervalos,
                         correlacion_pares, cuantil, describir, leer_grupos, resumir_lecturas)
from generar_datos import contenido_csv
from graficos import (figura_distribuciones, figura_lecturas, figura_relaciones,
                      guardar_entrega, np, plt)

DATOS = UNIDAD / "datos/consumos_por_grupo.csv"
CORRECCIONES = UNIDAD.parent / "unidad08-preparacion-datos/datos/correcciones_verificadas.json"


class Resumenes(unittest.TestCase):
    def test_cero_y_faltante_son_distintos(self):
        r = describir([0, None, 6])
        self.assertEqual((r["n"], r["faltantes"], r["media"], r["mediana"]), (2, 1, 3, 3))

    def test_vacio_o_todo_faltante_no_inventa_estadisticos(self):
        for valores in ([], [None, None]):
            with self.subTest(valores=valores):
                r = describir(valores)
                self.assertEqual(r["n"], 0)
                self.assertIsNone(r["media"])
                self.assertIsNone(r["q1"])

    def test_cuantiles_con_referencia_independiente(self):
        valores = [1, 2, 3, 7, 8, 11, 14, 100]
        self.assertEqual(cuantil(valores, .25), 2.75)
        for p in (0, .25, .5, .75, 1):
            self.assertAlmostEqual(cuantil(valores, p), np.quantile(valores, p, method="linear"))
        self.assertEqual(cuantil([4], .75), 4)

    def test_rechaza_no_finitos(self):
        for valor in (math.inf, -math.inf, math.nan):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                describir([valor])

    def test_correlacion_requiere_variacion_y_dos_pares(self):
        for filas in ([], [{"horas_uso": 1, "consumo_kwh": 2}],
                      [{"horas_uso": 1, "consumo_kwh": y} for y in (2, 3)]):
            with self.subTest(filas=filas):
                self.assertIsNone(correlacion_pares(filas)["r"])

    def test_correlacion_cuenta_solo_pares_completos(self):
        filas = [{"horas_uso": x, "consumo_kwh": y} for x, y in ((1, 3), (2, 6), (None, 5), (4, None))]
        r = correlacion_pares(filas)
        self.assertEqual(r["n_pares"], 2)
        self.assertAlmostEqual(r["r"], 1)

    def test_bordes_histograma_cuentan_extremos_una_vez(self):
        self.assertEqual(contar_intervalos([0, 1, 2, 4], [0, 1, 2, 4]), [1, 1, 2])

    def test_histograma_no_descarta_datos_fuera_de_rango(self):
        for valores, bordes in (([5], [0, 4]), ([math.nan], [0, 4]), ([1], [0, 0, 4]), ([1], [0, math.inf])):
            with self.subTest(valores=valores, bordes=bordes), self.assertRaises(ValueError):
                contar_intervalos(valores, bordes)


class Datos(unittest.TestCase):
    def test_generador_reproduce_csv_publicado(self):
        self.assertEqual(contenido_csv().encode("utf-8"), DATOS.read_bytes())

    def test_fuentes_se_conservan_y_quedan_identificadas(self):
        fuente = UNIDAD.parent / "unidad07-obtencion-datos/datos/lecturas_sinteticas.csv"
        antes = fuente.read_bytes()
        analisis = analizar_lecturas()
        self.assertEqual(fuente.read_bytes(), antes)
        self.assertEqual(analisis["preparacion"]["sha256_origen"], hashlib.sha256(antes).hexdigest())

    def test_lecturas_no_confunden_fila_y_consumo_disponible(self):
        sensores = analizar_lecturas()["resumen"]["sensores"]
        for sensor, esperado in {"S1": (4, 3, 1, 0), "S2": (3, 3, 0, 1), "S3": (1, 1, 0, 3)}.items():
            d = sensores[sensor]
            self.assertEqual((d["preparados"], d["consumo"]["n"], d["consumo"]["faltantes"], d["sin_preparar"]), esperado)
            self.assertEqual(d["consumo"]["n"] + d["consumo"]["faltantes"] + d["sin_preparar"], 4)
        self.assertEqual(sensores["S1"]["serie"], [10, 12, None, 14])
        self.assertEqual(sensores["S3"]["serie"], [None, None, 0, None])

    def test_correccion_cambia_solo_la_disponibilidad_correspondiente(self):
        base = analizar_lecturas()
        corregido = analizar_lecturas(CORRECCIONES)
        s = corregido["resumen"]["sensores"]
        self.assertEqual(s["S2"]["serie"], [8, 9, 10, 11])
        self.assertEqual(s["S2"]["consumo"]["media"], 9.5)
        for sensor in ("S1", "S3"):
            self.assertEqual(s[sensor], base["resumen"]["sensores"][sensor])

    def test_rechaza_claves_preparadas_repetidas_o_fuera_del_plan(self):
        informe = analizar_lecturas()["preparacion"]
        repetido = copy.deepcopy(informe)
        repetido["resultado"]["preparados"].append(repetido["resultado"]["preparados"][0])
        with self.assertRaises(ValueError):
            resumir_lecturas(repetido)
        informe["resultado"]["preparados"][0]["valores"]["fecha"] = "2030-01-01"
        with self.assertRaises(ValueError):
            resumir_lecturas(informe)

    def test_grupos_y_total_con_resultados_conocidos(self):
        filas, r = analizar_grupos(DATOS)
        self.assertEqual(r["total"]["n"], 48)
        self.assertEqual(r["total"]["media"], 18.625)
        self.assertEqual(r["grupos"]["A"]["consumo"]["media"], 10.625)
        self.assertEqual(r["grupos"]["B"]["consumo"]["media"], 26.625)
        self.assertGreater(r["correlacion_total"]["r"], .8)
        for grupo in ("A", "B"):
            self.assertLess(r["grupos"][grupo]["correlacion"]["r"], -.9)
        self.assertEqual(correlacion_pares(filas), correlacion_pares(list(reversed(filas))))

    def test_intervalos_conservan_48_y_coinciden_con_numpy(self):
        for intervalos in (4, 8, 16):
            filas, r = analizar_grupos(DATOS, intervalos)
            esperado, _ = np.histogram([f["consumo_kwh"] for f in filas], bins=r["bordes_kwh"])
            self.assertEqual(sum(r["frecuencias"]), 48)
            self.assertEqual(r["frecuencias"], esperado.tolist())
        self.assertEqual(analizar_grupos(DATOS)[1]["frecuencias"], [0, 0, 20, 4, 0, 0, 20, 4])

    def test_lector_rechaza_entradas_ambiguas_o_invalidas(self):
        cabecera = "caso_id,grupo,horas_uso,consumo_kwh\n"
        casos = ["", "caso_id,grupo,horas_uso,horas_uso\n", cabecera,
                 cabecera + "a,A,1,2\na,B,2,3\n", cabecera + "a,C,1,2\nb,B,2,3\n"]
        for celda in ("", "NaN", "inf", "-1", "texto"):
            casos.append(cabecera + f"a,A,1,{celda}\nb,B,2,3\n")
        casos.extend([cabecera + "a,A,25,2\nb,B,2,3\n", cabecera + "a,A,1,2,extra\nb,B,2,3\n"])
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in casos:
                ruta.write_text(texto, encoding="utf-8")
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    leer_grupos(ruta)


class Graficos(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_lineas_conservan_huecos_y_cero(self):
        fig = figura_lecturas(analizar_lecturas())
        lineas = fig.axes[0].lines
        self.assertTrue(math.isnan(lineas[0].get_ydata()[2]))
        self.assertTrue(math.isnan(lineas[1].get_ydata()[2]))
        self.assertEqual(lineas[2].get_ydata()[2], 0)

    def test_barras_cobertura_particionan_el_plan_y_empiezan_en_cero(self):
        eje = figura_lecturas(analizar_lecturas()).axes[1]
        self.assertEqual(eje.get_ylim()[0], 0)
        for i in range(3):
            self.assertEqual(sum(eje.patches[i + j * 3].get_height() for j in range(3)), 4)

    def test_histograma_y_puntos_conservan_todos_los_casos(self):
        filas, r = analizar_grupos(DATOS)
        fig = figura_distribuciones(filas, r)
        self.assertEqual(sum(p.get_height() for p in fig.axes[0].patches), 48)
        self.assertEqual(sum(len(c.get_offsets()) for c in fig.axes[1].collections), 48)
        self.assertEqual(fig.axes[0].get_ylim()[0], 0)

    def test_dispersion_usa_los_mismos_pares_y_escalas(self):
        filas, r = analizar_grupos(DATOS)
        global_, grupos = figura_relaciones(filas, r).axes
        presentes = sorted(tuple(p) for p in global_.collections[0].get_offsets())
        separados = sorted(tuple(p) for c in grupos.collections for p in c.get_offsets())
        self.assertEqual(presentes, separados)
        self.assertEqual(global_.get_xlim(), grupos.get_xlim())
        self.assertEqual(global_.get_ylim(), grupos.get_ylim())

    def test_exportacion_incluye_archivos_legibles_y_no_sobrescribe(self):
        from PIL import Image
        analisis = analizar_lecturas()
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "informe"
            guardar_entrega(destino, analisis, {"lecturas": figura_lecturas(analisis)})
            with Image.open(destino / "lecturas.png") as imagen:
                self.assertEqual(imagen.size, (1800, 855))
                imagen.verify()
            self.assertIn("<svg", (destino / "lecturas.svg").read_text(encoding="utf-8"))
            r = json.loads((destino / "resumen.json").read_text(encoding="utf-8"))
            self.assertEqual(r["analisis"]["resumen"], analisis["resumen"])
            antes = (destino / "lecturas.png").read_bytes()
            with self.assertRaises(FileExistsError):
                guardar_entrega(destino, {}, {"lecturas": figura_lecturas(analisis)})
            self.assertEqual((destino / "lecturas.png").read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()

"""Referencias matemáticas, aislamiento de particiones y trazabilidad de figuras."""

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
from sklearn.metrics import confusion_matrix

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/"ejemplos"))
import interpretacion as d
import figuras


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


generador = cargar("generador18", UNIDAD/"datos/generar_datos.py")
manual = cargar("manual18", UNIDAD/"soluciones/03_explicar_a_mano.py")


def modificar(ruta, funcion):
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        campos, filas = lector.fieldnames, list(lector)
    funcion(filas)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = {n: {p: d.leer_csv(UNIDAD/"datos"/n/f"{p}.csv", n)[0]
                        for p in ("entrenamiento", "validacion")} for n in d.ENTRADAS}
        cls.modelos = {n: d.ajustar(f["entrenamiento"], n)[0] for n, f in cls.filas.items()}
        cls.informes = {n: d.ejecutar_experimento(n) for n in d.ENTRADAS}


class Matematicas(Base):
    def test_01_manual_y_dimension(self):
        self.assertEqual(manual.reconstruir(10, [3, 3, 1], [1, 1, -1]), 15)
        self.assertEqual(manual.reconstruir(10, [6, 0, 1], [1, 1, -1]), 15)
        with self.assertRaises(ValueError):
            manual.reconstruir(0, [1], [1, 2])

    def test_02_contribuciones_reconstruyen_todos_los_casos(self):
        modelo = self.modelos["consumo"]
        for x in d.matriz(self.filas["consumo"]["validacion"], "consumo"):
            c = d.explicar_lineal(modelo, x)
            self.assertAlmostEqual(c["base"]+sum(c["contribuciones"]), c["prediccion"], places=11)
            self.assertAlmostEqual(c["intercepto_original"]+np.dot(c["coef_original"], x), c["prediccion"], places=11)

    def test_03_minimos_cuadrados_independientes(self):
        filas = self.filas["consumo"]["entrenamiento"]
        x = np.array([[1, f["horas"], f["temperatura_c"]] for f in filas])
        beta = np.linalg.lstsq(x, [f["consumo_kwh"] for f in filas], rcond=None)[0]
        val = self.filas["consumo"]["validacion"]
        referencia = np.array([[1, f["horas"], f["temperatura_c"]] for f in val]) @ beta
        np.testing.assert_allclose(self.modelos["consumo"].predict(d.matriz(val, "consumo")), referencia, atol=1e-10)

    def test_04_rango_y_atribuciones_no_unicas(self):
        modelo = self.modelos["consumo"]
        e, r = modelo.steps[0][1], modelo.steps[1][1]
        self.assertEqual(r.rank_, 2)
        z = e.transform(d.matriz(self.filas["consumo"]["validacion"], "consumo"))
        np.testing.assert_allclose(z[:, 0], z[:, 1], atol=1e-12)
        alternativa = r.coef_.copy()
        alternativa[0] += 5
        alternativa[1] -= 5
        np.testing.assert_allclose(z @ alternativa, z @ r.coef_, atol=1e-11)
        self.assertGreater(abs(z[0, 0]*alternativa[0]-z[0, 0]*r.coef_[0]), 1)

    def test_05_escala_solo_train_y_base_media(self):
        train = self.filas["consumo"]["entrenamiento"]
        x = d.matriz(train, "consumo")
        e = self.informes["consumo"]["estado"]
        np.testing.assert_allclose(e["media"], x.mean(axis=0))
        np.testing.assert_allclose(e["escala"], x.std(axis=0, ddof=0))
        self.assertAlmostEqual(e["intercepto"], np.mean([f["consumo_kwh"] for f in train]))
        c = self.informes["consumo"]["caso_local"]
        self.assertLess(c["contribuciones"][2], 0)
        self.assertAlmostEqual(c["coef_original"][0], 60*c["coef_original"][1])

    def test_06_permutacion_referencia_independiente(self):
        class Predictor:
            def predict(self, x):
                return 2*x[:, 0]+x[:, 1]
        x = np.array([[0., 1.], [2., 3.], [4., 2.]])
        y = np.array([1., 6., 10.])
        resultado = d.permutar(Predictor(), x, y, {"a": [0]}, 4, 41)
        rng = np.random.Generator(np.random.PCG64(41))
        base = sum(abs(y[i]-(2*x[i, 0]+x[i, 1])) for i in range(3))/3
        esperados = []
        for _ in range(4):
            orden = rng.permutation(3)
            esperados.append(sum(abs(y[i]-(2*x[orden[i], 0]+x[i, 1])) for i in range(3))/3-base)
        np.testing.assert_allclose(resultado["bloques"]["a"]["deltas"], esperados)
        self.assertAlmostEqual(resultado["bloques"]["a"]["desviacion"], np.std(esperados, ddof=0))

    def test_07_bloque_preserva_dependencia_sin_mutar(self):
        entradas = []
        class Predictor:
            def predict(self, x):
                entradas.append(x.copy())
                return x[:, 0]
        x = np.array([[1., 60.], [2., 120.], [3., 180.]])
        original = x.copy()
        d.permutar(Predictor(), x, np.array([1, 2, 3]), {"juntas": [0, 1]}, 8)
        for visto in entradas:
            np.testing.assert_allclose(visto[:, 1], 60*visto[:, 0])
        np.testing.assert_array_equal(x, original)

    def test_08_permutacion_reproducible_y_modelo_inmutable(self):
        modelo = self.modelos["consumo"]
        estado = d.estado_modelo(modelo, "consumo")
        filas = self.filas["consumo"]["validacion"]
        args = (modelo, d.matriz(filas, "consumo"), [f["consumo_kwh"] for f in filas], {"h": [0]})
        a, b, c = d.permutar(*args), d.permutar(*args), d.permutar(*args, semilla=51)
        self.assertEqual(a, b)
        self.assertNotEqual(a["bloques"], c["bloques"])
        self.assertEqual(estado, d.estado_modelo(modelo, "consumo"))
        with self.assertRaises(ValueError):
            d.permutar(modelo, [[1, 2]], [1], {"h": [0]})
        with self.assertRaises(ValueError):
            d.permutar(*args[:-1], {"h": [10]})

    def test_09_recorridos_contrastados_con_biblioteca(self):
        modelo = self.modelos["alertas"]
        for x in d.matriz(self.filas["alertas"]["validacion"], "alertas"):
            c = d.explicar_arbol(modelo, x)
            self.assertEqual(c["hoja"], modelo.apply([x])[0])
            self.assertEqual(c["clase_reconstruida"], modelo.predict([x])[0])
            self.assertEqual([p["nodo"] for p in c["pasos"]]+[c["hoja"]], modelo.decision_path([x]).indices.tolist())
            np.testing.assert_allclose(c["fracciones_clase"], modelo.predict_proba([x])[0])

    def test_10_fronteras_float32_del_arbol(self):
        modelo = self.modelos["alertas"]
        for umbral in modelo.tree_.threshold[modelo.tree_.feature >= 0]:
            for x in (np.nextafter(np.float32(umbral), np.float32(-np.inf)), np.float32(umbral),
                      np.nextafter(np.float32(umbral), np.float32(np.inf))):
                c = d.explicar_arbol(modelo, [float(x)])
                self.assertEqual(c["hoja"], modelo.apply([[float(x)]])[0])

    def test_11_frecuencias_hojas_desde_datos(self):
        modelo = self.modelos["alertas"]
        filas = self.filas["alertas"]["entrenamiento"]
        hojas = modelo.apply(d.matriz(filas, "alertas"))
        for hoja in set(hojas):
            y = [f["requiere_revision"] for f, h in zip(filas, hojas) if h == hoja]
            self.assertEqual(len(y), modelo.tree_.n_node_samples[hoja])
            self.assertAlmostEqual(sum(y)/len(y), modelo.tree_.value[hoja, 0, 1])

    def test_12_confusion_y_tasas_referencia(self):
        r = self.informes["alertas"]["validacion"]
        filas = r["predicciones"]
        tn, fp, fn, tp = confusion_matrix([f["real"] for f in filas], [f["prediccion"] for f in filas], labels=[0, 1]).ravel()
        m = r["metricas"]
        self.assertEqual([m[k] for k in ("VN", "FP", "FN", "VP")], [tn, fp, fn, tp])
        self.assertAlmostEqual(m["recobrado"], tp/(tp+fn))
        self.assertAlmostEqual(m["tasa_fp"], fp/(fp+tn))

    def test_13_grupos_sin_soporte_y_con_cero(self):
        g = self.informes["alertas"]["validacion"]["grupos"]
        self.assertEqual(g["escaso"]["n"], 4)
        self.assertIsNone(g["escaso"]["recobrado"])
        self.assertEqual(g["escaso"]["tasa_fp"], 0)
        self.assertEqual(g["nuevo"]["n"], 0)
        self.assertIsNone(g["nuevo"]["tasa_fp"])
        self.assertIsNone(g["nuevo"]["exactitud"])
        self.assertIsNone(d.resumen_binario([1, 1], [0, 0])["precision"])
        self.assertEqual(d.resumen_binario([1, 1], [0, 0])["recobrado"], 0)
        self.assertIsNone(d.resumen_binario([1, 1], [1, 1])["tasa_fp"])

    def test_14_agregacion_ponderada_por_positivos(self):
        r = self.informes["alertas"]["validacion"]
        g, m = r["grupos"], r["metricas"]
        for clave in ("n", "VP", "VN", "FP", "FN"):
            self.assertEqual(sum(v[clave] for v in g.values()), m[clave])
        self.assertAlmostEqual(sum(v["fraccion_muestra"] for v in g.values()), 1)
        ponderado = sum(v["recobrado"]*v["positivos"] for v in g.values() if v["positivos"])/m["positivos"]
        self.assertAlmostEqual(ponderado, m["recobrado"])
        self.assertNotAlmostEqual(np.mean([v["recobrado"] for v in g.values() if v["positivos"]]), m["recobrado"])


class Separacion(Base):
    def test_15_ids_grupos_objetivos_no_son_entradas(self):
        for n, f in self.filas.items():
            cambiadas = copy.deepcopy(f["validacion"])
            for r in cambiadas:
                r["caso_id"] = "irrelevante"
                r[d.OBJETIVO[n]] = 100000
                r["grupo"] = "nuevo"
            np.testing.assert_array_equal(d.matriz(cambiadas, n), d.matriz(f["validacion"], n))

    def test_16_orden_lectura_ajuste_diagnostico_cierre(self):
        for n in d.ENTRADAS:
            eventos = []
            leer, ajustar = d.leer_csv, d.ajustar
            def lectura(ruta, nombre):
                eventos.append(Path(ruta).stem)
                return leer(ruta, nombre)
            def ajuste(filas, nombre):
                eventos.append("ajuste")
                return ajustar(filas, nombre)
            with patch.object(d, "leer_csv", side_effect=lectura), patch.object(d, "ajustar", side_effect=ajuste):
                d.ejecutar_experimento(n, evaluar_prueba=True)
            self.assertEqual(eventos, ["entrenamiento", "ajuste", "validacion", "prueba"])

    def test_17_desarrollo_no_necesita_archivo_prueba(self):
        for n in d.ENTRADAS:
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/n
                shutil.copytree(UNIDAD/"datos"/n, datos)
                (datos/"prueba.csv").unlink()
                r = d.ejecutar_experimento(n, datos)
                self.assertIsNone(r["prueba"])
                self.assertNotIn("prueba", r["fuentes"])

    def test_18_cierre_conserva_desarrollo(self):
        for n in d.ENTRADAS:
            r = d.ejecutar_experimento(n, evaluar_prueba=True)
            self.assertIsNotNone(r["prueba"])
            for clave in ("estado", "entrenamiento", "validacion", "linea_base_validacion", "caso_local", "permutacion"):
                self.assertEqual(r[clave], self.informes[n][clave])

    def test_19_etiquetas_validacion_no_alteran_modelo(self):
        for n in d.ENTRADAS:
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/n
                shutil.copytree(UNIDAD/"datos"/n, datos)
                def cambiar(filas):
                    for f in filas:
                        f[d.OBJETIVO[n]] = float(f[d.OBJETIVO[n]])+30 if n == "consumo" else 1-int(f[d.OBJETIVO[n]])
                modificar(datos/"validacion.csv", cambiar)
                r = d.ejecutar_experimento(n, datos)
                for clave in ("estado", "entrenamiento", "caso_local"):
                    self.assertEqual(r[clave], self.informes[n][clave])
                self.assertNotEqual(r["validacion"]["metricas"], self.informes[n]["validacion"]["metricas"])

    def test_20_etiquetas_prueba_no_alteran_predicciones(self):
        for n in d.ENTRADAS:
            original = d.ejecutar_experimento(n, evaluar_prueba=True)
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/n
                shutil.copytree(UNIDAD/"datos"/n, datos)
                def cambiar(filas):
                    for f in filas:
                        f[d.OBJETIVO[n]] = float(f[d.OBJETIVO[n]])+30 if n == "consumo" else 1-int(f[d.OBJETIVO[n]])
                modificar(datos/"prueba.csv", cambiar)
                r = d.ejecutar_experimento(n, datos, True)
                for clave in ("estado", "validacion", "caso_local", "permutacion"):
                    self.assertEqual(r[clave], original[clave])
                self.assertEqual([p["prediccion"] for p in r["prueba"]["predicciones"]], [p["prediccion"] for p in original["prueba"]["predicciones"]])
                self.assertNotEqual(r["prueba"]["metricas"], original["prueba"]["metricas"])

    def test_21_entradas_validacion_no_reajustan_escala(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"consumo"
            shutil.copytree(UNIDAD/"datos/consumo", datos)
            modificar(datos/"validacion.csv", lambda filas: [f.update(temperatura_c="90") for f in filas])
            r = d.ejecutar_experimento("consumo", datos)
            self.assertEqual(r["estado"], self.informes["consumo"]["estado"])
            self.assertNotEqual(r["validacion"]["predicciones"], self.informes["consumo"]["validacion"]["predicciones"])

    def test_22_ids_compartidos_rechazados(self):
        for fase in ("validacion", "prueba"):
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/"alertas"
                shutil.copytree(UNIDAD/"datos/alertas", datos)
                modificar(datos/f"{fase}.csv", lambda f: f[0].update(caso_id=self.filas["alertas"]["entrenamiento"][0]["caso_id"]))
                with self.assertRaisesRegex(ValueError, "IDs compartidos"):
                    d.ejecutar_experimento("alertas", datos, True)

    def test_23_csv_malformados_y_dominios(self):
        cabecera = "caso_id,grupo,lectura,requiere_revision\n"
        casos = ["", cabecera, "caso_id,grupo,lectura,lectura\na,estandar,0,0\n",
                 cabecera+"a,estandar,nan,0\n", cabecera+"a,desconocido,.5,0\n",
                 cabecera+"a,estandar,2,0\n", cabecera+"a,estandar,.5,2\n",
                 cabecera+"a,estandar,,0\n", cabecera+"a,estandar,.5,0,extra\n",
                 cabecera+"a,estandar,.5,0\na,estandar,.6,1\n"]
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"datos.csv"
            for texto in casos:
                with self.subTest(texto=texto):
                    ruta.write_text(texto, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        d.leer_csv(ruta, "alertas")
            ruta.write_text("caso_id,horas,minutos,temperatura_c,consumo_kwh\na,1,70,20,10\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "60"):
                d.leer_csv(ruta, "consumo")

    def test_24_clase_unica_y_auditoria_incompatible(self):
        filas = copy.deepcopy(self.filas["alertas"]["entrenamiento"])
        for f in filas:
            f["requiere_revision"] = 0
        with self.assertRaisesRegex(ValueError, "ambas clases"):
            d.ajustar(filas, "alertas")
        with self.assertRaises(ValueError):
            d.auditar(filas, [0])


class Artefactos(Base):
    def test_25_regeneracion_seis_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"nuevos"
            generador.generar(salida)
            for n in d.ENTRADAS:
                for p in generador.PARTICIONES:
                    self.assertEqual((salida/n/f"{p}.csv").read_bytes(), (UNIDAD/"datos"/n/f"{p}.csv").read_bytes())
            with self.assertRaises(FileExistsError):
                generador.generar(salida)

    def test_26_exportacion_json_csv_desarrollo_y_cierre(self):
        for n in d.ENTRADAS:
            for cierre in (False, True):
                r = d.ejecutar_experimento(n, evaluar_prueba=cierre)
                with tempfile.TemporaryDirectory() as tmp:
                    salida = Path(tmp)/"resultados"
                    d.exportar(r, salida)
                    self.assertEqual(json.loads((salida/"informe.json").read_text()), r)
                    self.assertEqual((salida/"predicciones_prueba.csv").exists(), cierre)
                    with (salida/"predicciones_validacion.csv").open() as f:
                        filas = list(csv.DictReader(f))
                    self.assertEqual(len(filas), r["validacion"]["metricas"]["n"])
                    np.testing.assert_allclose([float(f["prediccion"]) for f in filas], [f["prediccion"] for f in r["validacion"]["predicciones"]])
                    with self.assertRaises(FileExistsError):
                        d.exportar(r, salida)

    def test_27_recursos_publicados_corresponden(self):
        for n, r in self.informes.items():
            publicado = json.loads((UNIDAD/"recursos"/n/"informe.json").read_text())
            for clave in r:
                if clave != "versiones":
                    self.assertEqual(publicado[clave], r[clave])
            self.assertEqual(publicado["versiones"]["matplotlib"], figuras.VERSIONES_GRAFICAS["matplotlib"])
            self.assertIsNone(publicado["prueba"])

    def test_28_figuras_lineales_con_datos_correctos(self):
        r = self.informes["consumo"]
        figs = figuras.crear_figuras(r)
        try:
            np.testing.assert_allclose([p.get_width() for p in figs["contribuciones"].axes[0].patches], r["caso_local"]["contribuciones"])
            np.testing.assert_allclose([p.get_width() for p in figs["permutacion"].axes[0].patches], [v["media"] for v in r["permutacion"]["bloques"].values()])
        finally:
            for fig in figs.values():
                figuras.plt.close(fig)

    def test_29_figura_grupos_no_inventa_ceros(self):
        r = self.informes["alertas"]
        figs = figuras.crear_figuras(r)
        try:
            conteos, tasas = figs["grupos"].axes
            np.testing.assert_allclose([p.get_height() for p in tasas.patches], [46/47, 7/19])
            self.assertEqual(sum("No definido" in t.get_text() for t in tasas.texts), 2)
            for i, clave in enumerate(("VP", "FN", "FP", "VN")):
                self.assertEqual([p.get_height() for p in conteos.patches[4*i:4*i+4]], [v[clave] for v in r["validacion"]["grupos"].values()])
        finally:
            for fig in figs.values():
                figuras.plt.close(fig)

    def test_30_figuras_cierre_solo_validacion_y_formatos(self):
        for n in d.ENTRADAS:
            r = d.ejecutar_experimento(n, evaluar_prueba=True)
            r["prueba"] = {"contenido": "no graficar"}
            with tempfile.TemporaryDirectory() as tmp:
                figuras.guardar_figuras(r, tmp)
                esperados = ("contribuciones", "permutacion") if n == "consumo" else ("grupos",)
                for nombre in esperados:
                    self.assertTrue((Path(tmp)/f"{nombre}.png").read_bytes().startswith(b"\x89PNG"))
                    self.assertIn("<svg", (Path(tmp)/f"{nombre}.svg").read_text())


if __name__ == "__main__":
    unittest.main()

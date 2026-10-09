"""Referencias independientes de forward/backprop, selección, separación y artefactos."""
import copy
import csv
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.metrics import log_loss

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/"ejemplos"))
import redes as r
import figuras


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


generador = cargar("generador19", UNIDAD/"datos/generar_datos.py")
manual = cargar("manual19", UNIDAD/"soluciones/03_retropropagar_a_mano.py")


@lru_cache(maxsize=None)
def informe(nombre):
    return r.ejecutar_experimento(nombre)


def modificar(ruta, funcion):
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        campos, filas = lector.fieldnames, list(lector)
    funcion(filas)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def referencia(x, parametros):
    resultados = []
    for fila in x:
        if "W" in parametros:
            s = sum(a*b for a, b in zip(fila, parametros["W"]))+parametros["b"][0]
        else:
            h = [math.tanh(sum(fila[j]*parametros["W1"][j, k] for j in range(len(fila)))+parametros["b1"][k]) for k in range(len(parametros["b1"]))]
            s = sum(a*b for a, b in zip(h, parametros["W2"]))+parametros["b2"][0]
        resultados.append(float(s))
    return resultados


def objetivo_referencia(x, y, p, l2):
    logits = referencia(x, p)
    bce = sum(math.log1p(math.exp(-s if etiqueta else s)) for etiqueta, s in zip(y, logits))/len(y)
    return bce+l2/2*sum(float(v*v) for k, valores in p.items() if k.startswith("W") for v in valores.flat)


class Matematicas(unittest.TestCase):
    def setUp(self):
        self.x = np.array([[.2, -.7], [.8, .1], [-.4, .5]])
        self.y = np.array([0., 1., 1.])

    def test_01_paso_manual_gradientes_y_actualizacion(self):
        x, y = np.array([[1., -1.]]), np.array([1.])
        p = {"W1": np.array([[.5, -.5], [.5, -.5]]), "b1": np.zeros(2), "W2": np.array([1., -1.]), "b2": np.zeros(1)}
        esperado = manual.paso_manual()
        objetivo, grad = r.objetivo_gradiente(x, y, p)
        self.assertAlmostEqual(objetivo, esperado["bce_antes"])
        for k in p:
            np.testing.assert_allclose(grad[k], esperado["gradientes"][k])
            np.testing.assert_allclose(p[k]-.1*grad[k], esperado["parametros_nuevos"][k])
        s = r.adelante(x, esperado["parametros_nuevos"])[0]
        self.assertAlmostEqual(r.perdida(y, s), esperado["bce_despues"])
        self.assertLess(r.perdida(y, s), objetivo)

    def test_02_forward_escalar_independiente(self):
        for h in (0, 3):
            p = r.inicializar(2, h)
            np.testing.assert_allclose(r.adelante(self.x, p)[0], referencia(self.x, p), atol=1e-14)

    def test_03_diferencias_finitas_todos_los_parametros(self):
        eps = 1e-5
        for h in (0, 3):
            for l2 in (0., .2):
                p = r.inicializar(2, h, 7)
                objetivo, grad = r.objetivo_gradiente(self.x, self.y, p, l2)
                self.assertAlmostEqual(objetivo, objetivo_referencia(self.x, self.y, p, l2))
                for clave in p:
                    for indice in np.ndindex(p[clave].shape):
                        mas, menos = r.copiar(p), r.copiar(p)
                        mas[clave][indice] += eps
                        menos[clave][indice] -= eps
                        numerico = (objetivo_referencia(self.x, self.y, mas, l2)-objetivo_referencia(self.x, self.y, menos, l2))/(2*eps)
                        self.assertAlmostEqual(grad[clave][indice], numerico, places=8)

    def test_04_promedio_por_lote(self):
        p = r.inicializar(2, 3)
        valor, grad = r.objetivo_gradiente(self.x, self.y, p, .1)
        individuales = [r.objetivo_gradiente(self.x[i:i+1], self.y[i:i+1], p, .1) for i in range(3)]
        self.assertAlmostEqual(valor, sum(v for v, _ in individuales)/3)
        for k in p:
            np.testing.assert_allclose(grad[k], sum(g[k] for _, g in individuales)/3, atol=1e-14)

    def test_05_l2_no_penaliza_sesgos(self):
        p = r.inicializar(2, 3)
        a, ga = r.objetivo_gradiente(self.x, self.y, p, 0)
        b, gb = r.objetivo_gradiente(self.x, self.y, p, .2)
        self.assertAlmostEqual(b-a, .1*sum(np.sum(v*v) for k, v in p.items() if k.startswith("W")))
        for k in p:
            np.testing.assert_allclose(gb[k]-ga[k], .2*p[k] if k.startswith("W") else np.zeros_like(p[k]), atol=1e-14)

    def test_06_logits_extremos_sin_log_cero(self):
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            np.testing.assert_allclose(r.sigmoide([-1000, 0, 1000]), [0, .5, 1])
            self.assertEqual(r.perdida([0, 1], [-1000, 1000]), 0)
            self.assertEqual(r.perdida([1, 0], [-1000, 1000]), 1000)
            self.assertAlmostEqual(r.perdida([0, 1], [0, 0]), math.log(2))

    def test_07_perdida_con_biblioteca(self):
        s = np.array([-3., -.8, 1.2, 4.])
        self.assertAlmostEqual(r.perdida([0, 1, 1, 0], s), log_loss([0, 1, 1, 0], r.sigmoide(s)))

    def test_08_componer_capas_sin_activacion(self):
        p = r.inicializar(2, 3)
        p["b1"] = np.array([.1, .2, -.1])
        compuesto = (self.x @ p["W1"]+p["b1"]) @ p["W2"]+p["b2"][0]
        equivalente = self.x @ (p["W1"] @ p["W2"])+(p["b1"] @ p["W2"]+p["b2"][0])
        np.testing.assert_allclose(compuesto, equivalente)
        self.assertFalse(np.allclose(compuesto, r.adelante(self.x, p)[0]))

    def test_09_inicializacion_cero_no_rompe_simetria(self):
        p = {k: np.zeros_like(v) for k, v in r.inicializar(2, 3).items()}
        for _ in range(5):
            _, g = r.objetivo_gradiente(self.x, self.y, p)
            p = {k: v-.1*g[k] for k, v in p.items()}
        np.testing.assert_array_equal(p["W1"], 0)
        np.testing.assert_array_equal(p["W2"], 0)
        self.assertNotEqual(p["b2"][0], 0)

    def test_10_semilla_y_copia_independiente(self):
        p, q, distinto = r.inicializar(2, 3), r.inicializar(2, 3), r.inicializar(2, 3, 20)
        for k in p:
            np.testing.assert_array_equal(p[k], q[k])
        self.assertFalse(np.array_equal(p["W1"], distinto["W1"]))
        copia = r.copiar(p)
        copia["W1"][0, 0] += 1
        self.assertNotEqual(copia["W1"][0, 0], p["W1"][0, 0])

    def test_11_formas_y_valores_invalidos(self):
        for x, y in [([], []), ([[1, 2]], [[1]]), ([[1, 2]], [2]), ([[np.nan, 1]], [0])]:
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                r.validar_xy(x, y)
        with self.assertRaises(ValueError):
            r.adelante(self.x, {"W": np.zeros((2, 1)), "b": np.zeros(1)})
        with self.assertRaises(ValueError):
            r.objetivo_gradiente(self.x, self.y, r.inicializar(2, 3), -1)
        for epocas in (0, -1, True):
            with self.assertRaises(ValueError):
                r.entrenar(self.x, self.y, self.x, self.y, {"ocultas": 3, "l2": 0}, epocas)

    def test_12_conteo_de_parametros(self):
        self.assertEqual(sum(v.size for v in r.inicializar(2, 0).values()), 3)
        self.assertEqual(sum(v.size for v in r.inicializar(2, 8).values()), 33)
        self.assertEqual(sum(v.size for v in r.inicializar(2, 32).values()), 129)


class Entrenamiento(unittest.TestCase):
    def test_13_escalado_solo_entrenamiento(self):
        for nombre in r.CONFIGURACIONES:
            filas = r.leer_csv(UNIDAD/"datos"/nombre/"entrenamiento.csv")[0]
            x = r.matriz(filas)
            e = informe(nombre)["escala"]
            np.testing.assert_allclose(e["media"], np.mean(x, axis=0))
            np.testing.assert_allclose(e["escala"], np.std(x, axis=0, ddof=0))
        with self.assertRaises(ValueError):
            r.ajustar_escala(np.ones((2, 2)))

    def test_14_epoca_elegida_es_minimo_validacion(self):
        for nombre in r.CONFIGURACIONES:
            for c in informe(nombre)["candidatos"].values():
                if c["historial"]:
                    mejor = min(c["historial"], key=lambda h: h["bce_validacion"])
                    self.assertEqual(c["epoca_elegida"], mejor["epoca"])
                    self.assertAlmostEqual(c["validacion"]["metricas"]["bce"], mejor["bce_validacion"])

    def test_15_mejor_estado_no_es_ultima_referencia_mutada(self):
        i = informe("ruido")
        c = i["candidatos"]["red32"]
        self.assertLess(c["epoca_elegida"], r.EPOCAS["ruido"])
        self.assertNotEqual(c["parametros"], c["parametros_finales"])
        train = r.leer_csv(UNIDAD/"datos/ruido/entrenamiento.csv")[0]
        val = r.leer_csv(UNIDAD/"datos/ruido/validacion.csv")[0]
        parcial = r.entrenar(r.transformar(train, i["escala"]), [f["objetivo"] for f in train], r.transformar(val, i["escala"]), [f["objetivo"] for f in val], c["configuracion"], c["epoca_elegida"])
        for k in c["parametros"]:
            np.testing.assert_allclose(c["parametros"][k], parcial["parametros_finales"][k], atol=1e-12)
        self.assertGreater(c["historial"][-1]["bce_validacion"], c["validacion"]["metricas"]["bce"])

    def test_16_validacion_no_cambia_trayectoria_entrenada(self):
        x = np.array([[0., 0.], [1., .3], [-.3, 1.]])
        y = [0, 1, 1]
        config = {"ocultas": 3, "l2": .01}
        a = r.entrenar(x, y, x, y, config, 30, cada=5)
        b = r.entrenar(x, y, x*2, [1, 0, 0], config, 30, cada=5)
        for k in a["parametros_finales"]:
            np.testing.assert_array_equal(a["parametros_finales"][k], b["parametros_finales"][k])
        self.assertEqual([h["bce_entrenamiento"] for h in a["historial"]], [h["bce_entrenamiento"] for h in b["historial"]])
        self.assertNotEqual([h["bce_validacion"] for h in a["historial"]], [h["bce_validacion"] for h in b["historial"]])

    def test_17_empate_prioriza_orden_y_epoca_temprana(self):
        def c(valor):
            return {"validacion": {"metricas": {"bce": valor}}}
        self.assertEqual(r.seleccionar({"primero": c(.5), "segundo": c(.5-1e-13)}), "primero")
        self.assertEqual(r.seleccionar({"primero": c(.5), "segundo": c(.4)}), "segundo")
        x = np.array([[-1., 1.], [1., -1.]])
        modelo = r.entrenar(x, [0, 1], x, [0, 1], {"ocultas": 0, "l2": 0}, 3, cada=2)
        self.assertEqual([h["epoca"] for h in modelo["historial"]], [0, 2, 3])
        empate = r.entrenar(np.zeros((2, 2)), [0, 1], np.zeros((2, 2)), [0, 1], {"ocultas": 0, "l2": 0}, 3, cada=1)
        self.assertEqual(empate["epoca_elegida"], 0)

    def test_18_inicializacion_pareada_para_l2(self):
        candidatos = informe("ruido")["candidatos"]
        self.assertEqual(candidatos["red32"]["parametros_iniciales"], candidatos["red32_l2"]["parametros_iniciales"])
        self.assertNotEqual(candidatos["red32"]["parametros_finales"], candidatos["red32_l2"]["parametros_finales"])

    def test_19_xor_mejora_y_metricas_desde_predicciones(self):
        i = informe("xor")
        self.assertEqual(i["seleccionado"], "red8")
        self.assertLess(i["candidatos"]["red8"]["validacion"]["metricas"]["bce"], .02)
        for c in i["candidatos"].values():
            ev = c["validacion"]
            filas = ev["predicciones"]
            self.assertEqual(sum(f["real"] == f["prediccion"] for f in filas)/len(filas), ev["metricas"]["exactitud"])
            self.assertAlmostEqual(r.perdida([f["real"] for f in filas], [f["logit"] for f in filas]), ev["metricas"]["bce"])

    def test_20_prevalencia_y_empate_umbral(self):
        c = informe("xor")["candidatos"]["prevalencia"]
        self.assertEqual(c["n_parametros"], 1)
        self.assertTrue(all(f["probabilidad"] == .5 and f["prediccion"] == 1 for f in c["validacion"]["predicciones"]))


class Separacion(unittest.TestCase):
    def test_21_id_y_objetivo_fuera_de_entradas(self):
        filas = r.leer_csv(UNIDAD/"datos/xor/validacion.csv")[0]
        copia = copy.deepcopy(filas)
        for f in copia:
            f.update(caso_id="cambiado", objetivo=999)
        np.testing.assert_array_equal(r.matriz(filas), r.matriz(copia))

    def test_22_desarrollo_no_abre_prueba(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"datos"
            shutil.copytree(UNIDAD/"datos/xor", datos)
            (datos/"prueba.csv").unlink()
            i = r.ejecutar_experimento("xor", datos, epocas=20)
            self.assertIsNone(i["prueba"])
            self.assertNotIn("prueba", i["fuentes"])

    def test_23_seleccion_y_ajustes_antes_de_abrir_prueba(self):
        eventos = []
        leer, entrenar, seleccionar = r.leer_csv, r.entrenar, r.seleccionar
        def lectura(ruta):
            eventos.append(Path(ruta).stem)
            return leer(ruta)
        def ajuste(*args, **kwargs):
            eventos.append("ajuste")
            return entrenar(*args, **kwargs)
        def elegir(c):
            eventos.append("seleccion")
            return seleccionar(c)
        with patch.object(r, "leer_csv", side_effect=lectura), patch.object(r, "entrenar", side_effect=ajuste), patch.object(r, "seleccionar", side_effect=elegir):
            r.ejecutar_experimento("xor", evaluar_prueba=True, epocas=20)
        self.assertEqual(eventos, ["entrenamiento", "validacion", "ajuste", "ajuste", "seleccion", "prueba"])

    def test_24_etiquetas_prueba_no_cambian_ajuste_o_predicciones(self):
        for nombre in r.CONFIGURACIONES:
            original = r.ejecutar_experimento(nombre, evaluar_prueba=True, epocas=20)
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/nombre
                shutil.copytree(UNIDAD/"datos"/nombre, datos)
                modificar(datos/"prueba.csv", lambda filas: [f.update(objetivo="0") for f in filas])
                cambiado = r.ejecutar_experimento(nombre, datos, True, epocas=20)
                for k in ("escala", "candidatos", "seleccionado", "puntos_validacion"):
                    self.assertEqual(original[k], cambiado[k])
                self.assertEqual([f["probabilidad"] for f in original["prueba"]["predicciones"]], [f["probabilidad"] for f in cambiado["prueba"]["predicciones"]])
                self.assertNotEqual(original["prueba"]["metricas"], cambiado["prueba"]["metricas"])

    def test_25_ids_compartidos_en_validacion_y_cierre(self):
        train = r.leer_csv(UNIDAD/"datos/xor/entrenamiento.csv")[0]
        for fase in ("validacion", "prueba"):
            with tempfile.TemporaryDirectory() as tmp:
                datos = Path(tmp)/"datos"
                shutil.copytree(UNIDAD/"datos/xor", datos)
                modificar(datos/f"{fase}.csv", lambda f: f[0].update(caso_id=train[0]["caso_id"]))
                with self.assertRaisesRegex(ValueError, "IDs compartidos"):
                    r.ejecutar_experimento("xor", datos, True, epocas=10)

    def test_26_csv_invalidos_y_clase_unica(self):
        cab = "caso_id,senal_a,senal_b,objetivo\n"
        casos = ["", cab, "caso_id,senal_a,senal_a,objetivo\na,0,0,1\n", cab+"a,0,nan,0\n", cab+"a,2,0,0\n",
                 cab+"a,0,0,2\n", cab+"a,,0,0\n", cab+"a,0,0,0,extra\n", cab+"a,0,0,0\na,1,1,1\n"]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"malo.csv"
            for texto in casos:
                p.write_text(texto, encoding="utf-8")
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    r.leer_csv(p)
            datos = Path(tmp)/"datos"
            shutil.copytree(UNIDAD/"datos/xor", datos)
            modificar(datos/"entrenamiento.csv", lambda filas: [f.update(objetivo="0") for f in filas])
            with self.assertRaisesRegex(ValueError, "ambas clases"):
                r.ejecutar_experimento("xor", datos, epocas=10)


class Artefactos(unittest.TestCase):
    def test_27_regeneracion_seis_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"datos"
            generador.generar(salida)
            for nombre in r.CONFIGURACIONES:
                for fase in generador.PARTICIONES:
                    self.assertEqual((salida/nombre/f"{fase}.csv").read_bytes(), (UNIDAD/"datos"/nombre/f"{fase}.csv").read_bytes())
            with self.assertRaises(FileExistsError):
                generador.generar(salida)

    def test_28_exportacion_desarrollo_y_cierre(self):
        for cierre in (False, True):
            i = r.ejecutar_experimento("xor", evaluar_prueba=cierre, epocas=20)
            with tempfile.TemporaryDirectory() as tmp:
                salida = Path(tmp)/"nuevo"
                r.exportar(i, salida)
                self.assertEqual(json.loads((salida/"informe.json").read_text()), i)
                self.assertEqual((salida/"predicciones_prueba.csv").exists(), cierre)
                with (salida/"predicciones_validacion.csv").open() as f:
                    filas = list(csv.DictReader(f))
                for n, c in i["candidatos"].items():
                    np.testing.assert_allclose([float(f["probabilidad"]) for f in filas if f["candidato"] == n], [f["probabilidad"] for f in c["validacion"]["predicciones"]])
                with self.assertRaises(FileExistsError):
                    r.exportar(i, salida)

    def test_29_informes_publicados_coinciden(self):
        for nombre in r.CONFIGURACIONES:
            publicado = json.loads((UNIDAD/"recursos"/nombre/"informe.json").read_text())
            actual = informe(nombre)
            for k in actual:
                if k != "versiones":
                    self.assertEqual(publicado[k], actual[k])
            self.assertIsNone(publicado["prueba"])

    def test_30_curvas_corresponden_y_no_usan_prueba(self):
        for nombre in r.CONFIGURACIONES:
            i = copy.deepcopy(informe(nombre))
            i["prueba"] = {"no": "utilizar"}
            figs = figuras.crear_figuras(i)
            try:
                fig = figs["aprendizaje" if nombre == "xor" else "curvas"]
                for ax, n in zip(fig.axes, r.CONFIGURACIONES[nombre]):
                    c = i["candidatos"][n]
                    np.testing.assert_allclose(ax.lines[0].get_ydata(), [h["bce_entrenamiento"] for h in c["historial"]])
                    np.testing.assert_allclose(ax.lines[1].get_ydata(), [h["bce_validacion"] for h in c["historial"]])
                    np.testing.assert_allclose(ax.lines[2].get_xdata(), [c["epoca_elegida"]]*2)
            finally:
                for fig in figs.values():
                    figuras.plt.close(fig)

    def test_31_fronteras_muestras_de_validacion_y_probabilidades(self):
        i = informe("xor")
        visto = []
        adelante = figuras.adelante
        def observar(x, p):
            s, h = adelante(x, p)
            visto.append((x.copy(), s.copy()))
            return s, h
        with patch.object(figuras, "adelante", side_effect=observar):
            figs = figuras.crear_figuras(i)
        try:
            self.assertEqual(len(visto), 2)
            for ax in figs["fronteras"].axes[:2]:
                total = sum(len(c.get_offsets()) for c in ax.collections if isinstance(c, figuras.matplotlib.collections.PathCollection))
                self.assertEqual(total, len(i["puntos_validacion"]))
            for (x, s), nombre in zip(visto, ("lineal", "red8")):
                p = r.copiar(i["candidatos"][nombre]["parametros"])
                np.testing.assert_allclose(s, referencia(x, p), atol=1e-12)
        finally:
            for fig in figs.values():
                figuras.plt.close(fig)

    def test_32_formatos_graficos(self):
        with tempfile.TemporaryDirectory() as tmp:
            for nombre in r.CONFIGURACIONES:
                carpeta = Path(tmp)/nombre
                carpeta.mkdir()
                figuras.guardar_figuras(informe(nombre), carpeta)
                archivos = list(carpeta.iterdir())
                self.assertEqual(len(archivos), 4 if nombre == "xor" else 2)
                for p in archivos:
                    if p.suffix == ".png":
                        self.assertTrue(p.read_bytes().startswith(b"\x89PNG"))
                    else:
                        self.assertIn("<svg", p.read_text())


if __name__ == "__main__":
    unittest.main()

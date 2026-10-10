"""Comprobaciones matemáticas, de información permitida y de artefactos."""
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
import torch
from torch import nn

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/"ejemplos"))
import pytorch_curso as curso
from equivalencia import comprobar
from figuras import crear_figuras
import matplotlib.pyplot as plt


def cargar_archivo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class PruebasPyTorch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        cls.equivalencia = comprobar()
        cls.informe = curso.ejecutar_experimento()
        cls.generador = cargar_archivo("datos_u20", UNIDAD/"datos/generar_datos.py")

    def copiar_datos(self, destino):
        shutil.copytree(UNIDAD/"datos/minilotes", destino)

    def escribir(self, ruta, filas):
        with ruta.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(filas)

    def test_01_forward_escalar_independiente(self):
        i = self.equivalencia
        p = i["estado_inicial_numpy"]
        salidas = []
        for x in i["configuracion"]["x"]:
            ocultas = [np.tanh(sum(x[k]*p["W1"][k][j] for k in range(2))+p["b1"][j]) for j in range(3)]
            salidas.append(sum(ocultas[j]*p["W2"][j] for j in range(3))+p["b2"][0])
        np.testing.assert_allclose(salidas, i["logits_torch"], atol=1e-12, rtol=0)

    def test_02_gradientes_diferencias_finitas(self):
        i = self.equivalencia
        p = {k: np.array(v) for k, v in i["estado_inicial_numpy"].items()}
        x, y = np.array(i["configuracion"]["x"]), np.array(i["configuracion"]["y"])
        def objetivo():
            s = np.tanh(x@p["W1"]+p["b1"])@p["W2"]+p["b2"]
            return np.logaddexp(0, (1-2*y)*s).mean()+.025*sum((p[k]**2).sum() for k in ("W1", "W2"))
        for k in p:
            for indice in np.ndindex(p[k].shape):
                original = p[k][indice]
                p[k][indice] = original+1e-6
                mas = objetivo()
                p[k][indice] = original-1e-6
                menos = objetivo()
                p[k][indice] = original
                self.assertAlmostEqual((mas-menos)/2e-6, np.array(i["gradientes_torch"][k])[indice], places=8)

    def test_03_actualizacion_sgd_todos_los_parametros(self):
        i = self.equivalencia
        for k, p in i["estado_inicial_numpy"].items():
            esperado = np.array(p)-.1*np.array(i["gradientes_numpy"][k])
            np.testing.assert_allclose(esperado, i["estado_tras_paso_torch"][k], atol=1e-12, rtol=0)
        self.assertLess(max(i["errores_maximos"].values()), 1e-12)

    def test_04_bce_extrema_y_gradiente(self):
        s = torch.tensor([-1000., 1000.], dtype=torch.float64, requires_grad=True)
        perdida = nn.BCEWithLogitsLoss()(s, torch.tensor([1., 0.], dtype=torch.float64))
        perdida.backward()
        self.assertEqual(perdida.item(), 1000.)
        self.assertEqual(s.grad.tolist(), [-.5, .5])

    def test_05_memoria_compartida_y_copia(self):
        a = np.array([1., 2.])
        compartido, copia = torch.from_numpy(a), torch.tensor(a)
        a[0] = 8
        self.assertEqual(compartido[0].item(), 8)
        self.assertEqual(copia[0].item(), 1)
        separado = compartido.detach().clone()
        compartido.detach()[0] = 9
        self.assertEqual(separado[0].item(), 8)

    def test_06_acumulacion_manual(self):
        modulo = cargar_archivo("manual_u20", UNIDAD/"soluciones/03_acumular_gradientes.py")
        self.assertEqual(modulo.demostrar(), (15., 30., 15., .5, .125))

    def test_07_forma_lote_unitario(self):
        self.assertEqual(curso.Red([12, 8])(torch.zeros(1, 2)).shape, (1,))

    def test_08_eval_conserva_autograd(self):
        modelo = curso.Red([]).eval()
        modelo(torch.ones(2, 2)).sum().backward()
        self.assertIsNotNone(modelo.capas[0].weight.grad)

    def test_09_no_grad_no_cambia_modo(self):
        modelo = curso.Red([]).train()
        with torch.no_grad():
            salida = modelo(torch.ones(2, 2))
        self.assertTrue(modelo.training)
        self.assertFalse(salida.requires_grad)

    def test_10_dropout_ilustra_modo(self):
        capa = nn.Dropout(p=1.)
        self.assertEqual(capa(torch.ones(3)).tolist(), [0., 0., 0.])
        self.assertEqual(capa.eval()(torch.ones(3)).tolist(), [1., 1., 1.])

    def test_11_copia_estado_independiente(self):
        modelo = curso.Red([])
        antes = curso.copiar_estado(modelo)
        esperado = antes["capas.0.weight"].clone()
        with torch.no_grad():
            modelo.capas[0].weight.add_(1)
        self.assertTrue(torch.equal(antes["capas.0.weight"], esperado))
        self.assertFalse(torch.equal(antes["capas.0.weight"], modelo.capas[0].weight))

    def test_12_parametros_y_presupuesto(self):
        for nombre, n in (("lineal", 3), ("red12_8", 149)):
            c = self.informe["candidatos"][nombre]
            self.assertEqual(c["n_parametros"], n)
            self.assertEqual(c["actualizaciones_totales"], 600)
            self.assertEqual(len(c["historial"]), 13)

    def test_13_cada_fila_una_vez_y_lote_parcial(self):
        for nombre in ("lineal", "red12_8"):
            ordenes = self.informe["candidatos"][nombre]["ordenes"]
            self.assertEqual(sorted(ordenes[0]["indices"]), list(range(150)))
            self.assertTrue(all(o["tamanos"] == [32, 32, 32, 32, 22] for o in ordenes))

    def test_14_orden_cambia_sin_favorecer_candidato(self):
        a = self.informe["candidatos"]["lineal"]["ordenes"]
        b = self.informe["candidatos"]["red12_8"]["ordenes"]
        self.assertEqual(a, b)
        self.assertNotEqual(a[0]["sha256_indices"], a[1]["sha256_indices"])

    def test_15_repetibilidad_mismo_entorno(self):
        primero = curso.ejecutar_experimento(epocas=2)
        segundo = curso.ejecutar_experimento(epocas=2)
        self.assertEqual(primero, segundo)

    def test_16_bce_pondera_ultimo_minilote(self):
        x = torch.tensor([[0., 0.], [1., 0.], [2., 0.]])
        y = torch.tensor([0., 1., 0.])
        modelo = curso.Red([])
        with torch.no_grad():
            modelo.capas[0].weight.copy_(torch.tensor([[2., 0.]]))
            modelo.capas[0].bias.zero_()
        esperado = (np.log(2)+np.logaddexp(0, -2)+np.logaddexp(0, 4))/3
        self.assertAlmostEqual(curso.perdida_evaluacion(modelo, x, y, lote=2), esperado, places=6)
        incorrecto = ((np.log(2)+np.logaddexp(0, -2))/2+np.logaddexp(0, 4))/2
        self.assertGreater(abs(esperado-incorrecto), .1)

    def test_17_presupuestos_invalidos(self):
        x, y = torch.zeros(3, 2), torch.zeros(3)
        for opcion in ({"epocas": 0}, {"lote": -1}, {"cada": 0}, {"epocas": True}):
            with self.assertRaises(ValueError):
                curso.entrenar(x, y, x, y, [], **opcion)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"caso.json"
            for cambio in ({"tasa": float("nan")}, {"tasa": 0}, {"l2": -1}, {"semilla": -1}):
                datos = dict(self.equivalencia["configuracion"], **cambio)
                ruta.write_text(json.dumps(datos), encoding="utf-8")
                with self.assertRaises(ValueError):
                    comprobar(ruta)

    def test_18_empate_conserva_orden(self):
        candidatos = {n: {"validacion": {"metricas": {"bce": v}}} for n, v in (("a", .5), ("b", .5-1e-9))}
        self.assertEqual(curso.seleccionar(candidatos), "a")

    def test_19_no_lee_prueba_en_desarrollo(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"datos"
            self.copiar_datos(datos)
            (datos/"prueba.csv").unlink()
            informe = curso.ejecutar_experimento(datos, epocas=2)
            self.assertIsNone(informe["prueba"])
            self.assertNotIn("prueba", informe["fuentes"])

    def test_20_abre_prueba_despues_de_seleccionar(self):
        eventos = []
        original_leer, original_elegir = curso.referencia.leer_csv, curso.seleccionar
        def leer(ruta):
            eventos.append(Path(ruta).name)
            return original_leer(ruta)
        def elegir(candidatos):
            eventos.append("seleccion")
            return original_elegir(candidatos)
        with patch.object(curso.referencia, "leer_csv", side_effect=leer), patch.object(curso, "seleccionar", side_effect=elegir):
            curso.ejecutar_experimento(evaluar_prueba=True, epocas=2)
        self.assertLess(eventos.index("seleccion"), eventos.index("prueba.csv"))

    def test_21_etiquetas_prueba_no_cambian_ajuste_ni_predicciones(self):
        original = curso.ejecutar_experimento(evaluar_prueba=True, epocas=2)
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"datos"
            self.copiar_datos(datos)
            filas, _ = curso.referencia.leer_csv(datos/"prueba.csv")
            for f in filas:
                f["objetivo"] = 1-f["objetivo"]
            self.escribir(datos/"prueba.csv", filas)
            cambiado = curso.ejecutar_experimento(datos, evaluar_prueba=True, epocas=2)
        self.assertEqual(original["candidatos"], cambiado["candidatos"])
        self.assertEqual(original["seleccionado"], cambiado["seleccionado"])
        self.assertEqual([f["logit"] for f in original["prueba"]["predicciones"]],
                         [f["logit"] for f in cambiado["prueba"]["predicciones"]])

    def test_22_validacion_no_cambia_trayectoria_de_pesos(self):
        original = curso.ejecutar_experimento(epocas=2)
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"datos"
            self.copiar_datos(datos)
            filas, _ = curso.referencia.leer_csv(datos/"validacion.csv")
            for f in filas:
                f["objetivo"] = 1-f["objetivo"]
            self.escribir(datos/"validacion.csv", filas)
            cambiado = curso.ejecutar_experimento(datos, epocas=2)
        self.assertEqual(original["escala"], cambiado["escala"])
        for n in ("lineal", "red12_8"):
            for campo in ("estado_inicial", "estado_final", "ordenes"):
                self.assertEqual(original["candidatos"][n][campo], cambiado["candidatos"][n][campo])

    def test_23_escala_solo_entrenamiento(self):
        filas, _ = curso.referencia.leer_csv(UNIDAD/"datos/minilotes/entrenamiento.csv")
        x = curso.referencia.matriz(filas)
        np.testing.assert_allclose(self.informe["escala"]["media"], np.mean(x, axis=0), atol=1e-15)
        np.testing.assert_allclose(self.informe["escala"]["escala"], np.std(x, axis=0), atol=1e-15)

    def test_24_rechaza_ids_compartidos(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = Path(tmp)/"datos"
            self.copiar_datos(datos)
            filas, _ = curso.referencia.leer_csv(datos/"validacion.csv")
            filas[0]["caso_id"] = "u20-entrenamiento-001"
            self.escribir(datos/"validacion.csv", filas)
            with self.assertRaisesRegex(ValueError, "IDs compartidos"):
                curso.ejecutar_experimento(datos, epocas=2)

    def test_25_rechaza_etiqueta_invalida(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"mal.csv"
            ruta.write_text("caso_id,senal_a,senal_b,objetivo\na,0,0,2\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                curso.referencia.leer_csv(ruta)

    def test_26_regeneracion_exacta(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"nuevos"
            self.generador.generar(salida)
            for ruta in salida.rglob("*"):
                if ruta.is_file():
                    self.assertEqual(ruta.read_bytes(), (UNIDAD/"datos"/ruta.relative_to(salida)).read_bytes())

    def test_27_recarga_igual_en_cpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"modelo.pt"
            curso.guardar_modelo(self.informe, ruta)
            modelo, escala = curso.cargar_modelo(ruta)
            esperado = self.informe["candidatos"][self.informe["seleccionado"]]["validacion"]
            self.assertEqual(curso.evaluar(self.informe["puntos_validacion"], escala, modelo), esperado)
            self.assertTrue(all(p.device.type == "cpu" for p in modelo.parameters()))
            self.assertFalse(modelo.training)

    def test_28_rechaza_estado_incompatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"modelo.pt"
            curso.guardar_modelo(self.informe, ruta)
            original = torch.load(ruta, weights_only=True)
            mutaciones = [lambda d: d.update(entradas=["senal_b", "senal_a"]),
                          lambda d: d["escala"].update(escala=[0., 1.]),
                          lambda d: d["state_dict"].update({next(iter(d["state_dict"])): torch.zeros(1)}),
                          lambda d: d["state_dict"][next(iter(d["state_dict"]))].fill_(float("nan"))]
            for mutar in mutaciones:
                cambiado = copy.deepcopy(original)
                mutar(cambiado)
                torch.save(cambiado, ruta)
                with self.assertRaises(ValueError):
                    curso.cargar_modelo(ruta)

    def test_29_exportacion_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                curso.exportar(self.informe, tmp)

    def test_30_exportacion_predicciones_y_recarga(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"salida"
            comprobacion = curso.exportar(self.informe, salida)
            self.assertEqual(comprobacion["max_error_logits"], 0.)
            self.assertFalse((salida/"predicciones_prueba.csv").exists())
            self.assertEqual(json.loads((salida/"informe.json").read_text()), self.informe)
            with (salida/"predicciones_validacion.csv").open() as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 240)
            for fila in filas:
                original = next(p for p in self.informe["candidatos"][fila["candidato"]]["validacion"]["predicciones"] if p["caso_id"] == fila["caso_id"])
                self.assertEqual(float(fila["logit"]), original["logit"])

    def test_31_figuras_corresponden_a_informe(self):
        figuras = crear_figuras(self.informe)
        try:
            for ax, nombre in zip(figuras["aprendizaje"].axes, ("lineal", "red12_8")):
                h = self.informe["candidatos"][nombre]["historial"]
                np.testing.assert_array_equal(ax.lines[1].get_ydata(), [f["bce_validacion"] for f in h])
                self.assertEqual(ax.lines[2].get_xdata()[0], self.informe["candidatos"][nombre]["epoca_elegida"])
            ax = figuras["frontera"].axes[0]
            malla = np.asarray(ax.collections[0].get_array())
            self.assertGreaterEqual(malla.min(), 0)
            self.assertLessEqual(malla.max(), 1)
            self.assertEqual(sum(len(c.get_offsets()) for c in ax.collections[-2:]), 80)
        finally:
            for f in figuras.values():
                plt.close(f)

    def test_32_epoca_elegida_reconstruye_minimo_registrado(self):
        for nombre in ("lineal", "red12_8"):
            c = self.informe["candidatos"][nombre]
            mejor = c["historial"][0]
            for h in c["historial"][1:]:
                if h["bce_validacion"] < mejor["bce_validacion"]-1e-8:
                    mejor = h
            self.assertEqual(c["epoca_elegida"], mejor["epoca"])
            self.assertAlmostEqual(c["validacion"]["metricas"]["bce"], mejor["bce_validacion"], places=6)

    def test_33_figura_gradientes(self):
        figuras = crear_figuras(self.equivalencia)
        try:
            alturas = [p.get_height() for p in figuras["gradientes"].axes[0].patches]
            esperado = [v for a in self.equivalencia["gradientes_numpy"].values() for v in np.asarray(a).ravel()]
            np.testing.assert_allclose(alturas[:13], esperado, atol=1e-12)
            np.testing.assert_allclose(alturas[13:], esperado, atol=1e-12)
        finally:
            plt.close(figuras["gradientes"])

    def test_34_informe_publicado_reproducible(self):
        publicado = json.loads((UNIDAD/"recursos/minilotes/informe.json").read_text())
        self.assertEqual(publicado["fuentes"], self.informe["fuentes"])
        self.assertEqual(publicado["seleccionado"], self.informe["seleccionado"])
        self.assertIsNone(publicado["prueba"])
        for nombre in ("lineal", "red12_8"):
            self.assertEqual(publicado["candidatos"][nombre]["epoca_elegida"], self.informe["candidatos"][nombre]["epoca_elegida"])
            np.testing.assert_allclose([p["logit"] for p in publicado["candidatos"][nombre]["validacion"]["predicciones"]],
                                       [p["logit"] for p in self.informe["candidatos"][nombre]["validacion"]["predicciones"]], atol=1e-5, rtol=1e-5)


if __name__ == "__main__":
    unittest.main()

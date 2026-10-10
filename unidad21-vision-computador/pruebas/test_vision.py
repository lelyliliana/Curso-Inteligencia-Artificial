"""Cálculos de filtros, procedencia de imágenes y evaluación separada."""
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch
from torch import nn

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/"ejemplos"))
import vision
from filtros import correlacion2d, comprobar_manual, ejecutar_filtros, X_MANUAL, K_MANUAL
from figuras_vision import crear_figuras, casos_dificiles
import matplotlib.pyplot as plt


class PruebasVision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        cls.informe = vision.ejecutar_experimento()
        cls.corto = vision.ejecutar_experimento(epocas=2)
        cls.train = vision.leer_particion(UNIDAD/"datos", "entrenamiento")
        cls.val = vision.leer_particion(UNIDAD/"datos", "validacion")
        cls.filtros = ejecutar_filtros()

    def copiar_datos(self, raiz):
        destino = Path(raiz)/"datos"
        shutil.copytree(UNIDAD/"datos", destino)
        return destino

    def filas_csv(self, datos, nombre):
        with (datos/f"{nombre}.csv").open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def escribir_csv(self, datos, nombre, filas):
        with (datos/f"{nombre}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(filas)

    def test_01_salida_manual(self):
        self.assertEqual(comprobar_manual()["salida"], [[0., -1., -2.], [-1., 1., 2.], [2., -1., -3.]])
        self.assertEqual(comprobar_manual()["error_maximo"], 0.)

    def test_02_correlacion_no_invierte_kernel(self):
        a = correlacion2d(X_MANUAL, K_MANUAL)
        b = correlacion2d(X_MANUAL, K_MANUAL[::-1, ::-1])
        np.testing.assert_array_equal(a, -b)
        self.assertFalse(np.array_equal(a, b))

    def test_03_paso_relleno_y_kernel_invalido(self):
        a = correlacion2d(X_MANUAL, K_MANUAL, paso=2, relleno=1)
        b = nn.functional.conv2d(torch.tensor(X_MANUAL)[None, None], torch.tensor(K_MANUAL)[None, None], stride=2, padding=1)
        np.testing.assert_array_equal(a, b.numpy()[0, 0])
        self.assertEqual(a.shape, (3, 3))
        for x, k, extras in ((X_MANUAL, np.ones((9, 9)), {}), (X_MANUAL, K_MANUAL, {"paso": 0}),
                             (X_MANUAL, [[float("nan")]], {})):
            with self.assertRaises(ValueError):
                correlacion2d(x, k, **extras)

    def test_04_canales_y_conversion_gris(self):
        rgb = np.array(self.filtros["rgb_hwc"])
        nchw = torch.tensor(rgb).permute(2, 0, 1).unsqueeze(0)
        self.assertEqual(list(nchw.shape), [1, 3, 24, 24])
        self.assertEqual(nchw[0, 2, 4, 10].item(), rgb[4, 10, 2])
        aproximado = (rgb*np.array([.299, .587, .114])).sum(axis=-1)
        np.testing.assert_allclose(np.array(self.filtros["gris"])*255, aproximado, atol=.51, rtol=0)

    def test_05_normalizacion_solo_train(self):
        p = self.informe["preparacion"]
        esperado = self.train["pixeles"].astype(float)/255
        self.assertAlmostEqual(p["media"], esperado.mean(), places=14)
        self.assertAlmostEqual(p["escala"], esperado.std(), places=14)
        x = vision.tensor_imagenes(self.train["pixeles"], p)
        self.assertEqual(list(x.shape), [120, 1, 16, 16])
        self.assertAlmostEqual(x.mean().item(), 0., places=6)
        self.assertAlmostEqual(x.std(correction=0).item(), 1., places=6)

    def test_06_rechaza_intensidad_constante(self):
        with self.assertRaises(ValueError):
            vision.ajustar_normalizacion(np.zeros((2, 16, 16), dtype=np.uint8))

    def test_07_no_convierte_modo_ni_resolucion_en_silencio(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            ruta = datos/filas[0]["archivo"]
            Image.new("RGB", (16, 16)).save(ruta)
            filas[0]["sha256"] = hashlib.sha256(ruta.read_bytes()).hexdigest()
            self.escribir_csv(datos, "validacion", filas)
            with self.assertRaisesRegex(ValueError, "modo L"):
                vision.leer_particion(datos, "validacion")

    def test_08_rechaza_rutas_fuera_de_imagenes(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            filas[0]["archivo"] = "../ajeno.png"
            self.escribir_csv(datos, "validacion", filas)
            with self.assertRaisesRegex(ValueError, "dentro de imagenes"):
                vision.leer_particion(datos, "validacion")

    def test_09_detecta_cambio_de_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            (datos/filas[0]["archivo"]).write_bytes(b"no es el PNG original")
            with self.assertRaisesRegex(ValueError, "huella"):
                vision.leer_particion(datos, "validacion")

    def test_10_rechaza_duplicados_dentro_de_particion(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            filas[1]["archivo"], filas[1]["sha256"] = filas[0]["archivo"], filas[0]["sha256"]
            self.escribir_csv(datos, "validacion", filas)
            with self.assertRaisesRegex(ValueError, "Píxeles duplicados"):
                vision.leer_particion(datos, "validacion")

    def test_11_escenas_separadas(self):
        a = set(f["escena_id"] for f in self.train["filas"])
        b = set(f["escena_id"] for f in self.val["filas"])
        self.assertEqual((len(a), len(b), len(a & b)), (60, 30, 0))
        val = copy.deepcopy(self.val)
        val["filas"][0]["escena_id"] = self.train["filas"][0]["escena_id"]
        with self.assertRaisesRegex(ValueError, "escena_id"):
            vision.comprobar_separacion(self.train, val)

    def test_12_ids_separados(self):
        val = copy.deepcopy(self.val)
        val["filas"][0]["imagen_id"] = self.train["filas"][0]["imagen_id"]
        with self.assertRaisesRegex(ValueError, "imagen_id"):
            vision.comprobar_separacion(self.train, val)

    def test_13_pixeles_separados_aunque_se_renombre(self):
        val = copy.deepcopy(self.val)
        val["filas"][0]["sha256_pixeles"] = self.train["filas"][0]["sha256_pixeles"]
        with self.assertRaisesRegex(ValueError, "sha256_pixeles"):
            vision.comprobar_separacion(self.train, val)

    def test_14_clase_coherente_dentro_de_escena(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            filas[1]["clase"] = str((int(filas[0]["clase"])+1) % 3)
            self.escribir_csv(datos, "validacion", filas)
            with self.assertRaisesRegex(ValueError, "clases distintas"):
                vision.leer_particion(datos, "validacion")

    def test_15_desarrollo_no_necesita_prueba(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            for fila in self.filas_csv(datos, "prueba"):
                (datos/fila["archivo"]).unlink()
            (datos/"prueba.csv").unlink()
            informe = vision.ejecutar_experimento(datos, epocas=2)
            self.assertEqual(informe, self.corto)
            self.assertIsNone(informe["prueba"])

    def test_16_cierre_despues_de_seleccion(self):
        eventos = []
        leer, elegir = vision.leer_particion, vision.seleccionar
        def registrar_lectura(datos, nombre):
            eventos.append(nombre)
            return leer(datos, nombre)
        def registrar_seleccion(candidatos):
            eventos.append("seleccion")
            return elegir(candidatos)
        with patch.object(vision, "leer_particion", side_effect=registrar_lectura), patch.object(vision, "seleccionar", side_effect=registrar_seleccion):
            vision.ejecutar_experimento(evaluar_prueba=True, epocas=2)
        self.assertLess(eventos.index("seleccion"), eventos.index("prueba"))

    def test_17_etiquetas_prueba_no_cambian_modelo(self):
        a = vision.ejecutar_experimento(evaluar_prueba=True, epocas=2)
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "prueba")
            for fila in filas:
                fila["clase"] = str((int(fila["clase"])+1) % 3)
            self.escribir_csv(datos, "prueba", filas)
            b = vision.ejecutar_experimento(datos, evaluar_prueba=True, epocas=2)
        self.assertEqual(a["candidatos"], b["candidatos"])
        self.assertEqual(a["seleccionado"], b["seleccionado"])
        self.assertEqual([p["logits"] for p in a["prueba"]["predicciones"]], [p["logits"] for p in b["prueba"]["predicciones"]])

    def test_18_validacion_no_modifica_escala_ni_trayectoria(self):
        with tempfile.TemporaryDirectory() as tmp:
            datos = self.copiar_datos(tmp)
            filas = self.filas_csv(datos, "validacion")
            for fila in filas:
                fila["clase"] = str((int(fila["clase"])+1) % 3)
                ruta = datos/fila["archivo"]
                with Image.open(ruta) as imagen:
                    pixeles = 255-np.array(imagen)
                Image.fromarray(pixeles).save(ruta)
                fila["sha256"] = hashlib.sha256(ruta.read_bytes()).hexdigest()
            self.escribir_csv(datos, "validacion", filas)
            b = vision.ejecutar_experimento(datos, epocas=2)
        self.assertEqual(self.corto["preparacion"], b["preparacion"])
        for nombre in ("lineal", "cnn", "cnn_aumento"):
            self.assertEqual(self.corto["candidatos"][nombre]["estado_final"], b["candidatos"][nombre]["estado_final"])

    def test_19_parametros_y_presupuesto(self):
        for nombre, n in (("lineal", 771), ("cnn", 363), ("cnn_aumento", 363)):
            c = self.informe["candidatos"][nombre]
            self.assertEqual(c["n_parametros"], n)
            self.assertEqual(c["actualizaciones"], 300)
            self.assertEqual(len(c["historial"]), 13)

    def test_20_formas_intermedias(self):
        modelo = vision.Clasificador("cnn")
        x = torch.zeros(1, 1, 16, 16)
        formas = []
        for capa in modelo.red:
            x = capa(x)
            formas.append(list(x.shape))
        self.assertEqual(formas, [[1,4,16,16], [1,4,16,16], [1,4,8,8], [1,8,8,8], [1,8,8,8], [1,8,1,1], [1,8], [1,3]])

    def test_21_gradiente_de_filtro(self):
        x = torch.tensor([[[[1., 2.], [0., 3.]]]], dtype=torch.float64)
        k = torch.tensor([[[[1., 0.], [0., -1.]]]], dtype=torch.float64, requires_grad=True)
        s = nn.functional.conv2d(x, k)
        (.5*s.square().sum()).backward()
        self.assertEqual(s.item(), -2.)
        np.testing.assert_array_equal(k.grad.numpy(), -2*x.numpy())

    def test_22_entropia_estable_y_referencia_torch(self):
        s = [[1000., 999., 998.], [-1000., -999., -998.]]
        y = [0, 2]
        m, p = vision.metricas(s, y)
        esperado = nn.functional.cross_entropy(torch.tensor(s, dtype=torch.float64), torch.tensor(y)).item()
        self.assertAlmostEqual(m["ce"], esperado, places=12)
        np.testing.assert_allclose(p.sum(axis=1), [1,1], atol=1e-14)
        m2, p2 = vision.metricas(np.array(s)+10000, y)
        self.assertAlmostEqual(m["ce"], m2["ce"], places=12)

    def test_23_matriz_y_metricas_por_clase(self):
        m, _ = vision.metricas([[2,0,0], [0,2,0], [0,2,0], [0,2,0]], [0,0,1,2])
        self.assertEqual(m["matriz"], [[1,1,0], [0,1,0], [0,1,0]])
        self.assertEqual(m["exactitud"], .5)
        self.assertAlmostEqual(m["macro_f1"], (2/3+.5+0)/3)
        self.assertIsNone(m["por_clase"][2]["precision"])
        self.assertEqual(m["por_clase"][2]["recobrado"], 0.)

    def test_24_reflejo_conserva_original(self):
        x = torch.arange(40.).reshape(10,1,2,2)
        original = x.clone()
        aumentado, cantidad = vision.reflejar_lote(x, torch.Generator().manual_seed(2121))
        self.assertTrue(torch.equal(x, original))
        self.assertGreater(cantidad, 0)
        for antes, despues in zip(x, aumentado):
            self.assertTrue(torch.equal(antes, despues) or torch.equal(antes.flip(-1), despues))

    def test_25_reflejo_reproducible(self):
        x = torch.arange(80.).reshape(20,1,2,2)
        a, n = vision.reflejar_lote(x, torch.Generator().manual_seed(2121))
        b, m = vision.reflejar_lote(x, torch.Generator().manual_seed(2121))
        self.assertEqual(n, m)
        self.assertTrue(torch.equal(a, b))

    def test_26_evaluacion_sin_aumentos(self):
        c = self.informe["candidatos"]
        self.assertEqual(c["cnn"]["reflejos_entrenamiento"], 0)
        self.assertGreater(c["cnn_aumento"]["reflejos_entrenamiento"], 0)
        modelo = vision.restaurar("cnn_aumento", c["cnn_aumento"]["estado"])
        with patch.object(vision, "reflejar_lote", side_effect=AssertionError("Aumento durante evaluación")):
            vision.evaluar(self.val, self.informe["preparacion"], modelo)

    def test_27_repetibilidad(self):
        self.assertEqual(self.corto, vision.ejecutar_experimento(epocas=2))

    def test_28_mejor_estado_y_desempate(self):
        for nombre in ("lineal", "cnn", "cnn_aumento"):
            c = self.informe["candidatos"][nombre]
            mejor = c["historial"][0]
            for h in c["historial"][1:]:
                if h["ce_validacion"] < mejor["ce_validacion"]-1e-7:
                    mejor = h
            self.assertEqual(c["epoca_elegida"], mejor["epoca"])
            self.assertAlmostEqual(c["validacion"]["metricas"]["ce"], mejor["ce_validacion"], places=6)
        empate = {n: {"validacion": {"metricas": {"ce": v}}} for n, v in (("a", .5), ("b", .5-1e-8))}
        self.assertEqual(vision.seleccionar(empate), "a")

    def test_29_estado_clonado(self):
        modelo = vision.Clasificador("cnn")
        antes = vision.copiar_estado(modelo)
        valor = antes["red.0.weight"].clone()
        with torch.no_grad():
            modelo.red[0].weight.add_(1)
        self.assertTrue(torch.equal(antes["red.0.weight"], valor))

    def test_30_recarga_exacta_en_cpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"modelo.pt"
            vision.guardar_modelo(self.informe, ruta)
            modelo, prep = vision.cargar_modelo(ruta)
            self.assertFalse(modelo.training)
            self.assertTrue(all(p.device.type == "cpu" for p in modelo.parameters()))
            self.assertEqual(vision.evaluar(self.val, prep, modelo), self.informe["candidatos"][self.informe["seleccionado"]]["validacion"])

    def test_31_rechaza_artefactos_incompatibles(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp)/"modelo.pt"
            vision.guardar_modelo(self.informe, ruta)
            original = torch.load(ruta, weights_only=True)
            cambios = [lambda d: d.update(clases=["vertical", "horizontal", "diagonal"]),
                       lambda d: d["preparacion"].update(forma_chw=[3,16,16]),
                       lambda d: d["preparacion"].update(escala=0),
                       lambda d: d["state_dict"]["red.0.weight"].fill_(float("nan"))]
            for cambio in cambios:
                contenido = copy.deepcopy(original)
                cambio(contenido)
                torch.save(contenido, ruta)
                with self.assertRaises(ValueError):
                    vision.cargar_modelo(ruta)

    def test_32_exportacion_correspondencia_y_no_sobrescritura(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"salida"
            self.assertEqual(vision.exportar(self.informe, salida), 0.)
            self.assertEqual(json.loads((salida/"informe.json").read_text()), self.informe)
            self.assertFalse((salida/"predicciones_prueba.csv").exists())
            with (salida/"predicciones_validacion.csv").open() as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 240)
            for f in filas:
                p = next(p for p in self.informe["candidatos"][f["candidato"]]["validacion"]["predicciones"] if p["imagen_id"] == f["imagen_id"])
                self.assertEqual(float(f["p_diagonal"]), p["probabilidades"][2])
            with self.assertRaises(FileExistsError):
                vision.exportar(self.informe, salida)

    def test_33_regeneracion_de_manifiestos_y_pixeles(self):
        spec = importlib.util.spec_from_file_location("generador_u21", UNIDAD/"datos/generar_datos.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp)/"nuevos"
            modulo.generar(salida)
            for ruta in salida.rglob("*"):
                if ruta.is_file():
                    self.assertEqual(ruta.read_bytes(), (UNIDAD/"datos"/ruta.relative_to(salida)).read_bytes())

    def test_34_curvas_y_matriz_publicadas(self):
        publicado = json.loads((UNIDAD/"recursos/trazos/informe.json").read_text())
        self.assertEqual(publicado["fuentes"], self.informe["fuentes"])
        self.assertEqual(publicado["seleccionado"], self.informe["seleccionado"])
        for n in vision.CANDIDATOS:
            self.assertAlmostEqual(publicado["candidatos"][n]["validacion"]["metricas"]["ce"], self.informe["candidatos"][n]["validacion"]["metricas"]["ce"], places=5)
        figuras = crear_figuras(self.informe)
        try:
            for linea, n in zip(figuras["aprendizaje_matriz"].axes[1].lines, vision.CANDIDATOS[1:]):
                np.testing.assert_array_equal(linea.get_ydata(), [h["ce_validacion"] for h in self.informe["candidatos"][n]["historial"]])
            np.testing.assert_array_equal(figuras["aprendizaje_matriz"].axes[2].images[0].get_array(), self.informe["candidatos"][self.informe["seleccionado"]]["validacion"]["metricas"]["matriz"])
        finally:
            for f in figuras.values():
                plt.close(f)

    def test_35_galeria_conserva_pixeles_y_ordena_dificultad(self):
        casos = casos_dificiles(self.informe)
        valores = [p["probabilidades"][p["real"]] for p in casos]
        self.assertEqual(valores, sorted(valores))
        pixeles = {f["imagen_id"]: f["pixeles"] for f in self.informe["casos_validacion"]}
        figuras = crear_figuras(self.informe)
        try:
            for ax, caso in zip(figuras["casos_dificiles"].axes, casos):
                np.testing.assert_array_equal(ax.images[0].get_array(), pixeles[caso["imagen_id"]])
                self.assertEqual(ax.images[0].get_clim(), (0,255))
        finally:
            for f in figuras.values():
                plt.close(f)

    def test_36_figura_rgb_y_respuestas(self):
        figuras = crear_figuras(self.filtros)
        try:
            fig = figuras["pixeles_filtros"]
            np.testing.assert_array_equal(fig.axes[0].images[0].get_array(), self.filtros["rgb_hwc"])
            sobel = np.array(self.filtros["sobel_x"])
            self.assertEqual(sobel.shape, (22,22))
            self.assertLess(sobel.min(), 0)
            self.assertGreater(sobel.max(), 0)
        finally:
            plt.close(figuras["pixeles_filtros"])


if __name__ == "__main__":
    unittest.main()

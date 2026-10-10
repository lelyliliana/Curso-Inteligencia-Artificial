"""Pruebas matemáticas, particiones, gradientes, entradas y artefactos."""

from collections import Counter
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch
from torch import nn

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import adaptacion as a
import multimodal as m
from comun import cargar, comprobar_familias, configurar, guardar, huella, restaurar_estado

configurar()


def png(modo="L", size=(20, 16), valor=128):
    buffer = io.BytesIO()
    Image.new(modo, size, color=valor).save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


class LoRATest(unittest.TestCase):
    def test_producto_manual_independiente(self):
        base = nn.Linear(3, 2, bias=False, dtype=torch.float64)
        capa = a.LinealLoRA(base, 1, 1)
        with torch.no_grad():
            base.weight.copy_(torch.tensor([[1, 0, -1], [0, 2, 1]]))
            capa.A.copy_(torch.tensor([[1, -1, 0]]))
            capa.B.copy_(torch.tensor([[.5], [-.5]]))
        self.assertEqual(capa(torch.tensor([2., 1., 3.], dtype=torch.float64)).tolist(), [-.5, 4.5])

    def test_inicializacion_preserva_base(self):
        capa = a.LinealLoRA(nn.Linear(5, 4), 2, 2)
        x = torch.randn(2, 3, 5)
        self.assertTrue(torch.equal(capa(x), capa.base(x)))
        self.assertEqual(int(torch.count_nonzero(capa.B)), 0)
        self.assertGreater(int(torch.count_nonzero(capa.A)), 0)

    def test_gradientes_iniciales(self):
        capa = a.LinealLoRA(nn.Linear(3, 2), 1, 1)
        capa(torch.ones(4, 3)).sum().backward()
        self.assertTrue(all(p.grad is None for p in capa.base.parameters()))
        self.assertEqual(int(torch.count_nonzero(capa.A.grad)), 0)
        self.assertGreater(int(torch.count_nonzero(capa.B.grad)), 0)

    def test_gradiente_b_con_diferencias_finitas(self):
        capa = a.LinealLoRA(nn.Linear(3, 2, dtype=torch.float64), 1, 2)
        x = torch.tensor([[2., 1., -1.]], dtype=torch.float64)
        capa(x).square().sum().backward()
        analitico = float(capa.B.grad[0, 0])
        with torch.no_grad():
            capa.B[0, 0] = 1e-6
            mas = float(capa(x).square().sum())
            capa.B[0, 0] = -1e-6
            menos = float(capa(x).square().sum())
        self.assertAlmostEqual(analitico, (mas - menos) / 2e-6, places=7)

    def test_fusion_y_sesgo(self):
        capa = a.LinealLoRA(nn.Linear(7, 4, dtype=torch.float64), 2, 4)
        with torch.no_grad():
            capa.B.normal_()
        x = torch.randn(3, 7, dtype=torch.float64)
        self.assertTrue(torch.allclose(capa(x), capa.fusionada()(x), atol=1e-12, rtol=0))
        self.assertTrue(torch.equal(capa.base.bias, capa.fusionada().bias))

    def test_fusion_no_muta_base(self):
        capa = a.LinealLoRA(nn.Linear(3, 2), 1, 1)
        original = capa.base.weight.detach().clone()
        with torch.no_grad():
            capa.B.fill_(2)
        fusion = capa.fusionada()
        self.assertTrue(torch.equal(original, capa.base.weight))
        self.assertFalse(torch.equal(original, fusion.weight))

    def test_desactivar_recupera_base(self):
        capa = a.LinealLoRA(nn.Linear(3, 2), 1, 1)
        with torch.no_grad():
            capa.B.fill_(1)
        capa.activo = False
        x = torch.randn(2, 3)
        self.assertTrue(torch.equal(capa(x), capa.base(x)))

    def test_rangos_y_alpha_invalidos(self):
        for rango in (0, -1, 4, True, 1.5):
            with self.assertRaises(ValueError):
                a.LinealLoRA(nn.Linear(3, 2), rango, 1)
        for alpha in (0, -1, True, float("nan")):
            with self.assertRaises(ValueError):
                a.LinealLoRA(nn.Linear(3, 2), 1, alpha)

    def test_parametros_del_transformer(self):
        modelo, _ = a.modelo_inicial("lora")
        entrenables = {n: p.numel() for n, p in modelo.named_parameters() if p.requires_grad}
        self.assertEqual(entrenables, {"salida.A": 64, "salida.B": 52})
        self.assertEqual(sum(p.numel() for p in modelo.parameters()), 11182)
        completo, _ = a.modelo_inicial("completo")
        self.assertEqual(sum(p.numel() for p in completo.parameters() if p.requires_grad), 11066)

    def test_pasos_actualizan_solo_adaptacion(self):
        train = a.previo.leer(UNIDAD / "datos/adaptacion/entrenamiento.json")
        val = a.previo.leer(UNIDAD / "datos/adaptacion/validacion.json")
        modelo, _, _ = a.adaptar("lora", train, val, epocas=2)
        base, _ = a.modelo_inicial("base")
        for k, v in base.state_dict().items():
            destino = k.replace("salida.", "salida.base.") if k.startswith("salida.") else k
            self.assertTrue(torch.equal(v, modelo.state_dict()[destino]))
        self.assertGreater(int(torch.count_nonzero(modelo.salida.B)), 0)


class DatosTest(unittest.TestCase):
    def test_regeneracion_identica(self):
        spec = importlib.util.spec_from_file_location("datos_u31", UNIDAD / "datos/generar_datos.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        with tempfile.TemporaryDirectory() as temporal:
            modulo.generar(temporal)
            for f in Path(temporal).rglob("*"):
                if f.is_file():
                    self.assertEqual(f.read_bytes(), (UNIDAD / "datos" / f.relative_to(temporal)).read_bytes())

    def test_particiones_adaptacion(self):
        grupos = [a.previo.leer(UNIDAD / f"datos/adaptacion/{fase}.json") for fase in ("entrenamiento", "validacion", "prueba")]
        comprobar_familias(*grupos)
        self.assertEqual([len(g) for g in grupos], [48, 24, 24])
        for g in grupos:
            self.assertTrue(all(v == 2 for v in Counter(f["familia"] for f in g).values()))

    def test_particiones_multimodal(self):
        grupos = [m.leer(f) for f in ("entrenamiento", "validacion", "prueba")]
        comprobar_familias(*grupos)
        self.assertEqual([len(g) for g in grupos], [96, 48, 48])
        imagenes = [{f["imagen"] for f in g} for g in grupos]
        for i in range(3):
            self.assertEqual(len(imagenes[i]), [24, 12, 12][i])
            for j in range(i):
                self.assertFalse(imagenes[i] & imagenes[j])

    def test_detector_de_cruces_y_duplicados(self):
        fila = {"id": "a", "familia": "f"}
        for grupos in (([fila], [fila]), ([fila, fila],), ([],)):
            with self.assertRaises(ValueError):
                comprobar_familias(*grupos)

    def test_vocabulario_heredado_sin_unk(self):
        _, vocab = a.modelo_inicial("base")
        for fase in ("entrenamiento", "validacion", "prueba"):
            for f in a.previo.leer(UNIDAD / f"datos/adaptacion/{fase}.json"):
                for campo in ("prefijo", "continuacion"):
                    self.assertNotIn(a.previo.UNK, a.previo.codificar(f[campo], vocab))

    def test_nueva_convencion_distinta_de_original(self):
        for fase in ("entrenamiento", "validacion", "prueba"):
            for f in a.previo.leer(UNIDAD / f"datos/adaptacion/{fase}.json"):
                self.assertEqual(a.regla(f), f["continuacion"])
                self.assertNotEqual(a.regla(f, anterior=True), f["continuacion"])
        self.assertEqual(set(a.CODIGOS), set(a.CODIGOS.values()))

    def test_preexposicion_no_se_oculta(self):
        base_train = cargar(UNIDAD.parent / "unidad25-transformers-generativos/datos/entrenamiento.json")
        cierre = cargar(UNIDAD / "datos/adaptacion/prueba.json")
        self.assertTrue({f["prefijo"] for f in base_train} & {f["prefijo"] for f in cierre})

    def test_balance_y_ambiguedad_unimodal(self):
        for fase in ("entrenamiento", "validacion", "prueba"):
            filas = m.leer(fase)
            for texto in {f["texto"] for f in filas}:
                y = [f["etiqueta"] for f in filas if f["texto"] == texto]
                self.assertEqual(sum(y) * 2, len(y))
            maximo_vision = sum(max(Counter(f["etiqueta"] for f in filas if f["imagen"] == img).values())
                                 for img in {f["imagen"] for f in filas})
            self.assertEqual(maximo_vision / len(filas), .75)

    def test_referencia_visual_desde_pixeles(self):
        for fase in ("entrenamiento", "validacion", "prueba"):
            filas = m.leer(fase)
            self.assertEqual(m.referencia(filas), {"correctas": len(filas), "total": len(filas)})


class MultimodalTest(unittest.TestCase):
    def test_medias_imagen_uniforme(self):
        self.assertTrue(np.allclose(m.rasgos_imagen(png(valor=128)), [128/255, 128/255], atol=1e-6))

    def test_regiones_independientes(self):
        x = np.zeros((16, 20), dtype=np.uint8)
        x[5:11, 2:7] = 255
        b = io.BytesIO()
        Image.fromarray(x).save(b, format="PNG")
        b.seek(0)
        np.testing.assert_array_equal(m.rasgos_imagen(b), [1, 0])

    def test_modo_tamano_formato(self):
        for archivo in (png("RGB"), png(size=(16, 20))):
            with self.assertRaises(ValueError):
                m.rasgos_imagen(archivo)
        with self.assertRaises(ValueError):
            m.rasgos_imagen(None)

    def test_texto_equivalente(self):
        for lado, valor in (("izquierda", [1, 0]), ("derecha", [0, 1])):
            for verbo in ("estado", "consulta"):
                np.testing.assert_array_equal(m.rasgos_texto(f"{verbo} {lado}"), valor)

    def test_texto_ambiguo_o_desconocido(self):
        for texto in (None, "", "izquierda", "estado izquierda\n", "no izquierda, derecha", "estado arriba"):
            with self.assertRaises(ValueError):
                m.rasgos_texto(texto)

    def test_ablacion_sin_leer_modalidad_excluida(self):
        with patch.object(m, "rasgos_imagen", side_effect=AssertionError("No leer imagen")):
            np.testing.assert_array_equal(m.rasgos(None, "estado derecha", "texto"), [0, 1])
        with patch.object(m, "rasgos_texto", side_effect=AssertionError("No leer texto")):
            self.assertEqual(len(m.rasgos(png(), None, "vision")), 2)

    def test_orden_y_formas(self):
        f = m.rasgos(png(valor=255), "estado derecha", "fusion")
        np.testing.assert_array_equal(f, [1, 1, 0, 1])
        for modo, dim, n in (("vision", 2, 42), ("texto", 2, 42), ("fusion", 4, 58)):
            modelo = m.crear(modo)
            self.assertEqual(tuple(modelo(torch.zeros(3, dim)).shape), (3, 2))
            self.assertEqual(sum(p.numel() for p in modelo.parameters()), n)

    def test_etiquetas_no_entran_en_rasgos(self):
        filas = m.leer("validacion")[:4]
        cambiadas = [{**f, "etiqueta": 1 - f["etiqueta"]} for f in filas]
        for modo in m.MODOS:
            self.assertTrue(torch.equal(m.preparar(filas, modo)[0], m.preparar(cambiadas, modo)[0]))

    def test_rechazo_antes_del_modelo(self):
        modelo = m.crear("fusion")
        with patch.object(modelo, "forward", side_effect=AssertionError("No clasificar")):
            for ruta, texto in ((None, "estado izquierda"), (png(), None), (png("RGB"), "estado izquierda")):
                self.assertEqual(m.predecir(modelo, "fusion", ruta, texto)["estado"], "rechazada")

    def test_matriz_y_ce_con_referencia_independiente(self):
        modelo = m.crear("fusion")
        with torch.no_grad():
            for p in modelo.parameters():
                p.zero_()
        filas = m.leer("validacion")
        r = m.evaluar(modelo, "fusion", filas)
        self.assertEqual(r["matriz"], [[24, 0], [24, 0]])
        self.assertAlmostEqual(r["ce"], np.log(2), places=6)


class PersistenciaTest(unittest.TestCase):
    def test_adapter_solo_a_b_y_base_identificada(self):
        obj = cargar(UNIDAD / "recursos/adaptacion/lora.json")
        self.assertEqual(set(obj["estado"]), {"A", "B"})
        self.assertEqual(obj["base_sha256"], huella(a.BASE))

    def test_rechaza_otra_base_y_vocabulario(self):
        obj = cargar(UNIDAD / "recursos/adaptacion/lora.json")
        for campo, valor in (("base_sha256", "otra"), ("vocabulario", []), ("config", {}), ("fuentes", {})):
            with self.assertRaises(ValueError):
                a.restaurar(obj | {campo: valor})

    def test_rechaza_adapter_nan_o_forma(self):
        obj = cargar(UNIDAD / "recursos/adaptacion/lora.json")
        for valor in ([[float("nan")]], [[0]], {}):
            copia = deepcopy(obj)
            copia["estado"]["A"] = valor
            with self.assertRaises((ValueError, TypeError)):
                a.restaurar(copia)

    def test_estado_completo_y_base_recargan(self):
        filas = a.previo.leer(UNIDAD / "datos/adaptacion/validacion.json")
        informe = cargar(UNIDAD / "recursos/adaptacion/informe.json")
        for metodo in a.METODOS:
            modelo, vocab = a.restaurar(cargar(UNIDAD / f"recursos/adaptacion/{metodo}.json"))
            self.assertEqual(a.evaluar(modelo, vocab, filas), informe["candidatos"][metodo]["validacion"])

    def test_multimodal_config_fuentes_y_estado(self):
        obj = cargar(UNIDAD / "recursos/multimodal/modelo.json")
        for campo, valor in (("config", {}), ("fuentes", {}), ("estado", {})):
            with self.assertRaises(ValueError):
                m.restaurar(obj | {campo: valor})

    def test_modos_recargados_conservan_predicciones(self):
        filas = m.leer("validacion")
        informe = cargar(UNIDAD / "recursos/multimodal/informe.json")
        for modo in m.MODOS:
            modelo = m.restaurar(cargar(UNIDAD / f"recursos/multimodal/{modo}.json"))
            self.assertEqual(m.evaluar(modelo, modo, filas), informe["candidatos"][modo]["validacion"])

    def test_guardado_json_y_no_finitos(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "estado.json"
            guardar(ruta, {"a": [1, 2]})
            self.assertEqual(cargar(ruta), {"a": [1, 2]})
            with self.assertRaises(ValueError):
                guardar(ruta, {"a": float("nan")})

    def test_restaurar_no_admite_claves_extra(self):
        modelo = m.crear("fusion")
        with self.assertRaises(ValueError):
            restaurar_estado(modelo, {"extra": []})


class ProtocoloYArtefactosTest(unittest.TestCase):
    def test_seleccion_adaptacion_criterio_prefijado(self):
        r = cargar(UNIDAD / "recursos/adaptacion/informe.json")
        self.assertEqual(a.seleccionar(r["candidatos"]), r["seleccionado"])
        c = deepcopy(r["candidatos"])
        c["lora"]["validacion"]["n_exactas"] = 0
        self.assertEqual(a.seleccionar(c), "completo")

    def test_epocas_minimizan_ce_sin_prueba(self):
        for tipo in ("adaptacion", "multimodal"):
            r = cargar(UNIDAD / f"recursos/{tipo}/informe.json")
            self.assertIsNone(r["prueba"])
            for c in r["candidatos"].values():
                h = c["entrenamiento"]
                if h["curva"]:
                    self.assertEqual(h["epoca"], min(h["curva"], key=lambda e: e["ce_val"])["epoca"])

    def test_entrenamiento_no_lee_prueba(self):
        for fuentes in (a.fuentes(), m.fuentes()):
            self.assertFalse(any("prueba" in k for k in fuentes))
        self.assertNotIn("prueba", a.desarrollar.__code__.co_names)

    def test_cierre_adaptacion_sin_entrenar(self):
        with patch.object(a, "adaptar", side_effect=AssertionError("No entrenar")):
            r = a.cerrar(UNIDAD / "recursos/adaptacion/modelo.json")
        self.assertEqual(r, cargar(UNIDAD / "recursos/adaptacion/cierre.json"))
        self.assertEqual(r["evaluacion"]["n_exactas"], 24)

    def test_cierre_multimodal_sin_entrenar(self):
        with patch.object(m, "entrenar", side_effect=AssertionError("No entrenar")):
            r = m.cerrar(UNIDAD / "recursos/multimodal/modelo.json")
        self.assertEqual(r, cargar(UNIDAD / "recursos/multimodal/cierre.json"))
        self.assertEqual(r["evaluacion"]["correctas"], 48)

    def test_diagnosticos_modalidades(self):
        d = cargar(UNIDAD / "recursos/multimodal/cierre.json")["diagnosticos"]
        for clave in ("imagen_ausente", "texto_ausente", "texto_ambiguo", "imagen_incompatible"):
            self.assertEqual(d[clave]["estado"], "rechazada")
            self.assertIsNone(d[clave]["clase"])
        self.assertEqual((d["izquierda"]["clase"], d["derecha"]["clase"]), ("apagada", "encendida"))

    def test_fusion_y_base_en_informe(self):
        d = cargar(UNIDAD / "recursos/adaptacion/informe.json")["candidatos"]["lora"]["diagnostico"]
        self.assertTrue(d["base_intacta"])
        self.assertTrue(d["desactivado_igual_base"])
        self.assertLessEqual(d["error_max_fusion"], 1e-5)

    def test_manual_conservado(self):
        r = cargar(UNIDAD / "recursos/manual/lora_manual.json")
        self.assertEqual(r["salida"], [-.5, 4.5])
        self.assertEqual(r["parametros_adaptacion"], 5)


if __name__ == "__main__":
    unittest.main()

"""Causalidad, referencias independientes, aceptación, contrato y traspaso del proyecto."""

import copy
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.metrics import mean_absolute_error

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ejemplos"))
import contrato
import proyecto
import servicio


def modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


generador = modulo("generador35", RAIZ / "datos/generar_datos.py")
demo = modulo("demo35", RAIZ / "ejemplos/02_probar_entrega.py")
manual = modulo("manual35", RAIZ / "soluciones/03_aceptacion_a_mano.py")
PROTOCOLO = proyecto.leer(RAIZ / "datos/protocolo.json")
MODELO = RAIZ / "recursos/modelo.json"


def datos(fase):
    return proyecto.leer(RAIZ / "datos" / f"{fase}.json")


class ContratoTemporal(unittest.TestCase):
    def validar(self, cambios=None):
        return contrato.validar({**demo.CONSULTA, **(cambios or {})}, PROTOCOLO["contrato"])

    def rechaza(self, codigo, cambios):
        with self.assertRaises(contrato.ErrorEntrada) as ctx:
            self.validar(cambios)
        self.assertEqual(ctx.exception.codigo, codigo)

    def test_horizonte_desde_medicion(self):
        e = self.validar()
        self.assertEqual(e["objetivo"] - e["medido"], timedelta(hours=1))
        self.assertEqual(e["minutos_hasta_objetivo"], 55)

    def test_offset_equivalente(self):
        e = self.validar({"medido_en": "2026-10-20T15:00:00+00:00"})
        self.assertEqual(e, self.validar())

    def test_fechas_invalidas(self):
        for valor in (None, "ayer", "2026-10-20T10:00:00", "9999-12-31T23:00:00-05:00", "x" * 41):
            with self.subTest(valor=valor):
                self.rechaza("fecha_invalida", {"medido_en": valor})

    def test_hora_alineada(self):
        self.rechaza("hora_no_alineada", {"medido_en": "2026-10-20T10:00:01-05:00"})

    def test_lectura_tardia_no_se_usa(self):
        self.rechaza("lectura_no_disponible", {"recibido_en": "2026-10-20T10:06:00-05:00"})

    def test_orden_temporal(self):
        for campo in ("recibido_en", "decidir_en"):
            self.rechaza("orden_temporal", {campo: "2026-10-20T09:59:00-05:00"})

    def test_limite_edad_inclusivo(self):
        self.assertEqual(self.validar({"decidir_en": "2026-10-20T10:15:00-05:00"})["minutos_hasta_objetivo"], 45)
        self.rechaza("lectura_caducada", {"decidir_en": "2026-10-20T10:15:01-05:00"})

    def test_potencia_y_tipos(self):
        for valor in (None, "42", True, -1, 201, float("nan"), float("inf")):
            with self.subTest(valor=valor):
                self.rechaza("potencia_invalida", {"potencia_kw": valor})
        self.assertEqual(self.validar({"potencia_kw": 0})["potencia_kw"], 0)

    def test_campos_exactos(self):
        for valor in (None, [], {}, {**demo.CONSULTA, "objetivo_kw": 44}):
            with self.assertRaises(contrato.ErrorEntrada) as ctx:
                contrato.validar(valor, PROTOCOLO["contrato"])
            self.assertEqual(ctx.exception.codigo, "campos_invalidos")

    def test_delta_calendario_fin_semana(self):
        e = self.validar({"medido_en": "2026-10-23T23:00:00-05:00", "recibido_en": "2026-10-23T23:01:00-05:00",
                          "decidir_en": "2026-10-23T23:05:00-05:00"})
        self.assertEqual(contrato.incrementos(e)[2], -1)


class DatosYModelos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = datos("entrenamiento")
        cls.val = datos("validacion")
        cls.modelos = proyecto.ajustar(cls.train, PROTOCOLO)

    def test_regeneracion_identica(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            for fase in ("entrenamiento", "validacion", "prueba"):
                self.assertEqual((Path(d) / f"{fase}.json").read_bytes(), (RAIZ / "datos" / f"{fase}.json").read_bytes())

    def test_particiones_y_disponibilidad_etiquetas(self):
        grupos = [self.train, self.val, datos("prueba")]
        self.assertEqual(list(map(len, grupos)), [720, 240, 240])
        ids = [f["id"] for g in grupos for f in g]
        self.assertEqual(len(set(ids)), 1200)
        for anterior, siguiente in zip(grupos, grupos[1:]):
            self.assertLessEqual(anterior[-1]["instante_objetivo"], siguiente[0]["entrada"]["decidir_en"])

    def test_mismos_rechazos_todos_los_candidatos(self):
        resultados = [proyecto.evaluar(m, self.val, PROTOCOLO) for m in self.modelos.values()]
        for r in resultados:
            self.assertEqual(r["admitidas"], 236)
            self.assertEqual(len(r["rechazadas"]), 4)
            self.assertEqual([c["id"] for c in r["casos"]], [c["id"] for c in resultados[0]["casos"]])
            self.assertEqual(r["rechazadas"], resultados[0]["rechazadas"])

    def test_rechazos_no_predicen_ni_leen_etiqueta(self):
        fila = copy.deepcopy(self.val[21])  # PF0742: recepción posterior a la decisión.
        del fila["objetivo_kw"]
        with patch.object(proyecto, "predecir", side_effect=AssertionError("No inferir")):
            r = proyecto.evaluar(self.modelos["persistencia"], [fila], PROTOCOLO)
        self.assertEqual(r["admitidas"], 0)
        self.assertIsNone(r["mae_kw"])

    def test_incremento_ecuaciones_normales(self):
        pares, _ = proyecto.preparar(self.train, PROTOCOLO)
        x = np.asarray([contrato.incrementos(e) for _, e in pares])
        y = np.asarray([f["objetivo_kw"] - e["potencia_kw"] for f, e in pares])
        z = (x - x.mean(axis=0)) / x.std(axis=0)
        a = np.column_stack([np.ones(len(z)), z])
        ref = np.linalg.solve(a.T @ a + np.diag([0, 1, 1, 1]), a.T @ y)
        m = self.modelos["ridge_incremento"]
        np.testing.assert_allclose([m["intercepto"], *m["coef"]], ref, atol=1e-12)

    def test_traslacion_nivel_sin_reentrenar(self):
        m = self.modelos["ridge_incremento"]
        a = contrato.validar(demo.CONSULTA, PROTOCOLO["contrato"])
        b = contrato.validar({**demo.CONSULTA, "potencia_kw": 50}, PROTOCOLO["contrato"])
        self.assertAlmostEqual(proyecto.predecir(m, b)["prediccion_kw"] - proyecto.predecir(m, a)["prediccion_kw"], 8)

    def test_persistencia_exacta_y_codigo_u34_reutilizado(self):
        e = contrato.validar(demo.CONSULTA, PROTOCOLO["contrato"])
        self.assertEqual(proyecto.predecir(self.modelos["persistencia"], e)["prediccion_kw"], 42)
        propia = proyecto.predecir(self.modelos["ridge_nivel"], e)["prediccion_kw"]
        anterior = proyecto.energia.predecir(self.modelos["ridge_nivel"], contrato.nivel(e))["prediccion_kw"]
        self.assertEqual(propia, anterior)

    def test_etiquetas_no_cambian_predicciones(self):
        otras = copy.deepcopy(self.val)
        for f in otras:
            f["objetivo_kw"] += 500
        m = self.modelos["ridge_incremento"]
        a, b = proyecto.evaluar(m, self.val, PROTOCOLO), proyecto.evaluar(m, otras, PROTOCOLO)
        self.assertEqual([c["prediccion_kw"] for c in a["casos"]], [c["prediccion_kw"] for c in b["casos"]])
        self.assertNotEqual(a["mae_kw"], b["mae_kw"])

    def test_mae_independiente_y_cobertura(self):
        r = proyecto.evaluar(self.modelos["ridge_incremento"], self.val, PROTOCOLO)
        esperado = mean_absolute_error([c["objetivo_kw"] for c in r["casos"]], [c["prediccion_kw"] for c in r["casos"]])
        self.assertAlmostEqual(r["mae_kw"], esperado)
        self.assertAlmostEqual(r["cobertura"], 236 / 240)

    def test_aceptacion_no_oculta_baja_cobertura(self):
        r = {"mae_kw": 1.5, "cobertura": .94}
        a = proyecto.aceptacion(r, {"mae_kw": 2}, PROTOCOLO)
        self.assertEqual(a["reduccion_relativa_mae"], .25)
        self.assertFalse(a["cumple_criterio_didactico"])
        self.assertFalse(a["autoriza_uso_real"])
        self.assertEqual(manual.calcular()["condiciones"], a["condiciones"])

    def test_aceptacion_sin_casos_o_referencia_perfecta(self):
        for mae, base, cobertura in ((None, None, None), (0, 0, 1)):
            a = proyecto.aceptacion({"mae_kw": mae, "cobertura": cobertura}, {"mae_kw": base}, PROTOCOLO)
            self.assertIsNone(a["reduccion_relativa_mae"])
            self.assertFalse(a["cumple_criterio_didactico"])


class VersionYServicio(unittest.TestCase):
    def test_desarrollo_no_abre_prueba(self):
        original = proyecto.leer
        def leer(ruta):
            if Path(ruta).name == "prueba.json":
                raise AssertionError("cierre abierto")
            return original(ruta)
        with patch.object(proyecto, "leer", side_effect=leer):
            modelo, informe = proyecto.desarrollar()
        self.assertEqual(modelo, proyecto.cargar(MODELO))
        self.assertEqual(informe, proyecto.leer(RAIZ / "recursos/validacion.json"))

    def test_cierre_sin_ajuste_ni_seleccion(self):
        with patch.object(proyecto, "ajustar", side_effect=AssertionError("ajuste")), \
             patch.object(proyecto, "desarrollar", side_effect=AssertionError("selección")):
            r = proyecto.cerrar(MODELO)
        self.assertEqual(r, proyecto.leer(RAIZ / "recursos/prueba.json"))
        self.assertEqual([c["id"] for c in r["resultado"]["casos"]], [c["id"] for c in r["referencia"]["casos"]])

    def test_huella_modelo_y_fuentes(self):
        m = proyecto.cargar(MODELO)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "modelo.json"
            m["modelo"]["intercepto"] += 1
            proyecto.guardar(p, m)
            with self.assertRaisesRegex(ValueError, "huella"):
                proyecto.cargar(p)
        with patch.object(proyecto, "fuentes", return_value={}):
            with self.assertRaisesRegex(ValueError, "fuentes"):
                proyecto.cargar(MODELO)

    def test_modelo_se_carga_una_vez(self):
        with patch.object(servicio, "cargar", wraps=proyecto.cargar) as carga:
            s = servicio.Servicio(MODELO)
            s.responder(demo.codificar(demo.CONSULTA))
            s.responder(demo.codificar(demo.CONSULTA))
        self.assertEqual(carga.call_count, 1)

    def test_ids_generados_y_correlacion(self):
        s = servicio.Servicio(MODELO)
        a, b = [s.responder(demo.codificar(demo.CONSULTA)) for _ in range(2)]
        self.assertNotEqual(a["solicitud_id"], b["solicitud_id"])
        self.assertEqual([e["solicitud_id"] for e in s.eventos], [a["solicitud_id"], b["solicitud_id"]])

    def test_registro_sin_entrada_ni_prediccion(self):
        s = servicio.Servicio(MODELO)
        s.responder(demo.codificar(demo.CONSULTA))
        self.assertEqual(set(s.eventos[-1]), {"solicitud_id", "modelo_sha256", "politica", "estado", "codigo", "duracion_ms"})
        self.assertNotIn("potencia_kw", json.dumps(list(s.eventos)))

    def test_historial_acotado_contador_acumulado(self):
        s = servicio.Servicio(MODELO)
        self.assertIsNone(s.metricas()["fraccion_rechazada"])
        for _ in range(70):
            s.responder(b"{")
        self.assertEqual(len(s.eventos), 64)
        self.assertEqual(s.metricas()["solicitudes"], 70)
        self.assertEqual(s.metricas()["fraccion_rechazada"], 1)

    def test_json_invalido_repetido_no_finito_utf8(self):
        for contenido in (b"{", b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff'):
            with self.assertRaises(contrato.ErrorEntrada) as ctx:
                servicio.decodificar(contenido)
            self.assertEqual(ctx.exception.codigo, "json_invalido")

    def test_limite_de_bytes(self):
        self.assertEqual(servicio.decodificar(b"{}" + b" " * 16382), {})
        with self.assertRaises(contrato.ErrorEntrada) as ctx:
            servicio.decodificar(b" " * 16385)
        self.assertEqual(ctx.exception.codigo, "tamano_invalido")

    def test_rechazo_no_infiere(self):
        s = servicio.Servicio(MODELO)
        with patch.object(servicio, "predecir", side_effect=AssertionError("No inferir")):
            r = s.responder(demo.codificar({**demo.CONSULTA, "potencia_kw": -1}))
        self.assertEqual(r["codigo"], "potencia_invalida")
        self.assertNotIn("resultado", r)

    def test_error_interno_degrada_sin_detalle_privado(self):
        s = servicio.Servicio(MODELO)
        with patch.object(servicio, "predecir", side_effect=RuntimeError("dato privado")):
            r = s.responder(demo.codificar(demo.CONSULTA))
        self.assertEqual(r["codigo"], "error_interno")
        self.assertFalse(s.activo)
        self.assertNotIn("dato privado", json.dumps(r))
        siguiente = s.responder(demo.codificar(demo.CONSULTA))
        self.assertEqual(siguiente["codigo"], "mantenimiento")

    def test_referencia_explicita_sin_cambiar_modelo(self):
        original = MODELO.read_bytes()
        s = servicio.Servicio(MODELO, referencia=True)
        r = s.responder(demo.codificar(demo.CONSULTA))
        self.assertEqual(r["politica"], "persistencia")
        self.assertEqual(r["resultado"]["prediccion_kw"], 42)
        self.assertEqual(MODELO.read_bytes(), original)

    def test_recuperacion_recreando_servicio(self):
        s = servicio.Servicio(MODELO)
        s.activo = False
        self.assertEqual(s.responder(demo.codificar(demo.CONSULTA))["codigo"], "mantenimiento")
        nuevo = servicio.Servicio(MODELO)
        self.assertIn("resultado", nuevo.responder(demo.codificar(demo.CONSULTA)))

    def test_captura_funcional_sin_fijar_tiempos(self):
        a = proyecto.leer(RAIZ / "recursos/entrega.json")
        b = demo.probar(MODELO)
        self.assertEqual(a["metricas"], b["metricas"])
        for captura in (a, b):
            self.assertEqual([x["respuesta"]["solicitud_id"] for x in captura["respuestas"]], [x["solicitud_id"] for x in captura["eventos"]])
        self.assertEqual([x["respuesta"]["estado"] for x in a["respuestas"]], [x["respuesta"]["estado"] for x in b["respuestas"]])

    def test_cli_real_entrada_valida_y_referencia(self):
        programa = RAIZ / "ejemplos/predecir.py"
        for extras, politica in (([], "ridge_incremento"), (["--referencia"], "persistencia")):
            r = subprocess.run([sys.executable, str(programa), "--entrada", str(RAIZ / "datos/consulta.json"), *extras],
                               capture_output=True, text=True, timeout=15)
            self.assertEqual(r.returncode, 0, r.stderr)
            salida, evento = json.loads(r.stdout), json.loads(r.stderr)
            self.assertEqual(salida["politica"], politica)
            self.assertEqual(salida["solicitud_id"], evento["solicitud_id"])

    def test_cli_real_rechazo(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "invalida.json"
            p.write_text('{"potencia_kw":1}')
            r = subprocess.run([sys.executable, str(RAIZ / "ejemplos/predecir.py"), "--entrada", str(p)],
                               capture_output=True, text=True, timeout=15)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)["codigo"], "campos_invalidos")


if __name__ == "__main__":
    unittest.main()

"""Las tolerancias numéricas no deben ocultar cambios de contrato o decisiones."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comparaciones import assert_resultados


class ComparacionesTest(unittest.TestCase):
    def test_precision_de_float_sin_cambiar_decisiones(self):
        esperado = {"clase": "alerta", "n": 2, "correcta": True, "p": [0.5, 0.0]}
        actual = {**esperado, "p": [0.5 + 1e-12, 1e-13]}
        assert_resultados(self, actual, esperado)

    def test_rechaza_cambios_de_clase_conteo_o_booleano(self):
        esperado = {"clase": "alerta", "n": 2, "correcta": True}
        for cambio in ({"clase": "normal"}, {"n": 3}, {"correcta": False}, {"n": 2.0}):
            with self.subTest(cambio=cambio), self.assertRaises(AssertionError):
                assert_resultados(self, {**esperado, **cambio}, esperado)

    def test_rechaza_campos_omitidos_y_adicionales(self):
        for actual in ({}, {"p": 0.5, "extra": None}):
            with self.subTest(actual=actual), self.assertRaises(AssertionError):
                assert_resultados(self, actual, {"p": 0.5})

    def test_rechaza_cambio_material_de_probabilidad(self):
        with self.assertRaises(AssertionError):
            assert_resultados(self, {"p": 0.51}, {"p": 0.5}, rtol=1e-6, atol=1e-7)

    def test_orden_y_longitud_siguen_siendo_exactos(self):
        for actual in (["b", "a"], ["a"], ["a", "b", "c"]):
            with self.subTest(actual=actual), self.assertRaises(AssertionError):
                assert_resultados(self, actual, ["a", "b"])

    def test_no_admite_numeros_no_finitos(self):
        for valor in (math.nan, math.inf, -math.inf):
            with self.subTest(valor=valor), self.assertRaises(AssertionError):
                assert_resultados(self, valor, valor)

    def test_tolerancia_especifica_no_se_extiende_a_otros_campos(self):
        limites = {("entrenamiento", "rmse"): (1e-10, 1e-5)}
        esperado = {"entrenamiento": {"rmse": 0.0}, "validacion": {"rmse": 1.0}}
        actual = {"entrenamiento": {"rmse": 8e-6}, "validacion": {"rmse": 1.0}}
        assert_resultados(self, actual, esperado, tolerancias=limites)
        actual["validacion"]["rmse"] += 8e-6
        with self.assertRaises(AssertionError):
            assert_resultados(self, actual, esperado, tolerancias=limites)

    def test_rechaza_tolerancias_invalidas(self):
        for parametros in ({"atol": -1}, {"rtol": math.inf},
                           {"tolerancias": {("p",): (math.nan, 0)}}):
            with self.subTest(parametros=parametros), self.assertRaises(ValueError):
                assert_resultados(self, 1.0, 1.0, **parametros)


if __name__ == "__main__":
    unittest.main()

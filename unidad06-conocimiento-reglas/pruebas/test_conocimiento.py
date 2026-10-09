"""Contrasta inferencia y CSP con referencias exhaustivas independientes."""

from itertools import product
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
from reglas import Regla, explicar, inferir, leer_base
from restricciones import leer_problema, resolver


class PruebasReglas(unittest.TestCase):
    def test_cadena_y_explicacion(self):
        hechos, reglas, incompatibles = leer_base(UNIDAD / "datos/reglas_revision.json")
        r = inferir(hechos, reglas, incompatibles)
        self.assertEqual([regla.nombre for regla in r["traza"]], ["r1", "r2", "r3"])
        self.assertIn("proponer_visita", r["hechos"])
        self.assertIn("      sensor_verificado: hecho inicial", explicar("proponer_visita", r))
        self.assertEqual(r["conflictos"], [])

    def test_conjuncion_exige_todos_los_hechos(self):
        r = inferir({"a"}, [Regla("r", ("a", "b"), "c")])
        self.assertNotIn("c", r["hechos"])
        self.assertIn("no equivale", explicar("c", r)[0])

    def test_ciclo_no_inventa_hechos_y_termina_con_semilla(self):
        reglas = [Regla("r1", ("a",), "b"), Regla("r2", ("b",), "a")]
        self.assertEqual(inferir(set(), reglas)["hechos"], set())
        r = inferir({"a"}, reglas)
        self.assertEqual(r["hechos"], {"a", "b"})
        self.assertEqual(len(r["traza"]), 1)
        self.assertEqual(len(explicar("b", r)), 2)

    def test_orden_afecta_traza_pero_no_cierre(self):
        reglas = [Regla("r1", ("a",), "b"), Regla("r2", ("b",), "c")]
        self.assertEqual(inferir({"a"}, reglas)["hechos"], inferir({"a"}, reglas[::-1])["hechos"])

    def test_conflicto_no_elimina_conclusiones(self):
        hechos, reglas, pares = leer_base(UNIDAD / "datos/reglas_revision.json")
        r = inferir(hechos | {"mantenimiento_programado"}, reglas, pares)
        self.assertEqual(r["conflictos"], [("proponer_visita", "posponer_visita")])
        self.assertTrue({"proponer_visita", "posponer_visita"} <= r["hechos"])

    def test_retirar_hecho_requiere_nuevo_cierre(self):
        hechos, reglas, pares = leer_base(UNIDAD / "datos/reglas_revision.json")
        original = hechos.copy()
        r = inferir(hechos - {"sensor_verificado"}, reglas, pares)
        self.assertNotIn("proponer_visita", r["hechos"])
        self.assertEqual(hechos, original)

    def test_id_duplicado_y_simbolo_invalido(self):
        with self.assertRaises(ValueError):
            inferir({"a"}, [Regla("r", ("a",), "b"), Regla("r", ("a",), "c")])
        with self.assertRaises(ValueError):
            inferir({"a or b"}, [])
        with self.assertRaises(ValueError):
            inferir(set(), [Regla("r", (), "a")])

    def test_cierre_contra_modelos_logicos(self):
        # Un átomo es consecuencia si aparece en todos los modelos de la base.
        rng = random.Random(61)
        atomos = ("a", "b", "c", "d")
        for _ in range(30):
            hechos = {a for a in atomos if rng.random() < .3}
            reglas = [Regla(f"r{i}", tuple(rng.sample(atomos, rng.randint(1, 2))), rng.choice(atomos))
                      for i in range(5)]
            modelos = []
            for bits in product((False, True), repeat=len(atomos)):
                verdaderos = {a for a, bit in zip(atomos, bits) if bit}
                if hechos <= verdaderos and all(
                    not set(r.condiciones) <= verdaderos or r.conclusion in verdaderos for r in reglas
                ):
                    modelos.append(verdaderos)
            consecuencias = set.intersection(*modelos)
            self.assertEqual(inferir(hechos, reglas)["hechos"], consecuencias)


class PruebasRestricciones(unittest.TestCase):
    def test_soluciones_conocidas(self):
        d, r = leer_problema(UNIDAD / "datos/horarios.json")
        resultado = resolver(d, r)
        self.assertEqual({tuple(s[v] for v in d) for s in resultado["soluciones"]},
                         {(1, 2, 3), (1, 3, 2), (2, 3, 1)})

    def test_imposible_y_dominio_vacio(self):
        d, r = leer_problema(UNIDAD / "datos/horarios_imposibles.json")
        self.assertEqual(resolver(d, r)["soluciones"], [])
        for poda in (False, True):
            self.assertEqual(resolver({"a": [], "b": [1]}, [], poda=poda)["soluciones"], [])
        d = {f"v{i}": list(range(8)) for i in range(7)}
        d["sin_valores"] = []
        self.assertEqual(resolver(d, [], orden="fija", poda=False)["intentos"], 0)

    def test_direccion_del_orden(self):
        d = {"a": [1, 2], "b": [1, 2]}
        self.assertEqual(resolver(d, [{"a": "b", "op": "<", "b": "a"}])["soluciones"],
                         [{"a": 2, "b": 1}])

    def test_sin_restricciones_y_entradas_no_mutadas(self):
        d = {"a": [1, 2], "b": [3, 4]}
        original = json.dumps(d)
        self.assertEqual(len(resolver(d, [])["soluciones"]), 4)
        self.assertEqual(json.dumps(d), original)

    def test_rechaza_datos_invalidos(self):
        for d in ({}, {"a": [True]}, {"a": [1, 1]}, {"a": "12"}):
            with self.assertRaises(ValueError):
                resolver(d, [])
        for r in ([{"a": "a", "op": "=", "b": "b"}], [{"a": "a", "op": "!=", "b": "z"}]):
            with self.assertRaises(ValueError):
                resolver({"a": [1], "b": [2]}, r)

    def test_variantes_contra_enumeracion_independiente(self):
        rng = random.Random(62)
        for _ in range(30):
            d = {v: rng.sample([1, 2, 3], rng.randint(0, 3)) for v in ("a", "b", "c")}
            rs = [{"a": a, "op": rng.choice(("!=", "<")), "b": b}
                  for a, b in (("a", "b"), ("b", "c"), ("c", "a")) if rng.random() < .7]
            referencia = set()
            for valores in product(*d.values()):
                s = dict(zip(d, valores))
                if all((s[r["a"]] != s[r["b"]]) if r["op"] == "!=" else (s[r["a"]] < s[r["b"]]) for r in rs):
                    referencia.add(valores)
            for orden, poda in product(("fija", "mrv"), (False, True)):
                soluciones = resolver(d, rs, orden, poda)["soluciones"]
                obtenidas = {tuple(s[v] for v in d) for s in soluciones}
                self.assertEqual(obtenidas, referencia)
                self.assertEqual(len(soluciones), len(obtenidas))


class PruebasArchivos(unittest.TestCase):
    def test_esquemas_incorrectos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.json"
            for datos in ([], {}, {"hechos": [], "reglas": {}, "incompatibles": []}):
                ruta.write_text(json.dumps(datos), encoding="utf-8")
                with self.assertRaises(ValueError):
                    leer_base(ruta)
            ruta.write_text('{"dominios": [], "restricciones": []}', encoding="utf-8")
            with self.assertRaises(ValueError):
                leer_problema(ruta)


if __name__ == "__main__":
    unittest.main()

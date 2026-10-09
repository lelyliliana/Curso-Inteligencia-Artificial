"""Referencias independientes, aislamiento de pliegues, cierre y artefactos."""

import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.model_selection import GridSearchCV
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import validacion as v
import figuras


def cargar_modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


manual = cargar_modulo("manual", UNIDAD / "soluciones/03_pliegues_a_mano.py")
generador = cargar_modulo("generador", UNIDAD / "datos/generar_datos.py")


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datos = {n: v.leer_csv(UNIDAD / "datos" / n / "desarrollo.csv", n)[0] for n in v.ENTRADAS}
        cls.informes = {n: v.ejecutar_experimento(n, UNIDAD / "datos" / n) for n in v.ENTRADAS}


class Matematica(Base):
    def test_mediana_manual(self):
        ev = manual.cv_mediana()
        self.assertEqual([r["mediana"] for r in ev], [7, 5, 3])
        self.assertEqual([r["mae"] for r in ev], [6, 1, 6])
        self.assertAlmostEqual(np.mean([r["mae"] for r in ev]), 13/3)
        self.assertAlmostEqual(np.std([r["mae"] for r in ev]), np.sqrt(50)/3)

    def test_distancias_y_pesos_independientes(self):
        filas = self.datos["ciclos"]
        x = v.matriz(filas, "ciclos")
        y = np.array([r["consumo_kwh"] for r in filas])
        train, val = v.pliegues(filas, "ciclos")[0]
        media, escala = x[train].mean(axis=0), x[train].std(axis=0)
        z, consultas = (x[train]-media)/escala, (x[val]-media)/escala
        distancias = np.sqrt(((consultas[:, None, :]-z[None, :, :])**2).sum(axis=2))
        for c, parametros in v.CANDIDATOS.items():
            if parametros is None:
                continue
            k = parametros["n_neighbors"]
            indices = np.argsort(distancias, axis=1)[:, :k]
            ds = np.take_along_axis(distancias, indices, axis=1)
            self.assertTrue(np.all(ds > 0))
            pesos = np.ones_like(ds) if parametros["weights"] == "uniform" else 1/ds
            referencia = (y[train][indices]*pesos).sum(axis=1)/pesos.sum(axis=1)
            registros = self.informes["ciclos"]["resultados_cv"][c]["predicciones_oof"][:len(val)]
            np.testing.assert_allclose([r["prediccion"] for r in registros], referencia, atol=1e-9)

    def test_vecinos_coincidentes(self):
        # Dos coincidencias de distancia cero deben excluir a los vecinos alejados.
        x = np.array([[0., 0.], [0., 0.], [10., 10.]])
        with threadpool_limits(limits=1):
            m = v.crear_modelo("knn3_distance").fit(x, [2., 6., 99.])
            self.assertAlmostEqual(m.predict([[0., 0.]])[0], 4.)

    def test_gridsearch_independiente(self):
        filas = self.datos["ciclos"]
        modelo = v.crear_modelo("knn3_uniform")
        busqueda = GridSearchCV(modelo, {"vecinos__n_neighbors": [3, 9, 21], "vecinos__weights": ["uniform", "distance"]},
                                cv=v.pliegues(filas, "ciclos"), scoring="neg_mean_absolute_error", refit=True, n_jobs=1)
        with threadpool_limits(limits=1):
            busqueda.fit(v.matriz(filas, "ciclos"), [f["consumo_kwh"] for f in filas])
        for parametros, media, desv in zip(busqueda.cv_results_["params"], busqueda.cv_results_["mean_test_score"], busqueda.cv_results_["std_test_score"]):
            c = f"knn{parametros['vecinos__n_neighbors']}_{parametros['vecinos__weights']}"
            ev = self.informes["ciclos"]["resultados_cv"][c]
            self.assertAlmostEqual(ev["mae_medio"], -media)
            self.assertAlmostEqual(ev["desviacion_mae"], desv)
        self.assertEqual(busqueda.best_params_, {"vecinos__n_neighbors": 3, "vecinos__weights": "distance"})

    def test_media_pliegues_y_oof(self):
        for nombre, informe in self.informes.items():
            for ev in informe["resultados_cv"].values():
                errores = [abs(r["residuo"]) for r in ev["predicciones_oof"]]
                self.assertAlmostEqual(ev["mae_oof"], sum(errores)/len(errores))
                self.assertAlmostEqual(ev["mae_medio"], ev["mae_oof"])
        # Con tamaños distintos las dos medias no coinciden en general.
        self.assertNotEqual(np.mean([2., 8.]), np.average([2., 8.], weights=[1, 3]))

    def test_desempate_sin_redondear(self):
        self.assertEqual(v.seleccionar({"mediana": {"mae_medio": 1+5e-11}, "knn3_uniform": {"mae_medio": 1}}), "mediana")
        self.assertEqual(v.seleccionar({"mediana": {"mae_medio": 1.0001}, "knn3_uniform": {"mae_medio": 1}}), "knn3_uniform")

    def test_filtracion_de_escala_cambia_consulta(self):
        r = manual.comparar_escala()
        self.assertEqual(r["correcta"]["prediccion"], 40.)
        self.assertEqual(r["filtrada"]["prediccion"], 20.)
        np.testing.assert_allclose(r["correcta"]["media"], [2, 10/3])

    def test_cortes_temporales(self):
        cortes = manual.cortes_temporales()
        self.assertEqual([val for _, val in cortes], [[6, 7], [8, 9], [10, 11]])
        for train, val in cortes:
            self.assertEqual(max(train)+2, min(val))
            self.assertFalse(set(train) & set(val))


class Separacion(Base):
    def test_cobertura_unica_y_disjunta(self):
        for nombre, filas in self.datos.items():
            vistos = []
            for train, val in v.pliegues(filas, nombre):
                self.assertFalse(set(train) & set(val))
                self.assertEqual(set(train) | set(val), set(range(len(filas))))
                vistos.extend(val)
            self.assertEqual(sorted(vistos), list(range(len(filas))))

    def test_equipos_aislados_y_diagnostico(self):
        informe = self.informes["equipos"]
        self.assertTrue(all(not p["equipos_compartidos"] for p in informe["cv"]["pliegues"]))
        self.assertTrue(all(p["equipos_compartidos"] for p in informe["diagnostico_filas"]["pliegues"]))
        self.assertLess(informe["diagnostico_filas"]["resultado"]["mae_medio"], informe["resultados_cv"][v.DIAGNOSTICO]["mae_medio"])

    def test_escala_solo_ajuste_del_pliegue(self):
        for nombre, filas in self.datos.items():
            x = v.matriz(filas, nombre)
            for p, ev in zip(self.informes[nombre]["cv"]["pliegues"], self.informes[nombre]["resultados_cv"]["knn3_uniform"]["pliegues"]):
                train = p["indices_ajuste"]
                np.testing.assert_allclose(ev["ajuste"]["escala"]["media"], x[train].mean(axis=0))
                np.testing.assert_allclose(ev["ajuste"]["escala"]["varianza"], x[train].var(axis=0))

    def test_alterar_validacion_no_cambia_ajuste_de_su_pliegue(self):
        filas = copy.deepcopy(self.datos["ciclos"])
        particiones = v.pliegues(filas, "ciclos")
        for i in particiones[0][1]:
            filas[i]["carga_prevista"] += 100
            filas[i]["consumo_kwh"] += 10
        with threadpool_limits(limits=1):
            ev = v.evaluar_cv(filas, "ciclos", particiones, "knn3_uniform")
        original = self.informes["ciclos"]["resultados_cv"]["knn3_uniform"]
        self.assertEqual(ev["pliegues"][0]["ajuste"], original["pliegues"][0]["ajuste"])
        self.assertEqual(ev["pliegues"][0]["entrenamiento"], original["pliegues"][0]["entrenamiento"])
        self.assertNotEqual(ev["pliegues"][0]["validacion"], original["pliegues"][0]["validacion"])

    def test_reajuste_usa_todo_desarrollo(self):
        for nombre, informe in self.informes.items():
            filas = self.datos[nombre]
            self.assertEqual(informe["reajuste"]["ids_ajuste"], [f["caso_id"] for f in filas])
            self.assertEqual(informe["reajuste"]["n_ajuste"], len(filas))
        np.testing.assert_allclose(self.informes["ciclos"]["reajuste"]["escala"]["media"], v.matriz(self.datos["ciclos"], "ciclos").mean(axis=0))
        self.assertAlmostEqual(self.informes["equipos"]["reajuste"]["valor"], np.median([f["respuesta"] for f in self.datos["equipos"]]))

    def test_sin_prueba_no_se_lee(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"desarrollo.csv").write_bytes((UNIDAD/"datos/ciclos/desarrollo.csv").read_bytes())
            self.assertIsNone(v.ejecutar_experimento("ciclos", d)["prueba"])

    def test_prueba_se_abre_despues_de_reajuste(self):
        eventos = []
        leer, resumir = v.leer_csv, v.resumen_modelo
        def registro_lectura(ruta, nombre):
            eventos.append(Path(ruta).name)
            return leer(ruta, nombre)
        def registro_modelo(modelo, ids):
            if len(ids) == 160:
                eventos.append("reajuste")
            return resumir(modelo, ids)
        with patch.object(v, "leer_csv", side_effect=registro_lectura), patch.object(v, "resumen_modelo", side_effect=registro_modelo):
            v.ejecutar_experimento("ciclos", UNIDAD/"datos/ciclos", True)
        self.assertEqual(eventos, ["desarrollo.csv", "reajuste", "prueba.csv"])

    def test_etiquetas_prueba_no_influyen(self):
        leer = v.leer_csv
        for nombre in v.ENTRADAS:
            original = v.ejecutar_experimento(nombre, UNIDAD/"datos"/nombre, True)
            def alterado(ruta, n):
                filas, fuente = leer(ruta, n)
                if Path(ruta).name == "prueba.csv":
                    for f in filas:
                        f[v.OBJETIVO[n]] += 1
                return filas, fuente
            with patch.object(v, "leer_csv", side_effect=alterado):
                nuevo = v.ejecutar_experimento(nombre, UNIDAD/"datos"/nombre, True)
            for clave in ("cv", "resultados_cv", "seleccionado", "reajuste", "diagnostico_filas"):
                self.assertEqual(nuevo[clave], original[clave])
            self.assertEqual([r["prediccion"] for r in nuevo["prueba"]["predicciones"]], [r["prediccion"] for r in original["prueba"]["predicciones"]])
            self.assertNotEqual(nuevo["prueba"]["metricas"]["sesgo"], original["prueba"]["metricas"]["sesgo"])

    def test_diagnostico_no_selecciona(self):
        original = v.evaluar_cv
        def diagnostico_extremo(filas, nombre, particiones, candidato):
            resultado = original(filas, nombre, particiones, candidato)
            if any({filas[j]["equipo_id"] for j in tr} & {filas[j]["equipo_id"] for j in va} for tr, va in particiones):
                resultado["mae_medio"] = 0.
            return resultado
        with patch.object(v, "evaluar_cv", side_effect=diagnostico_extremo):
            nuevo = v.ejecutar_experimento("equipos", UNIDAD/"datos/equipos")
        for clave in ("resultados_cv", "seleccionado", "reajuste"):
            self.assertEqual(nuevo[clave], self.informes["equipos"][clave])

    def test_presupuesto_y_mismos_casos(self):
        for nombre, total in (("ciclos", 29), ("equipos", 33)):
            informe = self.informes[nombre]
            self.assertEqual(informe["ajustes_realizados"], total)
            esperado = {f["caso_id"] for f in self.datos[nombre]}
            for ev in informe["resultados_cv"].values():
                self.assertEqual({r["caso_id"] for r in ev["predicciones_oof"]}, esperado)
                self.assertEqual(len(ev["predicciones_oof"]), len(esperado))


class DatosArtefactos(Base):
    def test_regeneracion(self):
        for ruta, texto in generador.contenidos().items():
            self.assertEqual(texto.encode(), (UNIDAD/"datos"/ruta).read_bytes())

    def test_lector_rechaza_datos_invalidos(self):
        original = (UNIDAD/"datos/ciclos/desarrollo.csv").read_text()
        variantes = ["", original.replace("carga_prevista", "horas_previstas", 1),
                     original.replace(original.splitlines()[1].split(",")[1], "nan", 1),
                     original + original.splitlines()[1] + "\n",
                     original.replace(original.splitlines()[1], original.splitlines()[1]+",3", 1),
                     original.replace(original.splitlines()[1].split(",")[1], "-1", 1)]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"datos.csv"
            for variante in variantes:
                p.write_text(variante)
                with self.assertRaises(ValueError):
                    v.leer_csv(p, "ciclos")

    def test_matriz_excluye_identificadores_y_objetivo(self):
        filas = copy.deepcopy(self.datos["equipos"])
        esperado = v.matriz(filas, "equipos")
        for f in filas:
            f.update(caso_id="otro", equipo_id="nuevo", respuesta=0)
        np.testing.assert_array_equal(v.matriz(filas, "equipos"), esperado)

    def test_insuficientes_casos_o_equipos(self):
        with self.assertRaises(ValueError):
            v.pliegues(self.datos["ciclos"][:24], "ciclos")
        with self.assertRaises(ValueError):
            v.pliegues(self.datos["equipos"][:36], "equipos")

    def test_prueba_rechaza_equipos_conocidos_e_ids_repetidos(self):
        leer = v.leer_csv
        for columna in ("caso_id", "equipo_id"):
            def alterado(ruta, nombre):
                filas, fuente = leer(ruta, nombre)
                if Path(ruta).name == "prueba.csv":
                    filas[0][columna] = self.datos["equipos"][0][columna]
                return filas, fuente
            with patch.object(v, "leer_csv", side_effect=alterado), self.assertRaises(ValueError):
                v.ejecutar_experimento("equipos", UNIDAD/"datos/equipos", True)

    def test_exportacion_cierre_solo_elegido(self):
        with tempfile.TemporaryDirectory() as d:
            informe = v.ejecutar_experimento("ciclos", UNIDAD/"datos/ciclos", True)
            destino = Path(d)/"salida"
            v.exportar(informe, destino)
            self.assertEqual(json.loads((destino/"informe.json").read_text()), informe)
            with (destino/"predicciones_prueba.csv").open() as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 64)
            self.assertEqual({f["candidato"] for f in filas}, {informe["seleccionado"]})
            with self.assertRaises(FileExistsError):
                v.exportar(informe, destino)

    def test_informes_publicados(self):
        for nombre, informe in self.informes.items():
            guardado = json.loads((UNIDAD/"recursos"/nombre/"informe.json").read_text())
            guardado.pop("versiones")
            actual = copy.deepcopy(informe)
            actual.pop("versiones")
            self.assertEqual(guardado, actual)
            self.assertIsNone(guardado["prueba"])
            self.assertEqual(set(guardado["fuentes"]), {"desarrollo"})

    def test_csv_publicados_corresponden_a_json(self):
        for nombre, informe in self.informes.items():
            esperado = [dict(candidato=c, **r) for c, ev in informe["resultados_cv"].items() for r in ev["predicciones_oof"]]
            with (UNIDAD/"recursos"/nombre/"predicciones_oof.csv").open() as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(filas, [{k: str(v) for k, v in r.items()} for r in esperado])


class Figuras(Base):
    def tearDown(self):
        figuras.plt.close("all")

    def test_busqueda_medias_y_puntos(self):
        informe = self.informes["ciclos"]
        fig = figuras.figura_busqueda(informe)
        eje = fig.axes[0]
        np.testing.assert_allclose([p.get_width() for p in eje.patches], [v["mae_medio"] for v in informe["resultados_cv"].values()])
        self.assertEqual(eje.get_xlim()[0], 0)
        dispersiones = [c for c in eje.collections if hasattr(c, "get_offsets") and len(c.get_offsets()) == 4]
        self.assertEqual(len(dispersiones), 7)
        for puntos, ev in zip(dispersiones, informe["resultados_cv"].values()):
            np.testing.assert_allclose(puntos.get_offsets()[:, 0], [p["validacion"]["mae"] for p in ev["pliegues"]])

    def test_mapa_pliegues(self):
        informe = self.informes["equipos"]
        fig = figuras.figura_particiones(informe)
        for eje, pliegues in zip(fig.axes, (informe["cv"]["pliegues"], informe["diagnostico_filas"]["pliegues"])):
            estados = np.asarray(eje.images[0].get_array())
            np.testing.assert_array_equal(estados.sum(axis=0), np.ones(144))
            for i, p in enumerate(pliegues):
                self.assertEqual(np.flatnonzero(estados[i]).tolist(), p["indices_validacion"])

    def test_diagnostico_candidato_fijo(self):
        informe = self.informes["equipos"]
        fig = figuras.figura_equipos(informe)
        eje = fig.axes[1]
        np.testing.assert_allclose([p.get_height() for p in eje.patches], [informe["diagnostico_filas"]["resultado"]["mae_medio"], informe["resultados_cv"][v.DIAGNOSTICO]["mae_medio"]])
        self.assertEqual(eje.get_ylim()[0], 0)

    def test_figuras_no_usan_prueba_y_no_sobrescriben(self):
        informe = copy.deepcopy(self.informes["equipos"])
        informe["prueba"] = {"contenido": "no tiene que leerse"}
        with tempfile.TemporaryDirectory() as d:
            figuras.guardar_figuras(informe, d)
            for nombre in ("particiones", "comparacion"):
                self.assertGreater(figuras.plt.imread(Path(d)/f"{nombre}.png").size, 0)
                self.assertIn("<svg", (Path(d)/f"{nombre}.svg").read_text())
            with self.assertRaises(FileExistsError):
                figuras.guardar_figuras(informe, d)


if __name__ == "__main__":
    unittest.main()

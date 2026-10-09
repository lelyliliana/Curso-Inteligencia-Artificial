"""Verifica métricas a mano, separación de casos y ausencia de ajuste con prueba."""

import copy
import csv
import io
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
sys.path.insert(0, str(UNIDAD / "datos"))
from generar_datos import contenidos
import flujo


def cargar(tarea):
    return {fase: flujo.leer_csv(UNIDAD / "datos" / tarea / f"{fase}.csv", tarea)[0]
            for fase in flujo.FASES}


class Metricas(unittest.TestCase):
    def test_regresion_con_calculo_manual_y_sesgo_firmado(self):
        r = flujo.metricas_regresion([10, 14, 12], [11, 12, 13])
        self.assertAlmostEqual(r["mae"], 4 / 3)
        self.assertAlmostEqual(r["rmse"], math.sqrt(2))
        self.assertEqual(r["sesgo"], 0)
        self.assertEqual(flujo.metricas_regresion([10, 14], [8, 12])["sesgo"], 2)

    def test_confusion_y_metricas_con_cuentas_independientes(self):
        r = flujo.metricas_clasificacion([1, 1, 0, 0, 0], [1, 0, 1, 0, 0])
        self.assertEqual([r[k] for k in ("VP", "VN", "FP", "FN")], [1, 2, 1, 1])
        self.assertEqual(r["exactitud"], .6)
        self.assertEqual(r["precision"], .5)
        self.assertEqual(r["recobrado"], .5)
        self.assertEqual(r["f1"], .5)

    def test_sin_predicciones_positivas_no_inventa_precision(self):
        r = flujo.metricas_clasificacion([0, 0, 1], [0, 0, 0])
        self.assertIsNone(r["precision"])
        self.assertEqual(r["recobrado"], 0)
        self.assertEqual(r["f1"], 0)

    def test_sin_positivos_ni_predicciones_f1_no_definido(self):
        r = flujo.metricas_clasificacion([0, 0], [0, 0])
        self.assertEqual(r["exactitud"], 1)
        self.assertIsNone(r["recobrado"])
        self.assertIsNone(r["f1"])

    def test_listas_vacias_desalineadas_y_no_finitas_se_rechazan(self):
        for real, pred in (([], []), ([1, 2], [1]), ([math.nan], [1]), ([1], [math.inf]), ([True], [1])):
            for funcion in (flujo.metricas_regresion, flujo.metricas_clasificacion):
                with self.subTest(real=real, pred=pred), self.assertRaises(ValueError):
                    funcion(real, pred)
        with self.assertRaises(ValueError):
            flujo.metricas_clasificacion([2], [0])
        with self.assertRaises(ValueError):
            flujo.metricas_regresion([1e308], [0])

    def test_empates_tienen_politica_determinista(self):
        self.assertEqual(flujo.mayoria([0, 1]), 0)
        r = {c: {"metricas": {"mae": 1}} for c in flujo.CANDIDATOS["regresion"]}
        self.assertEqual(flujo.seleccionar(r, "regresion"), "mediana")
        c = {m: {"metricas": {"f1": .5, "positivos": 1}} for m in flujo.CANDIDATOS["clasificacion"]}
        self.assertEqual(flujo.seleccionar(c, "clasificacion"), "mayoria")

    def test_validacion_sin_positivos_exige_revisar_protocolo(self):
        r = {m: {"metricas": flujo.metricas_clasificacion([0, 0], [1, 1])}
             for m in flujo.CANDIDATOS["clasificacion"]}
        with self.assertRaises(ValueError):
            flujo.seleccionar(r, "clasificacion")


class DatosYParticiones(unittest.TestCase):
    def test_generador_reproduce_los_seis_csv(self):
        archivos = contenidos()
        self.assertEqual(len(archivos), 6)
        for nombre, texto in archivos.items():
            self.assertEqual((UNIDAD / "datos" / nombre).read_bytes(), texto.encode("utf-8"))

    def test_tamanos_fechas_y_grupos_del_diseno(self):
        r, c = cargar("regresion"), cargar("clasificacion")
        self.assertEqual([len(r[f]) for f in flujo.FASES], [20, 6, 6])
        self.assertEqual([len(c[f]) for f in flujo.FASES], [32, 16, 16])
        self.assertEqual([len({v["equipo_id"] for v in c[f]}) for f in flujo.FASES], [4, 2, 2])
        flujo.validar_separacion(r, "regresion")
        flujo.validar_separacion(c, "clasificacion")

    def test_rechaza_ids_repetidos_dentro_y_entre_particiones(self):
        datos = cargar("regresion")
        for fase in ("entrenamiento", "validacion"):
            copia = copy.deepcopy(datos)
            copia[fase][1]["caso_id"] = copia["entrenamiento"][0]["caso_id"]
            with self.assertRaises(ValueError):
                flujo.validar_separacion(copia, "regresion")

    def test_rechaza_equipos_compartidos_incluso_con_ids_distintos(self):
        datos = cargar("clasificacion")
        datos["validacion"][0]["equipo_id"] = datos["entrenamiento"][0]["equipo_id"]
        with self.assertRaises(ValueError):
            flujo.validar_separacion(datos, "clasificacion")

    def test_rechaza_solapamiento_temporal_y_etiqueta_tardia(self):
        for campo in ("momento_prediccion", "objetivo_disponible"):
            datos = cargar("regresion")
            datos["entrenamiento"][-1][campo] = datos["validacion"][1]["momento_prediccion"]
            with self.assertRaises(ValueError):
                flujo.validar_separacion(datos, "regresion")

    def test_lector_rechaza_futuro_fechas_sin_zona_y_objetivo_ausente(self):
        original = (UNIDAD / "datos/regresion/entrenamiento.csv").read_text(encoding="utf-8")
        columnas = list(csv.DictReader(io.StringIO(original)).fieldnames)
        for campo, valor in (("entrada_disponible", "2030-01-01T00:00:00-05:00"),
                             ("momento_prediccion", "2026-01-02T00:00:00"),
                             ("objetivo_disponible", "2026-01-04T00:00:00-05:00"),
                             ("consumo_objetivo_kwh", ""), ("consumo_anterior_kwh", "NaN")):
            with tempfile.TemporaryDirectory() as carpeta:
                filas = list(csv.DictReader(io.StringIO(original)))
                filas[0][campo] = valor
                ruta = Path(carpeta) / "datos.csv"
                with ruta.open("w", encoding="utf-8", newline="") as archivo:
                    escritor = csv.DictWriter(archivo, fieldnames=columnas)
                    escritor.writeheader()
                    escritor.writerows(filas)
                with self.subTest(campo=campo), self.assertRaises(ValueError):
                    flujo.leer_csv(ruta, "regresion")

    def test_lector_rechaza_esquema_filas_incompletas_y_etiquetas_invalidas(self):
        cabecera = "caso_id,equipo_id,senal_previa,fallo_24h\n"
        ejemplos = ["", "caso_id,equipo_id,senal_previa,senal_previa\n", cabecera,
                    cabecera + "a,E1,alta\n", cabecera + "a,E1,alta,1,extra\n",
                    cabecera + "a,E1,otra,1\n", cabecera + "a,E1,alta,2\n"]
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "datos.csv"
            for texto in ejemplos:
                ruta.write_text(texto, encoding="utf-8")
                with self.subTest(texto=texto), self.assertRaises(ValueError):
                    flujo.leer_csv(ruta, "clasificacion")


class Flujo(unittest.TestCase):
    def test_predictores_solo_reciben_las_entradas_permitidas(self):
        for tarea, campo in (("regresion", "consumo_anterior_kwh"), ("clasificacion", "senal_previa")):
            filas = cargar(tarea)["validacion"]
            self.assertTrue(all(set(e) == {campo} for e in flujo.entradas_de(filas, tarea)))

    def test_persistencia_imputa_con_mediana_de_entrada_de_entrenamiento(self):
        datos = cargar("regresion")
        ajuste = flujo.ajustar(datos["entrenamiento"], "regresion")
        self.assertEqual(ajuste, {"mediana": 22, "media": 22, "mediana_entrada": 21.5})
        p = flujo.predecir([{"consumo_anterior_kwh": None}, {"consumo_anterior_kwh": 0}], ajuste, "persistencia", "regresion")
        self.assertEqual(p, [21.5, 0])

    def test_imputacion_sin_observaciones_se_rechaza(self):
        datos = cargar("regresion")["entrenamiento"]
        for fila in datos:
            fila["consumo_anterior_kwh"] = None
        with self.assertRaises(ValueError):
            flujo.ajustar(datos, "regresion")

    def test_categoria_sin_soporte_usa_mayoria_global(self):
        filas = [{"senal_previa": "baja", "fallo_24h": v} for v in (0, 0, 1)]
        ajuste = flujo.ajustar(filas, "clasificacion")
        self.assertEqual(ajuste["soportes"]["alta"], 0)
        self.assertEqual(flujo.predecir([{"senal_previa": "alta"}], ajuste, "por_senal", "clasificacion"), [0])

    def test_ejecucion_habitual_no_necesita_archivo_de_prueba(self):
        for tarea in ("regresion", "clasificacion"):
            with tempfile.TemporaryDirectory() as carpeta:
                for fase in ("entrenamiento", "validacion"):
                    shutil.copy2(UNIDAD / "datos" / tarea / f"{fase}.csv", carpeta)
                informe = flujo.ejecutar_experimento(tarea, carpeta)
                self.assertIsNone(informe["prueba"])
                self.assertNotIn("prueba", informe["fuentes"])

    def test_cambiar_validacion_no_cambia_parametros_de_ajuste(self):
        tarea = "regresion"
        original = flujo.leer_csv

        def cambiado(ruta, tarea):
            filas, huella = original(ruta, tarea)
            if Path(ruta).stem == "validacion":
                for fila in filas:
                    fila["consumo_anterior_kwh"] = 1000
                    fila["consumo_objetivo_kwh"] = 2000
            return filas, huella

        base = flujo.ejecutar_experimento(tarea, UNIDAD / "datos" / tarea)
        with patch.object(flujo, "leer_csv", side_effect=cambiado):
            modificado = flujo.ejecutar_experimento(tarea, UNIDAD / "datos" / tarea)
        self.assertEqual(base["ajuste"], modificado["ajuste"])
        self.assertNotEqual(base["validacion"], modificado["validacion"])

    def test_alterar_objetivos_de_prueba_no_cambia_ajuste_seleccion_ni_prediccion(self):
        for tarea in ("regresion", "clasificacion"):
            original = flujo.leer_csv

            def cambiado(ruta, tipo):
                filas, huella = original(ruta, tipo)
                if Path(ruta).stem == "prueba":
                    for fila in filas:
                        if tipo == "regresion":
                            fila["consumo_objetivo_kwh"] += 100
                        else:
                            fila["fallo_24h"] = 1 - fila["fallo_24h"]
                return filas, huella

            base = flujo.ejecutar_experimento(tarea, UNIDAD / "datos" / tarea, True)
            with patch.object(flujo, "leer_csv", side_effect=cambiado):
                cambiado_ = flujo.ejecutar_experimento(tarea, UNIDAD / "datos" / tarea, True)
            for campo in ("ajuste", "seleccionado", "validacion"):
                self.assertEqual(base[campo], cambiado_[campo])
            self.assertEqual([p["prediccion"] for p in base["prueba"]["predicciones"]],
                             [p["prediccion"] for p in cambiado_["prueba"]["predicciones"]])
            self.assertNotEqual(base["prueba"]["metricas"], cambiado_["prueba"]["metricas"])

    def test_resultados_de_regresion_y_mismos_casos_de_validacion(self):
        r = flujo.ejecutar_experimento("regresion", UNIDAD / "datos/regresion", True)
        self.assertEqual(r["seleccionado"], "persistencia")
        self.assertAlmostEqual(r["validacion"]["mediana"]["metricas"]["mae"], 17 / 6)
        self.assertAlmostEqual(r["validacion"]["persistencia"]["metricas"]["mae"], 12.5 / 6)
        self.assertEqual(r["prueba"]["metricas"]["mae"], 2.25)
        ids = [[p["caso_id"] for p in resultado["predicciones"]] for resultado in r["validacion"].values()]
        self.assertTrue(all(iguales == ids[0] for iguales in ids))

    def test_resultados_de_clasificacion_y_errores_por_equipo(self):
        r = flujo.ejecutar_experimento("clasificacion", UNIDAD / "datos/clasificacion", True)
        m = r["validacion"]["mayoria"]["metricas"]
        self.assertEqual(m["exactitud"], 13 / 16)
        self.assertEqual(m["FN"], 3)
        self.assertEqual(m["f1"], 0)
        self.assertEqual(r["seleccionado"], "por_senal")
        self.assertAlmostEqual(r["validacion"]["por_senal"]["metricas"]["f1"], 6 / 7)
        self.assertAlmostEqual(r["prueba"]["metricas"]["f1"], 8 / 9)
        errores = [p for p in r["validacion"]["por_senal"]["predicciones"] if p["resultado"] in ("FP", "FN")]
        self.assertEqual([(p["caso_id"], p["resultado"]) for p in errores], [("C06-08", "FP")])

    def test_exportacion_tiene_trazabilidad_y_no_sobrescribe(self):
        for cierre in (False, True):
            r = flujo.ejecutar_experimento("clasificacion", UNIDAD / "datos/clasificacion", cierre)
            with tempfile.TemporaryDirectory() as carpeta:
                destino = Path(carpeta) / "entrega"
                flujo.exportar(r, destino)
                self.assertEqual(json.loads((destino / "informe.json").read_text(encoding="utf-8")), r)
                self.assertEqual((destino / "predicciones_prueba.csv").exists(), cierre)
                with (destino / "predicciones_validacion.csv").open(encoding="utf-8", newline="") as archivo:
                    self.assertEqual(len(list(csv.DictReader(archivo))), 32)
                antes = (destino / "informe.json").read_bytes()
                with self.assertRaises(FileExistsError):
                    flujo.exportar(r, destino)
                self.assertEqual((destino / "informe.json").read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()

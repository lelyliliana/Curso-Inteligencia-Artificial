"""Casos de integridad, cobertura, disponibilidad y conservación de archivos."""

import copy
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
from perfil_datos import COLUMNAS, fecha_iso, interpretar, leer_csv, perfilar
from disponibilidad import auditar, instante, leer_eventos


def perfil(registros):
    return perfilar(registros, date(2026, 9, 1), date(2026, 9, 4), ["S1", "S2", "S3"])


class PruebasCSV(unittest.TestCase):
    def setUp(self):
        self.registros, self.huella = leer_csv(UNIDAD / "datos/lecturas_sinteticas.csv")

    def test_conteos_del_caso_manual(self):
        p = perfil(self.registros)
        self.assertEqual(p["filas"], 12)
        self.assertEqual(p["columnas"]["consumo_kwh"], {"validos": 10, "faltantes": 1, "invalidos": 1})
        self.assertEqual(len(p["incidencias"]), 4)
        for conteos in p["columnas"].values():
            self.assertEqual(sum(conteos.values()), 12)

    def test_duplicado_exacto_y_clave_con_textos_distintos(self):
        p = perfil(self.registros)
        self.assertEqual(p["duplicados_exactos_adicionales"], 1)
        self.assertEqual(p["claves_repetidas"], [
            {"clave": ["2026-09-01", "S3"], "registros": [10, 11], "textos_distintos": True},
            {"clave": ["2026-09-02", "S2"], "registros": [6, 7], "textos_distintos": False},
        ])

    def test_cobertura_cuenta_claves_no_filas(self):
        c = perfil(self.registros)["cobertura"]
        self.assertEqual((c["presentes"], c["esperadas"]), (10, 12))
        self.assertEqual(c["ausentes"], [["2026-09-02", "S3"], ["2026-09-04", "S3"]])
        self.assertEqual(perfil(self.registros * 2)["cobertura"], c)

    def test_claves_invalidas_y_fuera_del_plan(self):
        datos = copy.deepcopy(self.registros[:2])
        datos[0]["fecha"] = "2026-02-30"
        datos[1]["sensor_id"] = "S9"
        p = perfil(datos)
        self.assertEqual(p["registros_sin_clave"], [1])
        self.assertEqual(p["cobertura"]["presentes"], 0)
        self.assertEqual(p["cobertura"]["fuera_del_plan"], [["2026-09-02", "S9"]])

    def test_cero_faltante_e_invalido_son_distintos(self):
        self.assertEqual(interpretar("consumo_kwh", "0"), (0.0, "valido"))
        for texto in ("", "NA", "   "):
            self.assertEqual(interpretar("consumo_kwh", texto)[1], "faltante")
        for texto in ("-2", "NaN", "inf", "1,2", "abc", "1e999"):
            self.assertEqual(interpretar("consumo_kwh", texto)[1], "invalido")
        self.assertEqual(interpretar("horas_uso", "25")[1], "invalido")
        self.assertEqual(interpretar("temperatura_c", "-2")[1], "valido")

    def test_fecha_y_periodo(self):
        for texto in ("20260901", "2026-2-1", "2026-02-30"):
            with self.assertRaises(ValueError):
                fecha_iso(texto)
        for inicio, fin, sensores in [(date(2026, 9, 4), date(2026, 9, 1), ["S1"]),
                                     (date(2020, 1, 1), date(2026, 1, 1), ["S1"]),
                                     (date(2026, 9, 1), date(2026, 9, 4), []),
                                     (date(2026, 9, 1), date(2026, 9, 4), ["S1", "S1"]),
                                     (date(2026, 9, 1), date(2026, 9, 4), [" S1"]),
                                     (date(2026, 9, 1), date(2026, 9, 4), ["NA"])]:
            with self.assertRaises(ValueError):
                perfilar([], inicio, fin, sensores)

    def test_vacio_con_encabezado_y_conservacion(self):
        antes = copy.deepcopy(self.registros)
        perfil(self.registros)
        self.assertEqual(self.registros, antes)
        self.assertEqual(perfil([])["cobertura"]["presentes"], 0)
        self.assertEqual(self.huella, hashlib.sha256((UNIDAD / "datos/lecturas_sinteticas.csv").read_bytes()).hexdigest())

    def test_csv_bom_comillas_y_columnas_reordenadas(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "lecturas.csv"
            with ruta.open("w", encoding="utf-8-sig", newline="") as f:
                escritor = csv.writer(f)
                escritor.writerow(reversed(COLUMNAS))
                escritor.writerow(["8", "20", "10", "S,1", "2026-09-01"])
            filas, _ = leer_csv(ruta)
            self.assertEqual(filas[0]["sensor_id"], "S,1")
            self.assertEqual(filas[0]["consumo_kwh"], "10")

    def test_rechaza_estructura_rota(self):
        cabecera = ",".join(COLUMNAS)
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "lecturas.csv"
            for texto in ("", "fecha,fecha,consumo_kwh,temperatura_c,horas_uso\n",
                          cabecera + "\n2026-09-01,S1,2\n", cabecera + '\n"sin cierre'):
                ruta.write_text(texto, encoding="utf-8")
                with self.assertRaises((ValueError, csv.Error)):
                    leer_csv(ruta)
            ruta.write_text(cabecera + "\n", encoding="utf-8")
            self.assertEqual(leer_csv(ruta)[0], [])


class PruebasJSON(unittest.TestCase):
    def setUp(self):
        self.datos, _ = leer_eventos(UNIDAD / "datos/eventos_disponibilidad.json")

    def leer_copia(self, datos):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "eventos.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            return leer_eventos(ruta)

    def test_instante_de_decision_y_frontera_inclusiva(self):
        r = auditar(self.datos["registros"], instante("2026-09-05T09:00:00+00:00"))
        self.assertEqual(r["entradas_disponibles"], ["e01", "e03"])
        self.assertEqual([e["id"] for e in r["entradas_excluidas"]], ["e02", "e04"])
        self.assertEqual(r["objetivos"], ["e05", "e06"])

    def test_recibido_despues_y_objetivo_no_se_filtran_como_entradas(self):
        r = auditar(self.datos["registros"], instante("2026-09-05T09:10:00+00:00"))
        self.assertEqual(r["entradas_disponibles"], ["e01", "e02", "e03"])
        r = auditar(self.datos["registros"], instante("2026-09-05T12:00:00+00:00"))
        self.assertEqual(r["entradas_disponibles"], ["e01", "e02", "e03", "e04"])
        self.assertEqual(r["objetivos"], ["e05", "e06"])

    def test_zonas_equivalentes_y_hora_sin_zona(self):
        a = auditar(self.datos["registros"], instante("2026-09-05T09:00:00+00:00"))
        b = auditar(self.datos["registros"], instante("2026-09-05T04:00:00-05:00"))
        self.assertEqual(a, b)
        with self.assertRaises(ValueError):
            instante("2026-09-05T09:00:00")

    def test_llegada_anterior_a_observacion(self):
        self.datos["registros"][0]["disponible_en"] = "2026-09-05T07:00:00+00:00"
        with self.assertRaises(ValueError):
            self.leer_copia(self.datos)

    def test_ids_repetidos_y_rol_falso(self):
        datos = copy.deepcopy(self.datos)
        datos["registros"].append(datos["registros"][0])
        with self.assertRaises(ValueError):
            self.leer_copia(datos)
        self.datos["registros"][-1]["rol"] = "entrada"
        with self.assertRaises(ValueError):
            self.leer_copia(self.datos)

    def test_tipos_numericos_y_booleanos(self):
        for valor in (True, "12", float("nan"), float("inf"), -1):
            datos = copy.deepcopy(self.datos)
            datos["registros"][0]["valor"] = valor
            with self.assertRaises(ValueError):
                self.leer_copia(datos)
        self.datos["registros"][-1]["valor"] = 0
        with self.assertRaises(ValueError):
            self.leer_copia(self.datos)

    def test_clave_json_duplicada_y_esquema_incompleto(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "eventos.json"
            for texto in ('{"origen":{},"origen":{},"registros":[]}', '[]', '{"registros":{}}'):
                ruta.write_text(texto, encoding="utf-8")
                with self.assertRaises(ValueError):
                    leer_eventos(ruta)

    def test_vacio_y_entrada_no_mutada(self):
        antes = copy.deepcopy(self.datos)
        auditar(self.datos["registros"], instante("2026-09-05T09:00:00+00:00"))
        self.assertEqual(self.datos, antes)
        self.datos["registros"] = []
        datos, _ = self.leer_copia(self.datos)
        self.assertEqual(auditar(datos["registros"], instante("2026-09-05T09:00:00+00:00"))["entradas_disponibles"], [])


class PruebasComandos(unittest.TestCase):
    def test_exportacion_reproducible_y_sin_sobrescribir(self):
        for nombre, campo in (("01_perfilar_lecturas.py", "perfil"), ("02_auditar_disponibilidad.py", "auditoria")):
            with tempfile.TemporaryDirectory() as d:
                destino = Path(d) / "informe.json"
                comando = [sys.executable, str(UNIDAD / "ejemplos" / nombre), "--salida", str(destino)]
                r = subprocess.run(comando, cwd=d, capture_output=True, text=True, timeout=10)
                self.assertEqual(r.returncode, 0, r.stderr)
                original = destino.read_bytes()
                self.assertIn(campo, json.loads(original))
                r = subprocess.run(comando, cwd=d, capture_output=True, text=True, timeout=10)
                self.assertEqual(r.returncode, 2)
                self.assertEqual(destino.read_bytes(), original)

    def test_error_de_argumento_sin_traceback(self):
        comando = [sys.executable, str(UNIDAD / "ejemplos/02_auditar_disponibilidad.py"),
                   "--decision", "2026-09-05T09:00:00"]
        r = subprocess.run(comando, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 2)
        self.assertIn("zona", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()

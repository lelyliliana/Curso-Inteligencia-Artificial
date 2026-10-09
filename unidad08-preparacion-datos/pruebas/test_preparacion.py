"""Casos manuales, conservación de registros y separación del ajuste estadístico."""

import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
from preparacion import UNIDAD07, aplicar_correcciones, exportar, generar_informe, leer_csv, preparar
from transformaciones import Parametros, ajustar, leer_particiones, transformar

FUENTE = UNIDAD07 / "datos/lecturas_sinteticas.csv"
CORRECCIONES = UNIDAD / "datos/correcciones_verificadas.json"


class PruebasPreparacion(unittest.TestCase):
    def setUp(self):
        self.registros, self.huella = leer_csv(FUENTE)

    def probar_lote(self, lote):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "lote.json"
            ruta.write_text(json.dumps(lote), encoding="utf-8")
            return aplicar_correcciones(self.registros, ruta, self.huella)

    def test_resultados_manuales_sin_correccion(self):
        i = generar_informe(FUENTE)
        r = i["resultado"]
        self.assertEqual({f["registro_origen"] for f in r["preparados"]}, {1, 2, 3, 4, 5, 6, 9, 12})
        self.assertEqual([f["registro"] for f in r["cuarentena"]], [8, 10, 11])
        self.assertEqual(r["duplicados"], [{"registro": 7, "conservado_como_representante": 6}])
        self.assertEqual(i["despues"]["cobertura"]["presentes"], 8)

    def test_balance_y_trazabilidad_sin_perder_originales(self):
        i = generar_informe(FUENTE)
        r = i["resultado"]
        numeros = ([f["registro_origen"] for f in r["preparados"]]
                   + [f["registro"] for f in r["cuarentena"] + r["duplicados"]])
        self.assertEqual(sorted(numeros), list(range(1, 13)))
        self.assertEqual([f["original"] for f in i["trazabilidad"]], self.registros)

    def test_correccion_con_referencia_y_misma_unidad(self):
        i = generar_informe(FUENTE, CORRECCIONES)
        r = i["resultado"]
        self.assertEqual(len(r["preparados"]), 9)
        corregido = next(f for f in r["preparados"] if f["registro_origen"] == 8)
        self.assertEqual(corregido["valores"]["consumo_kwh"], 10)
        self.assertEqual(i["trazabilidad"][7]["original"]["consumo_kwh"], "-2")
        self.assertEqual(i["despues"]["cobertura"]["porcentaje"], 75.0)
        self.assertEqual([f["registro"] for f in r["cuarentena"]], [10, 11])

    def test_huella_distinta_rechaza_el_lote(self):
        lote = json.loads(CORRECCIONES.read_text(encoding="utf-8"))
        lote["sha256_origen"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "huella"):
            self.probar_lote(lote)

    def test_no_aplica_correcciones_ambiguas_o_sin_evidencia(self):
        for campo, valor in (("antes", "-3"), ("sensor_id", "S1"), ("despues", "-5"),
                             ("evidencia", ""), ("registro", 99), ("campo", "fecha")):
            lote = json.loads(CORRECCIONES.read_text(encoding="utf-8"))
            lote["cambios"][0][campo] = valor
            with self.assertRaises(ValueError):
                self.probar_lote(lote)
        lote = json.loads(CORRECCIONES.read_text(encoding="utf-8"))
        lote["cambios"].append(dict(lote["cambios"][0]))
        with self.assertRaisesRegex(ValueError, "dos veces"):
            self.probar_lote(lote)

    def test_conserva_faltantes_y_cero(self):
        r = preparar(self.registros)
        self.assertEqual(sum(bool(f["faltantes"]) for f in r["preparados"]), 3)
        fila = next(f for f in r["preparados"] if f["registro_origen"] == 12)
        self.assertEqual(fila["valores"]["consumo_kwh"], 0)
        self.assertIsNone(fila["valores"]["horas_uso"])

    def test_clave_invalida_va_a_cuarentena(self):
        datos = [dict(self.registros[0], fecha="2026-02-30"), dict(self.registros[1], sensor_id="NA")]
        r = preparar(datos)
        self.assertEqual(r["preparados"], [])
        self.assertEqual([f["motivos"] for f in r["cuarentena"]], [["clave_invalida"], ["clave_invalida"]])

    def test_conflicto_no_elige_la_fila_que_parece_valida(self):
        datos = [self.registros[0], dict(self.registros[0], consumo_kwh="-1")]
        r = preparar(datos)
        self.assertEqual(r["preparados"], [])
        self.assertEqual(len(r["cuarentena"]), 2)
        self.assertTrue(all(f["motivos"] == ["conflicto_de_clave"] for f in r["cuarentena"]))

    def test_duplicado_de_un_conflicto_conserva_referencia(self):
        datos = self.registros[9:11] + [self.registros[9]]
        r = preparar(datos)
        self.assertEqual(len(r["cuarentena"]), 2)
        self.assertEqual(r["duplicados"], [{"registro": 3, "conservado_como_representante": 1}])

    def test_no_muta_y_repetir_conserva_resultados(self):
        antes = copy.deepcopy(self.registros)
        primero = preparar(self.registros)
        self.assertEqual(preparar(self.registros), primero)
        self.assertEqual(self.registros, antes)
        copia, _, _ = aplicar_correcciones(self.registros, CORRECCIONES, self.huella)
        self.assertEqual(copia[7]["consumo_kwh"], "10")
        self.assertEqual(self.registros, antes)
        self.assertEqual(preparar([]), {"preparados": [], "duplicados": [], "cuarentena": []})

    def test_exportacion_huellas_y_no_sobrescritura(self):
        original = FUENTE.read_bytes()
        informe = generar_informe(FUENTE, CORRECCIONES)
        with tempfile.TemporaryDirectory() as d:
            destino = Path(d) / "preparacion"
            exportar(informe, destino)
            exportado = json.loads((destino / "informe.json").read_text(encoding="utf-8"))
            for nombre, huella in exportado["sha256_salidas"].items():
                self.assertEqual(huella, hashlib.sha256((destino / nombre).read_bytes()).hexdigest())
            with (destino / "preparados.csv").open(encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 9)
            self.assertEqual(next(f for f in filas if f["registro_origen"] == "3")["consumo_kwh"], "")
            with self.assertRaises(FileExistsError):
                exportar(informe, destino)
        self.assertEqual(FUENTE.read_bytes(), original)


class PruebasTransformaciones(unittest.TestCase):
    def test_parametros_y_valores_calculados_a_mano(self):
        p = ajustar([18, 20, None, 22])
        self.assertEqual(p, Parametros(20, 18, 22))
        self.assertEqual([r["escalado"] for r in transformar([18, 20, None, 22], p)], [0, .5, .5, 1])

    def test_fuera_del_rango_no_se_recorta(self):
        r = transformar([30, None, 40, 16], ajustar([18, 20, 22]))
        self.assertEqual([f["escalado"] for f in r], [3, .5, 5.5, -.5])

    def test_mascara_y_datos_originales(self):
        valores = [0, None, 2]
        antes = list(valores)
        r = transformar(valores, ajustar(valores))
        self.assertEqual([f["era_faltante"] for f in r], [False, True, False])
        self.assertEqual(r[1]["imputado"], 1)
        self.assertEqual(valores, antes)

    def test_validacion_no_modifica_ajuste(self):
        p = ajustar([18, 20, None, 22])
        transformar([30, None, 40], p)
        transformar([1000, None, -200], p)
        self.assertEqual(p, Parametros(20, 18, 22))
        self.assertEqual(ajustar([18, 20, None, 22, 30, None, 40]), Parametros(22, 18, 40))

    def test_todo_faltante_y_constante_requieren_decision(self):
        for valores in ([], [None, None], [3, None, 3]):
            with self.assertRaises(ValueError):
                ajustar(valores)

    def test_rechaza_invalidos_y_parametros_imposibles(self):
        for valor in (True, "20", float("nan"), float("inf"), 10**400):
            with self.assertRaises(ValueError):
                ajustar([18, valor, 22])
        for p in (Parametros(2, 1, 1), Parametros(0, 1, 3), Parametros(2, 1, float("inf"))):
            with self.assertRaises(ValueError):
                transformar([2], p)

    def test_esquema_e_identidades_entre_particiones(self):
        datos, _ = leer_particiones(UNIDAD / "datos/particiones_sinteticas.json")
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "particiones.json"
            datos["validacion"][0]["id"] = "t1"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identificadores"):
                leer_particiones(ruta)
            ruta.write_text('{"variable":"a","variable":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "repetida"):
                leer_particiones(ruta)


class PruebasComandos(unittest.TestCase):
    def test_ejecutan_fuera_de_la_raiz_y_exportan(self):
        with tempfile.TemporaryDirectory() as d:
            for programa, nombre in (("01_preparar_lecturas.py", "salida"), ("02_imputar_sin_filtracion.py", "transformacion.json")):
                destino = Path(d) / nombre
                comando = [sys.executable, str(UNIDAD / "ejemplos" / programa), "--salida", str(destino)]
                r = subprocess.run(comando, cwd=d, capture_output=True, text=True, timeout=10)
                self.assertEqual(r.returncode, 0, r.stderr)
                r = subprocess.run(comando, cwd=d, capture_output=True, text=True, timeout=10)
                self.assertEqual(r.returncode, 2)
                self.assertNotIn("Traceback", r.stderr)

    def test_contraejemplo_no_contamina_informe_correcto(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "informe.json"
            r = subprocess.run([sys.executable, str(UNIDAD / "ejemplos/02_imputar_sin_filtracion.py"),
                                "--comparar-filtracion", "--salida", str(ruta)],
                               capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Ajuste incorrecto: mediana=22", r.stdout)
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            self.assertEqual(datos["parametros_entrenamiento"], {"mediana": 20, "minimo": 18, "maximo": 22})


if __name__ == "__main__":
    unittest.main()

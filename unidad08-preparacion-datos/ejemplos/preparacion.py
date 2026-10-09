"""Preparación conservadora del esquema de la Unidad 7, con registro de decisiones."""

from collections import defaultdict
from datetime import date
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys

UNIDAD07 = Path(__file__).resolve().parents[2] / "unidad07-obtencion-datos"
sys.path.insert(0, str(UNIDAD07 / "ejemplos"))
from perfil_datos import COLUMNAS, RANGOS, interpretar, leer_csv, perfilar

POLITICA = "preparacion-conservadora-v1"


def sin_claves_repetidas(pares):
    resultado = {}
    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(f"Clave JSON repetida: {clave}")
        resultado[clave] = valor
    return resultado


def aplicar_correcciones(registros, ruta, huella):
    """Valida todas las correcciones contra el original antes de aplicar alguna."""
    copia = [dict(r) for r in registros]
    if ruta is None:
        return copia, [], None
    contenido = Path(ruta).read_bytes()
    datos = json.loads(contenido.decode("utf-8-sig"), object_pairs_hook=sin_claves_repetidas)
    if not isinstance(datos, dict) or set(datos) != {"sha256_origen", "cambios"}:
        raise ValueError("Las correcciones requieren sha256_origen y cambios.")
    if datos["sha256_origen"] != huella:
        raise ValueError("La huella de las correcciones no coincide con la fuente.")
    if not isinstance(datos["cambios"], list):
        raise ValueError("Cambios debe ser una lista.")
    campos = {"registro", "fecha", "sensor_id", "campo", "antes", "despues", "evidencia", "motivo"}
    usadas = set()
    for cambio in datos["cambios"]:
        if not isinstance(cambio, dict) or set(cambio) != campos:
            raise ValueError("Cada corrección debe incluir registro, clave, campo, antes, despues, evidencia y motivo.")
        n = cambio["registro"]
        if type(n) is not int or not 1 <= n <= len(registros):
            raise ValueError("Registro de corrección inexistente.")
        if any(not isinstance(cambio[c], str) for c in campos - {"registro"}):
            raise ValueError("Los campos de la corrección, salvo registro, deben ser textos.")
        campo = cambio["campo"]
        if campo not in RANGOS:
            raise ValueError("Solo se corrigen mediciones; no se pueden cambiar las claves.")
        if (n, campo) in usadas:
            raise ValueError("Una celda no puede corregirse dos veces en el mismo lote.")
        usadas.add((n, campo))
        original = registros[n - 1]
        if any(original[c] != cambio[c] for c in ("fecha", "sensor_id")) or original[campo] != cambio["antes"]:
            raise ValueError("La clave o el texto anterior no coincide con la corrección.")
        if not cambio["evidencia"].strip() or not cambio["motivo"].strip():
            raise ValueError("Cada corrección requiere evidencia y motivo no vacíos.")
        if interpretar(campo, cambio["despues"])[1] != "valido":
            raise ValueError("El valor corregido debe ser válido bajo el esquema.")
    for cambio in datos["cambios"]:
        copia[cambio["registro"] - 1][cambio["campo"]] = cambio["despues"]
    return copia, datos["cambios"], hashlib.sha256(contenido).hexdigest()


def preparar(registros):
    """Cada registro termina como conservado, duplicado o en cuarentena."""
    preparados, duplicados, cuarentena = [], [], []
    grupos = defaultdict(list)
    # Una clave inválida no puede entrar al agrupamiento de observaciones.
    for n, registro in enumerate(registros, 1):
        fecha, estado_f = interpretar("fecha", registro["fecha"])
        sensor, estado_s = interpretar("sensor_id", registro["sensor_id"])
        if estado_f != "valido" or estado_s != "valido":
            cuarentena.append({"registro": n, "motivos": ["clave_invalida"], "valores": dict(registro)})
        else:
            grupos[(fecha.isoformat(), sensor)].append((n, registro))
    for clave, grupo in grupos.items():
        firmas = {}
        representantes = []
        for n, registro in grupo:
            firma = tuple(registro[c] for c in COLUMNAS)
            if firma in firmas:
                duplicados.append({"registro": n, "conservado_como_representante": firmas[firma]})
            else:
                firmas[firma] = n
                representantes.append((n, registro))
        # No elegir arbitrariamente entre versiones diferentes de una misma clave.
        if len(representantes) > 1:
            for n, registro in representantes:
                cuarentena.append({"registro": n, "motivos": ["conflicto_de_clave"], "valores": dict(registro)})
            continue
        n, registro = representantes[0]
        valores, faltantes, invalidos = {}, [], []
        for campo in COLUMNAS:
            valor, estado = interpretar(campo, registro[campo])
            if estado == "invalido":
                invalidos.append(campo)
            elif estado == "faltante":
                faltantes.append(campo)
            valores[campo] = valor.isoformat() if isinstance(valor, date) else valor
        if invalidos:
            cuarentena.append({"registro": n, "motivos": [f"invalido:{c}" for c in invalidos], "valores": dict(registro)})
        else:
            preparados.append({"registro_origen": n, "valores": valores, "faltantes": faltantes})
    preparados.sort(key=lambda r: (r["valores"]["fecha"], r["valores"]["sensor_id"]))
    duplicados.sort(key=lambda r: r["registro"])
    cuarentena.sort(key=lambda r: r["registro"])
    return {"preparados": preparados, "duplicados": duplicados, "cuarentena": cuarentena}


def generar_informe(ruta, correcciones=None):
    originales, huella = leer_csv(ruta)
    corregidos, cambios, huella_cambios = aplicar_correcciones(originales, correcciones, huella)
    resultado = preparar(corregidos)
    posterior = [{c: "" if r["valores"][c] is None else str(r["valores"][c]) for c in COLUMNAS}
                 for r in resultado["preparados"]]
    plan = (date(2026, 9, 1), date(2026, 9, 4), ["S1", "S2", "S3"])
    estados = {}
    for r in resultado["preparados"]:
        estados[r["registro_origen"]] = "preparado"
    for r in resultado["cuarentena"]:
        estados[r["registro"]] = "cuarentena"
    for r in resultado["duplicados"]:
        estados[r["registro"]] = "duplicado"
    if (sorted(estados) != list(range(1, len(originales) + 1))
            or sum(len(resultado[k]) for k in resultado) != len(originales)):
        raise RuntimeError("La trazabilidad no cubre todos los registros de origen.")
    despues = perfilar(posterior, *plan)
    if despues["claves_repetidas"] or any(c["invalidos"] for c in despues["columnas"].values()):
        raise RuntimeError("La salida no cumple unicidad y validez de valores observados.")
    return {
        "politica": POLITICA, "python": platform.python_version(), "archivo_origen": Path(ruta).name,
        "sha256_origen": huella, "sha256_correcciones": huella_cambios, "correcciones": cambios,
        "plan_cobertura": {"inicio": "2026-09-01", "fin": "2026-09-04", "sensores": plan[2]},
        "antes": perfilar(originales, *plan), "despues": despues,
        "resultado": resultado,
        "trazabilidad": [{"registro": n, "estado": estados[n], "original": r}
                         for n, r in enumerate(originales, 1)],
    }


def exportar(informe, destino):
    """Crea una carpeta nueva; el informe final contiene huellas de los CSV."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    nombres = [*COLUMNAS, "registro_origen", "campos_faltantes"]
    with (destino / "preparados.csv").open("x", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=nombres)
        escritor.writeheader()
        for r in informe["resultado"]["preparados"]:
            escritor.writerow({**r["valores"], "registro_origen": r["registro_origen"],
                               "campos_faltantes": ";".join(r["faltantes"])})
    with (destino / "cuarentena.csv").open("x", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=[*COLUMNAS, "registro_origen", "motivos"])
        escritor.writeheader()
        for r in informe["resultado"]["cuarentena"]:
            escritor.writerow({**r["valores"], "registro_origen": r["registro"], "motivos": ";".join(r["motivos"])})
    registro_final = dict(informe)
    registro_final["sha256_salidas"] = {
        nombre: hashlib.sha256((destino / nombre).read_bytes()).hexdigest()
        for nombre in ("preparados.csv", "cuarentena.csv")
    }
    with (destino / "informe.json").open("x", encoding="utf-8") as f:
        json.dump(registro_final, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")

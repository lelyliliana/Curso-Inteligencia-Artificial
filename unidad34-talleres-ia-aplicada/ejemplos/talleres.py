"""Flujo compartido: seleccionar, guardar y evaluar solo el estado congelado."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import sklearn
import ambiente
import documentos
import energia

RAIZ = Path(__file__).resolve().parents[1]
MODULOS = {"energia": energia, "ambiente": ambiente, "documentos": documentos}


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def guardar(ruta, objeto):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(objeto):
    return hashlib.sha256(json.dumps(objeto, ensure_ascii=False, sort_keys=True, allow_nan=False,
                                     separators=(",", ":")).encode()).hexdigest()


def fuentes(taller):
    nombres = ["datos/protocolo.json", "datos/generar_datos.py", "ejemplos/talleres.py", f"ejemplos/{taller}.py",
               f"datos/{taller}/validacion.json"]
    nombres.append(f"datos/{taller}/" + ("corpus.json" if taller == "documentos" else "entrenamiento.json"))
    return {n: hashlib.sha256((RAIZ / n).read_bytes()).hexdigest() for n in nombres}


def cargar_modelo(ruta, taller):
    paquete = leer(ruta)
    cuerpo = {k: v for k, v in paquete.items() if k != "sha256"}
    if paquete.get("sha256") != huella(cuerpo):
        raise ValueError("La huella del modelo no coincide con su contenido")
    if paquete.get("version") != "u34-v1" or paquete.get("taller") != taller:
        raise ValueError("El modelo pertenece a otro taller o versión")
    if paquete["fuentes_sha256"] != fuentes(taller):
        raise ValueError("Las fuentes de desarrollo cambiaron; conservar evidencia o crear otra versión")
    return paquete


def desarrollo(taller):
    modulo = MODULOS[taller]
    protocolo = leer(RAIZ / "datos/protocolo.json")[taller]
    carpeta = RAIZ / "datos" / taller
    entrenamiento = leer(carpeta / ("corpus.json" if taller == "documentos" else "entrenamiento.json"))
    validacion = leer(carpeta / "validacion.json")
    elegido, estado, resultados = modulo.desarrollar(entrenamiento, validacion, protocolo)
    paquete = {"version": "u34-v1", "taller": taller, "elegido": elegido, "estado": estado,
               "protocolo": protocolo, "fuentes_sha256": fuentes(taller),
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__},
               "ids_ajuste": [f["id"] for f in entrenamiento], "ids_validacion": [f["id"] for f in validacion]}
    paquete["sha256"] = huella(paquete)
    # JSON de ida y vuelta, seguido por inferencia; no se vuelve a ajustar.
    recargado = json.loads(json.dumps(paquete, allow_nan=False))["estado"]
    repetido = (modulo.evaluar(recargado, validacion) if taller == "energia"
                else modulo.evaluar(recargado, validacion, protocolo))
    if repetido != resultados[elegido]:
        raise RuntimeError("La recarga alteró los resultados")
    return paquete, {"taller": taller, "fase": "validacion", "elegido": elegido,
                      "modelo_sha256": paquete["sha256"], "criterio": protocolo["criterio"],
                      "recarga_identica": True, "resultados": resultados}


def cierre(taller, ruta):
    paquete = cargar_modelo(ruta, taller)
    prueba = RAIZ / "datos" / taller / "prueba.json"
    filas = leer(prueba)
    modulo = MODULOS[taller]
    resultado = (modulo.evaluar(paquete["estado"], filas) if taller == "energia"
                 else modulo.evaluar(paquete["estado"], filas, paquete["protocolo"]))
    return {"taller": taller, "fase": "prueba", "elegido": paquete["elegido"],
            "modelo_sha256": paquete["sha256"], "datos_sha256": hashlib.sha256(prueba.read_bytes()).hexdigest(),
            "reajuste": False, "resultado": resultado}


def resumen(taller, nombre, resultado):
    if taller == "energia":
        return f"{nombre}: MAE={resultado['mae_kw']:.4f} kW; n={resultado['n']}"
    if taller == "ambiente":
        return f"{nombre}: costo={resultado['costo']}; FP={resultado['fp']}; FN={resultado['fn']}; n={resultado['n']}"
    return f"{nombre}: aceptadas={resultado['aceptadas']}/{resultado['n']}; costo={resultado['costo']}; respondidas={resultado['respondidas']}"


def ejecutar(taller):
    parser = argparse.ArgumentParser(description=f"Taller de {taller}: selección o cierre congelado.")
    parser.add_argument("--evaluar-prueba", action="store_true")
    parser.add_argument("--modelo", type=Path)
    parser.add_argument("--salida", type=Path, help="Carpeta para modelo e informe; por defecto solo imprime.")
    args = parser.parse_args()
    if args.evaluar_prueba != (args.modelo is not None):
        parser.error("Usa --evaluar-prueba junto con --modelo; desarrollo no recibe un modelo")
    try:
        if args.evaluar_prueba:
            informe = cierre(taller, args.modelo)
            print(f"Cierre {taller}: {resumen(taller, informe['elegido'], informe['resultado'])}")
            if args.salida:
                guardar(args.salida / "prueba.json", informe)
        else:
            paquete, informe = desarrollo(taller)
            for nombre, resultado in informe["resultados"].items():
                print(resumen(taller, nombre, resultado))
            print(f"Seleccionado {taller}: {informe['elegido']}. Recarga idéntica; prueba sin abrir.")
            if args.salida:
                guardar(args.salida / "modelo.json", paquete)
                guardar(args.salida / "validacion.json", informe)
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)

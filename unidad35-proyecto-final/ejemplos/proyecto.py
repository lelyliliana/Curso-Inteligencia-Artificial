"""Desarrollo y cierre reproducibles; tres candidatos fijados antes de ejecutar."""

import hashlib
import importlib.util
import json
from pathlib import Path
import platform

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import sklearn

from contrato import ErrorEntrada, validar, nivel, incrementos

RAIZ = Path(__file__).resolve().parents[1]
CURSO = RAIZ.parent
COMPARTIDO = CURSO / "unidad34-talleres-ia-aplicada/ejemplos/energia.py"
spec = importlib.util.spec_from_file_location("energia_u34", COMPARTIDO)
energia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(energia)


def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def guardar(ruta, objeto):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(objeto):
    return hashlib.sha256(json.dumps(objeto, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def fuentes():
    rutas = [RAIZ / n for n in ("datos/protocolo.json", "datos/generar_datos.py", "datos/entrenamiento.json",
                               "datos/validacion.json", "ejemplos/contrato.py", "ejemplos/proyecto.py")]
    rutas.append(COMPARTIDO)
    return {str(p.relative_to(CURSO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in rutas}


def preparar(filas, protocolo):
    admitidas, rechazadas = [], []
    for f in filas:
        try:
            entrada = validar(f["entrada"], protocolo["contrato"])
        except ErrorEntrada as error:
            rechazadas.append({"id": f["id"], "codigo": error.codigo})
        else:
            admitidas.append((f, entrada))
    return admitidas, rechazadas


def ajustar(filas, protocolo):
    pares, _ = preparar(filas, protocolo)
    filas_u34 = [{**nivel(e), "objetivo_kw": f["objetivo_kw"]} for f, e in pares]
    anteriores = energia.ajustar(filas_u34)
    x = np.asarray([incrementos(e) for _, e in pares])
    y = np.asarray([f["objetivo_kw"] - e["potencia_kw"] for f, e in pares])
    escala = StandardScaler().fit(x)
    estimador = Ridge(alpha=protocolo["alpha"], solver="svd").fit(escala.transform(x), y)
    incremento = {"tipo": "incremento", "media": escala.mean_.tolist(), "escala": escala.scale_.tolist(),
                  "coef": estimador.coef_.tolist(), "intercepto": float(estimador.intercept_),
                  "min_kw": anteriores["persistencia"]["min_kw"], "max_kw": anteriores["persistencia"]["max_kw"]}
    return {"persistencia": anteriores["persistencia"], "ridge_nivel": anteriores["ridge_1"], "ridge_incremento": incremento}


def predecir(modelo, entrada):
    if modelo["tipo"] == "incremento":
        x = np.asarray(incrementos(entrada))
        delta = float(((x - modelo["media"]) / modelo["escala"]) @ modelo["coef"] + modelo["intercepto"])
        prediccion = entrada["potencia_kw"] + delta
    else:
        prediccion = energia.predecir(modelo, nivel(entrada))["prediccion_kw"]
    fuera = not modelo["min_kw"] <= entrada["potencia_kw"] <= modelo["max_kw"]
    return {"prediccion_kw": prediccion, "instante_objetivo": entrada["objetivo"].isoformat(),
            "minutos_hasta_objetivo": entrada["minutos_hasta_objetivo"],
            "estado": "revisar" if fuera or prediccion < 0 else "estimacion", "fuera_rango": fuera}


def evaluar(modelo, filas, protocolo):
    pares, rechazadas = preparar(filas, protocolo)
    casos = [{"id": f["id"], "objetivo_kw": f["objetivo_kw"], **predecir(modelo, e)} for f, e in pares]
    n = len(casos)
    return {"total": len(filas), "admitidas": n, "cobertura": n / len(filas) if filas else None,
            "rechazadas": rechazadas, "mae_kw": sum(abs(c["prediccion_kw"] - c["objetivo_kw"]) for c in casos) / n if n else None,
            "sesgo_kw": sum(c["prediccion_kw"] - c["objetivo_kw"] for c in casos) / n if n else None,
            "marcadas_revision": sum(c["estado"] == "revisar" for c in casos), "casos": casos}


def aceptacion(resultado, referencia, protocolo):
    limites = protocolo["aceptacion_didactica"]
    mae, base = resultado["mae_kw"], referencia["mae_kw"]
    reduccion = 1 - mae / base if mae is not None and base not in (None, 0) else None
    condiciones = {"mae": mae is not None and mae <= limites["mae_maximo_kw"],
                   "mejora": reduccion is not None and reduccion >= limites["reduccion_minima_frente_persistencia"],
                   "cobertura": resultado["cobertura"] is not None and resultado["cobertura"] >= limites["cobertura_minima"]}
    return {"reduccion_relativa_mae": reduccion, "condiciones": condiciones,
            "cumple_criterio_didactico": all(condiciones.values()), "autoriza_uso_real": False}


def desarrollar():
    protocolo = leer(RAIZ / "datos/protocolo.json")
    train, val = (leer(RAIZ / "datos" / f"{f}.json") for f in ("entrenamiento", "validacion"))
    modelos = ajustar(train, protocolo)
    resultados = {k: evaluar(modelos[k], val, protocolo) for k in protocolo["candidatos"]}
    orden = protocolo["candidatos"]
    if any(r["mae_kw"] is None for r in resultados.values()):
        raise ValueError("No hay casos admitidos para seleccionar")
    elegido = min(orden, key=lambda k: (resultados[k]["mae_kw"], orden.index(k)))
    paquete = {"version": "u35-v1", "elegido": elegido, "modelo": modelos[elegido],
               "referencia": modelos["persistencia"], "protocolo": protocolo, "fuentes_sha256": fuentes(),
               "ids_ajuste": [f["id"] for f, _ in preparar(train, protocolo)[0]],
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__}}
    paquete["sha256"] = huella(paquete)
    recargado = json.loads(json.dumps(paquete, allow_nan=False))
    if evaluar(recargado["modelo"], val, protocolo) != resultados[elegido]:
        raise RuntimeError("La recarga alteró la evaluación")
    informe = {"fase": "validacion", "elegido": elegido, "modelo_sha256": paquete["sha256"],
               "recarga_identica": True, "resultados": resultados,
               "aceptacion": aceptacion(resultados[elegido], resultados["persistencia"], protocolo)}
    return paquete, informe


def cargar(ruta):
    paquete = leer(ruta)
    cuerpo = {k: v for k, v in paquete.items() if k != "sha256"}
    if paquete.get("sha256") != huella(cuerpo) or paquete.get("version") != "u35-v1":
        raise ValueError("Modelo con versión o huella inválida")
    if paquete["fuentes_sha256"] != fuentes():
        raise ValueError("Las fuentes del modelo cambiaron")
    return paquete


def cerrar(ruta):
    p = cargar(ruta)
    prueba = RAIZ / "datos/prueba.json"
    filas = leer(prueba)
    r = evaluar(p["modelo"], filas, p["protocolo"])
    base = evaluar(p["referencia"], filas, p["protocolo"])
    return {"fase": "prueba", "elegido": p["elegido"], "modelo_sha256": p["sha256"],
            "datos_sha256": hashlib.sha256(prueba.read_bytes()).hexdigest(), "reajuste": False,
            "resultado": r, "referencia": base, "aceptacion": aceptacion(r, base, p["protocolo"])}

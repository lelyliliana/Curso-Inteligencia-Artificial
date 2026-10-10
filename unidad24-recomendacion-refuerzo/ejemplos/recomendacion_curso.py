"""Popularidad y coseno de interacciones binarias, sin etiquetas de evaluación."""
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path

import numpy as np

UNIDAD = Path(__file__).resolve().parents[1]
K = 3
REGLAS = {"k": K, "candidatos": "catalogo_menos_historia_entrenamiento",
          "desempate": "popularidad_desc_id_asc", "sin_historia": "popularidad"}


def guardar_json(ruta, valor):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps(valor, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def leer_csv(ruta):
    with Path(ruta).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def leer_interacciones(ruta, items, parte):
    filas = leer_csv(ruta)
    if not filas:
        raise ValueError("No hay interacciones.")
    vistos, usuarios = set(), set()
    for fila in filas:
        if set(fila) != {"usuario", "elemento", "fecha"} or not fila["usuario"]:
            raise ValueError("Esquema de interacción inválido.")
        fecha = datetime.fromisoformat(fila["fecha"])
        dias = {"entrenamiento": range(1, 5), "validacion": (5,), "prueba": (6,)}[parte]
        if (fecha.tzinfo is None or fecha.utcoffset().total_seconds() != -18000
                or fecha.year != 2026 or fecha.month != 9 or fecha.day not in dias):
            raise ValueError("Fecha fuera de la partición declarada.")
        par = fila["usuario"], fila["elemento"]
        if par in vistos or fila["elemento"] not in items:
            raise ValueError("Interacción repetida o elemento fuera del catálogo.")
        if parte != "entrenamiento" and fila["usuario"] in usuarios:
            raise ValueError("Se espera un objetivo por usuario.")
        vistos.add(par)
        usuarios.add(fila["usuario"])
    return filas


def ajustar(items, filas):
    items = sorted(items)
    if not items or len(set(items)) != len(items):
        raise ValueError("Catálogo vacío o repetido.")
    usuarios = sorted({r["usuario"] for r in filas})
    indices = {item: j for j, item in enumerate(items)}
    iu = {u: i for i, u in enumerate(usuarios)}
    x = np.zeros((len(usuarios), len(items)))
    for r in filas:
        x[iu[r["usuario"]], indices[r["elemento"]]] = 1
    normas = np.linalg.norm(x, axis=0)
    divisor = np.outer(normas, normas)
    sim = np.divide(x.T @ x, divisor, out=np.zeros_like(divisor), where=divisor > 0)
    np.fill_diagonal(sim, 0)
    return {"formato": "recomendacion-v1", "reglas": dict(REGLAS), "items": items,
            "popularidad": x.sum(axis=0).tolist(), "similitud": sim.tolist(),
            "historiales": {u: [items[j] for j in np.flatnonzero(x[i])] for u, i in iu.items()}}


def recomendar(modelo, usuario, metodo=None, k=K):
    metodo = metodo or modelo["seleccionado"]
    if metodo not in ("popularidad", "coseno") or not isinstance(k, int) or k <= 0:
        raise ValueError("Método o K inválido.")
    items = modelo["items"]
    historia = set(modelo["historiales"].get(usuario, []))
    pop = np.asarray(modelo["popularidad"])
    if metodo == "coseno" and historia:
        indices = [i for i, item in enumerate(items) if item in historia]
        puntos = np.asarray(modelo["similitud"])[:, indices].sum(axis=1)
    else:
        puntos = pop
    orden = sorted((i for i, item in enumerate(items) if item not in historia),
                   key=lambda i: (-float(puntos[i]), -float(pop[i]), items[i]))
    return [items[i] for i in orden[:k]]


def metricas_lista(lista, objetivo):
    if not lista or len(set(lista)) != len(lista):
        raise ValueError("La lista debe tener elementos únicos.")
    posicion = lista.index(objetivo) + 1 if objetivo in lista else None
    return {"acierto": int(posicion is not None),
            "ndcg": 0.0 if posicion is None else float(1 / np.log2(posicion + 1))}


def evaluar(modelo, filas, metodo=None):
    casos = []
    for r in filas:
        historia = modelo["historiales"].get(r["usuario"], [])
        if r["elemento"] in historia or r["elemento"] not in modelo["items"]:
            raise ValueError("Objetivo fuera del conjunto candidato.")
        lista = recomendar(modelo, r["usuario"], metodo)
        casos.append({"usuario": r["usuario"], "objetivo": r["elemento"],
                      "grupo": "con_historia" if historia else "sin_historia",
                      "n_candidatos": len(modelo["items"]) - len(historia),
                      "lista": lista, **metricas_lista(lista, r["elemento"])})
    def resumir(grupo):
        if not grupo:
            return {"n": 0, "aciertos": 0, "recall_3": None, "ndcg_3": None, "cobertura": None}
        return {"n": len(grupo), "aciertos": sum(r["acierto"] for r in grupo),
                "recall_3": float(np.mean([r["acierto"] for r in grupo])),
                "ndcg_3": float(np.mean([r["ndcg"] for r in grupo])),
                "cobertura": len({i for r in grupo for i in r["lista"]}) / len(modelo["items"])}
    return {"global": resumir(casos),
            "grupos": {g: resumir([r for r in casos if r["grupo"] == g])
                       for g in ("con_historia", "sin_historia")}, "casos": casos}


def seleccionar(resultados):
    # El orden fija el desempate por la referencia más sencilla.
    return max(("popularidad", "coseno"), key=lambda m: resultados[m]["global"]["recall_3"])


def desarrollar(datos=UNIDAD / "datos"):
    datos = Path(datos)
    items = [r["elemento"] for r in leer_csv(datos / "catalogo.csv")]
    train = leer_interacciones(datos / "entrenamiento.csv", items, "entrenamiento")
    modelo = ajustar(items, train)
    val = leer_interacciones(datos / "validacion.csv", items, "validacion")
    resultados = {m: evaluar(modelo, val, m) for m in ("popularidad", "coseno")}
    modelo["seleccionado"] = seleccionar(resultados)
    modelo["fuentes"] = {p: huella(datos / f"{p}.csv") for p in ("catalogo", "entrenamiento", "validacion")}
    informe = {"protocolo": "v1", "seleccionado": modelo["seleccionado"],
               "validacion": resultados, "fuentes": modelo["fuentes"], "prueba": None}
    return modelo, informe


def cargar(ruta):
    m = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if m.get("formato") != "recomendacion-v1" or m.get("reglas") != REGLAS:
        raise ValueError("Formato o reglas incompatibles.")
    items = m["items"]
    pop, sim = np.asarray(m["popularidad"]), np.asarray(m["similitud"])
    if (not items or items != sorted(set(items)) or pop.shape != (len(items),)
            or sim.shape != (len(items), len(items)) or not np.isfinite(pop).all()
            or not np.isfinite(sim).all() or np.any(pop < 0) or np.any(sim < 0)
            or np.any(sim > 1 + 1e-12) or m["seleccionado"] not in ("popularidad", "coseno")):
        raise ValueError("Estado numérico incompatible.")
    for historia in m["historiales"].values():
        if len(historia) != len(set(historia)) or not set(historia) <= set(items):
            raise ValueError("Historial inválido.")
    return m


def cerrar(ruta_modelo, datos=UNIDAD / "datos"):
    modelo = cargar(ruta_modelo)
    ruta = Path(datos) / "prueba.csv"
    filas = leer_interacciones(ruta, modelo["items"], "prueba")
    return {"seleccionado": modelo["seleccionado"], "modelo_sha256": huella(ruta_modelo),
            "prueba_sha256": huella(ruta), "evaluacion": evaluar(modelo, filas)}


def exportar(modelo, informe, salida):
    salida = Path(salida)
    guardar_json(salida / "modelo.json", modelo)
    recargado = cargar(salida / "modelo.json")
    usuarios = [r["usuario"] for r in informe["validacion"][modelo["seleccionado"]]["casos"]]
    iguales = all(recomendar(modelo, u) == recomendar(recargado, u) for u in usuarios)
    if not iguales:
        raise RuntimeError("Cambió una lista tras recargar.")
    guardar_json(salida / "informe.json", informe)
    guardar_json(salida / "recarga.json", {"listas_iguales": iguales, "usuarios": len(usuarios),
                                           "modelo_sha256": huella(salida / "modelo.json")})

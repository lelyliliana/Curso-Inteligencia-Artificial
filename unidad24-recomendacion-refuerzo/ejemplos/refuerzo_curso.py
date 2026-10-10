"""Q-learning en una cuadrícula propia. No controla equipos ni usa servicios."""
import json
from pathlib import Path

import numpy as np

from recomendacion_curso import guardar_json, huella

ACCIONES = ("arriba", "derecha", "abajo", "izquierda")
DELTA = ((-1, 0), (0, 1), (1, 0), (0, -1))
ENTORNO = {"lado": 5, "inicio": 20, "meta": 4, "pozos": [6, 8, 16, 18],
           "prob_giro": 0.2, "r_meta": 1.0, "r_pozo": -1.0, "r_paso": -0.04,
           "limite": 60, "acciones": list(ACCIONES), "desempate_eval": "primera_accion"}
CONFIG = {"episodios": 2000, "alpha": 0.15, "gamma": 0.95,
          "epsilon_inicial": 1.0, "epsilon_final": 0.05, "decaimiento": 1500,
          "semillas": [2401, 2402, 2403, 2404, 2405]}
SEMILLAS_DESARROLLO = tuple(range(30000, 30200))
SEMILLAS_CIERRE = tuple(range(40000, 40200))


def transicion(estado, accion, azar, entorno=ENTORNO):
    """Función pura: azar uniforme [0,1), una muestra por transición."""
    lado = entorno["lado"]
    if not 0 <= estado < lado**2 or accion not in range(4) or not 0 <= azar < 1:
        raise ValueError("Estado, acción o azar fuera de rango.")
    if estado in [entorno["meta"], *entorno["pozos"]]:
        raise ValueError("Un terminal necesita reinicio; no admite otro paso.")
    p = entorno["prob_giro"]
    ejecutada = (accion - 1) % 4 if azar < p/2 else (accion + 1) % 4 if azar < p else accion
    fila, columna = divmod(estado, lado)
    df, dc = DELTA[ejecutada]
    nf, nc = fila + df, columna + dc
    siguiente = nf*lado + nc if 0 <= nf < lado and 0 <= nc < lado else estado
    terminal = siguiente == entorno["meta"] or siguiente in entorno["pozos"]
    recompensa = (entorno["r_meta"] if siguiente == entorno["meta"] else
                  entorno["r_pozo"] if siguiente in entorno["pozos"] else entorno["r_paso"])
    return siguiente, recompensa, terminal


def valor_actualizado(actual, recompensa, max_siguiente, terminal, alpha=0.15, gamma=0.95):
    objetivo = recompensa + (0.0 if terminal else gamma * max_siguiente)
    return actual + alpha * (objetivo - actual)


def epsilon(episodio, config=CONFIG):
    fraccion = min(episodio / (config["decaimiento"] - 1), 1.0)
    return config["epsilon_inicial"] + fraccion * (config["epsilon_final"] - config["epsilon_inicial"])


def accion_entrenamiento(q_fila, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    return int(rng.choice(np.flatnonzero(q_fila == q_fila.max())))


def entrenar(semilla, config=CONFIG, entorno=ENTORNO):
    # Corrientes distintas: cambiar exploración no consume sorteos del entorno.
    fuentes = np.random.SeedSequence(semilla).spawn(2)
    rng_ambiente, rng_agente = [np.random.default_rng(f) for f in fuentes]
    q = np.zeros((entorno["lado"]**2, 4))
    historia = []
    for episodio in range(config["episodios"]):
        estado, retorno, recompensa_total = entorno["inicio"], 0.0, 0.0
        terminal = False
        for t in range(entorno["limite"]):
            accion = accion_entrenamiento(q[estado], epsilon(episodio, config), rng_agente)
            siguiente, recompensa, terminal = transicion(estado, accion, rng_ambiente.random(), entorno)
            # Solo un terminal anula el valor futuro. El corte externo no lo anula.
            q[estado, accion] = valor_actualizado(q[estado, accion], recompensa, q[siguiente].max(),
                                                 terminal, config["alpha"], config["gamma"])
            retorno += config["gamma"]**t * recompensa
            recompensa_total += recompensa
            estado = siguiente
            if terminal:
                break
        historia.append({"episodio": episodio + 1, "retorno": retorno,
                         "recompensa_total": recompensa_total, "pasos": t + 1,
                         "exito": int(estado == entorno["meta"]), "truncado": int(not terminal)})
    return q, historia


def accion_referencia(estado, entorno=ENTORNO):
    return 0 if estado // entorno["lado"] > 0 else 1


def evaluar(q, semillas, entorno=ENTORNO, gamma=CONFIG["gamma"]):
    casos = []
    for semilla in semillas:
        rng = np.random.default_rng(semilla)
        estado, retorno, recompensa_total = entorno["inicio"], 0.0, 0.0
        terminal = False
        for t in range(entorno["limite"]):
            accion = accion_referencia(estado, entorno) if q is None else int(np.argmax(q[estado]))
            estado, recompensa, terminal = transicion(estado, accion, rng.random(), entorno)
            retorno += gamma**t * recompensa
            recompensa_total += recompensa
            if terminal:
                break
        casos.append({"semilla": semilla, "pasos": t + 1, "retorno": retorno,
                      "recompensa_total": recompensa_total, "exito": int(estado == entorno["meta"]),
                      "pozo": int(estado in entorno["pozos"]), "truncado": int(not terminal)})
    if not casos:
        raise ValueError("No hay episodios de evaluación.")
    resumen = {clave: float(np.mean([r[clave] for r in casos]))
               for clave in ("pasos", "retorno", "recompensa_total", "exito", "pozo", "truncado")}
    return {"n": len(casos), **resumen, "casos": casos}


def evaluar_tablas(modelo, semillas):
    referencia = evaluar(None, semillas, modelo["entorno"], modelo["config"]["gamma"])
    resultados = [{"semilla_entrenamiento": r["semilla"],
                   **evaluar(np.asarray(r["q"]), semillas, modelo["entorno"], modelo["config"]["gamma"])}
                  for r in modelo["tablas"]]
    agregado = {k: {"media": float(np.mean([r[k] for r in resultados])),
                   "desviacion": float(np.std([r[k] for r in resultados], ddof=0))}
                for k in ("exito", "pozo", "truncado", "retorno", "recompensa_total", "pasos")}
    return {"referencia": referencia, "q_learning": resultados, "entre_semillas": agregado}


def desarrollar():
    tablas, curvas = [], []
    for semilla in CONFIG["semillas"]:
        q, historia = entrenar(semilla)
        tablas.append({"semilla": semilla, "q": q.tolist()})
        bloques = [{"hasta_episodio": fin,
                    "retorno": float(np.mean([r["retorno"] for r in historia[fin-200:fin]])),
                    "exito": float(np.mean([r["exito"] for r in historia[fin-200:fin]]))}
                   for fin in range(200, CONFIG["episodios"] + 1, 200)]
        curvas.append({"semilla": semilla, "transiciones": sum(r["pasos"] for r in historia), "bloques": bloques})
    modelo = {"formato": "q-tabular-v1", "entorno": ENTORNO, "config": CONFIG, "tablas": tablas}
    informe = {"protocolo": "v1", "entrenamiento": curvas,
               "desarrollo": evaluar_tablas(modelo, SEMILLAS_DESARROLLO), "cierre": None}
    return modelo, informe


def cargar(ruta):
    m = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if (m.get("formato") != "q-tabular-v1" or m.get("entorno") != ENTORNO or m.get("config") != CONFIG
            or [r["semilla"] for r in m["tablas"]] != CONFIG["semillas"]):
        raise ValueError("Estado incompatible con el protocolo de esta práctica.")
    for r in m["tablas"]:
        q = np.asarray(r["q"])
        if q.shape != (25, 4) or not np.isfinite(q).all():
            raise ValueError("Tabla Q inválida.")
        if np.any(q[[ENTORNO["meta"], *ENTORNO["pozos"]]] != 0):
            raise ValueError("Se alteraron las filas terminales.")
    return m


def cerrar(ruta):
    m = cargar(ruta)
    return {"modelo_sha256": huella(ruta), "evaluacion": evaluar_tablas(m, SEMILLAS_CIERRE)}


def exportar(modelo, informe, salida):
    salida = Path(salida)
    guardar_json(salida / "modelo.json", modelo)
    nuevo = cargar(salida / "modelo.json")
    error = max(float(np.max(np.abs(np.asarray(a["q"]) - np.asarray(b["q"]))))
                for a, b in zip(modelo["tablas"], nuevo["tablas"]))
    if error != 0 or evaluar_tablas(nuevo, SEMILLAS_DESARROLLO) != informe["desarrollo"]:
        raise RuntimeError("Cambió la política o su evaluación al recargar.")
    guardar_json(salida / "informe.json", informe)
    guardar_json(salida / "recarga.json", {"error_maximo_q": error, "evaluacion_igual": True,
                                           "modelo_sha256": huella(salida / "modelo.json")})

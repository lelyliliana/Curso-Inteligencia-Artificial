"""Clasificación binaria con una capa oculta y retropropagación explícita."""
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import sys

import numpy as np
from threadpoolctl import threadpool_limits

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD.parent/"unidad10-flujo-lineas-base/ejemplos"))
from flujo import metricas_clasificacion

ENTRADAS = ("senal_a", "senal_b")
CONFIGURACIONES = {
    "xor": {"lineal": {"ocultas": 0, "l2": 0.}, "red8": {"ocultas": 8, "l2": 0.}},
    "ruido": {"lineal": {"ocultas": 0, "l2": 0.}, "red32": {"ocultas": 32, "l2": 0.},
              "red32_l2": {"ocultas": 32, "l2": .02}},
}
EPOCAS = {"xor": 3000, "ruido": 6000}
TASA = .15
CADA = 100
SEMILLA = 19
TOLERANCIA = 1e-12


def validar_xy(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.ndim != 2 or not len(x) or x.shape[1] < 1 or y.shape != (len(x),):
        raise ValueError("X debe ser una matriz no vacía e y un vector con una etiqueta por fila.")
    if not np.isfinite(x).all() or not np.isfinite(y).all() or not np.isin(y, [0, 1]).all():
        raise ValueError("Entradas finitas y etiquetas binarias requeridas.")
    return x, y


def sigmoide(s):
    s = np.asarray(s, dtype=float)
    if not np.isfinite(s).all():
        raise ValueError("Logits no finitos.")
    return np.exp(-np.logaddexp(0, -s))


def perdida(y, s):
    y, s = np.asarray(y, dtype=float), np.asarray(s, dtype=float)
    if y.ndim != 1 or not len(y) or y.shape != s.shape or not np.isin(y, [0, 1]).all() or not np.isfinite(s).all():
        raise ValueError("Pérdida: etiquetas binarias y logits finitos de igual forma vectorial.")
    # Evita log(0) y la cancelación de logaddexp(0,s)-y*s para logits grandes.
    return float(np.logaddexp(0, np.where(y == 1, -s, s)).mean())


def inicializar(d, h, semilla=SEMILLA):
    if type(d) is not int or d < 1 or type(h) is not int or h < 0:
        raise ValueError("Dimensiones enteras: d positivo, h no negativo.")
    if h == 0:
        return {"W": np.zeros(d), "b": np.zeros(1)}
    rng = np.random.Generator(np.random.PCG64(semilla))
    return {"W1": rng.normal(0, 1/np.sqrt(d), size=(d, h)), "b1": np.zeros(h),
            "W2": rng.normal(0, 1/np.sqrt(h), size=h), "b2": np.zeros(1)}


def copiar(parametros):
    return {k: np.asarray(v, dtype=float).copy() for k, v in parametros.items()}


def adelante(x, parametros):
    x = np.asarray(x, dtype=float)
    p = {k: np.asarray(v, dtype=float) for k, v in parametros.items()}
    if x.ndim != 2 or not len(x) or not np.isfinite(x).all() or any(not np.isfinite(v).all() for v in p.values()):
        raise ValueError("Matriz y parámetros finitos requeridos.")
    if set(p) == {"W", "b"}:
        if p["W"].shape != (x.shape[1],) or p["b"].shape != (1,):
            raise ValueError("Dimensiones incompatibles para la capa lineal.")
        s, h = x @ p["W"]+p["b"][0], None
    elif set(p) == {"W1", "b1", "W2", "b2"}:
        if p["W1"].ndim != 2 or p["W1"].shape[0] != x.shape[1]:
            raise ValueError("Dimensión incorrecta de W1.")
        ancho = p["W1"].shape[1]
        if ancho < 1 or p["b1"].shape != (ancho,) or p["W2"].shape != (ancho,) or p["b2"].shape != (1,):
            raise ValueError("Dimensiones incompatibles para la red.")
        h = np.tanh(x @ p["W1"]+p["b1"])
        s = h @ p["W2"]+p["b2"][0]
    else:
        raise ValueError("Estructura de parámetros desconocida.")
    if not np.isfinite(s).all():
        raise ValueError("La propagación produjo logits no finitos.")
    return s, h


def objetivo_gradiente(x, y, parametros, l2=0.):
    x, y = validar_xy(x, y)
    if not np.isfinite(l2) or l2 < 0:
        raise ValueError("L2 debe ser finita y no negativa.")
    p = {k: np.asarray(v, dtype=float) for k, v in parametros.items()}
    s, h = adelante(x, p)
    delta = (sigmoide(s)-y)/len(y)
    if h is None:
        g = {"W": x.T @ delta+l2*p["W"], "b": np.array([delta.sum()])}
    else:
        dh = delta[:, None]*p["W2"][None, :]*(1-h*h)
        g = {"W1": x.T @ dh+l2*p["W1"], "b1": dh.sum(axis=0),
             "W2": h.T @ delta+l2*p["W2"], "b2": np.array([delta.sum()])}
    penalizacion = l2/2*sum(float(np.sum(v*v)) for k, v in p.items() if k.startswith("W"))
    valor = perdida(y, s)+penalizacion
    if not np.isfinite(valor) or any(not np.isfinite(v).all() for v in g.values()):
        raise ValueError("Objetivo o gradiente no finitos.")
    return valor, g


def entrenar(x, y, xv, yv, config, epocas, tasa=TASA, cada=CADA, semilla=SEMILLA):
    x, y = validar_xy(x, y)
    xv, yv = validar_xy(xv, yv)
    if (x.shape[1] != xv.shape[1] or type(epocas) is not int or epocas < 1
            or type(cada) is not int or cada < 1 or not np.isfinite(tasa) or not 0 < tasa <= 1):
        raise ValueError("Dimensiones o presupuesto de entrenamiento inválidos.")
    p = inicializar(x.shape[1], config["ocultas"], semilla)
    iniciales, historial, mejor = copiar(p), [], None
    for epoca in range(epocas+1):
        objetivo, grad = objetivo_gradiente(x, y, p, config["l2"])
        if epoca % cada == 0 or epoca == epocas:
            entrada = {"epoca": epoca, "bce_entrenamiento": perdida(y, adelante(x, p)[0]),
                       "bce_validacion": perdida(yv, adelante(xv, p)[0]), "objetivo_entrenamiento": objetivo,
                       "norma_gradiente": float(np.sqrt(sum(np.sum(g*g) for g in grad.values())))}
            historial.append(entrada)
            if mejor is None or entrada["bce_validacion"] < mejor["bce"]-TOLERANCIA:
                mejor = {"bce": entrada["bce_validacion"], "epoca": epoca, "parametros": copiar(p)}
        if epoca < epocas:
            # Todos los gradientes se calculan con el mismo estado previo.
            p = {k: v-tasa*grad[k] for k, v in p.items()}
    return {"configuracion": dict(config), "epoca_elegida": mejor["epoca"],
            "parametros": mejor["parametros"], "parametros_finales": copiar(p), "parametros_iniciales": iniciales,
            "historial": historial, "n_parametros": sum(v.size for v in p.values())}


def leer_csv(ruta):
    contenido = Path(ruta).read_bytes()
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig")))
    esperadas = {"caso_id", *ENTRADAS, "objetivo"}
    if not lector.fieldnames or len(lector.fieldnames) != 4 or set(lector.fieldnames) != esperadas:
        raise ValueError("Esquema incorrecto: caso_id, senal_a, senal_b, objetivo.")
    filas, ids = [], set()
    for fila in lector:
        if None in fila or any(v is None or not v.strip() for v in fila.values()):
            raise ValueError("Filas incompletas o columnas adicionales.")
        fila = {k: v.strip() for k, v in fila.items()}
        if fila["caso_id"] in ids:
            raise ValueError("ID repetido dentro de una partición.")
        ids.add(fila["caso_id"])
        for c in ENTRADAS:
            fila[c] = float(fila[c])
            if not np.isfinite(fila[c]) or not -1 <= fila[c] <= 1:
                raise ValueError("Las señales deben ser finitas y pertenecer a [-1,1].")
        if fila["objetivo"] not in ("0", "1"):
            raise ValueError("El objetivo debe ser 0 o 1.")
        fila["objetivo"] = int(fila["objetivo"])
        filas.append(fila)
    if not filas:
        raise ValueError("Partición vacía.")
    return filas, {"archivo": Path(ruta).name, "n": len(filas), "sha256": hashlib.sha256(contenido).hexdigest()}


def matriz(filas):
    return np.array([[f[c] for c in ENTRADAS] for f in filas], dtype=float)


def ajustar_escala(x):
    media, escala = x.mean(axis=0), x.std(axis=0, ddof=0)
    if not np.isfinite(media).all() or not np.isfinite(escala).all() or (escala == 0).any():
        raise ValueError("Cada entrada debe variar en entrenamiento para este protocolo.")
    return {"media": media.tolist(), "escala": escala.tolist()}


def transformar(filas, escala):
    return (matriz(filas)-np.array(escala["media"]))/np.array(escala["escala"])


def evaluar(filas, parametros, escala):
    y = [f["objetivo"] for f in filas]
    s = adelante(transformar(filas, escala), parametros)[0]
    prob = sigmoide(s)
    pred = (prob >= .5).astype(int).tolist()
    m = metricas_clasificacion(y, pred)
    m["bce"] = perdida(y, s)
    return {"metricas": m, "predicciones": [{"caso_id": f["caso_id"], "real": f["objetivo"],
            "probabilidad": float(p), "logit": float(v), "prediccion": c} for f, p, v, c in zip(filas, prob, s, pred)]}


def seleccionar(candidatos):
    elegido = None
    for nombre, candidato in candidatos.items():
        if elegido is None or candidato["validacion"]["metricas"]["bce"] < candidatos[elegido]["validacion"]["metricas"]["bce"]-TOLERANCIA:
            elegido = nombre
    if elegido is None:
        raise ValueError("No hay candidatos.")
    return elegido


def serializar(valor):
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if isinstance(valor, dict):
        return {k: serializar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [serializar(v) for v in valor]
    return valor


def ejecutar_experimento(nombre, datos=None, evaluar_prueba=False, epocas=None):
    if nombre not in CONFIGURACIONES:
        raise ValueError("Laboratorio desconocido.")
    datos = Path(datos) if datos is not None else UNIDAD/"datos"/nombre
    presupuesto = EPOCAS[nombre] if epocas is None else epocas
    with threadpool_limits(limits=1):
        train, ft = leer_csv(datos/"entrenamiento.csv")
        if {f["objetivo"] for f in train} != {0, 1}:
            raise ValueError("Entrenamiento requiere ambas clases.")
        escala = ajustar_escala(matriz(train))
        val, fv = leer_csv(datos/"validacion.csv")
        ids = {f["caso_id"] for f in train}
        if ids.intersection(f["caso_id"] for f in val):
            raise ValueError("IDs compartidos entre particiones.")
        ids.update(f["caso_id"] for f in val)
        x, xv = transformar(train, escala), transformar(val, escala)
        y, yv = [f["objetivo"] for f in train], [f["objetivo"] for f in val]
        prevalencia = sum(y)/len(y)
        base = {"W": np.zeros(2), "b": np.array([np.log(prevalencia/(1-prevalencia))])}
        candidatos = {"prevalencia": {"configuracion": {"tipo": "constante"}, "epoca_elegida": 0,
                       "n_parametros": 1, "parametros": base, "historial": [],
                       "entrenamiento": evaluar(train, base, escala), "validacion": evaluar(val, base, escala)}}
        for candidato, config in CONFIGURACIONES[nombre].items():
            modelo = entrenar(x, y, xv, yv, config, presupuesto)
            modelo["entrenamiento"] = evaluar(train, modelo["parametros"], escala)
            modelo["validacion"] = evaluar(val, modelo["parametros"], escala)
            candidatos[candidato] = modelo
        elegido = seleccionar(candidatos)
        informe = {"laboratorio": nombre, "protocolo": "u19-v1-bce-validacion", "entradas": list(ENTRADAS),
                   "versiones": {"python": platform.python_version(), "numpy": np.__version__},
                   "fuentes": {"entrenamiento": ft, "validacion": fv}, "escala": escala,
                   "puntos_validacion": val,
                   "entrenamiento_config": {"epocas": presupuesto, "tasa": TASA, "cada": CADA, "semilla": SEMILLA,
                                             "umbral": .5, "tolerancia": TOLERANCIA, "lote": "completo"},
                   "candidatos": candidatos, "seleccionado": elegido, "prueba": None}
        # La prueba solo se abre tras finalizar ajuste, selección de época y arquitectura.
        if evaluar_prueba:
            prueba, fp = leer_csv(datos/"prueba.csv")
            if ids.intersection(f["caso_id"] for f in prueba):
                raise ValueError("IDs compartidos entre particiones.")
            informe["fuentes"]["prueba"] = fp
            informe["prueba"] = evaluar(prueba, candidatos[elegido]["parametros"], escala)
    return serializar(informe)


def exportar(informe, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    (salida/"informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for fase in ("entrenamiento", "validacion", "prueba"):
        if fase == "prueba":
            if informe["prueba"] is None:
                continue
            filas = [dict(candidato=informe["seleccionado"], **f) for f in informe["prueba"]["predicciones"]]
        else:
            filas = [dict(candidato=n, **f) for n, c in informe["candidatos"].items() for f in c[fase]["predicciones"]]
        with (salida/f"predicciones_{fase}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(filas)

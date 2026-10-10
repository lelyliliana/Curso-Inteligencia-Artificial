"""Representación, clasificación y persistencia de un corpus didáctico pequeño."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import unicodedata
import warnings

import numpy as np
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

UNIDAD = Path(__file__).resolve().parents[1]
CLASES = ("acceso", "material", "horario")
TOKENIZADOR = "nfc-casefold-letras-numeros-v1"
PATRON = re.compile(r"[^\W\d_]+|\d+", flags=re.UNICODE)
CAMPOS = ["id", "familia", "tema", "texto", "clase", "sha256"]


def tokens(texto):
    if not isinstance(texto, str):
        raise ValueError("El texto debe ser una cadena.")
    return PATRON.findall(unicodedata.normalize("NFC", texto.casefold()))


def terminos(texto, ngramas=1):
    if ngramas not in (1, 2):
        raise ValueError("Solo se admiten unigramas o unigramas y bigramas.")
    palabras = tokens(texto)
    return palabras + ([f"{a} {b}" for a, b in zip(palabras, palabras[1:])] if ngramas == 2 else [])


def vectorizador(ngramas=1):
    return TfidfVectorizer(tokenizer=tokens, token_pattern=None, lowercase=False,
                           ngram_range=(1, ngramas), norm="l2", smooth_idf=True,
                           sublinear_tf=False, dtype=np.float64)


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def leer_particion(ruta):
    with Path(ruta).open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        if lector.fieldnames != CAMPOS:
            raise ValueError("Cabecera de datos inesperada.")
        filas = list(lector)
    if not filas:
        raise ValueError("La partición está vacía.")
    familias = {}
    for fila in filas:
        if any(not isinstance(fila.get(c), str) or not fila[c].strip() for c in CAMPOS):
            raise ValueError("Campos vacíos o incompletos.")
        if None in fila or fila["clase"] not in CLASES or not tokens(fila["texto"]):
            raise ValueError("Fila o clase inválida.")
        if hashlib.sha256(fila["texto"].encode("utf-8")).hexdigest() != fila["sha256"]:
            raise ValueError("La huella del texto no coincide.")
        anterior = familias.setdefault(fila["familia"], fila["clase"])
        if anterior != fila["clase"]:
            raise ValueError("Una familia tiene etiquetas incompatibles.")
    validar_separacion(filas)
    return filas


def validar_separacion(*particiones):
    ids, documentos, familias_previas = set(), set(), set()
    for filas in particiones:
        familias = {f["familia"] for f in filas}
        if familias & familias_previas:
            raise ValueError("Familias compartidas entre particiones.")
        familias_previas.update(familias)
        for f in filas:
            documento = tuple(tokens(f["texto"]))
            if f["id"] in ids or documento in documentos:
                raise ValueError("ID o texto normalizado duplicado.")
            ids.add(f["id"])
            documentos.add(documento)


def etiquetas(filas):
    return np.array([CLASES.index(f["clase"]) for f in filas])


def softmax(logits):
    z = np.asarray(logits, dtype=float)
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def metricas(y, p):
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    if (y.ndim != 1 or len(y) == 0 or p.shape != (len(y), 3)
            or not np.isin(y, [0, 1, 2]).all() or not np.isfinite(p).all()
            or (p < 0).any() or not np.allclose(p.sum(axis=1), 1)):
        raise ValueError("Etiquetas o probabilidades inválidas.")
    y = y.astype(int)
    pred = p.argmax(axis=1)  # Empates: primer índice en CLASES.
    matriz = np.zeros((3, 3), dtype=int)
    np.add.at(matriz, (y, pred), 1)
    por_clase = []
    for k, nombre in enumerate(CLASES):
        tp, real, elegido = int(matriz[k, k]), int(matriz[k].sum()), int(matriz[:, k].sum())
        por_clase.append({"clase": nombre, "soporte": real,
                          "precision": tp / elegido if elegido else None,
                          "recobrado": tp / real if real else None,
                          "f1": 2 * tp / (real + elegido) if real + elegido else 0.0})
    return {"ce": float(-np.log(np.maximum(p[np.arange(len(y)), y], np.finfo(float).tiny)).mean()),
            "exactitud": float(np.mean(pred == y)),
            "macro_f1": float(np.mean([m["f1"] for m in por_clase])),
            "matriz": matriz.tolist(), "por_clase": por_clase}


def ajustar(filas, nombre):
    y = etiquetas(filas)
    if set(y) != {0, 1, 2}:
        raise ValueError("Entrenamiento debe contener las tres clases.")
    estado = {"formato": 1, "tokenizador": TOKENIZADOR, "clases": list(CLASES), "nombre": nombre}
    if nombre == "prevalencia":
        estado.update(tipo="prevalencia", probabilidades=(np.bincount(y, minlength=3) / len(y)).tolist())
        return estado
    if nombre not in ("unigramas", "bigramas"):
        raise ValueError("Candidato desconocido.")
    ngramas = 1 if nombre == "unigramas" else 2
    vec = vectorizador(ngramas)
    textos = [f["texto"] for f in filas]
    x = vec.fit_transform(textos)
    modelo = LogisticRegression(C=1.0, l1_ratio=0.0, solver="lbfgs", max_iter=1000, tol=1e-9)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        modelo.fit(x, y)
    estado.update(tipo="tfidf_logistica", ngramas=ngramas, vocabulario=vec.get_feature_names_out().tolist(),
                  idf=vec.idf_.tolist(), coeficientes=modelo.coef_.tolist(), sesgos=modelo.intercept_.tolist(),
                  ajuste={"C": 1.0, "l1_ratio": 0.0, "solver": "lbfgs", "max_iter": 1000,
                          "tol": 1e-9, "iteraciones": modelo.n_iter_.tolist()})
    # Contraste de la implementación legible con la biblioteca que ajustó el modelo.
    np.testing.assert_allclose(transformar(textos, estado), x.toarray(), atol=1e-12, rtol=0)
    np.testing.assert_allclose(predecir(textos, estado), modelo.predict_proba(x), atol=1e-12, rtol=0)
    return estado


def validar_estado(estado):
    if (estado.get("formato") != 1 or estado.get("tokenizador") != TOKENIZADOR
            or estado.get("clases") != list(CLASES)):
        raise ValueError("Formato, tokenizador u orden de clases incompatible.")
    if estado.get("tipo") == "prevalencia":
        p = np.array(estado["probabilidades"], dtype=float)
        if p.shape != (3,) or not np.isfinite(p).all() or (p <= 0).any() or not np.isclose(p.sum(), 1):
            raise ValueError("Prevalencias inválidas.")
    elif estado.get("tipo") == "tfidf_logistica":
        vocab = estado["vocabulario"]
        if (not vocab or any(not isinstance(t, str) or not t for t in vocab)
                or len(set(vocab)) != len(vocab) or estado["ngramas"] not in (1, 2)):
            raise ValueError("Vocabulario o ngramas inválidos.")
        n = len(vocab)
        for campo, forma in (("idf", (n,)), ("coeficientes", (3, n)), ("sesgos", (3,))):
            a = np.asarray(estado[campo], dtype=float)
            if a.shape != forma or not np.isfinite(a).all():
                raise ValueError(f"Forma o valores inválidos: {campo}.")
        if (np.asarray(estado["idf"]) < 1).any():
            raise ValueError("IDF suavizado debe ser al menos uno.")
    else:
        raise ValueError("Tipo de modelo desconocido.")


def transformar(textos, estado):
    """Versión densa didáctica; el ajuste usa matrices dispersas de scikit-learn."""
    vocabulario = {t: i for i, t in enumerate(estado["vocabulario"])}
    x = np.zeros((len(textos), len(vocabulario)), dtype=float)
    for i, texto in enumerate(textos):
        for termino, cuenta in Counter(terminos(texto, estado["ngramas"])).items():
            if termino in vocabulario:
                x[i, vocabulario[termino]] = cuenta
    x *= np.asarray(estado["idf"])
    normas = np.linalg.norm(x, axis=1, keepdims=True)
    return np.divide(x, normas, out=np.zeros_like(x), where=normas != 0)


def predecir(textos, estado):
    validar_estado(estado)
    if estado["tipo"] == "prevalencia":
        return np.tile(estado["probabilidades"], (len(textos), 1))
    return softmax(transformar(textos, estado) @ np.asarray(estado["coeficientes"]).T + estado["sesgos"])


def evaluar(filas, estado, con_metricas=True):
    textos = [f["texto"] for f in filas]
    p = predecir(textos, estado)
    vocab = set(estado.get("vocabulario", []))
    registros = []
    for fila, prob in zip(filas, p):
        ts = tokens(fila["texto"])
        oov = sum(t not in vocab for t in ts) / len(ts) if ts and vocab else None
        registros.append({**fila, "predicha": CLASES[int(prob.argmax())], "probabilidades": prob.tolist(),
                          "fraccion_tokens_desconocidos": oov,
                          "vector_cero": not any(t in vocab for t in ts) if vocab else None})
    return {"metricas": metricas(etiquetas(filas), p) if con_metricas else None, "registros": registros}


def seleccionar(candidatos):
    elegido = next(iter(candidatos))
    for nombre, candidato in candidatos.items():
        if candidato["validacion"]["metricas"]["ce"] < candidatos[elegido]["validacion"]["metricas"]["ce"] - 1e-9:
            elegido = nombre
    return elegido


def ejecutar_experimento(datos=UNIDAD / "datos", evaluar_prueba=False):
    datos = Path(datos)
    train = leer_particion(datos / "entrenamiento.csv")
    val = leer_particion(datos / "validacion.csv")
    validar_separacion(train, val)
    candidatos = {}
    for nombre in ("prevalencia", "unigramas", "bigramas"):
        estado = ajustar(train, nombre)
        candidatos[nombre] = {"estado": estado, "entrenamiento": evaluar(train, estado), "validacion": evaluar(val, estado)}
    elegido = seleccionar(candidatos)
    estado = candidatos[elegido]["estado"]
    informe = {"versiones": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__},
               "fuentes": {p: huella(datos / f"{p}.csv") for p in ("entrenamiento", "validacion")},
               "candidatos": candidatos, "seleccionado": elegido, "prueba": None}
    # Diagnósticos predefinidos: no intervienen en ajuste ni selección.
    diagnosticos = json.loads((datos / "diagnosticos.json").read_text(encoding="utf-8"))
    informe["fuentes"]["diagnosticos"] = huella(datos / "diagnosticos.json")
    informe["diagnosticos"] = {n: evaluar(diagnosticos, c["estado"], False) for n, c in candidatos.items()}
    if evaluar_prueba:
        prueba = leer_particion(datos / "prueba.csv")
        validar_separacion(train, val, prueba)
        informe["fuentes"]["prueba"] = huella(datos / "prueba.csv")
        informe["prueba"] = evaluar(prueba, estado)
    return informe


def escribir_json(ruta, contenido):
    Path(ruta).write_text(json.dumps(contenido, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def cargar_modelo(ruta):
    try:
        estado = json.loads(Path(ruta).read_text(encoding="utf-8"))
        validar_estado(estado)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Estructura de modelo incompleta o inválida.") from error
    return estado


def exportar(informe, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    elegido = informe["candidatos"][informe["seleccionado"]]
    escribir_json(salida / "informe.json", informe)
    escribir_json(salida / "modelo.json", elegido["estado"])
    recuperado = cargar_modelo(salida / "modelo.json")
    registros = elegido["validacion"]["registros"] + informe["diagnosticos"][informe["seleccionado"]]["registros"]
    referencia = np.array([r["probabilidades"] for r in registros])
    error = float(np.abs(predecir([r["texto"] for r in registros], recuperado) - referencia).max())
    if error > 1e-12:
        raise RuntimeError("La recarga no conserva las probabilidades.")
    escribir_json(salida / "recarga.json", {"error_maximo_probabilidades": error, "tolerancia": 1e-12,
                                           "modelo_sha256": huella(salida / "modelo.json")})
    conjuntos = {p: elegido[p] for p in ("entrenamiento", "validacion")}
    if informe["prueba"] is not None:
        conjuntos["prueba"] = informe["prueba"]
        escribir_json(salida / "cierre.json", {"seleccionado": informe["seleccionado"],
                                              "metricas": informe["prueba"]["metricas"],
                                              "fuentes": informe["fuentes"],
                                              "modelo_sha256": huella(salida / "modelo.json"),
                                              "reajuste": False})
    for particion, resultado in conjuntos.items():
        with (salida / f"predicciones_{particion}.csv").open("w", encoding="utf-8", newline="") as f:
            campos = ["id", "familia", "texto", "clase", "predicha", *[f"p_{c}" for c in CLASES], "fraccion_tokens_desconocidos", "vector_cero"]
            escritor = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
            escritor.writeheader()
            for r in resultado["registros"]:
                fila = {k: r[k] for k in campos if k in r}
                fila.update({f"p_{c}": p for c, p in zip(CLASES, r["probabilidades"])})
                escritor.writerow(fila)
    return error

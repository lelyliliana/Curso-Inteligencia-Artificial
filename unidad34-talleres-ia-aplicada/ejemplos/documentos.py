"""Asistente extractivo: TF-IDF, abstención y cita del párrafo completo; sin LLM."""

from collections import Counter
import math
import re
import unicodedata

VACIAS = set("a al de del el en es la las los para por que se un una y como donde cuando cuanto cual hay puedo mi".split())


def tokens(texto):
    texto = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return [t for t in re.findall(r"[a-z0-9]+", texto) if t not in VACIAS]


def validar(entrada):
    if not isinstance(entrada, dict) or set(entrada) != {"pregunta"}:
        raise ValueError("Documentos requiere exactamente: pregunta")
    texto = entrada["pregunta"]
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 400:
        raise ValueError("pregunta debe ser texto no vacío de hasta 400 caracteres")
    return texto


def vector(texto, vocabulario, idf):
    conteos = Counter(tokens(texto))
    v = [conteos[t] * peso for t, peso in zip(vocabulario, idf)]
    norma = math.sqrt(sum(x * x for x in v))
    return [x / norma for x in v] if norma else v


def ajustar(corpus):
    if not corpus or len({d["id"] for d in corpus}) != len(corpus):
        raise ValueError("El corpus debe tener documentos e identificadores únicos")
    textos = [tokens(d["texto"]) for d in corpus]
    vocabulario = sorted(set(t for ts in textos for t in ts))
    idf = [math.log((1 + len(corpus)) / (1 + sum(t in ts for ts in textos))) + 1 for t in vocabulario]
    return {"corpus": corpus, "vocabulario": vocabulario, "idf": idf,
            "matriz": [vector(d["texto"], vocabulario, idf) for d in corpus]}


def predecir(modelo, consulta):
    pregunta = validar(consulta)
    corpus = modelo["corpus"]
    if modelo["tipo"] == "solapamiento":
        q = set(tokens(pregunta))
        puntuaciones = [len(q & set(tokens(d["texto"]))) / len(q) if q else 0 for d in corpus]
    else:
        q = vector(pregunta, modelo["vocabulario"], modelo["idf"])
        puntuaciones = [sum(a * b for a, b in zip(q, v)) for v in modelo["matriz"]]
    i = min(range(len(corpus)), key=lambda j: (-puntuaciones[j], corpus[j]["id"]))
    score = puntuaciones[i]
    if score <= 0 or score < modelo["umbral"]:
        return {"estado": "sin_evidencia", "documento": None, "puntuacion": score,
                "respuesta": None, "cita": None}
    d = corpus[i]
    return {"estado": "fragmento", "documento": d["id"], "puntuacion": score,
            "respuesta": d["texto"], "cita": {"documento": d["id"], "version": d["version"],
                                                "inicio": 0, "fin": len(d["texto"])}}


def evaluar(modelo, preguntas, protocolo):
    casos = []
    for f in preguntas:
        salida = predecir(modelo, {"pregunta": f["pregunta"]})
        acierto = salida["documento"] == f["documento_esperado"]
        costo = (0 if acierto else protocolo["costo_abstencion_respondible"]
                 if salida["documento"] is None else protocolo["costo_respuesta_incorrecta"])
        casos.append({"id": f["id"], "familia": f["familia"], "esperado": f["documento_esperado"],
                      "aceptada": acierto, "costo": costo, **salida})
    respondidas = sum(c["documento"] is not None for c in casos)
    correctas_respondidas = sum(c["aceptada"] and c["documento"] is not None for c in casos)
    familias = sorted({c["familia"] for c in casos})
    return {"n": len(casos), "aceptadas": sum(c["aceptada"] for c in casos),
            "respondidas": respondidas, "costo": sum(c["costo"] for c in casos),
            "cobertura": respondidas / len(casos),
            "precision_respondidas": correctas_respondidas / respondidas if respondidas else None,
            "familias_completas": sum(all(c["aceptada"] for c in casos if c["familia"] == f) for f in familias),
            "familias": len(familias), "casos": casos}


def desarrollar(corpus, validacion, protocolo):
    indice = ajustar(corpus)
    candidatos = protocolo["candidatos"]
    modelos = {"solapamiento": {"tipo": "solapamiento", "corpus": corpus, "umbral": 0.0}}
    for nombre in candidatos[1:]:
        modelos[nombre] = {**indice, "tipo": "tfidf", "umbral": float(nombre.split("_")[1])}
    resultados = {k: evaluar(modelos[k], validacion, protocolo) for k in candidatos}
    elegido = min(candidatos, key=lambda k: (resultados[k]["costo"], resultados[k]["respondidas"], candidatos.index(k)))
    return elegido, modelos[elegido], resultados

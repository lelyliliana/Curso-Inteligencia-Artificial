"""Fusión de rasgos de imagen y texto; no utiliza un modelo de visión-lenguaje."""

from copy import deepcopy
import io
import math
from pathlib import Path
import re

import numpy as np
from PIL import Image
import torch
from torch import nn
import torch.nn.functional as F

from comun import (UNIDAD, cargar, comprobar_familias, configurar, estado_json, guardar,
                   huella, huellas_codigo, restaurar_estado, verificar_huellas)

DATOS = UNIDAD / "datos/multimodal"
MODOS = ("vision", "texto", "fusion")
CONFIG = {"ocultas": 8, "semilla": 3111, "epocas": 120, "evaluar_cada": 10, "lr": .03,
          "imagen": [20, 16], "regiones": [[5, 11, 2, 7], [5, 11, 13, 18]],
          "clases": ["apagada", "encendida"], "umbral_regla": .5}


def rasgos_imagen(ruta):
    if ruta is None:
        raise ValueError("imagen_ausente")
    with Image.open(ruta) as imagen:
        if imagen.format != "PNG" or imagen.mode != "L" or imagen.size != (20, 16):
            raise ValueError("imagen_incompatible")
        x = np.asarray(imagen, dtype=np.float32) / 255
    return np.array([x[a:b, c:d].mean() for a, b, c, d in CONFIG["regiones"]], dtype=np.float32)


def rasgos_texto(texto):
    if not isinstance(texto, str) or not texto:
        raise ValueError("texto_ausente")
    m = re.fullmatch(r"(?:estado|consulta) (izquierda|derecha)", texto)
    if m is None:
        raise ValueError("texto_fuera_gramatica")
    return np.array([m[1] == "izquierda", m[1] == "derecha"], dtype=np.float32)


def rasgos(ruta, texto, modo):
    if modo not in MODOS:
        raise ValueError("modo_invalido")
    partes = []
    if modo != "texto":
        partes.append(rasgos_imagen(ruta))
    if modo != "vision":
        partes.append(rasgos_texto(texto))
    return np.concatenate(partes)


def leer(fase):
    if fase not in ("entrenamiento", "validacion", "prueba"):
        raise ValueError("Fase inválida")
    filas = cargar(DATOS / f"{fase}.json")
    for f in filas:
        if (set(f) != {"id", "familia", "imagen", "texto", "etiqueta"}
                or type(f["etiqueta"]) is not int or f["etiqueta"] not in (0, 1)
                or not isinstance(f["familia"], str) or not f["familia"]):
            raise ValueError("Registro multimodal inválido")
        ruta = (DATOS / f["imagen"]).resolve()
        if not ruta.is_relative_to(DATOS.resolve()):
            raise ValueError("Ruta de imagen fuera del conjunto")
    return filas


def preparar(filas, modo):
    x = np.stack([rasgos(DATOS / f["imagen"], f["texto"], modo) for f in filas])
    return torch.tensor(x), torch.tensor([f["etiqueta"] for f in filas], dtype=torch.long)


def crear(modo):
    if modo not in MODOS:
        raise ValueError("Modo inválido")
    configurar()
    torch.manual_seed(CONFIG["semilla"])
    return nn.Sequential(nn.Linear(4 if modo == "fusion" else 2, CONFIG["ocultas"]),
                         nn.Tanh(), nn.Linear(CONFIG["ocultas"], 2))


@torch.inference_mode()
def evaluar(modelo, modo, filas):
    modelo.eval()
    x, y = preparar(filas, modo)
    logits = modelo(x)
    pred = logits.argmax(1)
    matriz = [[int(((y == i) & (pred == j)).sum()) for j in (0, 1)] for i in (0, 1)]
    casos = [{"id": f["id"], "familia": f["familia"], "etiqueta": int(y[i]),
              "predicha": int(pred[i]), "prob_encendida": float(logits.softmax(1)[i, 1]),
              "correcta": bool(pred[i] == y[i])} for i, f in enumerate(filas)]
    familias = {f["familia"] for f in filas}
    return {"total": len(filas), "correctas": int((pred == y).sum()),
            "exactitud": float((pred == y).double().mean()), "ce": float(F.cross_entropy(logits, y)),
            "matriz": matriz, "familias": len(familias),
            "familias_completas": sum(all(c["correcta"] for c in casos if c["familia"] == fam) for fam in familias),
            "casos": casos}


def referencia(filas):
    aciertos = 0
    for f in filas:
        luces = rasgos_imagen(DATOS / f["imagen"])
        lado = int(rasgos_texto(f["texto"]).argmax())
        aciertos += int(luces[lado] > CONFIG["umbral_regla"]) == f["etiqueta"]
    return {"correctas": aciertos, "total": len(filas)}


def entrenar(modo, train, val, epocas=CONFIG["epocas"]):
    comprobar_familias(train, val)
    modelo = crear(modo)
    opt = torch.optim.Adam(modelo.parameters(), lr=CONFIG["lr"])
    x, y = preparar(train, modo)
    mejor_ce, mejor, elegida, curva = math.inf, None, 0, []
    for epoca in range(epocas + 1):
        if epoca:
            modelo.train()
            opt.zero_grad(set_to_none=True)
            F.cross_entropy(modelo(x), y).backward()
            opt.step()
        if epoca % CONFIG["evaluar_cada"] == 0 or epoca == epocas:
            a, b = evaluar(modelo, modo, train), evaluar(modelo, modo, val)
            curva.append({"epoca": epoca, "ce_train": a["ce"], "ce_val": b["ce"]})
            if b["ce"] < mejor_ce:
                mejor_ce, mejor, elegida = b["ce"], deepcopy(modelo.state_dict()), epoca
    modelo.load_state_dict(mejor)
    modelo.eval()
    return modelo, {"epoca": elegida, "curva": curva, "parametros": sum(p.numel() for p in modelo.parameters())}


def fuentes():
    r = huellas_codigo(["ejemplos/multimodal.py"])
    for fase in ("entrenamiento", "validacion"):
        p = f"datos/multimodal/{fase}.json"
        r[p] = huella(UNIDAD / p)
        for fila in leer(fase):
            p = "datos/multimodal/" + fila["imagen"]
            r[p] = huella(UNIDAD / p)
    return r


def empaquetar(modelo, modo):
    return {"formato": "fusion-curso-v1", "modo": modo, "config": CONFIG,
            "fuentes": fuentes(), "estado": estado_json(modelo)}


def restaurar(obj):
    if (obj.get("formato") != "fusion-curso-v1" or obj.get("config") != CONFIG
            or obj.get("fuentes") != fuentes()):
        raise ValueError("Modelo multimodal incompatible")
    verificar_huellas(obj["fuentes"])
    return restaurar_estado(crear(obj["modo"]), obj["estado"])


@torch.inference_mode()
def predecir(modelo, modo, ruta, texto):
    try:
        x = rasgos(ruta, texto, modo)
    except (ValueError, OSError) as e:
        return {"estado": "rechazada", "motivo": str(e), "clase": None}
    modelo.eval()
    logits = modelo(torch.tensor(x).unsqueeze(0))
    return {"estado": "ok", "clase": CONFIG["clases"][int(logits.argmax(1))]}


def desarrollar(salida=None):
    train, val = leer("entrenamiento"), leer("validacion")
    comprobar_familias(train, val)
    resultados, estados = {}, {}
    for modo in MODOS:
        modelo, historia = entrenar(modo, train, val)
        obj = empaquetar(modelo, modo)
        nuevo = restaurar(obj)
        with torch.inference_mode():
            x = preparar(val, modo)[0]
            if not torch.equal(modelo(x), nuevo(x)):
                raise RuntimeError("La recarga cambió logits")
        r = evaluar(modelo, modo, val)
        if r != evaluar(nuevo, modo, val):
            raise RuntimeError("La recarga cambió predicciones")
        resultados[modo] = {"entrenamiento": historia, "validacion": r}
        estados[modo] = obj
    elegido = min(MODOS, key=lambda m: (resultados[m]["validacion"]["ce"], m))
    informe = {"seleccionado": elegido, "candidatos": resultados, "config": CONFIG,
               "referencia_regla": referencia(val), "recarga_identica": True, "prueba": None}
    if salida:
        for nombre, obj in estados.items():
            guardar(salida / f"{nombre}.json", obj)
        guardar(salida / "modelo.json", estados[elegido])
        guardar(salida / "informe.json", informe)
    return estados[elegido], informe


def cerrar(ruta):
    obj = cargar(ruta)
    modelo = restaurar(obj)
    grupos = [leer(f) for f in ("entrenamiento", "validacion", "prueba")]
    comprobar_familias(*grupos)
    filas = grupos[-1]
    imagenes = [{f["imagen"] for f in grupo} for grupo in grupos]
    if any(imagenes[i] & imagenes[j] for i in range(3) for j in range(i)):
        raise ValueError("Imágenes compartidas entre particiones")
    # El diagnóstico de pares utiliza una escena cuyas luces sean distintas.
    fila = next(f for f in filas if rasgos_imagen(DATOS / f["imagen"])[0] < .5
                and rasgos_imagen(DATOS / f["imagen"])[1] > .5)
    imagen = DATOS / fila["imagen"]
    incompatible = io.BytesIO()
    Image.new("RGB", (20, 16)).save(incompatible, format="PNG")
    incompatible.seek(0)
    diagnosticos = {"imagen_ausente": predecir(modelo, obj["modo"], None, "estado izquierda"),
                   "texto_ausente": predecir(modelo, obj["modo"], imagen, None),
                   "texto_ambiguo": predecir(modelo, obj["modo"], imagen, "no consultes izquierda; consulta derecha"),
                   "imagen_incompatible": predecir(modelo, obj["modo"], incompatible, "estado izquierda"),
                   "izquierda": predecir(modelo, obj["modo"], imagen, "estado izquierda"),
                   "derecha": predecir(modelo, obj["modo"], imagen, "estado derecha")}
    return {"modo": obj["modo"], "modelo_sha256": huella(ruta),
            "prueba_sha256": huella(DATOS / "prueba.json"),
            "imagenes_sha256": {f["imagen"]: huella(DATOS / f["imagen"]) for f in filas},
            "evaluacion": evaluar(modelo, obj["modo"], filas), "referencia_regla": referencia(filas),
            "escena_diagnostico": fila["familia"], "diagnosticos": diagnosticos}

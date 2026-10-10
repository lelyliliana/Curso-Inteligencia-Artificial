"""LoRA en la cabeza del transformer propio; nunca altera el checkpoint base."""

from copy import deepcopy
import math
import re
import sys

import torch
from torch import nn
import torch.nn.functional as F

from comun import (UNIDAD, cargar, comprobar_familias, configurar, estado_json, guardar,
                   huella, huellas_codigo, restaurar_estado, verificar_huellas)

sys.path.insert(0, str(UNIDAD.parent / "unidad25-transformers-generativos/ejemplos"))
import transformer_curso as previo

BASE = UNIDAD.parent / "unidad25-transformers-generativos/recursos/generacion/modelo.json"
CODIGOS = {"bajo": "alto", "medio": "bajo", "alto": "medio"}
CONFIG = {"rango": 2, "alpha": 2, "semilla": 3101, "epocas": 160,
          "evaluar_cada": 20, "lr_lora": .03, "lr_completo": .003, "clip": 1.0}
METODOS = ("base", "lora", "completo")


class LinealLoRA(nn.Module):
    def __init__(self, base, rango=2, alpha=2):
        super().__init__()
        if not isinstance(base, nn.Linear) or type(rango) is not int or not 1 <= rango <= min(base.weight.shape):
            raise ValueError("Capa o rango inválidos")
        if type(alpha) not in (int, float) or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("alpha inválido")
        self.base = base.requires_grad_(False)
        self.rango, self.alpha = rango, alpha
        self.activo = True
        self.A = nn.Parameter(torch.randn(rango, base.in_features, dtype=base.weight.dtype) * .02)
        self.B = nn.Parameter(torch.zeros(base.out_features, rango, dtype=base.weight.dtype))

    def forward(self, x):
        base = self.base(x)
        return base + F.linear(F.linear(x, self.A), self.B) * (self.alpha / self.rango) if self.activo else base

    def fusionada(self):
        capa = deepcopy(self.base)
        with torch.no_grad():
            capa.weight.add_((self.alpha / self.rango) * self.B @ self.A)
        return capa


def modelo_inicial(metodo):
    if metodo not in METODOS:
        raise ValueError("Método inválido")
    configurar()
    modelo, vocab = previo.cargar(BASE)
    modelo.requires_grad_(metodo == "completo")
    if metodo == "lora":
        torch.manual_seed(CONFIG["semilla"])
        modelo.salida = LinealLoRA(modelo.salida, CONFIG["rango"], CONFIG["alpha"])
    return modelo, vocab


def regla(fila, anterior=False):
    m = re.fullmatch(r"tema (energia|agua|aire|suelo) zona (norte|sur|este|oeste) nivel (bajo|medio|alto) formato (breve|detallado) salida", fila["prefijo"])
    if m is None:
        raise ValueError("Prefijo fuera de gramática")
    tema, zona, nivel, formato = m.groups()
    nivel = nivel if anterior else CODIGOS[nivel]
    return f"{tema} {zona} {nivel} ." if formato == "breve" else f"informe {tema} en {zona} con nivel {nivel} ."


def evaluar(modelo, vocab, filas):
    r = previo.evaluar(modelo, vocab, filas)
    familias = {f["familia"] for f in filas}
    aciertos = {c["id"]: c["exacta"] for c in r["casos"]}
    r["familias_completas"] = sum(all(aciertos[f["id"]] for f in filas if f["familia"] == fam) for fam in familias)
    return r


def adaptar(metodo, train, val, epocas=CONFIG["epocas"]):
    comprobar_familias(train, val)
    modelo, vocab = modelo_inicial(metodo)
    parametros = [p for p in modelo.parameters() if p.requires_grad]
    n_entrenables = sum(p.numel() for p in parametros)
    if metodo == "base":
        return modelo, vocab, {"entrenables": 0, "epoca": 0, "curva": []}
    opt = torch.optim.Adam(parametros, lr=CONFIG[f"lr_{metodo}"])
    x, y, mask = previo.preparar(train, vocab)
    mejor_ce, epoca_elegida, mejor, curva = math.inf, 0, None, []
    for epoca in range(epocas + 1):
        if epoca:
            modelo.train()
            opt.zero_grad(set_to_none=True)
            loss = previo.perdida(modelo(x), y, mask)
            loss.backward()
            nn.utils.clip_grad_norm_(parametros, CONFIG["clip"])
            opt.step()
        if epoca % CONFIG["evaluar_cada"] == 0 or epoca == epocas:
            a = previo.evaluar(modelo, vocab, train, False)
            b = previo.evaluar(modelo, vocab, val, False)
            curva.append({"epoca": epoca, "ce_train": a["ce"], "ce_val": b["ce"]})
            if b["ce"] < mejor_ce:
                mejor_ce, epoca_elegida, mejor = b["ce"], epoca, deepcopy(modelo.state_dict())
    modelo.load_state_dict(mejor)
    modelo.eval()
    return modelo, vocab, {"entrenables": n_entrenables, "epoca": epoca_elegida, "curva": curva}


def fuentes():
    r = huellas_codigo(["ejemplos/adaptacion.py", "../unidad25-transformers-generativos/ejemplos/transformer_curso.py"])
    for fase in ("entrenamiento", "validacion"):
        ruta = f"datos/adaptacion/{fase}.json"
        r[ruta] = huella(UNIDAD / ruta)
    return r


def empaquetar(modelo, metodo, vocab):
    estado = {"A": modelo.salida.A.detach().tolist(), "B": modelo.salida.B.detach().tolist()} if metodo == "lora" else estado_json(modelo) if metodo == "completo" else {}
    return {"formato": "adaptacion-curso-v1", "metodo": metodo, "base_sha256": huella(BASE),
            "config": CONFIG, "vocabulario": vocab, "fuentes": fuentes(), "estado": estado}


def restaurar(obj):
    if (obj.get("formato") != "adaptacion-curso-v1" or obj.get("base_sha256") != huella(BASE)
            or obj.get("config") != CONFIG or obj.get("fuentes") != fuentes()):
        raise ValueError("Adaptación incompatible con esta base/configuración")
    verificar_huellas(obj["fuentes"])
    modelo, vocab = modelo_inicial(obj["metodo"])
    if vocab != obj.get("vocabulario"):
        raise ValueError("Vocabulario incompatible")
    if obj["metodo"] == "lora":
        estado = estado_json(modelo.salida)
        if set(obj["estado"]) != {"A", "B"}:
            raise ValueError("Se esperan únicamente A y B")
        estado.update(obj["estado"])
        restaurar_estado(modelo.salida, estado)
    elif obj["metodo"] == "completo":
        restaurar_estado(modelo, obj["estado"])
    elif obj["estado"] != {}:
        raise ValueError("La base congelada no necesita estado extra")
    return modelo.eval(), vocab


def seleccionar(resultados):
    return min(METODOS, key=lambda m: (-resultados[m]["validacion"]["n_exactas"],
                                      resultados[m]["entrenamiento"]["entrenables"],
                                      resultados[m]["validacion"]["ce"], m))


def desarrollar(salida=None):
    train = previo.leer(UNIDAD / "datos/adaptacion/entrenamiento.json")
    val = previo.leer(UNIDAD / "datos/adaptacion/validacion.json")
    anterior = [{**f, "continuacion": regla(f, anterior=True)} for f in val]
    resultados, estados = {}, {}
    for metodo in METODOS:
        modelo, vocab, historia = adaptar(metodo, train, val)
        obj = empaquetar(modelo, metodo, vocab)
        nuevo, _ = restaurar(obj)
        x = previo.preparar(val, vocab)[0]
        with torch.inference_mode():
            if not torch.equal(modelo(x), nuevo(x)):
                raise RuntimeError("La recarga cambió logits")
        r = evaluar(modelo, vocab, val)
        if r != evaluar(nuevo, vocab, val):
            raise RuntimeError("La recarga cambió generaciones")
        diagnostico = {}
        if metodo == "lora":
            base, _ = modelo_inicial("base")
            originales = base.state_dict()
            actuales = modelo.state_dict()
            intactos = all(torch.equal(v, actuales[k if not k.startswith("salida.") else k.replace("salida.", "salida.base.")]) for k, v in originales.items())
            if not intactos:
                raise RuntimeError("LoRA alteró la base")
            fusionado = deepcopy(modelo)
            fusionado.salida = modelo.salida.fusionada()
            with torch.inference_mode():
                error = float((modelo(x) - fusionado(x)).abs().max())
                if error > 1e-5:
                    raise RuntimeError("Fusión fuera de tolerancia")
            modelo.salida.activo = False
            with torch.inference_mode():
                desactivado = torch.equal(modelo(x), base(x))
            modelo.salida.activo = True
            diagnostico = {"base_intacta": intactos, "desactivado_igual_base": desactivado, "error_max_fusion": error}
        resultados[metodo] = {"entrenamiento": historia, "validacion": r,
                             "convencion_anterior": evaluar(modelo, vocab, anterior), "diagnostico": diagnostico}
        estados[metodo] = obj
    elegido = seleccionar(resultados)
    informe = {"seleccionado": elegido, "candidatos": resultados, "config": CONFIG,
               "referencia_regla": {"exactas": sum(regla(f) == f["continuacion"] for f in val), "total": len(val)},
               "recarga_identica": True, "prueba": None}
    if salida:
        for nombre, obj in estados.items():
            guardar(salida / f"{nombre}.json", obj)
        guardar(salida / "modelo.json", estados[elegido])
        guardar(salida / "informe.json", informe)
    return estados[elegido], informe


def cerrar(ruta):
    obj = cargar(ruta)
    modelo, vocab = restaurar(obj)
    grupos = [previo.leer(UNIDAD / f"datos/adaptacion/{f}.json") for f in ("entrenamiento", "validacion", "prueba")]
    comprobar_familias(*grupos)
    filas = grupos[-1]
    return {"metodo": obj["metodo"], "modelo_sha256": huella(ruta),
            "prueba_sha256": huella(UNIDAD / "datos/adaptacion/prueba.json"),
            "evaluacion": evaluar(modelo, vocab, filas),
            "referencia_regla": {"exactas": sum(regla(f) == f["continuacion"] for f in filas), "total": len(filas)}}

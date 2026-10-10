"""Figuras de resultados medidos y escenas sintéticas, sin generación de IA."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from PIL import Image

from comun import UNIDAD, cargar

plt.rcParams.update({"font.size": 10, "svg.hashsalt": "unidad31"})


def guardar(fig, salida, nombre):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida / f"{nombre}.png", dpi=160)
    fig.savefig(salida / f"{nombre}.svg", metadata={"Date": None})
    plt.close(fig)
    p = salida / f"{nombre}.svg"
    p.write_text("\n".join(l.rstrip() for l in p.read_text().splitlines()) + "\n")


def adaptacion(informe, salida):
    candidatos = informe["candidatos"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    for nombre, color in (("lora", "#087e8b"), ("completo", "#9b5de5")):
        curva = candidatos[nombre]["entrenamiento"]["curva"]
        ax[0].plot([r["epoca"] for r in curva], [r["ce_val"] for r in curva], label=nombre, color=color)
    ax[0].set(yscale="log", xlabel="Actualizaciones", ylabel="CE de validación (escala log)", title="Aprender la nueva convención")
    ax[0].legend()
    nombres = list(candidatos)
    valores = [candidatos[n]["validacion"]["n_exactas"] for n in nombres]
    ax[1].bar(nombres, valores, color=["#888888", "#087e8b", "#9b5de5"])
    ax[1].set(ylim=(0, 28), ylabel="Secuencias exactas de 24", title="Validación con generación libre")
    ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    for i, n in enumerate(nombres):
        ax[1].text(i, valores[i] + .5, f"{valores[i]}/24\n{candidatos[n]['entrenamiento']['entrenables']} entrenables", ha="center", fontsize=9)
    fig.suptitle("Unidad 31 · adaptación de un transformer propio en CPU")
    guardar(fig, salida, "adaptacion")


def multimodal(informe, salida):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    nombres = list(informe["candidatos"])
    colores = {"vision": "#ef8354", "texto": "#888888", "fusion": "#087e8b"}
    valores = [informe["candidatos"][n]["validacion"]["correctas"] for n in nombres]
    ax[0].bar(nombres, valores, color=[colores[n] for n in nombres])
    ax[0].set(ylim=(0, 55), ylabel="Pares correctos de 48", title="Qué aporta cada modalidad")
    ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))
    for i, v in enumerate(valores):
        ax[0].text(i, v + 1, f"{v}/48", ha="center")
    for n in nombres:
        curva = informe["candidatos"][n]["entrenamiento"]["curva"]
        ax[1].plot([r["epoca"] for r in curva], [r["ce_val"] for r in curva], label=n, color=colores[n])
    ax[1].set(xlabel="Actualizaciones", ylabel="CE de validación", title="Selección sin abrir prueba")
    ax[1].legend()
    fig.suptitle("Unidad 31 · imágenes + consultas de una gramática cerrada")
    guardar(fig, salida, "modalidades")
    filas = cargar(UNIDAD / "datos/multimodal/validacion.json")
    estados = {}
    for f in filas:
        etiquetas = {x["texto"].split()[1]: x["etiqueta"] for x in filas if x["familia"] == f["familia"]}
        estados.setdefault((etiquetas["izquierda"], etiquetas["derecha"]), f)
    elegidas = [estados[k] for k in sorted(estados)]
    fig, ax = plt.subplots(2, 2, figsize=(8, 5.5), constrained_layout=True)
    for a, f in zip(ax.flat, elegidas):
        with Image.open(UNIDAD / "datos/multimodal" / f["imagen"]) as im:
            a.imshow(im, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        etiquetas = {x["texto"].split()[1]: x["etiqueta"] for x in filas if x["familia"] == f["familia"]}
        a.set_title(f"{f['familia']} · izquierda={etiquetas['izquierda']}, derecha={etiquetas['derecha']}")
        a.set_xticks([])
        a.set_yticks([])
    fig.suptitle("Misma imagen, distintas consultas · 0 apagada, 1 encendida")
    guardar(fig, salida, "escenas")

"""Figuras de complejidad, árbol y fronteras: entrenamiento y validación."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from sklearn.tree import plot_tree

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
NOMBRES = {"mayoria": "Mayoría", "arbol_1": "Profundidad 1", "arbol_3": "Profundidad 3",
           "arbol_libre": "Sin límite", "arbol": "Árbol", "bagging": "Bagging", "bosque": "Bosque"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.axisbelow": True, "savefig.dpi": 150, "svg.hashsalt": "curso-ia-unidad13"})


def terminar(figura, titulo, nota, inferior=.1):
    figura.suptitle(titulo, x=.05, ha="left", fontsize=16, fontweight="bold")
    figura.text(.05, .025, nota, fontsize=10, color="#45515C")
    figura.tight_layout(rect=(.01, inferior, .99, .92), w_pad=2)
    return figura


def figura_complejidad(informe, modelos):
    fig, (curvas, barras) = plt.subplots(1, 2, figsize=(13, 5.8))
    inferior, superior = informe["rangos_entrenamiento"]["senal_a"]
    rejilla = np.linspace(inferior, superior, 1200).reshape(-1, 1)
    for nombre, color, estilo in (("arbol_1", "#CC79A7", ":"), ("arbol_libre", "#D55E00", "--"),
                                  ("arbol_3", "#0072B2", "-")):
        curvas.plot(rejilla[:, 0], modelos[nombre].predict_proba(rejilla)[:, 1], color=color,
                    linestyle=estilo, label=NOMBRES[nombre], linewidth=1.8)
    filas = informe["validacion"]["arbol_3"]["predicciones"]
    curvas.scatter([f["senal_a"] for f in filas], [f["real"] for f in filas], color="#192630", marker="x",
                   s=25, label=f"Etiquetas de validación: n={len(filas)}", zorder=4)
    curvas.set(xlabel="Señal A (índice sintético)", ylabel="Probabilidad estimada de clase 1",
               ylim=(-.05, 1.3), yticks=np.linspace(0, 1, 6), title="Las hojas producen escalones")
    curvas.legend(fontsize=8, frameon=False, ncol=2, loc="upper center")
    nombres = list(modelos)
    posiciones = np.arange(len(nombres))
    for fase, color, desplazamiento in (("entrenamiento", "#A7B4BD", -.18), ("validacion", "#0072B2", .18)):
        valores = [informe[fase][c]["metricas"]["f1"] for c in nombres]
        rectangulos = barras.bar(posiciones + desplazamiento, valores, width=.36, color=color, label=fase.capitalize())
        barras.bar_label(rectangulos, labels=[f"{v:.2f}" for v in valores], fontsize=8, padding=3)
    barras.set(xticks=posiciones, xticklabels=[NOMBRES[c] for c in nombres], ylim=(0, 1.18),
                ylabel="F1 de la clase 1", title="Ajuste perfecto no decide la selección")
    barras.tick_params(axis="x", labelsize=8)
    barras.legend(frameon=False, fontsize=9, loc="upper left")
    for eje in (curvas, barras):
        eje.grid(axis="y", alpha=.2)
    return terminar(fig, "Complejidad: aprender la franja o sus perturbaciones",
                    "Datos sintéticos · Curvas dentro del rango de entrenamiento · Selección por F1 de validación · Prueba no interviene")


def figura_arbol(informe, modelos):
    fig, eje = plt.subplots(figsize=(15, 8))
    plot_tree(modelos["arbol_3"], feature_names=["señal A"], class_names=["0", "1"],
              node_ids=True, filled=True, rounded=True, precision=3, fontsize=9, ax=eje)
    return terminar(fig, "Leer el árbol controlado: profundidad máxima 3, mínimo 5 casos por hoja",
                    "Datos sintéticos · Solo entrenamiento · Izquierda: condición verdadera (≤); derecha: falsa (>)\n"
                    "samples: casos; value: conteos [clase 0, clase 1]; class: clase mayoritaria, empate a 0", inferior=.13)


def figura_fronteras(informe, modelos):
    fig, ejes = plt.subplots(1, 3, figsize=(14, 5.7), sharex=True, sharey=True)
    limites = informe["rangos_entrenamiento"]
    bordes_a = np.linspace(*limites["senal_a"], 131)
    bordes_b = np.linspace(*limites["senal_b"], 131)
    a = (bordes_a[:-1] + bordes_a[1:]) / 2
    b = (bordes_b[:-1] + bordes_b[1:]) / 2
    xx, yy = np.meshgrid(a, b)
    puntos = np.column_stack((xx.ravel(), yy.ravel()))
    filas = informe["validacion"]["arbol"]["predicciones"]
    for eje, nombre in zip(ejes, ("arbol", "bagging", "bosque")):
        ps = modelos[nombre].predict_proba(puntos)[:, 1].reshape(xx.shape)
        mapa = eje.pcolormesh(bordes_a, bordes_b, ps, cmap="cividis", norm=Normalize(0, 1), shading="flat", rasterized=True)
        eje.contour(xx, yy, ps, levels=[.5], colors="white", linewidths=.8)
        for clase, marca, color in ((0, "o", "#202C35"), (1, "^", "#E36B5A")):
            grupo = [f for f in filas if f["real"] == clase]
            eje.scatter([f["senal_a"] for f in grupo], [f["senal_b"] for f in grupo], marker=marca,
                        color=color, edgecolors="white", linewidths=.45, s=23, label=f"Real {clase}")
        f1 = informe["validacion"][nombre]["metricas"]["f1"]
        eje.set(xlabel="Señal A", title=f"{NOMBRES[nombre]} · F1 validación={f1:.3f}", xlim=(0, 100), ylim=(0, 100))
    ejes[0].set_ylabel("Señal B")
    ejes[0].legend(frameon=True, framealpha=.9, fontsize=8, loc="upper left")
    fig.suptitle("Ensambles: distintas particiones, mismas observaciones de validación", x=.05, ha="left", fontsize=16, fontweight="bold")
    fig.subplots_adjust(left=.055, right=.89, bottom=.18, top=.83, wspace=.12)
    barra = fig.add_axes((.92, .25, .015, .5))
    fig.colorbar(mapa, cax=barra, label="Probabilidad estimada de clase 1")
    n = informe["fuentes"]["validacion"]["n"]
    fig.text(.05, .04, f"Datos sintéticos · n={n} por panel · Fondo: rango rectangular de entrenamiento; borde blanco: p=0,5\n"
             "Puntos: etiquetas de validación · La región rectangular no garantiza cobertura conjunta ni calibración", fontsize=10, color="#45515C")
    return fig


def construir_figuras(informe, modelos):
    if informe["experimento"] == "franja":
        return {"complejidad": figura_complejidad(informe, modelos), "arbol_controlado": figura_arbol(informe, modelos)}
    return {"fronteras": figura_fronteras(informe, modelos)}


def guardar_figuras(informe, modelos, destino):
    figuras = construir_figuras(informe, modelos)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                metadata = {"Date": None} if extension == "svg" else None
                with (Path(destino) / f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata=metadata)
    finally:
        for figura in figuras.values():
            plt.close(figura)

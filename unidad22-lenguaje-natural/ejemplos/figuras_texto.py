"""Figuras construidas desde informes; no ajustan modelos ni abren prueba."""
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from texto_curso import CLASES


def guardar(figura, salida, nombre):
    salida = Path(salida)
    figura.savefig(salida / f"{nombre}.png", dpi=160)
    ruta = salida / f"{nombre}.svg"
    figura.savefig(ruta)
    ruta.write_text("\n".join(l.rstrip() for l in ruta.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(figura)


def celdas(ax, matriz, fmt, vmax, cmap="Blues"):
    matriz = np.asarray(matriz)
    ax.imshow(matriz, cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
    for (i, j), v in np.ndenumerate(matriz):
        ax.text(j, i, format(v, fmt), ha="center", va="center", color="white" if v > vmax * .55 else "#17263b", fontsize=11)


def figura_representacion(informe):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
    for ax, campo, titulo, fmt, vmax in zip(axes, ("conteos", "tfidf"), ("Conteos: repeticiones por documento", "TF-IDF con norma L2 por fila"), (".0f", ".3f"), (2, 1)):
        celdas(ax, informe[campo], fmt, vmax)
        ax.set_xticks(range(3), informe["vocabulario"])
        ax.set_yticks(range(3), ["D1: acceso aula aula", "D2: acceso material", "D3: material"] if ax is axes[0] else ["D1", "D2", "D3"])
        ax.set_title(titulo, fontsize=11, pad=12)
    fig.suptitle("Las columnas se aprenden solo del corpus de entrenamiento", fontsize=14)
    fig.text(.5, .035, "DF = [2, 1, 2]   ·   IDF = [1,288; 1,693; 1,288]   ·   «galaxia» queda fuera del vocabulario", ha="center", fontsize=10)
    fig.subplots_adjust(left=.19, right=.97, top=.81, bottom=.17, wspace=.35)
    return fig


def figura_comparacion(informe):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    nombres = list(informe["candidatos"])
    xs = np.arange(len(nombres))
    for delta, particion, color in ((-.18, "entrenamiento", "#397d91"), (.18, "validacion", "#ce7540")):
        valores = [informe["candidatos"][n][particion]["metricas"]["ce"] for n in nombres]
        barras = axes[0].bar(xs + delta, valores, .36, label=particion, color=color)
        axes[0].bar_label(barras, fmt="%.3f", padding=3, fontsize=9)
    axes[0].set_xticks(xs, nombres)
    techo = max(c[p]["metricas"]["ce"] for c in informe["candidatos"].values() for p in ("entrenamiento", "validacion"))
    axes[0].set_ylim(0, max(1.4, 1.25 * techo))
    axes[0].set_ylabel("Entropía cruzada media (menor es mejor)")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].set_title("Tres candidatos predefinidos")
    elegido = informe["seleccionado"]
    m = informe["candidatos"][elegido]["validacion"]["metricas"]
    celdas(axes[1], m["matriz"], "d", max(1, np.max(m["matriz"])))
    axes[1].set_xticks(range(3), CLASES)
    axes[1].set_yticks(range(3), CLASES)
    axes[1].set_xlabel("Clase predicha")
    axes[1].set_ylabel("Clase de referencia")
    axes[1].set_title(f"Validación del elegido: {elegido}")
    fig.suptitle("Clasificación de peticiones sintéticas", fontsize=15)
    resumen = []
    for particion in ("entrenamiento", "validacion"):
        registros = informe["candidatos"][elegido][particion]["registros"]
        resumen.append(f"{len(registros)} textos / {len({r['familia'] for r in registros})} familias de {particion}")
    fig.text(.5, .025, "   ·   ".join(resumen) + "   ·   No muestra prueba", ha="center", fontsize=10)
    fig.subplots_adjust(left=.07, right=.97, bottom=.18, top=.81, wspace=.38)
    return fig


def figura_diagnosticos(informe):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 8.5))
    for ax, nombre in zip(axes, ("unigramas", "bigramas")):
        registros = informe["diagnosticos"][nombre]["registros"]
        celdas(ax, [r["probabilidades"] for r in registros], ".2f", 1, "YlGnBu")
        ax.set_xticks(range(3), CLASES)
        etiquetas = [f"{r['id']} · {r['tipo']}\n" + textwrap.fill(r['texto'], 36) for r in registros]
        ax.set_yticks(range(len(registros)), etiquetas if ax is axes[0] else [r["id"] for r in registros], fontsize=9)
        ax.set_title(nombre, pad=12)
    fig.suptitle("Probabilidades en casos fijados antes del ajuste", fontsize=15)
    fig.text(.5, .025, "d04–d06 y d08 no tienen una clase única válida. El clasificador siempre elige; no implementa abstención.\nEstos nueve casos diagnostican límites: no estiman rendimiento en una población.", ha="center", fontsize=10)
    fig.subplots_adjust(left=.32, right=.98, bottom=.10, top=.89, wspace=.25)
    return fig


def guardar_figuras(informe, salida):
    guardar(figura_comparacion(informe), salida, "comparacion_matriz")
    guardar(figura_diagnosticos(informe), salida, "diagnosticos")

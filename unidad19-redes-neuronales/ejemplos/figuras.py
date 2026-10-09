"""Fronteras y curvas de desarrollo; nunca accede a prueba."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from redes import adelante, sigmoide

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "curso-unidad19",
                     "axes.spines.top": False, "axes.spines.right": False})


def curvas(informe, nombres, titulo):
    fig, ejes = plt.subplots(1, len(nombres), figsize=(5*len(nombres), 4.8), squeeze=False, sharey=True)
    for ax, nombre in zip(ejes[0], nombres):
        c = informe["candidatos"][nombre]
        h = c["historial"]
        epocas = [p["epoca"] for p in h]
        ax.plot(epocas, [p["bce_entrenamiento"] for p in h], label="Entrenamiento", color="#287c96")
        ax.plot(epocas, [p["bce_validacion"] for p in h], label="Validación", color="#b04d2f")
        ax.axvline(c["epoca_elegida"], color="#444444", linestyle="--", linewidth=1, label="Época elegida")
        ax.set_title(f"{nombre} · {c['n_parametros']} parámetros\népoca elegida: {c['epoca_elegida']}")
        ax.set_xlabel("Época (una actualización con todo entrenamiento)")
        ax.grid(alpha=.15)
    ejes[0, 0].set_ylabel("Entropía cruzada binaria, sin penalización")
    ejes[0, -1].legend(fontsize=8, loc="best")
    fig.suptitle(titulo, fontsize=13)
    fig.text(.5, .015, "Datos sintéticos · Elegir una época utiliza validación; las curvas no son evidencia de prueba independiente.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .055, 1, .95))
    return fig


def crear_figuras(informe):
    if informe["laboratorio"] == "ruido":
        return {"curvas": curvas(informe, ["lineal", "red32", "red32_l2"], "Pocos datos y ruido: comparar el mejor estado con seguir entrenando")}
    resultado = {"aprendizaje": curvas(informe, ["lineal", "red8"], "Una capa oculta aprende una separación no lineal")}
    fig, ejes = plt.subplots(1, 2, figsize=(10.8, 5.1), sharex=True, sharey=True)
    coord = np.linspace(-1, 1, 121)
    xx, yy = np.meshgrid(coord, coord)
    malla = np.column_stack((xx.ravel(), yy.ravel()))
    z = (malla-np.array(informe["escala"]["media"]))/np.array(informe["escala"]["escala"])
    puntos = informe["puntos_validacion"]
    for ax, nombre in zip(ejes, ("lineal", "red8")):
        c = informe["candidatos"][nombre]
        prob = sigmoide(adelante(z, c["parametros"])[0]).reshape(xx.shape)
        mapa = ax.contourf(xx, yy, prob, levels=np.linspace(0, 1, 11), cmap="coolwarm", alpha=.72)
        if prob.min() < .5 < prob.max():
            ax.contour(xx, yy, prob, levels=[.5], colors="#222222", linewidths=1)
        for clase, color in ((0, "#1d4b8e"), (1, "#b32724")):
            grupo = [p for p in puntos if p["objetivo"] == clase]
            ax.scatter([p["senal_a"] for p in grupo], [p["senal_b"] for p in grupo], c=color, edgecolors="white", linewidths=.5, s=20, label=f"Real {clase}")
        ax.set_title(f"{nombre} · época {c['epoca_elegida']}\nexactitud validación: {c['validacion']['metricas']['exactitud']:.3f}")
        ax.set_xlabel("Señal A, escala original")
        ax.set_aspect("equal")
    ejes[0].set_ylabel("Señal B, escala original")
    ejes[1].legend(fontsize=8, loc="lower right")
    fig.subplots_adjust(left=.08, right=.87, bottom=.19, top=.82, wspace=.18)
    cax = fig.add_axes([.90, .24, .018, .53])
    fig.colorbar(mapa, cax=cax, label="p(1) del modelo")
    fig.suptitle("XOR: salida logística lineal frente a red con tanh", fontsize=13)
    fig.text(.5, .04, "Puntos: validación · Línea oscura: p=0,5 cuando existe · El fondo interpola también zonas sin ejemplos.\nDatos sintéticos; sin evidencia causal ni rendimiento garantizado fuera de la muestra.", ha="center", fontsize=9)
    resultado["fronteras"] = fig
    return resultado


def guardar_figuras(informe, salida):
    for nombre, fig in crear_figuras(informe).items():
        for extension in ("png", "svg"):
            meta = {"Date": None} if extension == "svg" else {"Software": "Curso de Inteligencia Artificial"}
            fig.savefig(Path(salida)/f"{nombre}.{extension}", dpi=150, metadata=meta)
        plt.close(fig)

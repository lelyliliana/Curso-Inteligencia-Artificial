"""Figuras de desarrollo: asignaciones, selección y alertas, nunca prueba."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from flujo_no_supervisado import puntuar

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
COLORES = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 150, "svg.hashsalt": "curso-ia-unidad14"})


def figura_grupos(informe):
    fig, ejes = plt.subplots(1, 3, figsize=(13.5, 5.4), sharex=True, sharey=True)
    for eje, c in zip(ejes, informe["modelos"]):
        filas = informe["validacion"][c]["predicciones"]
        centros = np.array(informe["modelos"][c]["centros_originales"])
        for i in range(len(centros)):
            grupo = [f for f in filas if f["grupo"] == i]
            eje.scatter([f["horas_uso"] for f in grupo], [f["consumo_kwh"] for f in grupo], color=COLORES[i], s=24, label=f"Grupo {i}")
        eje.scatter(centros[:, 0], centros[:, 1], s=130, marker="X", color="black", edgecolors="white", label="Centros aprendidos")
        valor = informe["validacion"][c]["metricas"]["silueta"]
        etiqueta = "no definida" if valor is None else f"{valor:.3f}"
        eje.set(title=f"{c} · silueta={etiqueta}", xlabel="Horas de uso", xlim=(0, 24), ylim=(0, 300))
        eje.legend(fontsize=8, frameon=False, loc="upper left")
        eje.grid(alpha=.15)
    ejes[0].set_ylabel("Consumo (kWh)")
    fig.suptitle("Mismos perfiles de validación, distintas particiones", x=.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(.05, .025, "Datos sintéticos · Distancias calculadas después de escalar con entrenamiento\nColores: identificadores arbitrarios de cada ajuste; no son etiquetas verdaderas ni se alinean entre paneles", fontsize=10)
    fig.tight_layout(rect=(.01, .12, .99, .91))
    return fig


def figura_diagnosticos(informe):
    fig, (inercia, siluetas) = plt.subplots(1, 2, figsize=(11, 5.2))
    candidatos = list(informe["modelos"])
    ks = [informe["modelos"][c]["parametros"]["n_clusters"] for c in candidatos]
    inercia.plot(ks, [informe["modelos"][c]["inercia_entrenamiento"] for c in candidatos], "o-", color=COLORES[0])
    inercia.set(xlabel="Número de grupos k", ylabel="Suma de distancias cuadradas en z", title="Ajuste: inercia de entrenamiento", xticks=ks, ylim=(0, None))
    valores = [informe["validacion"][c]["metricas"]["silueta"] for c in candidatos]
    rectangulos = siluetas.bar(ks, [np.nan if v is None else v for v in valores], color=COLORES[2])
    siluetas.bar_label(rectangulos, labels=["ND" if v is None else f"{v:.3f}" for v in valores], padding=3)
    siluetas.set(xlabel="Número de grupos k", ylabel="Silueta media de validación", title="Selección: mayor silueta definida", xticks=ks, ylim=(-1, 1))
    for eje in (inercia, siluetas):
        eje.grid(axis="y", alpha=.2)
        eje.set_axisbelow(True)
    fig.suptitle("Una mejor inercia no basta para elegir k", x=.06, ha="left", fontsize=16, fontweight="bold")
    fig.text(.06, .03, "Datos sintéticos · Escala y centros aprendidos solo con entrenamiento\nLa silueta mide una geometría interna; no demuestra categorías verdaderas ni utilidad real", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .91))
    return fig


def figura_alertas(informe, ajuste):
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8.5))
    escala = ajuste["escala"]
    a, b = np.meshgrid(np.linspace(0, 100, 180), np.linspace(0, 100, 180))
    z = escala.transform(np.column_stack((a.ravel(), b.ravel())))
    for columna, c in enumerate(("distancia_centro", "aislamiento")):
        eje, ordenados = ejes[:, columna]
        umbral = informe["modelos"][c]["umbral"]
        puntuaciones = puntuar(c, ajuste["modelos"][c], z)
        mapa = (puntuaciones.reshape(a.shape) > umbral).astype(int)
        eje.pcolormesh(a, b, mapa, cmap=ListedColormap(["#E8EDF1", "#F9D9C5"]), vmin=0, vmax=1, shading="nearest", rasterized=True)
        filas = informe["validacion"][c]["predicciones"]
        for clase, marca, color in ((0, "o", "#0072B2"), (1, "^", "#B44014")):
            grupo = [f for f in filas if f["real"] == clase]
            eje.scatter([f["senal_a"] for f in grupo], [f["senal_b"] for f in grupo], marker=marca, color=color,
                        s=26, edgecolors="white", linewidths=.4, label="Ordinario" if clase == 0 else "Inusual sintético")
        m = informe["validacion"][c]["metricas"]
        eje.set(title=f"{c} · FP={m['FP']}; FN={m['FN']}", xlabel="Señal A", ylabel="Señal B", xlim=(0, 100), ylim=(0, 100))
        eje.legend(fontsize=8, loc="upper left")
        filas = sorted(filas, key=lambda f: f["puntuacion"])
        ordenados.scatter(range(1, len(filas)+1), [f["puntuacion"] for f in filas],
                           c=["#B44014" if f["real"] else "#0072B2" for f in filas], s=19)
        ordenados.axhline(umbral, linestyle="--", color="black", label=f"Umbral={umbral:.3f}")
        ordenados.set(xlabel="Posición ordenada por puntuación (validación)", ylabel="Puntuación; mayor = más inusual")
        ordenados.legend(fontsize=8)
        ordenados.grid(alpha=.2)
    fig.suptitle("Alertar es priorizar una revisión", x=.06, ha="left", fontsize=17, fontweight="bold")
    fig.text(.06, .02, "Datos sintéticos · Fondo naranja: alerta; gris: sin alerta · Umbral fijado con calibración, no con estos puntos\nLas puntuaciones usan escalas distintas y no son probabilidades · Fondo fuera del rango aprendido: solo ilustra la regla", fontsize=10)
    fig.tight_layout(rect=(.01, .10, .99, .94))
    return fig


def construir_figuras(informe, ajuste):
    return ({"grupos": figura_grupos(informe), "diagnosticos": figura_diagnosticos(informe)}
            if informe["experimento"] == "grupos" else {"alertas": figura_alertas(informe, ajuste)})


def guardar_figuras(informe, ajuste, destino):
    figuras = construir_figuras(informe, ajuste)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                with (Path(destino) / f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata={"Date": None} if extension == "svg" else None)
    finally:
        for figura in figuras.values():
            plt.close(figura)

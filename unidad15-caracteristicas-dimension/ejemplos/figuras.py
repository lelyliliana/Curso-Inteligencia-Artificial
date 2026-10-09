"""Tres figuras de desarrollo; no se vuelve a ajustar ni se utiliza prueba."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "savefig.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.hashsalt": "curso-ia-unidad15"})


def figura_caracteristicas(informe):
    fig, ejes = plt.subplots(1, 2, figsize=(11.5, 5.4), sharex=True, sharey=True)
    limites = [v for c in ("originales", "interaccion") for r in informe["validacion"][c]["predicciones"] for v in (r["real"], r["prediccion"])]
    superior = max(limites)*1.08
    inferior = min(0, min(limites)*1.08)
    for eje, c, color in zip(ejes, ("originales", "interaccion"), ("#D55E00", "#0072B2")):
        filas = informe["validacion"][c]["predicciones"]
        eje.scatter([r["real"] for r in filas], [r["prediccion"] for r in filas], color=color, s=25)
        eje.plot([inferior, superior], [inferior, superior], "--", color="#64727D", label="Predicción = real")
        eje.set(xlabel="Consumo real (kWh)", title=f"{c} · MAE={informe['validacion'][c]['metricas']['mae']:.3f} kWh",
                xlim=(inferior, superior), ylim=(inferior, superior), aspect="equal")
        eje.grid(alpha=.2)
        eje.legend(fontsize=9)
    ejes[0].set_ylabel("Consumo predicho (kWh)")
    fig.suptitle("La interacción mejora este modelo de consumo", x=.04, ha="left", fontsize=16, fontweight="bold")
    fig.text(.04, .025, "Datos sintéticos · Mismos casos de validación · Escala y coeficientes aprendidos solo con entrenamiento\nLa característica derivada usa horas y potencia previstas; la lectura posterior al cierre queda excluida", fontsize=10)
    fig.tight_layout(rect=(.01, .13, .99, .90))
    return fig


def figura_proyeccion(informe):
    fig, (original, componentes) = plt.subplots(1, 2, figsize=(12, 5.8))
    filas = informe["validacion"]["pca1"]["predicciones"]
    x = np.array([[r["senal_a"], r["senal_b"]] for r in filas])
    y = np.array([r["real"] for r in filas])
    recon = np.array([r["reconstruccion"] for r in informe["validacion"]["pca1"]["representaciones"]])
    t = np.array([r["coordenadas"] for r in informe["validacion"]["pca2"]["representaciones"]])
    for punto, proyectado in zip(x, recon):
        original.plot([punto[0], proyectado[0]], [punto[1], proyectado[1]], color="#9BA6AF", linewidth=.8)
    original.scatter(recon[:, 0], recon[:, 1], marker="x", color="black", s=20, label="Reconstrucción con PC1")
    original.scatter(x[:, 0], x[:, 1], c=y, cmap="viridis", s=22)
    limites = (min(x.min(), recon.min())-2, max(x.max(), recon.max())+2)
    original.set(xlabel="Señal A", ylabel="Señal B", title="Las señales parecen redundantes", aspect="equal", xlim=limites, ylim=limites)
    original.legend(fontsize=8)
    mapa = componentes.scatter(t[:, 0], t[:, 1], c=y, cmap="viridis", s=26)
    componentes.set(xlabel="Coordenada PC1", ylabel="Coordenada PC2", title="La dirección pequeña distingue respuestas")
    fig.colorbar(mapa, ax=componentes, label="Índice de respuesta real")
    for eje in (original, componentes):
        eje.grid(alpha=.2)
    fig.suptitle("Conservar la nube no garantiza conservar el objetivo", x=.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(.05, .025, "Datos sintéticos · Validación; ejes PCA aprendidos solo con entrenamiento · Panel derecho: escalas visuales distintas\nEl objetivo se usa aquí para colorear y evaluar, nunca para aprender los ejes de PCA", fontsize=10)
    fig.tight_layout(rect=(.01, .13, .99, .91))
    return fig


def figura_compromiso(informe):
    fig, ejes = plt.subplots(1, 3, figsize=(13.5, 5.4))
    reducidas = ("pca1", "pca2")
    valores = [sum(informe["modelos"][c]["pca"]["proporcion_varianza"]) for c in reducidas]
    barras = ejes[0].bar(reducidas, valores, color="#009E73")
    ejes[0].bar_label(barras, labels=[f"{v:.4%}" for v in valores], padding=3)
    ejes[0].set(title="Varianza retenida: entrenamiento", ylabel="Proporción", ylim=(0, 1.16))
    valores = [informe["validacion"][c]["metricas"]["mse_reconstruccion_z"] for c in reducidas]
    barras = ejes[1].bar(reducidas, valores, color="#CC79A7")
    ejes[1].bar_label(barras, labels=[f"{v:.2e}" for v in valores], padding=3)
    ejes[1].set(title="Reconstrucción: validación", ylabel="Error cuadrado medio por celda en z")
    candidatos = list(informe["modelos"])
    valores = [informe["validacion"][c]["metricas"]["mae"] for c in candidatos]
    barras = ejes[2].bar(candidatos, valores, color="#0072B2")
    ejes[2].bar_label(barras, labels=[f"{v:.3f}" for v in valores], padding=3)
    ejes[2].set(title="Predicción: validación", ylabel="MAE del índice de respuesta")
    for eje in ejes:
        eje.set_axisbelow(True)
        eje.grid(axis="y", alpha=.2)
        eje.margins(y=.17)
    fig.suptitle("Tres preguntas: varianza, reconstrucción y predicción", x=.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(.05, .03, "Datos sintéticos · PCA con dos componentes rota las dos entradas, sin comprimirlas\nSelección por MAE de validación; la varianza y la reconstrucción son diagnósticos, no el criterio de elección", fontsize=10)
    fig.tight_layout(rect=(.01, .13, .99, .91))
    return fig


def construir_figuras(informe, modelos):
    return ({"caracteristicas": figura_caracteristicas(informe)} if informe["experimento"] == "interaccion"
            else {"proyeccion": figura_proyeccion(informe), "compromiso": figura_compromiso(informe)})


def guardar_figuras(informe, modelos, destino):
    figuras = construir_figuras(informe, modelos)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                with (Path(destino) / f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata={"Date": None} if extension == "svg" else None)
    finally:
        for figura in figuras.values():
            plt.close(figura)

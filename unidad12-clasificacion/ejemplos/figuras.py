"""Visualiza ajuste y decisiones sin introducir prueba en figuras de desarrollo."""

from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as error:
    raise RuntimeError("Instala dependencias: python -m pip install -r unidad12-clasificacion/requirements.txt") from error

from clasificacion import probabilidades

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__, "numpy": np.__version__}
NOMBRES = {"mayoria": "Mayoría", "siempre_1": "Siempre 1", "logistica_050": "Umbral 0,5",
           "logistica_020": "Umbral 0,2", "logistica_080": "Umbral 0,8"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.axisbelow": True, "savefig.dpi": 150, "svg.hashsalt": "curso-ia-unidad12"})


def terminar(figura, titulo, nota, inferior=.07):
    figura.suptitle(titulo, x=.055, ha="left", fontsize=16, fontweight="bold")
    figura.text(.055, .02, nota, fontsize=10, color="#45515C")
    figura.tight_layout(rect=(.01, inferior, .99, .92), w_pad=2)
    return figura


def figura_aprendizaje(informe):
    modelo = informe["modelo_logistico"]
    fig, (curva, descenso) = plt.subplots(1, 2, figsize=(12, 5.6))
    rejilla = np.linspace(*modelo["rango_x"], 200).tolist()
    curva.plot(rejilla, probabilidades(modelo, rejilla)[0], color="#0072B2", label="Probabilidad estimada")
    # Agrupar entradas repetidas evita ocultar casos superpuestos; no se añade jitter.
    for fase, color, marca in (("entrenamiento", "#697680", "o"), ("validacion", "#D55E00", "x")):
        grupos = {}
        for r in informe[fase]["logistica_050"]["predicciones"]:
            grupos.setdefault(r["senal_previa"], []).append(r["real"])
        curva.scatter(list(grupos), [sum(v) / len(v) for v in grupos.values()],
                      color=color, marker=marca, s=40, label=f"Proporción por señal: {fase}", zorder=3)
    curva.axhline(.5, color="#45515C", linestyle="--", linewidth=1, label="Umbral 0,5")
    curva.set(xlabel="Señal previa (índice sintético)", ylabel="Probabilidad / proporción positiva",
              title="Relación aprendida y proporciones observadas", ylim=(-.03, 1.03))
    curva.legend(fontsize=8, frameon=False, loc="upper left")
    historial = modelo["historial"]
    descenso.plot([r["paso"] for r in historial], [r["objetivo"] for r in historial], color="#0072B2")
    descenso.set(xlabel="Actualizaciones de gradiente", ylabel="Pérdida media + penalización",
                 title="Objetivo de entrenamiento, cada 100 pasos", ylim=(0, None))
    for eje in (curva, descenso):
        eje.grid(alpha=.2)
    return terminar(fig, "Aprender una probabilidad, después tomar una decisión",
                    "Datos sintéticos · Los puntos son proporciones por señal, no casos individuales ni una curva de calibración")


def figura_umbrales(informe):
    fig, (metricas, errores) = plt.subplots(1, 2, figsize=(13, 5.7))
    nombres = list(informe["candidatos"])
    posiciones = np.arange(len(nombres))
    for metrica, color, desplazamiento in (("exactitud", "#A7B4BD", -.19), ("f1", "#0072B2", .19)):
        valores = [informe["validacion"][c]["metricas"][metrica] for c in nombres]
        barras = metricas.bar(posiciones + desplazamiento, valores, width=.38, color=color, label=metrica.capitalize())
        metricas.bar_label(barras, labels=[f"{v:.2f}" for v in valores], fontsize=8, padding=3)
    metricas.set(xticks=posiciones, xticklabels=[NOMBRES[c] for c in nombres], ylim=(0, 1.16),
                 ylabel="Valor de la métrica", title="Exactitud alta puede ocultar positivos omitidos")
    metricas.legend(frameon=False, fontsize=9)
    logisticos = ("logistica_020", "logistica_050", "logistica_080")
    posiciones = np.arange(len(logisticos))
    for metrica, color, desplazamiento in (("FP", "#E69F00", -.19), ("FN", "#CC79A7", .19)):
        valores = [informe["validacion"][c]["metricas"][metrica] for c in logisticos]
        barras = errores.bar(posiciones + desplazamiento, valores, width=.38, color=color, label=metrica)
        errores.bar_label(barras, fontsize=9, padding=3)
    errores.set(xticks=posiciones, xticklabels=[NOMBRES[c] for c in logisticos], ylim=(0, None),
                ylabel="Número de casos", title="Mismas probabilidades; distintos FP y FN")
    errores.margins(y=.2)
    errores.legend(frameon=False, loc="upper right", ncol=2)
    for eje in (metricas, errores):
        eje.grid(axis="y", alpha=.2)
        eje.tick_params(axis="x", labelsize=8)
    fuente = informe["fuentes"]["validacion"]
    return terminar(fig, "Desbalance y umbral: decidir qué errores estamos comparando",
                    f"Datos sintéticos · Solo validación: n={fuente['n']}, positivos={fuente['positivos']} · Selección por F1; barras desde cero")


def figura_matrices(informe):
    nombres = ("mayoria", "logistica_050") if informe["experimento"] == "equilibrado" else ("mayoria", "logistica_050", "logistica_020")
    fig, ejes = plt.subplots(1, len(nombres), figsize=(4.4 * len(nombres), 5.2), squeeze=False)
    n = informe["fuentes"]["validacion"]["n"]
    for eje, nombre in zip(ejes[0], nombres):
        m = informe["validacion"][nombre]["metricas"]
        matriz = np.array([[m["VN"], m["FP"]], [m["FN"], m["VP"]]])
        eje.imshow(matriz, cmap="Blues", vmin=0, vmax=n)
        for (i, j), valor in np.ndenumerate(matriz):
            etiqueta = (("VN", "FP"), ("FN", "VP"))[i][j]
            eje.text(j, i, f"{etiqueta}\n{valor}", ha="center", va="center", fontsize=14,
                     color="white" if valor > n * .55 else "#192630")
        eje.set(xticks=[0, 1], xticklabels=["0", "1"], yticks=[0, 1], yticklabels=["0", "1"],
                xlabel="Clase predicha", ylabel="Clase real", title=NOMBRES[nombre])
    return terminar(fig, "Matriz de confusión: contar cada tipo de resultado",
                    f"Datos sintéticos · Validación: n={n} en cada matriz · Filas: reales; columnas: predicciones · Escala de color común 0–{n}", inferior=.15)


def construir_figuras(informe):
    if informe["experimento"] == "equilibrado":
        return {"aprendizaje": figura_aprendizaje(informe)}
    return {"umbrales": figura_umbrales(informe), "matrices": figura_matrices(informe)}


def guardar_figuras(informe, destino):
    figuras = construir_figuras(informe)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                metadata = {"Date": None} if extension == "svg" else None
                with (Path(destino) / f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata=metadata)
    finally:
        for figura in figuras.values():
            plt.close(figura)

"""Figuras de desarrollo: selección, pertenencia a pliegues y diagnóstico fijo."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import numpy as np

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "savefig.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.hashsalt": "curso-ia-unidad16"})


def panel_busqueda(eje, informe):
    resultados = informe["resultados_cv"]
    nombres = list(resultados)
    medias = [v["mae_medio"] for v in resultados.values()]
    desvs = [v["desviacion_mae"] for v in resultados.values()]
    colores = ["#009E73" if c == informe["seleccionado"] else "#0072B2" for c in nombres]
    eje.barh(nombres, medias, color=colores, alpha=.8)
    eje.errorbar(medias, np.arange(len(nombres)), xerr=desvs, fmt="none", ecolor="#34424B", capsize=4)
    for i, ev in enumerate(resultados.values()):
        eje.scatter([p["validacion"]["mae"] for p in ev["pliegues"]], [i]*4,
                    s=21, color="#222222", zorder=3)
    eje.invert_yaxis()
    eje.set(xlabel="MAE · puntos: cada pliegue", title="Media y dispersión de validación")
    eje.set_xlim(left=0)
    eje.grid(axis="x", alpha=.2)


def figura_busqueda(informe):
    fig, eje = plt.subplots(figsize=(10.5, 5.6))
    panel_busqueda(eje, informe)
    eje.set_xlabel("MAE de consumo (kWh) · puntos: cada pliegue")
    fig.suptitle("Elegir una configuración con cuatro pliegues", x=.04, ha="left", fontsize=16, fontweight="bold")
    fig.text(.04, .03, "Ciclos sintéticos · Escala aprendida dentro de cada pliegue · Verde: elegido por media de MAE\nBarras de error: ± una desviación entre pliegues (ddof=0); no son intervalos de confianza", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .92))
    return fig


def figura_particiones(informe):
    fig, ejes = plt.subplots(2, 1, figsize=(11, 5.8), sharex=True)
    n = informe["fuentes"]["desarrollo"]["n"]
    for eje, pliegues, titulo in zip(ejes, (informe["cv"]["pliegues"], informe["diagnostico_filas"]["pliegues"]),
                                    ("GroupKFold: cada equipo queda de un solo lado", "KFold por filas: el mismo equipo aparece en ambos lados")):
        estados = np.zeros((len(pliegues), n), dtype=int)
        for i, p in enumerate(pliegues):
            estados[i, p["indices_validacion"]] = 1
        eje.imshow(estados, aspect="auto", interpolation="nearest", cmap=ListedColormap(["#DAE3EA", "#D55E00"]), vmin=0, vmax=1)
        eje.set(title=titulo, yticks=range(4), yticklabels=range(1, 5), ylabel="Pliegue")
    # Los índices están en el orden original del CSV; localizar los equipos, sin suponer tamaños.
    filas = informe["resultados_cv"]["mediana"]["predicciones_oof"]
    equipo_por_id = {r["caso_id"]: r["equipo_id"] for r in filas}
    equipos = [equipo_por_id[c] for c in informe["reajuste"]["ids_ajuste"]]
    cortes = [0] + [i for i in range(1, n) if equipos[i] != equipos[i-1]] + [n]
    for eje in ejes:
        for corte in cortes[1:-1]:
            eje.axvline(corte-.5, color="white", linewidth=.8)
    ejes[-1].set_xticks([(a+b-1)/2 for a, b in zip(cortes, cortes[1:])], [equipos[a] for a in cortes[:-1]])
    ejes[-1].set_xlabel("Casos en orden del CSV · límites y nombres de equipos")
    fig.legend(handles=[Patch(color="#DAE3EA", label="Ajuste"), Patch(color="#D55E00", label="Validación")],
               loc="lower right", bbox_to_anchor=(.98, .01), ncol=2)
    fig.suptitle("La unidad de separación cambia la pregunta", x=.04, ha="left", fontsize=16, fontweight="bold")
    fig.text(.04, .035, f"{n} observaciones sintéticas · {len(set(equipos))} equipos de desarrollo\nEl diagnóstico por filas no decide la configuración", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .91))
    return fig


def figura_equipos(informe):
    fig, ejes = plt.subplots(1, 2, figsize=(13, 5.7), gridspec_kw={"width_ratios": [1.6, 1]})
    panel_busqueda(ejes[0], informe)
    ejes[0].set_xlabel("MAE de respuesta · GroupKFold")
    diag = informe["diagnostico_filas"]
    c = diag["candidato_fijo"]
    valores = [diag["resultado"]["mae_medio"], informe["resultados_cv"][c]["mae_medio"]]
    barras = ejes[1].bar(["Filas mezcladas", "Equipos separados"], valores, color=["#CC79A7", "#D55E00"])
    ejes[1].bar_label(barras, labels=[f"{v:.3f}" for v in valores], padding=4)
    ejes[1].set(title="Mismo candidato: knn3_uniform", ylabel="Media de MAE", ylim=(0, max(valores)*1.2))
    ejes[1].grid(axis="y", alpha=.2)
    fig.suptitle("Una buena puntuación por filas puede engañar", x=.03, ha="left", fontsize=16, fontweight="bold")
    fig.text(.03, .025, "Datos sintéticos · Izquierda: selección para equipos nuevos; puntos y ± desviación, sin interpretación de intervalo\nDerecha: diagnóstico fijado antes del cierre; cambian los pliegues, no el candidato · Prueba no aparece en estas figuras", fontsize=10)
    fig.tight_layout(rect=(.01, .15, .99, .91))
    return fig


def construir_figuras(informe):
    return ({"busqueda": figura_busqueda(informe)} if informe["experimento"] == "ciclos"
            else {"particiones": figura_particiones(informe), "comparacion": figura_equipos(informe)})


def guardar_figuras(informe, destino):
    figuras = construir_figuras(informe)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                with (Path(destino) / f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata={"Date": None} if extension == "svg" else None)
    finally:
        for figura in figuras.values():
            plt.close(figura)

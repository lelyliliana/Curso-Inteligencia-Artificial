"""Tres figuras de validación; nunca se consulta prueba ni se elige otra política."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__, "numpy": np.__version__}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "savefig.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.hashsalt": "curso-ia-unidad17"})


def figura_costos(informe):
    fig, ejes = plt.subplots(1, 2, figsize=(13.5, 5.7), gridspec_kw={"width_ratios": [1.2, 1]})
    candidatos = list(informe["validacion"])
    medidas = [ev["metricas"] for ev in informe["validacion"].values()]
    fp = np.array([m["FP"]*informe["costos"]["FP"] for m in medidas])
    fn = np.array([m["FN"]*informe["costos"]["FN"] for m in medidas])
    etiquetas = [c+(" ← elegida" if c == informe["seleccionado"] else "") for c in candidatos]
    ejes[0].barh(etiquetas, fp, label="Costo de FP", color="#0072B2")
    barras = ejes[0].barh(etiquetas, fn, left=fp, label="Costo de FN", color="#D55E00")
    ejes[0].bar_label(barras, labels=[str(v) for v in fp+fn], padding=3)
    ejes[0].invert_yaxis()
    ejes[0].set(title="Costo total = FP + 6 × FN", xlabel="Unidades convencionales de costo", xlim=(0, max(fp+fn)*1.16))
    ejes[0].legend(loc="lower right", fontsize=9)
    for nombre, color in (("precision", "#0072B2"), ("recobrado", "#D55E00"), ("f1", "#009E73")):
        ejes[1].plot(range(len(candidatos)), [np.nan if m[nombre] is None else m[nombre] for m in medidas], marker="o", label=nombre, color=color)
    ejes[1].set(xticks=range(len(candidatos)), xticklabels=["nadie", ".8", ".6", ".5", ".4", ".2", ".1", "0"],
                title="Las métricas describen compromisos distintos", xlabel="Política: nadie o puntuación ≥ umbral", ylabel="Proporción", ylim=(0, 1.07))
    ejes[1].legend(fontsize=9)
    for eje in ejes:
        eje.grid(alpha=.2)
        eje.set_axisbelow(True)
    fig.suptitle("La decisión depende del costo de los errores", x=.03, ha="left", fontsize=16, fontweight="bold")
    fig.text(.03, .025, "Datos sintéticos · Mismos casos y puntuaciones de validación · Los costos se fijaron antes de seleccionar\nLa precisión de una política sin alertas no está definida; se deja sin punto", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .92))
    return fig


def figura_ordenacion(informe):
    fig, ejes = plt.subplots(1, 3, figsize=(14.5, 5.6))
    d, cuadrado = informe["diagnostico_ordenacion"], informe["diagnostico_cuadrado"]
    puntos = d["puntos"]
    if d["auc_roc"] is not None:
        ejes[0].plot([p["tasa_fp"] for p in puntos], [p["recobrado"] for p in puntos], "o-", color="#0072B2", markersize=4,
                     label=f"ROC AUC={d['auc_roc']:.3f}")
    else:
        ejes[0].text(.05, .85, "ROC AUC no definida")
    ejes[0].plot([0, 1], [0, 1], "--", color="#73808A")
    ejes[0].set(title="Ordenación: ROC", xlabel="Tasa de falsos positivos", ylabel="Recobrado")
    if d["ap"] is not None:
        ejes[1].step([0]+[p["recobrado"] for p in puntos[1:]], [1]+[p["precision"] for p in puntos[1:]], where="pre",
                     color="#0072B2", label=f"AP={d['ap']:.3f}")
        ejes[1].axhline(d["prevalencia"], linestyle="--", color="#73808A", label=f"Prevalencia={d['prevalencia']:.3f}")
    else:
        ejes[1].text(.05, .85, "AP no definida: sin positivos")
    ejes[1].set(title="Ordenación: precisión–recobrado", xlabel="Recobrado", ylabel="Precisión")
    for nombre, diagnostico, color in (("s", d, "#0072B2"), ("s²", cuadrado, "#D55E00")):
        grupos = [g for g in diagnostico["fiabilidad"] if g["n"]]
        ejes[2].plot([g["puntuacion_media"] for g in grupos], [g["fraccion_positiva"] for g in grupos], "o-", color=color,
                     label=f"{nombre}: Brier={diagnostico['brier']:.3f}")
        for g in grupos:
            ejes[2].annotate(f"n={g['n']}", (g["puntuacion_media"], g["fraccion_positiva"]), xytext=(3, 6 if nombre == "s" else -14),
                             textcoords="offset points", fontsize=8, color=color)
    ejes[2].plot([0, 1], [0, 1], "--", color="#73808A")
    ejes[2].set(title="Diagnóstico probabilístico por intervalos", xlabel="Puntuación media del intervalo", ylabel="Fracción positiva observada")
    for eje in ejes:
        eje.set(xlim=(0, 1), ylim=(0, 1.03))
        eje.grid(alpha=.2)
        if eje.get_legend_handles_labels()[0]:
            eje.legend(fontsize=8, loc="upper left" if eje == ejes[2] else "lower right")
    fig.suptitle("El mismo orden puede tener distinto error probabilístico", x=.03, ha="left", fontsize=16, fontweight="bold")
    fig.text(.03, .025, "Validación sintética · s y s² conservan orden y empates: misma ROC y AP; sus números cambian\nPR usa escalones de AP, no área trapezoidal · Intervalos fijos: algunos vacíos; no se ajusta un calibrador", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .92))
    return fig


def figura_capacidad(informe):
    fig, ejes = plt.subplots(1, 2, figsize=(13.5, 5.7), gridspec_kw={"width_ratios": [1.2, 1]})
    elegido = informe["validacion"][informe["seleccionado"]]
    lotes = list(elegido["por_lote"])
    x = np.arange(len(lotes))
    ejes[0].bar(x-.18, [informe["diagnostico_sin_cupo"]["por_lote"][l]["alertas"] for l in lotes], width=.36,
                label="Umbral 0.5 sin cupo (diagnóstico)", color="#D55E00")
    ejes[0].bar(x+.18, [elegido["por_lote"][l]["alertas"] for l in lotes], width=.36,
                label=informe["seleccionado"], color="#009E73")
    ejes[0].axhline(informe["cupo_por_lote"], linestyle="--", color="#34424B", label=f"Cupo por lote: {informe['cupo_por_lote']}")
    ejes[0].set(title="Un umbral por sí solo no garantiza capacidad", xlabel="Lote de validación", ylabel="Revisiones propuestas",
                xticks=x, xticklabels=[l.split("-")[-1] for l in lotes], ylim=(0, None))
    ejes[0].legend(fontsize=8, loc="upper left")
    candidatos = list(informe["validacion"])
    valores = [informe["validacion"][c]["metricas"]["costo_total"] for c in candidatos]
    barras = ejes[1].barh(candidatos, valores, color=["#009E73" if c == informe["seleccionado"] else "#0072B2" for c in candidatos])
    ejes[1].bar_label(barras, padding=3)
    ejes[1].invert_yaxis()
    ejes[1].set(title="Comparar solo políticas que respetan el cupo", xlabel="Costo total = FP + 4 × FN", xlim=(0, max(valores)*1.14))
    for eje in ejes:
        eje.grid(alpha=.2)
        eje.set_axisbelow(True)
    fig.suptitle("Seleccionar una política con capacidad limitada", x=.03, ha="left", fontsize=16, fontweight="bold")
    fig.text(.03, .025, "Datos sintéticos · Validación · El cupo se aplica dentro de cada lote antes de consultar las etiquetas\nDesempate entre políticas: menor costo, menos alertas, orden publicado · Entre casos: puntuación descendente, ID ascendente", fontsize=10)
    fig.tight_layout(rect=(.01, .14, .99, .92))
    return fig


def construir_figuras(informe):
    return ({"costos": figura_costos(informe), "ordenacion": figura_ordenacion(informe)} if informe["experimento"] == "costos"
            else {"capacidad": figura_capacidad(informe)})


def guardar_figuras(informe, destino):
    figuras = construir_figuras(informe)
    try:
        for nombre, figura in figuras.items():
            for extension in ("png", "svg"):
                with (Path(destino)/f"{nombre}.{extension}").open("xb") as archivo:
                    figura.savefig(archivo, format=extension, metadata={"Date": None} if extension == "svg" else None)
    finally:
        for figura in figuras.values():
            plt.close(figura)

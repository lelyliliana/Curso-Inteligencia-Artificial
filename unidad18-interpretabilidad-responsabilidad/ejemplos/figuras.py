"""Figuras de desarrollo: siempre usan validación, incluso al abrir el cierre."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "curso-unidad18",
                     "axes.spines.top": False, "axes.spines.right": False})


def crear_figuras(informe):
    figuras = {}
    if informe["laboratorio"] == "consumo":
        c = informe["caso_local"]
        fig, ax = plt.subplots(figsize=(9, 4.8))
        valores = c["contribuciones"]
        ax.barh(informe["entradas"], valores, color=["#237c94" if v >= 0 else "#bb512f" for v in valores])
        ax.axvline(0, color="#444444", linewidth=.8)
        for i, v in enumerate(valores):
            ax.text(v + (.12 if v >= 0 else -.12), i, f"{v:+.3f}", va="center", ha="left" if v >= 0 else "right")
        margen = max(1, max(abs(v) for v in valores)*.25)
        ax.set_xlim(min(0, min(valores))-margen, max(0, max(valores))+margen)
        ax.set_xlabel("Contribución respecto de las medias de entrenamiento (kWh)")
        ax.set_title(f"Un caso de validación: {c['caso_id']}\nBase {c['base']:.3f} + contribuciones = {c['reconstruccion']:.3f} kWh")
        fig.text(.5, .02, "Datos sintéticos · Descomposición del modelo; no atribución causal.", ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .055, 1, 1))
        figuras["contribuciones"] = fig

        p = informe["permutacion"]
        nombres = list(p["bloques"])
        medias = [p["bloques"][n]["media"] for n in nombres]
        desv = [p["bloques"][n]["desviacion"] for n in nombres]
        fig, ax = plt.subplots(figsize=(9, 5.1))
        ax.barh(["Horas", "Minutos (duplicado)", "Temperatura", "Horas y minutos juntos"], medias, xerr=desv,
                color=["#237c94"]*3+["#bb512f"], capsize=4)
        ax.axvline(0, color="#444444", linewidth=.8)
        ax.set_xlabel("Aumento del MAE de validación al permutar (kWh)")
        ax.set_title(f"Dependencia del modelo de sus entradas\nMAE original: {p['mae_original']:.3f} kWh; {p['repeticiones']} repeticiones")
        fig.text(.5, .02, "Barras: media ± desviación poblacional entre permutaciones; no intervalo de confianza.\nEl bloque conjunto conserva minutos = 60 × horas. Datos sintéticos.", ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .08, 1, 1))
        figuras["permutacion"] = fig
    else:
        grupos = informe["validacion"]["grupos"]
        nombres = list(grupos)
        posiciones = np.arange(len(nombres))
        fig, (ax, tasas) = plt.subplots(1, 2, figsize=(11, 5))
        acumulado = np.zeros(len(nombres))
        for clave, color in (("VP", "#237c94"), ("FN", "#bb512f"), ("FP", "#d2a443"), ("VN", "#c3cbd0")):
            valores = np.array([grupos[g][clave] for g in nombres])
            ax.bar(posiciones, valores, bottom=acumulado, label=clave, color=color)
            acumulado += valores
        for i, n in enumerate(acumulado):
            ax.text(i, n+1, f"n={int(n)}", ha="center", fontsize=9)
        ax.set_ylim(0, max(acumulado)*1.16)
        ax.set_ylabel("Casos de validación")
        ax.set_title("El total también depende del tamaño del grupo")
        ax.legend(ncol=4, loc="upper right", fontsize=8)
        for i, g in enumerate(nombres):
            m = grupos[g]
            if m["recobrado"] is not None:
                tasas.bar(i, m["recobrado"], color="#237c94")
                tasas.text(i, m["recobrado"]+.025, f"{m['VP']}/{m['positivos']}", ha="center")
            else:
                tasas.text(i, .13, "No definido\n0 positivos" if m["n"] else "No definido\nsin muestras", ha="center", fontsize=9)
        tasas.set_ylim(0, 1.15)
        tasas.set_ylabel("Recobrado = VP / positivos")
        tasas.set_title("Un recorrido correcto puede omitir positivos")
        for panel in (ax, tasas):
            panel.set_xticks(posiciones, nombres, rotation=18)
        fig.suptitle("Auditoría por condiciones de medición · árbol fijo", fontsize=13)
        fig.text(.5, .025, "Datos sintéticos · Grupos definidos por el generador; estas tasas no demuestran equidad en una población real.", ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .07, 1, .95))
        figuras["grupos"] = fig
    return figuras


def guardar_figuras(informe, salida):
    for nombre, fig in crear_figuras(informe).items():
        for extension in ("png", "svg"):
            metadata = {"Date": None} if extension == "svg" else {"Software": "Curso de Inteligencia Artificial"}
            fig.savefig(Path(salida)/f"{nombre}.{extension}", dpi=150, metadata=metadata)
        plt.close(fig)

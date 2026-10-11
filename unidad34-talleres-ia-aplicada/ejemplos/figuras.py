"""Figuras de evidencia publicada; no entrena ni selecciona usando prueba."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
AZUL, OCRE, ROJO, GRIS = "#187c80", "#c68a37", "#b54a46", "#74838c"


def leer(taller, fase):
    return json.loads((RAIZ / "recursos" / taller / f"{fase}.json").read_text(encoding="utf-8"))


def guardar(fig, salida, nombre):
    fig.text(.05, .025, "Datos ficticios · Estados elegidos en validación · Cierre sin reajuste", fontsize=10, color="#4e5a60")
    fig.subplots_adjust(left=.075, right=.97, top=.81, bottom=.20, wspace=.32)
    fig.savefig(salida / f"{nombre}.png", dpi=150, facecolor=fig.get_facecolor())
    fig.savefig(salida / f"{nombre}.svg", metadata={"Date": None}, facecolor=fig.get_facecolor())
    svg = salida / f"{nombre}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.facecolor": "#fffdf8", "figure.facecolor": "#f6f3eb",
                         "svg.hashsalt": "u34-talleres", "axes.titleweight": "bold"})
    v, p = leer("energia", "validacion"), leer("energia", "prueba")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("Energía: mejorar en validación no garantiza conservar el error", fontsize=16, x=.05, ha="left", y=.95)
    etiquetas = ["Persistencia\nvalidación", "Ridge\nvalidación", "Ridge\ncierre"]
    valores = [v["resultados"][k]["mae_kw"] for k in ("persistencia", "ridge_1")] + [p["resultado"]["mae_kw"]]
    barras = ax[0].bar(etiquetas, valores, color=[GRIS, AZUL, OCRE], width=.6)
    ax[0].bar_label(barras, fmt="%.3f", padding=4)
    ax[0].set(ylabel="MAE (kW), menor es mejor", ylim=(0, 4.5), title="192 decisiones en cada fase")
    casos = p["resultado"]["casos"]
    x = [int(c["id"][1:]) for c in casos]
    ax[1].plot(x, [c["objetivo_kw"] for c in casos], color=GRIS, label="Valor observado", lw=1.3)
    ax[1].plot(x, [c["prediccion_kw"] for c in casos], color=AZUL, label="Ridge congelado", lw=1.4)
    ax[1].axvline(840, color=ROJO, linestyle="--", lw=1, label="Cambio artificial +5 kW")
    ax[1].set(xlabel="Hora objetivo desde el inicio", ylabel="Potencia (kW)", title="Cierre: mismo edificio ficticio")
    ax[1].legend(fontsize=8, loc="lower left")
    guardar(fig, salida, "energia")

    v, p = leer("ambiente", "validacion"), leer("ambiente", "prueba")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("Ambiente: revisar costos y omisiones por zona", fontsize=16, x=.05, ha="left", y=.95)
    resultados = list(v["resultados"].values())
    etiquetas = ["Ninguna", "Todas", "Log. 0,3", "Log. 0,5", "Log. 0,7"]
    barras = ax[0].bar(etiquetas, [r["costo"] for r in resultados], color=[GRIS, GRIS, AZUL, GRIS, GRIS], width=.65)
    ax[0].bar_label(barras, padding=4)
    ax[0].set(ylabel="Costo ficticio = FP + 4·FN", ylim=(0, 260), title="Validación: 120 registros, 3 zonas")
    zonas = p["resultado"]["por_zona"]
    x = np.arange(len(zonas))
    b1 = ax[1].bar(x - .18, [z["fp"] for z in zonas.values()], .36, color=OCRE, label="Falsas propuestas (FP)")
    b2 = ax[1].bar(x + .18, [z["fn"] for z in zonas.values()], .36, color=ROJO, label="Omisiones (FN)")
    ax[1].bar_label(b1, padding=3)
    ax[1].bar_label(b2, padding=3)
    ax[1].set(xticks=x, xticklabels=list(zonas), ylabel="Número de registros", ylim=(0, 16),
              title="Cierre: 40 registros por zona; umbral 0,3")
    ax[1].legend(fontsize=8)
    guardar(fig, salida, "ambiente")

    v, p = leer("documentos", "validacion"), leer("documentos", "prueba")
    resultados = [v["resultados"][v["elegido"]], p["resultado"]]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("Documentos: una cita exacta puede no responder la pregunta", fontsize=16, x=.05, ha="left", y=.95)
    x = np.arange(2)
    fondo = np.zeros(2)
    for nombre, respondida, aceptada, color in (("Fragmento pertinente", True, True, AZUL),
                                               ("Abstención correcta", False, True, GRIS),
                                               ("Fragmento incorrecto", True, False, ROJO),
                                               ("Abstención en respondible", False, False, OCRE)):
        conteos = [sum((c["documento"] is not None) == respondida and c["aceptada"] == aceptada for c in r["casos"]) for r in resultados]
        barras = ax[0].bar(x, conteos, bottom=fondo, width=.5, label=nombre, color=color)
        ax[0].bar_label(barras, labels=[str(n) if n else "" for n in conteos], label_type="center", color="white")
        fondo += conteos
    ax[0].set(xticks=x, xticklabels=["Validación", "Cierre"], ylabel="Preguntas (12 por fase)", ylim=(0, 13), title="TF-IDF con umbral 0,4")
    ax[0].legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, -.10), ncol=2, frameon=False)
    barras = ax[1].bar(["Validación", "Cierre"], [r["costo"] for r in resultados], color=[AZUL, OCRE], width=.5)
    ax[1].bar_label(barras, padding=4)
    ax[1].set(ylabel="Costo: 3·errores + omisiones", ylim=(0, 8), title="Familias completas: 4/6 → 2/6")
    guardar(fig, salida, "documentos")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    generar(parser.parse_args().salida)
    print("Figuras U34: energía, ambiente y documentos; validación y cierre separados.")

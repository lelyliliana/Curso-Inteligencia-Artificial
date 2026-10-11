"""Resultados publicados del proyecto: calidad y cobertura con poblaciones explícitas."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    v = json.loads((RAIZ / "recursos/validacion.json").read_text())
    p = json.loads((RAIZ / "recursos/prueba.json").read_text())
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.hashsalt": "u35-proyecto", "axes.titleweight": "bold"})
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 5.2), facecolor="#f6f3eb")
    fig.suptitle("Proyecto final: estimar cambios y conservar los fallos", x=.055, ha="left", y=.96, fontsize=17)
    etiquetas = ["Persistencia\nvalidación", "Ridge nivel\nvalidación", "Incremento\nvalidación", "Persistencia\ncierre", "Incremento\ncierre"]
    valores = [r["mae_kw"] for r in v["resultados"].values()] + [p["referencia"]["mae_kw"], p["resultado"]["mae_kw"]]
    barras = ax[0].bar(range(5), valores, color=["#849097", "#849097", "#187c80", "#c68a37", "#187c80"], width=.65)
    ax[0].bar_label(barras, fmt="%.3f", padding=4)
    ax[0].set(xticks=range(5), xticklabels=etiquetas, ylabel="MAE (kW), menor es mejor", ylim=(0, 6), title="236 casos admitidos en cada fase")
    ax[0].tick_params(axis="x", labelsize=8)
    casos = p["resultado"]["casos"]
    x = [int(c["id"][2:]) for c in casos]
    ax[1].plot(x, [c["objetivo_kw"] for c in casos], color="#849097", lw=1.4, label="Observado")
    ax[1].plot(x, [c["prediccion_kw"] for c in casos], color="#187c80", lw=1.2, label="Incremento congelado")
    for t in (1070, 1140):
        ax[1].axvline(t, color="#b54a46", lw=1, linestyle="--")
    ax[1].set(xlabel="Hora objetivo (cierre)", ylabel="Potencia (kW)", title="Cambios de nivel: +6 y −7 kW")
    ax[1].legend(fontsize=9, loc="lower right")
    for a in ax:
        a.set_facecolor("#fffdf8")
    fig.text(.055, .095, "Cobertura por fase: 236/240 = 98,33 %. Cuatro rechazos informados aparte; no se borran del total.", fontsize=10)
    fig.text(.055, .045, "Serie ficticia nueva · Selección en validación · Cierre sin reajuste · No mide ahorro ni eficacia real", color="#52616b", fontsize=10)
    fig.subplots_adjust(left=.07, right=.97, top=.82, bottom=.25, wspace=.3)
    fig.savefig(salida / "proyecto.png", dpi=150, facecolor=fig.get_facecolor())
    fig.savefig(salida / "proyecto.svg", metadata={"Date": None}, facecolor=fig.get_facecolor())
    svg = salida / "proyecto.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    generar(parser.parse_args().salida)
    print("Figura final: MAE y cobertura separados; fallos del cierre conservados.")

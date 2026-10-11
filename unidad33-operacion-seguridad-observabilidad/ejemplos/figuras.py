"""Visualiza los conteos capturados; no vuelve a ejecutar ni a medir el servidor."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

UNIDAD = Path(__file__).resolve().parents[1]


def generar(salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    datos = [json.loads((UNIDAD / f"recursos/{n}.json").read_text()) for n in ("observacion", "fallos")]
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "curso-u33"})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    fig.patch.set_facecolor("#f7f6ef")
    colores = ["#147d73", "#c68b32", "#b34c44"]
    x = np.arange(2)
    piso = np.zeros(2)
    for campo, etiqueta, color in zip(("exitos_2xx", "rechazos_4xx", "fallos_5xx"),
                                      ("2xx: respuesta de éxito", "4xx: entrada rechazada", "5xx: fallo/no disponible"), colores):
        valores = [d["resumen"]["prediccion_POST"][campo] for d in datos]
        barras = axes[0].bar(x, valores, bottom=piso, color=color, label=etiqueta, width=.55)
        for barra, valor, base in zip(barras, valores, piso):
            if valor:
                axes[0].text(barra.get_x()+barra.get_width()/2, base+valor/2, str(valor), ha="center", va="center", color="white", weight="bold")
        piso += valores
    axes[0].set(xticks=x, xticklabels=["Observación\n4 POST", "Fallos inyectados\n10 POST"], ylabel="Respuestas preparadas", title="Separar éxito, rechazo y fallo", ylim=(0,12))
    axes[0].legend(fontsize=8, loc="upper left")
    fallos = datos[1]
    total = fallos["resumen"]["terminadas"]
    f_total = sum(v for k,v in fallos["resumen"]["por_status"].items() if k.startswith("5"))
    p = fallos["resumen"]["prediccion_POST"]
    axes[1].bar([0,1], [f_total/total, p["fallos_5xx"]/p["total"]], color=["#607a86", "#b34c44"], width=.55)
    for i, (a,b) in enumerate(((f_total,total),(p["fallos_5xx"],p["total"]))):
        axes[1].text(i,a/b+.015,f"{a}/{b} = {a/b:.0%}",ha="center",weight="bold")
    axes[1].set(xticks=[0,1],xticklabels=["Todas las rutas", "Solo POST de predicción"],title="Misma cifra, distinto denominador",ylabel="Fracción de 5xx",ylim=(0,.6))
    axes[1].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
    for ax in axes:
        ax.spines[["top","right"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="y",alpha=.15)
    fig.suptitle("Operación observable: leer la métrica junto a su población", fontsize=15, weight="bold")
    fig.text(.5,.01,"Capturas locales con casos prefijados y fallos artificiales. No estiman disponibilidad de producción.",ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.94))
    fig.savefig(salida/"operacion.png",dpi=150)
    fig.savefig(salida/"operacion.svg",metadata={"Date":None})
    plt.close(fig)
    svg=salida/"operacion.svg"
    svg.write_text("\n".join(l.rstrip() for l in svg.read_text().splitlines())+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida",default=str(UNIDAD/"recursos"))
    generar(p.parse_args().salida)
    print("Figura: conteos y denominadores de las capturas publicadas.")

"""Gráficos a partir de informes; nunca abren datos reservados."""
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from series_curso import ZONA, fecha


def guardar(fig, salida, nombre):
    salida = Path(salida)
    fig.savefig(salida / f"{nombre}.png", dpi=160)
    p = salida / f"{nombre}.svg"
    fig.savefig(p)
    p.write_text("\n".join(l.rstrip() for l in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def figura_auditoria(r):
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 6.2), sharex=True)
    filas = r["archivo"]["registros"]
    for a in filas:
        if a["valor"] is not None:
            axes[0].scatter(a["hora"], a["valor"], color="#c5713b" if a["hora"] == 5 else "#47788f", marker="x" if a["hora"] == 5 else "o", s=60)
    axes[0].annotate("Dos valores: conflicto", (5, 35), (6, 34), arrowprops={"arrowstyle": "->"})
    axes[0].annotate("Medida a las 07:00;\nllega a las 09:30", (7, 27), (8.3, 24), arrowprops={"arrowstyle": "->"}, fontsize=9)
    axes[0].set_title("Archivo completo: muestra retrospectiva, incluye lecturas futuras")
    v = r["hora8"]["valores"]
    axes[1].step(range(9), v, where="post", color="#327d73", label="Historia disponible y relleno hacia delante")
    ind = np.flatnonzero(r["hora8"]["relleno"])
    axes[1].scatter(ind, np.asarray(v)[ind], marker="s", s=70, facecolors="none", edgecolors="#c5713b", label="Valor rellenado")
    axes[1].set_title("Decisión a las 08:10: solo se utiliza la información recibida")
    axes[1].set_ylim(19, 28)
    axes[1].legend(loc="lower right", fontsize=9)
    for ax in axes:
        ax.axvline(8 + 1/6, color="#777777", ls="--", lw=1)
        ax.set_ylabel("Temperatura (°C)")
        ax.grid(alpha=.15)
    axes[1].set_xticks(range(12), [f"{h:02d}:00" for h in range(12)], fontsize=9)
    axes[1].set_xlabel("1 de agosto de 2026 · UTC−05:00")
    fig.suptitle("Evento, llegada y disponibilidad son tiempos distintos", fontsize=14)
    fig.subplots_adjust(left=.08, right=.97, top=.86, bottom=.11, hspace=.40)
    return fig


def figura_pronostico(r):
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7))
    nombres = list(r["candidatos"])
    xx = np.arange(3)
    for delta, p, color in ((-.18, "entrenamiento", "#397d91"), (.18, "validacion", "#c5713b")):
        vals = [r["candidatos"][n][p]["metricas"]["mae"] for n in nombres]
        barras = axes[0].bar(xx + delta, vals, width=.36, label=p, color=color)
        axes[0].bar_label(barras, fmt="%.3f", padding=3)
    axes[0].set_xticks(xx, nombres)
    axes[0].set_ylabel("MAE (°C); menor es mejor")
    alto = max(c[p]["metricas"]["mae"] for c in r["candidatos"].values() for p in ("entrenamiento", "validacion"))
    axes[0].set_ylim(0, alto * 1.35)
    axes[0].legend(fontsize=9, loc="upper right")
    c = r["conjuntos"]["validacion"]
    pred = r["candidatos"][r["seleccionado"]]["validacion"]["predicciones"]
    # Romper líneas donde no existe un caso evaluable: no dibujar una interpolación.
    horas = [m["objetivo_h"] for m in c["metadatos"]]
    rejilla = range(min(horas), max(horas) + 1)
    fechas = [datetime.fromisoformat(fecha(h)) for h in rejilla]
    reales, predichas = dict(zip(horas, c["y"])), dict(zip(horas, pred))
    axes[1].plot(fechas, [reales.get(h, np.nan) for h in rejilla], color="#223343", lw=1.3, label="Referencia observada")
    axes[1].plot(fechas, [predichas.get(h, np.nan) for h in rejilla], color="#d07935", lw=1, ls="--", label=f"Pronóstico: {r['seleccionado']}")
    axes[1].axvline(datetime.fromisoformat(fecha(672)), color="#777777", ls=":", label="Cambio sintético")
    axes[1].set_ylabel("Temperatura (°C)")
    axes[1].set_xlabel("Hora objetivo · validación · UTC−05:00")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m", tz=ZONA))
    axes[1].legend(fontsize=9, loc="upper left", ncol=3)
    axes[1].grid(alpha=.15)
    fig.suptitle(f"Pronóstico directo a {r['horizonte']} h · parámetros fijos, observaciones nuevas en cada origen", fontsize=13)
    fig.subplots_adjust(left=.08, right=.98, top=.89, bottom=.09, hspace=.38)
    return fig


def figura_errores(r):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    e = r["candidatos"][r["seleccionado"]]["validacion"]
    dias = list(e["por_dia"])
    vals = [e["por_dia"][d]["mae"] for d in dias]
    b = axes[0].bar(np.arange(len(dias)), vals, color="#397d91")
    axes[0].bar_label(b, fmt="%.2f", fontsize=8, padding=3)
    axes[0].set_xticks(range(len(dias)), [datetime.fromisoformat(d).strftime("%d/%m") for d in dias], rotation=35)
    axes[0].set_ylim(0, max(vals) * 1.3)
    axes[0].set_title("Error por día del objetivo")
    grupos = [e["resto"], e["transicion_24h"]]
    b = axes[1].bar([0, 1], [g["mae"] if g["n"] else np.nan for g in grupos], color=["#397d91", "#c5713b"])
    axes[1].bar_label(b, labels=[f"{g['mae']:.3f} °C\nn={g['n']}" if g["n"] else "" for g in grupos], padding=4)
    for i, g in enumerate(grupos):
        if not g["n"]:
            axes[1].text(i, .05, "Sin casos\nn=0", transform=axes[1].get_xaxis_transform(), ha="center")
    axes[1].set_xticks([0, 1], ["Resto de validación", "Primeras 24 h\ntras cambio"])
    axes[1].set_ylim(0, max(.01, max((g["mae"] for g in grupos if g["n"]), default=1)) * 1.45)
    axes[1].set_title("Condición definida por el generador")
    for ax in axes:
        ax.set_ylabel("MAE (°C)")
    fig.suptitle(f"Auditoría de {r['seleccionado']} a {r['horizonte']} h · solo validación", fontsize=14)
    fig.text(.5, .025, "Los errores horarios están relacionados: estas barras no son intervalos de confianza.", ha="center", fontsize=10)
    fig.subplots_adjust(left=.07, right=.98, top=.82, bottom=.20, wspace=.3)
    return fig


def guardar_figuras(r, salida):
    guardar(figura_pronostico(r), salida, "pronostico")
    guardar(figura_errores(r), salida, "errores")

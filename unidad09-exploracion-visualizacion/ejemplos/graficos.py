"""Figuras con Matplotlib; solo se importa al pedir exportación o probar gráficos."""

import json
from pathlib import Path
import platform

try:
    import matplotlib
    matplotlib.use("Agg")  # Exporta sin abrir ventanas; funciona en CPU sin escritorio.
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import numpy as np
except ImportError as error:
    raise RuntimeError(
        "Instala las dependencias: python -m pip install -r "
        "unidad09-exploracion-visualizacion/requirements.txt"
    ) from error

from exploracion import numero

AZUL, NARANJA, VERDE = "#0072B2", "#D55E00", "#009E73"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 13,
    "axes.labelsize": 11, "axes.spines.top": False, "axes.spines.right": False,
    "axes.axisbelow": True, "savefig.dpi": 150, "svg.hashsalt": "curso-ia-unidad09",
})


def terminar(figura, titulo, nota):
    figura.suptitle(titulo, x=0.06, ha="left", fontsize=17, fontweight="bold")
    figura.text(0.06, 0.025, nota, fontsize=10, color="#45515C")
    figura.tight_layout(rect=(0.015, 0.08, 0.99, 0.92), w_pad=3)
    return figura


def figura_lecturas(analisis):
    resumen = analisis["resumen"]
    sensores = resumen["sensores"]
    fig, (lineas, cobertura) = plt.subplots(1, 2, figsize=(12, 5.7))
    fechas = resumen["fechas"]
    for (sensor, datos), color, marcador in zip(sensores.items(), (AZUL, NARANJA, VERDE), ("o", "s", "^")):
        valores = [np.nan if v is None else v for v in datos["serie"]]
        lineas.plot(range(len(fechas)), valores, marker=marcador, color=color,
                    linewidth=2, markersize=7, label=f"{sensor}: n={datos['consumo']['n']}")
    lineas.set(xticks=range(len(fechas)), xticklabels=[f[8:] + "/" + f[5:7] for f in fechas],
               xlabel="Día de 2026 · UTC−05:00", ylabel="Consumo diario (kWh)",
               title="Un hueco no es un consumo de cero")
    lineas.set_ylim(bottom=-0.6)  # Margen para que el marcador de cero se vea completo.
    lineas.grid(axis="y", alpha=0.2)
    lineas.legend(loc="upper left", bbox_to_anchor=(0, -0.20), ncol=3, fontsize=9, frameon=False)
    categorias = (("Con consumo", AZUL, "", lambda d: d["consumo"]["n"]),
                  ("Consumo faltante", "#E5A82D", "//", lambda d: d["consumo"]["faltantes"]),
                  ("Sin fila preparada", "#D8DEE3", "xx", lambda d: d["sin_preparar"]))
    base = np.zeros(len(sensores))
    for etiqueta, color, trama, cantidad in categorias:
        cuentas = [cantidad(d) for d in sensores.values()]
        cobertura.bar(list(sensores), cuentas, bottom=base, label=etiqueta,
                      color=color, hatch=trama, edgecolor="white", width=0.62)
        for i, n in enumerate(cuentas):
            if n:
                cobertura.text(i, base[i] + n / 2, str(n), ha="center", va="center",
                               color="white" if etiqueta == "Con consumo" else "#25313B", weight="bold")
        base += cuentas
    cobertura.set(ylabel="Días del plan", xlabel="Sensor", ylim=(0, max(base) + 0.5),
                  title="Denominador: 4 días por sensor")
    cobertura.yaxis.set_major_locator(MaxNLocator(integer=True))
    cobertura.legend(loc="upper left", bbox_to_anchor=(0, -0.20), fontsize=9, frameon=False, ncol=2)
    cambios = len(analisis["preparacion"]["correcciones"])
    return terminar(fig, "Lecturas preparadas: valores y cobertura",
                    f"Datos sintéticos · Política de la Unidad 8 · Correcciones aplicadas: {cambios} · Sin imputación")


def figura_distribuciones(filas, resumen):
    fig, (histograma, cajas) = plt.subplots(1, 2, figsize=(12, 5.5))
    grupos = [[f["consumo_kwh"] for f in filas if f["grupo"] == g] for g in ("A", "B")]
    histograma.hist(grupos, bins=resumen["bordes_kwh"], stacked=True,
                    color=(AZUL, NARANJA), edgecolor="white", label=("A", "B"))
    histograma.set(xlabel="Consumo por caso-día (kWh)", ylabel="Número de casos",
                   title=f"Frecuencias · {len(resumen['frecuencias'])} intervalos comunes", ylim=(0, None))
    histograma.set_xticks(resumen["bordes_kwh"][::2] if len(resumen["bordes_kwh"]) > 9
                         else resumen["bordes_kwh"])
    histograma.yaxis.set_major_locator(MaxNLocator(integer=True))
    histograma.legend(title="Grupo", frameon=False)
    elementos = cajas.boxplot(grupos, patch_artist=True, whis=1.5,
                              medianprops={"color": "#192630", "linewidth": 2})
    for caja, color in zip(elementos["boxes"], (AZUL, NARANJA)):
        caja.set_facecolor(color)
        caja.set_alpha(0.6)
    # Los puntos reales acompañan al resumen: desplazamiento visual fijo, sin azar.
    for i, (valores, color, marcador) in enumerate(zip(grupos, (AZUL, NARANJA), ("o", "s")), start=1):
        x = [i + 0.23 + ((j % 4) - 1.5) * 0.03 for j in range(len(valores))]
        cajas.scatter(x, valores, edgecolor=color, facecolor="none", marker=marcador, s=19, zorder=3)
    cajas.set(xticks=[1, 2], xticklabels=[f"{g}\nn={len(v)}" for g, v in zip(("A", "B"), grupos)],
              ylabel="Consumo por caso-día (kWh)", title="Mediana, cuartiles y observaciones", ylim=(0, None))
    for eje in (histograma, cajas):
        eje.grid(axis="y", alpha=0.2)
    return terminar(fig, "Distribuciones: el promedio no cuenta toda la historia",
                    f"Datos sintéticos · {len(filas)} casos completos · Cajas: Q1–Q3; bigotes: regla 1.5 × RIC · Sin inferencia poblacional")


def figura_relaciones(filas, resumen):
    fig, ejes = plt.subplots(1, 2, figsize=(12, 5.5), sharex=True, sharey=True)
    ejes[0].scatter([f["horas_uso"] for f in filas], [f["consumo_kwh"] for f in filas],
                   color="#657580", s=32, alpha=0.8)
    ejes[0].set_title(f"Todos los casos · n={len(filas)} · r={numero(resumen['correlacion_total']['r'])}")
    for grupo, color, marcador in zip(("A", "B"), (AZUL, NARANJA), ("o", "s")):
        parte = [f for f in filas if f["grupo"] == grupo]
        r = resumen["grupos"][grupo]["correlacion"]["r"]
        ejes[1].scatter([f["horas_uso"] for f in parte], [f["consumo_kwh"] for f in parte],
                       color=color, marker=marcador, s=32, label=f"{grupo}: n={len(parte)}, r={numero(r)}")
    ejes[1].set_title("Al separar por grupo, cambia la asociación")
    ejes[1].legend(frameon=False, loc="upper left", fontsize=10)
    ejes[0].set_ylabel("Consumo por caso-día (kWh)")
    for eje in ejes:
        eje.set(xlabel="Horas de uso por caso-día", xlim=(0, None), ylim=(0, None))
        eje.grid(alpha=0.2)
    return terminar(fig, "Una correlación global puede ocultar dos patrones",
                    "Datos sintéticos · Mismos datos y escalas en ambos paneles · Asociación descriptiva; no efecto causal")


def guardar_entrega(destino, resumen, figuras):
    destino = Path(destino)
    try:
        destino.mkdir(parents=True, exist_ok=False)
        for nombre, figura in figuras.items():
            figura.savefig(destino / f"{nombre}.png")
            figura.savefig(destino / f"{nombre}.svg", metadata={"Date": None})
        entrega = {"versiones": {"python": platform.python_version(),
                                  "matplotlib": matplotlib.__version__, "numpy": np.__version__},
                   "analisis": resumen}
        with (destino / "resumen.json").open("x", encoding="utf-8") as archivo:
            json.dump(entrega, archivo, ensure_ascii=False, indent=2, allow_nan=False)
            archivo.write("\n")
    finally:
        for figura in figuras.values():
            plt.close(figura)

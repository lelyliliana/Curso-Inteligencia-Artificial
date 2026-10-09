"""Figuras de ajuste, complejidad y residuos; nunca mezclan prueba en la selección."""

from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as error:
    raise RuntimeError("Instala dependencias: python -m pip install -r unidad11-regresion/requirements.txt") from error

from regresion import predecir

VERSIONES_GRAFICAS = {"matplotlib": matplotlib.__version__, "numpy": np.__version__}
COLORES = {"recta": "#0072B2", "cuadratica": "#009E73", "grado9": "#D55E00"}
ESTILOS = {"recta": "-", "cuadratica": "--", "grado9": ":"}
NOMBRES = {"mediana": "Mediana", "media": "Media", "recta": "Recta",
           "cuadratica": "Cuadrática", "grado9": "Grado 9"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.axisbelow": True, "savefig.dpi": 150, "svg.hashsalt": "curso-ia-unidad11"})


def terminar(figura, titulo, nota):
    figura.suptitle(titulo, x=.055, ha="left", fontsize=16, fontweight="bold")
    figura.text(.055, .025, nota, fontsize=10, color="#45515C")
    figura.tight_layout(rect=(.01, .08, .99, .92), w_pad=2)
    return figura


def puntos(informe, eje):
    for fase, color, marca in (("entrenamiento", "#7A858E", "o"), ("validacion", "#192630", "x")):
        filas = informe[fase]["recta"]["predicciones"]
        eje.scatter([f["horas_planificadas"] for f in filas], [f["real"] for f in filas],
                    color=color, marker=marca, s=28, label=f"{fase.capitalize()}: n={len(filas)}", zorder=3)


def figura_lineal(informe):
    fig, (ajuste, residuos) = plt.subplots(1, 2, figsize=(12, 5.6))
    modelo = informe["modelos"]["recta"]
    rejilla = np.linspace(*modelo["rango_x"], 200).tolist()
    puntos(informe, ajuste)
    a, b = modelo["coeficientes"]
    ajuste.plot(rejilla, predecir(modelo, rejilla), color=COLORES["recta"],
                 label=f"Recta: {a:.2f} + {b:.2f} × horas")
    ajuste.axhline(informe["modelos"]["media"]["coeficientes"][0], color="#D55E00", ls="--", label="Media de entrenamiento")
    ajuste.set(xlabel="Horas planificadas por ciclo", ylabel="Consumo por ciclo (kWh)",
               title=f"Ajuste: n={informe['fuentes']['entrenamiento']['n']}; validación: n={informe['fuentes']['validacion']['n']}")
    ajuste.legend(fontsize=9, frameon=False)
    filas = informe["validacion"]["recta"]["predicciones"]
    residuos.scatter([f["horas_planificadas"] for f in filas], [f["residuo"] for f in filas], marker="x", s=40, color=COLORES["recta"])
    residuos.axhline(0, color="#657580", linewidth=1)
    limite = max(.1, max(abs(f["residuo"]) for f in filas) * 1.6)
    residuos.set(xlabel="Horas planificadas por ciclo", ylabel="Real − predicción (kWh)",
                 title="Residuos de la recta en validación", ylim=(-limite, limite))
    for eje in (ajuste, residuos):
        eje.grid(alpha=.2)
    return terminar(fig, "Una recta y sus errores fuera de entrenamiento",
                    "Datos sintéticos · Se muestran entrenamiento y validación · Prueba no interviene en estas figuras")


def figura_complejidad(informe):
    fig, (curvas, errores) = plt.subplots(1, 2, figsize=(13, 6))
    puntos(informe, curvas)
    for nombre in ("recta", "cuadratica", "grado9"):
        modelo = informe["modelos"][nombre]
        rejilla = np.linspace(*modelo["rango_x"], 500).tolist()
        curvas.plot(rejilla, predecir(modelo, rejilla), label=NOMBRES[nombre], color=COLORES[nombre],
                    linestyle=ESTILOS[nombre], linewidth=2)
    curvas.set(xlabel="Horas planificadas por ciclo", ylabel="Consumo por ciclo (kWh)",
               title="Tres formas de ajustar los mismos ciclos")
    curvas.legend(fontsize=9, frameon=False, loc="upper left")
    candidatos = list(informe["modelos"])
    posiciones = np.arange(len(candidatos))
    for fase, desplazamiento, color, trama in (("entrenamiento", -.18, "#A7B4BD", "//"),
                                               ("validacion", .18, "#0072B2", "")):
        valores = [informe[fase][c]["metricas"]["mae"] for c in candidatos]
        barras = errores.bar(posiciones + desplazamiento, valores, width=.36, label=fase.capitalize(),
                             color=color, hatch=trama, edgecolor="white")
        errores.bar_label(barras, labels=[f"{v:.2f}" for v in valores], fontsize=8, padding=3)
    errores.set(xticks=posiciones, xticklabels=[NOMBRES[c] for c in candidatos], ylabel="MAE (kWh)",
                title="Menor error de entrenamiento no decide", ylim=(0, None))
    errores.margins(y=.17)
    errores.legend(frameon=False, fontsize=9)
    for eje in (curvas, errores):
        eje.grid(axis="y", alpha=.2)
    return terminar(fig, "Complejidad: ajustar más no siempre ayuda a predecir",
                    "Datos sintéticos · Ajuste por mínimos cuadrados; selección por MAE de validación · Barras desde cero")


def figura_residuos(informe):
    fig, ejes = plt.subplots(1, 3, figsize=(13, 5), sharex=True, sharey=True)
    nombres = ("recta", "cuadratica", "grado9")
    limite = max(.1, max(abs(r["residuo"]) for c in nombres
                        for r in informe["validacion"][c]["predicciones"]) * 1.2)
    for nombre, eje, marca in zip(nombres, ejes, ("o", "s", "^")):
        ev = informe["validacion"][nombre]
        filas = ev["predicciones"]
        eje.scatter([f["horas_planificadas"] for f in filas], [f["residuo"] for f in filas],
                    color=COLORES[nombre], marker=marca, s=45)
        eje.axhline(0, color="#657580", linewidth=1)
        eje.set(xlabel="Horas planificadas por ciclo", ylim=(-limite, limite),
                title=f"{NOMBRES[nombre]} · MAE={ev['metricas']['mae']:.3f}")
        eje.grid(alpha=.2)
    ejes[0].set_ylabel("Real − predicción (kWh)")
    n = informe["fuentes"]["validacion"]["n"]
    return terminar(fig, "Los residuos revelan errores que un promedio oculta",
                    f"Datos sintéticos · Solo validación: n={n} por candidato · Mismos casos y misma escala vertical")


def construir_figuras(informe):
    if informe["experimento"] == "lineal":
        return {"recta_residuos": figura_lineal(informe)}
    return {"complejidad": figura_complejidad(informe), "residuos": figura_residuos(informe)}


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

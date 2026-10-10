"""Figuras de cálculos e informes existentes; sin ajuste ni lectura de prueba."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORES = ("#286b91", "#ce793d", "#397b62")


def guardar(fig, salida, nombre):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        p = salida / f"{nombre}.{extension}"
        fig.savefig(p, dpi=150, bbox_inches="tight")
        if extension == "svg":
            p.write_text("\n".join(s.rstrip() for s in p.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def atencion(r, salida):
    fig, axs = plt.subplots(1, 2, figsize=(8, 4.3), layout="constrained")
    for ax, clave, titulo in zip(axs, ("pesos_libres", "pesos_causales"), ("Sin máscara", "Con máscara causal")):
        valores = np.asarray(r[clave])
        im = ax.imshow(valores, vmin=0, vmax=1, cmap="Blues")
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{valores[i,j]:.3f}", ha="center", va="center", color="white" if valores[i,j] > .6 else "black")
        ax.set(xticks=range(3), xticklabels=[1,2,3], yticks=range(3), yticklabels=[1,2,3],
               xlabel="Posición consultada (K,V)", ylabel="Posición que consulta (Q)", title=titulo)
    fig.colorbar(im, ax=axs, label="Peso de atención", shrink=.75)
    fig.supxlabel("Cada fila suma 1. La diagonal está permitida; el futuro recibe peso cero.", fontsize=10)
    guardar(fig, salida, "atencion")


def generacion(r, salida):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6), layout="constrained")
    h = r["entrenamiento_transformer"]
    x = [v["epoca"] for v in h["curva"]]
    for clave, etiqueta, color in (("ce_train", "Entrenamiento", COLORES[0]), ("ce_val", "Validación", COLORES[1])):
        axs[0].plot(x, [v[clave] for v in h["curva"]], label=etiqueta, color=color)
    axs[0].axvline(h["epoca_elegida"], linestyle=":", color="#555555", label="Estado elegido")
    axs[0].axhline(r["candidatos"]["bigramas"]["validacion"]["ce"], linestyle="--", color=COLORES[2], label="Bigramas · validación")
    axs[0].set(xlabel="Época / actualización", ylabel="CE de continuación (nats/token)", title="Aprendizaje condicional")
    axs[0].legend(fontsize=8)
    for i, (nombre, c) in enumerate(r["candidatos"].items()):
        m = c["validacion"]
        barras = axs[1].bar(np.arange(2) + (i-.5)*.32, [m["exactitud_token"], m["exactitud_secuencia"]],
                            width=.32, color=COLORES[i], label=nombre.capitalize())
        axs[1].bar_label(barras, fmt="%.3f", padding=3)
    axs[1].set(xticks=range(2), xticklabels=["Token con historia\ncorrecta anterior", "Secuencia\nautorregresiva"], ylim=(0,1.15),
               ylabel="Exactitud de validación", title="Dos evaluaciones diferentes")
    axs[1].legend(loc="upper left", fontsize=8)
    fig.supxlabel("Mismas reglas sintéticas; combinaciones separadas por familia. No mide verdad factual.", fontsize=10)
    guardar(fig, salida, "aprendizaje")

    logits = np.log([4., 2., 1.])
    fig, ax = plt.subplots(figsize=(7.5, 4.5), layout="constrained")
    for i, temperatura in enumerate((.5, 1., 2.)):
        pesos = np.exp((logits-logits.max()) / temperatura)
        probs = pesos / pesos.sum()
        barras = ax.bar(np.arange(3)+(i-1)*.24, probs, width=.24, label=f"T={temperatura:g}", color=COLORES[i])
        ax.bar_label(barras, fmt="%.3f", padding=3, fontsize=9)
    ax.set(xticks=range(3), xticklabels=["A", "B", "C"], ylim=(0,1), ylabel="Probabilidad de muestreo",
           title="Mismos logits [ln 4, ln 2, 0], distinta temperatura")
    ax.legend()
    fig.supxlabel("Ejemplo manual independiente del corpus. El máximo sigue siendo A; muestrear puede elegir otro.", fontsize=9)
    guardar(fig, salida, "temperatura")

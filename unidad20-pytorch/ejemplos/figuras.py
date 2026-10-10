"""Gráficos a partir del informe de desarrollo, sin leer prueba."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from pytorch_curso import restaurar


def crear_figuras(informe):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    if informe["laboratorio"] == "equivalencia":
        etiquetas, a, b = [], [], []
        for k, valores in informe["gradientes_numpy"].items():
            v = np.asarray(valores).ravel()
            etiquetas.extend(f"{k}[{i}]" for i in range(len(v)))
            a.extend(v)
            b.extend(np.asarray(informe["gradientes_torch"][k]).ravel())
        fig, ax = plt.subplots(figsize=(10, 4.4), layout="constrained")
        xx = np.arange(len(a))
        ax.bar(xx-.18, a, width=.36, label="NumPy", color="#21618c")
        ax.bar(xx+.18, b, width=.36, label="PyTorch", color="#dc7633")
        ax.set_xticks(xx, etiquetas, rotation=40, ha="right")
        ax.axhline(0, color="gray", linewidth=.7)
        ax.set(title="Los 13 gradientes coinciden dentro de 1e−12", ylabel="Derivada de BCE + L2")
        ax.legend()
        return {"gradientes": fig}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3), layout="constrained", sharey=True)
    for ax, nombre in zip(axes, ("lineal", "red12_8")):
        c = informe["candidatos"][nombre]
        h = c["historial"]
        for campo, etiqueta, color in (("bce_entrenamiento", "Entrenamiento", "#21618c"),
                                        ("bce_validacion", "Validación", "#dc7633")):
            ax.plot([f["epoca"] for f in h], [f[campo] for f in h], label=etiqueta, color=color)
        ax.axvline(c["epoca_elegida"], color="#566573", linestyle="--", label="Época elegida")
        ax.set(title=nombre, xlabel="Época", ylabel="BCE sin penalización")
        ax.legend()
    fig.suptitle("Evaluación del estado fijo al terminar cada intervalo")
    frontera, ax = plt.subplots(figsize=(7, 5.3), layout="constrained")
    elegido = informe["seleccionado"]
    modelo = restaurar(elegido, informe["candidatos"][elegido]["estado"])
    a, b = np.meshgrid(np.linspace(-1, 1, 121), np.linspace(-1, 1, 121))
    puntos = np.column_stack([a.ravel(), b.ravel()])
    escala = informe["escala"]
    x = torch.tensor((puntos-np.array(escala["media"]))/np.array(escala["escala"]), dtype=torch.float32)
    with torch.no_grad():
        p = torch.sigmoid(modelo(x)).numpy().reshape(a.shape)
    fondo = ax.pcolormesh(a, b, p, vmin=0, vmax=1, cmap="RdBu_r", shading="auto", rasterized=True)
    frontera.colorbar(fondo, ax=ax, label="Probabilidad estimada de clase 1")
    ax.contour(a, b, p, levels=[.5], colors="black", linewidths=1)
    val = informe["puntos_validacion"]
    for clase, marca in ((0, "o"), (1, "^")):
        filas = [f for f in val if f["objetivo"] == clase]
        ax.scatter([f["senal_a"] for f in filas], [f["senal_b"] for f in filas],
                   marker=marca, c="white", edgecolors="black", s=35, label=f"Real {clase}")
    ax.set(title=f"{elegido}: estado elegido y casos de validación", xlabel="Señal A", ylabel="Señal B")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.16), ncol=2, frameon=False)
    return {"aprendizaje": fig, "frontera": frontera}


def guardar_figuras(informe, salida):
    for nombre, fig in crear_figuras(informe).items():
        for extension in ("png", "svg"):
            ruta = Path(salida)/f"{nombre}.{extension}"
            fig.savefig(ruta, dpi=150)
            if extension == "svg":
                ruta.write_text("\n".join(linea.rstrip() for linea in ruta.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
        plt.close(fig)

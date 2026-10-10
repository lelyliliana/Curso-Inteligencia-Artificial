"""Figuras de desarrollo a partir del informe, sin abrir imágenes de prueba."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def casos_dificiles(informe, cantidad=8):
    pred = informe["candidatos"][informe["seleccionado"]]["validacion"]["predicciones"]
    # Menor probabilidad de la clase real = mayor pérdida individual; desempate por ID.
    return sorted(pred, key=lambda p: (p["probabilidades"][p["real"]], p["imagen_id"]))[:cantidad]


def crear_figuras(informe):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    if informe["laboratorio"] == "filtros":
        fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.2), layout="constrained")
        rgb = np.array(informe["rgb_hwc"], dtype=np.uint8)
        axes[0, 0].imshow(rgb, interpolation="nearest")
        axes[0, 0].set_title("RGB original · 24×24")
        for ax, canal, nombre in ((axes[0, 1], 0, "R: intensidad roja"), (axes[0, 2], 1, "G: intensidad verde"),
                                 (axes[0, 3], 2, "B: intensidad azul")):
            ax.imshow(rgb[:, :, canal], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
            ax.set_title(nombre+" · 0–255")
        for ax, clave, titulo in ((axes[1, 0], "gris", "Conversión L / 255 · 24×24"), (axes[1, 1], "suavizada", "Media local 3×3 · 22×22")):
            ax.imshow(informe[clave], cmap="gray", vmin=0, vmax=1, interpolation="nearest")
            ax.set_title(titulo)
        z = np.array(informe["sobel_x"])
        limite = max(float(np.abs(z).max()), 1e-9)
        im = axes[1, 2].imshow(z, cmap="RdBu_r", vmin=-limite, vmax=limite, interpolation="nearest")
        axes[1, 2].set_title("Sobel X · respuesta con signo")
        fig.colorbar(im, ax=axes[1, 2], shrink=.7)
        manual = np.array(informe["manual"]["salida"])
        axes[1, 3].imshow(manual, cmap="RdBu_r", vmin=-3, vmax=3, interpolation="nearest")
        axes[1, 3].set_title("Caso manual · salida 3×3")
        axes[1, 3].set_xticks(range(3))
        axes[1, 3].set_yticks(range(3))
        for (f, c), v in np.ndenumerate(manual):
            axes[1, 3].text(c, f, f"{v:g}", ha="center", va="center", color="white" if abs(v) >= 2 else "black")
        for ax in axes.ravel():
            ax.set(xlabel="Columna", ylabel="Fila")
        fig.suptitle("Píxeles y filtros fijos: inspección, sin entrenamiento")
        return {"pixeles_filtros": fig}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), layout="constrained")
    for nombre, color in (("lineal", "#7f8c8d"), ("cnn", "#21618c"), ("cnn_aumento", "#dc7633")):
        c = informe["candidatos"][nombre]
        for ax, campo in zip(axes[:2], ("ce_entrenamiento", "ce_validacion")):
            ax.plot([h["epoca"] for h in c["historial"]], [h[campo] for h in c["historial"]], label=nombre, color=color)
        h = next(h for h in c["historial"] if h["epoca"] == c["epoca_elegida"])
        axes[1].scatter([h["epoca"]], [h["ce_validacion"]], color=color, s=35)
    for ax, titulo in zip(axes[:2], ("Entrenamiento sin aumentos al evaluar", "Validación · puntos: estados elegidos")):
        ax.set(title=titulo, xlabel="Época", ylabel="Entropía cruzada")
        ax.legend()
    elegido = informe["seleccionado"]
    matriz = np.array(informe["candidatos"][elegido]["validacion"]["metricas"]["matriz"])
    axes[2].imshow(matriz, cmap="Blues", vmin=0, vmax=max(1, int(matriz.max())))
    for (f, c), v in np.ndenumerate(matriz):
        axes[2].text(c, f, str(v), ha="center", va="center", color="white" if v > matriz.max()/2 else "black")
    axes[2].set(xticks=range(3), yticks=range(3), xticklabels=informe["clases"], yticklabels=informe["clases"],
                xlabel="Predicha", ylabel="Real", title=f"{elegido} · validación")
    axes[2].tick_params(axis="x", rotation=30)
    galeria, cuadrantes = plt.subplots(2, 4, figsize=(11, 7.4), layout="constrained")
    galeria.set_constrained_layout_pads(h_pad=.12, w_pad=.06, hspace=.12, wspace=.03)
    por_id = {p["imagen_id"]: p["pixeles"] for p in informe["casos_validacion"]}
    for ax, p in zip(cuadrantes.ravel(), casos_dificiles(informe)):
        ax.imshow(por_id[p["imagen_id"]], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        real, pred = informe["clases"][p["real"]], informe["clases"][p["prediccion"]]
        identificador = p["imagen_id"].replace("u21-validacion-", "escena ")
        ax.set_title(f"{identificador}\nReal: {real}\nPred.: {pred} · p(real)={p['probabilidades'][p['real']]:.3f}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    galeria.suptitle("Los ocho casos de mayor pérdida en validación · escala fija 0–255")
    return {"aprendizaje_matriz": fig, "casos_dificiles": galeria}


def guardar_figuras(informe, salida):
    for nombre, fig in crear_figuras(informe).items():
        for extension in ("png", "svg"):
            ruta = Path(salida)/f"{nombre}.{extension}"
            fig.savefig(ruta, dpi=150)
            if extension == "svg":
                ruta.write_text("\n".join(linea.rstrip() for linea in ruta.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
        plt.close(fig)

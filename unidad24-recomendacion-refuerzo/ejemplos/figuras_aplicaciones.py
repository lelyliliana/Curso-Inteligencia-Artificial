"""Figuras desde estados e informes: no ajustan ni leen datos de prueba."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

COLORES = ("#246b91", "#d47731", "#348264", "#925a9a", "#747b31")


def guardar(fig, salida, nombre):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        ruta = salida / f"{nombre}.{extension}"
        fig.savefig(ruta, dpi=150, bbox_inches="tight")
        if extension == "svg":
            ruta.write_text("\n".join(l.rstrip() for l in ruta.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def recomendacion(informe, salida):
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    primero = next(iter(informe["validacion"].values()))
    ns = [primero["global"]["n"], primero["grupos"]["con_historia"]["n"], primero["grupos"]["sin_historia"]["n"]]
    for j, (nombre, r) in enumerate(informe["validacion"].items()):
        valores = [r["global"], r["grupos"]["con_historia"], r["grupos"]["sin_historia"]]
        barras = ax.bar(np.arange(3) + (j-.5)*.34, [v["recall_3"] or 0 for v in valores],
                        width=.34, label=nombre.capitalize(), color=COLORES[j])
        ax.bar_label(barras, labels=[f"{v['aciertos']}/{v['n']}" if v["n"] else "Sin casos" for v in valores], padding=4)
    ax.set(xticks=range(3), xticklabels=[f"{g} (n={n})" for g, n in zip(("Todos", "Con historia", "Sin historia"), ns)],
           ylabel="Recall@3 del objetivo observado", ylim=(0, 1),
           title="Recomendación · validación con historial fijo")
    ax.legend()
    fig.supxlabel("Catálogo completo menos historial; un objetivo por persona. Datos ficticios.", fontsize=10)
    guardar(fig, salida, "recomendacion")


def refuerzo(modelo, informe, salida):
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.7), layout="constrained")
    for j, c in enumerate(informe["entrenamiento"]):
        x = [b["hasta_episodio"] for b in c["bloques"]]
        axs[0].plot(x, [b["retorno"] for b in c["bloques"]], color=COLORES[j], label=str(c["semilla"]))
    axs[0].set(title="Entrenamiento con exploración", xlabel="Episodio (bloques de 200)", ylabel="Retorno descontado medio")
    axs[0].legend(title="Semilla", ncol=2, fontsize=8)
    e = informe["desarrollo"]
    for ax, clave, titulo, etiqueta in (
            (axs[1], "retorno", "Evaluación · objetivo aprendido", "Retorno descontado medio"),
            (axs[2], "exito", "Evaluación · llegar a la meta", "Fracción de episodios con éxito")):
        ax.scatter(range(5), [r[clave] for r in e["q_learning"]], c=COLORES, s=55)
        ax.axhline(e["referencia"][clave], color="#444444", linestyle="--", label="Ruta fija informada")
        ax.set(title=titulo, xticks=range(5), xticklabels=modelo["config"]["semillas"],
               xlabel="Semilla de entrenamiento", ylabel=etiqueta)
        ax.tick_params(axis="x", labelrotation=45)
        ax.legend(loc="lower right", fontsize=8)
    axs[2].set_ylim(0, 1.02)
    fig.supxlabel("200 episodios de desarrollo por política; mismo tablero y azar de evaluación compartido.", fontsize=10)
    guardar(fig, salida, "aprendizaje")

    fig, ax = plt.subplots(figsize=(6.5, 6), layout="constrained")
    e, tabla = modelo["entorno"], modelo["tablas"][0]
    q = np.asarray(tabla["q"])
    flechas = ("↑", "→", "↓", "←")
    for s in range(25):
        f, c = divmod(s, 5)
        color = "#e7f0f5"
        texto = flechas[int(np.argmax(q[s]))]
        if s in e["pozos"]:
            color, texto = "#f4cdcb", "POZO"
        elif s == e["meta"]:
            color, texto = "#cce5d4", "META"
        ax.add_patch(Rectangle((c-.5, f-.5), 1, 1, facecolor=color, edgecolor="white", linewidth=2))
        ax.text(c, f, texto, ha="center", va="center", fontsize=14 if len(texto) > 1 else 24)
        if s == e["inicio"]:
            ax.text(c, f+.33, "INICIO", ha="center", fontsize=9)
    ax.set(xlim=(-.5, 4.5), ylim=(4.5, -.5), xticks=range(5), yticks=range(5),
           xlabel="Columna", ylabel="Fila", title=f"Política solicitada · semilla {tabla['semilla']}")
    ax.set_aspect("equal")
    fig.supxlabel("Primera semilla, sin selección. El ambiente puede girar la acción (20 %).", fontsize=10)
    guardar(fig, salida, "politica")

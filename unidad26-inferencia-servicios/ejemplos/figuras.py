"""Figuras del informe existente: no realizan inferencias."""


def dibujar(informe, salida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    resumen = informe["resumen"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    for i, (campo, titulo) in enumerate((("contrato_valido", "Contrato válido"), ("finalizada", "Parada normal"),
                                       ("coincide", "Texto coincide"), ("aceptada", "Aceptada"))):
        axes[0].bar(np.arange(2) + (i-1.5)*0.18, [r[campo] for r in resumen], width=0.18, label=titulo)
    axes[0].set(xticks=[0, 1], xticklabels=["Máximo 4", "Máximo 48"], ylim=(0, 5.5),
                yticks=range(5), ylabel="Casos de cuatro", title="Una respuesta recibida puede fallar")
    axes[0].legend(fontsize=9, loc="upper center", ncol=2)
    for j, limite in enumerate((4, 48)):
        filas = [f for f in informe["filas"] if f["limite"] == limite and f["contrato_valido"]]
        axes[1].scatter([j + (i-1.5)*0.04 for i in range(len(filas))], [f["pared_s"] for f in filas], s=65)
        mediana = resumen[j]["mediana_pared_s"]
        if mediana is not None:
            axes[1].plot([j-0.18, j+0.18], [mediana]*2, color="#242424", linewidth=2)
    maximo = max((f["pared_s"] for f in informe["filas"] if f["contrato_valido"]), default=1)
    axes[1].set(xticks=[0, 1], xticklabels=["Máximo 4", "Máximo 48"], xlim=(-0.5, 1.5),
                ylim=(0, maximo * 1.25), ylabel="Tiempo de pared (s)", title="Cada punto es una petición válida")
    fig.suptitle(f"{informe['modelo']} en CPU · captura local · calentamiento excluido", fontsize=14)
    axes[1].text(0.5, 0.97, "Línea: mediana; una ejecución por caso", transform=axes[1].transAxes,
                 ha="center", va="top", fontsize=9)
    salida.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida / "evaluacion.png", dpi=160)
    fig.savefig(salida / "evaluacion.svg")
    svg = salida / "evaluacion.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)

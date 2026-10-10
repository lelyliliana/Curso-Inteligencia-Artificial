"""Gráficos derivados del informe, sin inferencia ni ajuste."""
def dibujar(informe, salida):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), layout='constrained')
    ev = informe['evaluaciones']
    x = np.arange(len(ev))
    for j, (campo, nombre) in enumerate((('precision','P@3'), ('recall','Recall@3'), ('rr','MRR@3'))):
        vals = [e['resumen'][campo] for e in ev]
        bars = axes[0].bar(x+(j-1)*.22, vals, width=.22, label=nombre)
        axes[0].bar_label(bars, fmt='%.2f', fontsize=9, padding=3)
    axes[0].set(xticks=x, xticklabels=[e['resumen']['metodo'] for e in ev], ylim=(0,1.23),
                ylabel='Media en 8 consultas respondibles', title='Recuperar y ordenar documentos relevantes')
    axes[0].legend(ncol=3, fontsize=9, loc='upper center')
    # Un solo espacio de puntuaciones en este panel; no compararlas entre modelos.
    e = ev[-1]
    for i, f in enumerate(e['filas']):
        es = f['respondible']
        axes[1].scatter(i, f['top'][0]['puntuacion'], s=80,
                        marker='o' if es else 'X', color='#226b94' if es else '#c24130')
    axes[1].scatter([], [], marker='o', c='#226b94', label='Tiene respuesta en corpus')
    axes[1].scatter([], [], marker='X', c='#c24130', label='Sin respuesta en corpus')
    axes[1].set(xticks=range(len(e['filas'])), xticklabels=[f['id'] for f in e['filas']],
                ylim=(0,1), ylabel='Coseno del primer candidato',
                title=f"{e['resumen']['metodo']}: parecido no garantiza respuesta")
    axes[1].tick_params(axis='x', rotation=50)
    axes[1].legend(fontsize=9, loc='lower left')
    fig.suptitle(f"Unidad 28 · {informe['fase']} · colección ficticia, embeddings reales", fontsize=14)
    salida.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida/'recuperacion.png', dpi=160)
    fig.savefig(salida/'recuperacion.svg')
    svg = salida/'recuperacion.svg'
    svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')
    plt.close(fig)

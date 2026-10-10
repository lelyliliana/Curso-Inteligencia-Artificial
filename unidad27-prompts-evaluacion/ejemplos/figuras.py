"""Exporta análisis existente; no llama modelos ni selecciona candidatos."""


def dibujar(informe, salida):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    resumen = informe['resumen']
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), layout='constrained')
    x = np.arange(len(resumen))
    for j, (campo, etiqueta) in enumerate((('json_valido','JSON'), ('forma','Forma'),
                                          ('contenido','Contenido'), ('aceptada','Aceptada'))):
        axes[0].bar(x+(j-1.5)*.18, [r[campo] for r in resumen], width=.18, label=etiqueta)
    n = max(r['intentos'] for r in resumen)
    etiquetas = [r['candidato'].replace('_','\n') for r in resumen]
    axes[0].set(xticks=x, xticklabels=etiquetas, ylabel=f'Casos de {n}',
                ylim=(0, n*1.35), yticks=range(0,n+1,2), title='Formato válido no demuestra acierto')
    axes[0].legend(fontsize=9, ncol=2, loc='upper center')
    estados = ('ok', 'ausente', 'conflicto')
    matriz = np.array([[r['por_estado'][e]['aceptadas']/r['por_estado'][e]['n']
                        if r['por_estado'][e]['n'] else float('nan') for e in estados] for r in resumen])
    axes[1].imshow(matriz, cmap='Blues', vmin=0, vmax=1, aspect='auto')
    for i,r in enumerate(resumen):
        for j,e in enumerate(estados):
            dato = r['por_estado'][e]
            axes[1].text(j,i,f"{dato['aceptadas']}/{dato['n']}",ha='center',va='center',
                         color='white' if matriz[i,j] > .6 else '#152238', fontsize=14)
    axes[1].set(xticks=range(3), xticklabels=estados, yticks=x,
                yticklabels=[r['candidato'] for r in resumen], title='Aceptadas por estado esperado')
    fig.suptitle(f"{informe['modelo']} · {informe['fase']} · captura local en CPU", fontsize=14)
    salida.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida/'evaluacion.png', dpi=160)
    fig.savefig(salida/'evaluacion.svg')
    svg=salida/'evaluacion.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)

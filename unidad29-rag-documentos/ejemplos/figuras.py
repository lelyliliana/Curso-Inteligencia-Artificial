"""Gráficos del informe de RAG, sin inferencia adicional."""
def dibujar(informe,salida):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    rs=informe['resumenes']; x=np.arange(len(rs))
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.9),layout='constrained')
    for j,(campo,nombre) in enumerate((('contexto_suficiente','Contexto suficiente'),
                                     ('aceptada','RAG aceptada'),('extractiva_util','Extractiva útil'))):
        barras=axes[0].bar(x+(j-1)*.23,[r[campo] for r in rs],width=.23,label=nombre)
        axes[0].bar_label(barras,padding=3)
    axes[0].set(xticks=x,xticklabels=[f"k={r['k']}" for r in rs],ylim=(0,13.3),yticks=range(0,11,2),
                ylabel='Consultas de 10',title='Evidencia disponible y respuesta final')
    axes[0].legend(fontsize=9,loc='upper center')
    estados=('ok','ausente','conflicto')
    matriz=np.array([[r['por_estado'][e]['aceptadas']/r['por_estado'][e]['n'] for e in estados] for r in rs])
    axes[1].imshow(matriz,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    for i,r in enumerate(rs):
        for j,e in enumerate(estados):
            d=r['por_estado'][e]
            axes[1].text(j,i,f"{d['aceptadas']}/{d['n']}",ha='center',va='center',fontsize=16,
                         color='white' if matriz[i,j]>.6 else '#102030')
    axes[1].set(xticks=range(3),xticklabels=estados,yticks=x,yticklabels=[f"k={r['k']}" for r in rs],
                title='Respuestas RAG aceptadas por estado del corpus')
    fig.suptitle(f"Unidad 29 · {informe['fase']} · documentos ficticios e inferencia real",fontsize=14)
    salida.mkdir(parents=True,exist_ok=True)
    fig.savefig(salida/'rag.png',dpi=160); fig.savefig(salida/'rag.svg')
    svg=salida/'rag.svg'; svg.write_text('\n'.join(l.rstrip() for l in svg.read_text().splitlines())+'\n')
    plt.close(fig)

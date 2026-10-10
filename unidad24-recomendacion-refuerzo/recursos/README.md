# Recursos y reproducción — Unidad 24

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Fichas](fichas.md)

## Artefactos publicados

| Práctica | Estado | Desarrollo | Recarga | Cierre |
|---|---|---|---|---|
| Recomendación | [modelo.json](recomendacion/modelo.json) | [informe.json](recomendacion/informe.json) | [recarga.json](recomendacion/recarga.json) | [cierre.json](recomendacion/cierre.json) |
| Refuerzo | [modelo.json](refuerzo/modelo.json) | [informe.json](refuerzo/informe.json) | [recarga.json](refuerzo/recarga.json) | [cierre.json](refuerzo/cierre.json) |

Las listas y objetivos por usuario se incluyen en los informes de recomendación. En refuerzo se conservan los 200 episodios por política y fase, sus semillas, retornos y desenlaces; la historia de entrenamiento se resume en diez bloques de 200 episodios. No se guardan todas las transiciones del entrenamiento. Las tablas son estados para evaluar una política, no puntos de reanudación: no incluyen los estados de los generadores ni contadores suficientes para continuar exactamente el entrenamiento.

Las figuras se construyen desde esos informes, sin volver a ajustar:

- Recomendación por grupo: [PNG](recomendacion/recomendacion.png) y [SVG](recomendacion/recomendacion.svg).
- Entrenamiento, retorno y éxito de evaluación: [PNG](refuerzo/aprendizaje.png) y [SVG](refuerzo/aprendizaje.svg).
- Política de la primera semilla: [PNG](refuerzo/politica.png) y [SVG](refuerzo/politica.svg).

Se revisaron visualmente las tres figuras. Son resultados sintéticos, sin intervalos de confianza. Las líneas de entrenamiento incluyen exploración; los puntos de evaluación usan tablas fijas. Los SVG pueden variar en metadatos e identificadores al regenerar, por lo que la verificación relevante contrasta los datos representados, no todos sus bytes.

Desde la raíz:

```bash
python unidad24-recomendacion-refuerzo/ejemplos/01_recomendar_recursos.py --salida resultados/u24/recomendacion --graficos
python unidad24-recomendacion-refuerzo/ejemplos/02_aprender_politica.py --salida resultados/u24/refuerzo --graficos
python unidad24-recomendacion-refuerzo/ejemplos/01_recomendar_recursos.py --evaluar-prueba --modelo resultados/u24/recomendacion/modelo.json --salida resultados/u24/recomendacion
python unidad24-recomendacion-refuerzo/ejemplos/02_aprender_politica.py --evaluar-prueba --modelo resultados/u24/refuerzo/modelo.json --salida resultados/u24/refuerzo
```

La ruta `resultados/` está ignorada por Git. El cierre requiere un archivo guardado y solo escribe `cierre.json`, dejando intacto el modelo. Guarda la huella SHA-256 del estado leído. Para auditar directamente los estados publicados, usa sus rutas como `--modelo` y una carpeta propia como `--salida`.

## Fuentes primarias consultadas

Consultadas el 10 de octubre de 2026. No se copiaron conjuntos de datos ni figuras de estas fuentes.

- [Sarwar, Karypis, Konstan y Riedl (2001), filtrado colaborativo entre elementos](https://grouplens.org/site-content/uploads/Item-Based-WWW-2001.pdf): fundamento de relaciones entre elementos. El curso adapta un coseno binario para ranking; no reproduce su modelo de valoraciones.
- [Watkins y Dayan (1992), Q-learning](https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf): actualización y condiciones teóricas. El presupuesto de esta práctica no verifica condiciones asintóticas de convergencia.
- [Gymnasium: handling time limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/): distinción entre terminal y truncamiento; referencia conceptual, no dependencia instalada.
- [NumPy 2.2: Generator](https://numpy.org/doc/2.2/reference/random/generator.html): generadores con semilla y separación de corrientes. Se fija la versión efectivamente comprobada.
- [Matplotlib: savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html): exportación de figuras; el enlace estable puede describir una versión más reciente que la utilizada aquí, 3.10.8.

La comprobación se hizo en el entorno de la [Unidad 20](../../unidad20-pytorch/recursos/entorno-verificado.txt), sin instalación adicional. La unidad requiere únicamente NumPy y Matplotlib. La comprobación de todo el curso necesita las dependencias acumuladas indicadas en el [índice](../../README.md).

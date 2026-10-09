# Recursos reproducibles de métricas y decisiones

[Unidad](../README.md)

Los cálculos de políticas usan biblioteca estándar de Python 3.12.3. Las figuras se generaron con Matplotlib 3.10.8 y NumPy 2.2.6. Las pruebas contrastaron métricas con scikit-learn 1.9.1. Se reutilizó el entorno anterior, cuyas dependencias se registran en la [Unidad 13](../../unidad13-arboles-ensambles/recursos/entorno-verificado.txt); no se instalaron paquetes nuevos. Protocolo `metricas-decisiones-v1`.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Costos y métricas por política | [PNG](costos/costos.png) | [SVG](costos/costos.svg) | [Costos](costos/informe.json) |
| Ordenación y diagnóstico probabilístico | [PNG](costos/ordenacion.png) | [SVG](costos/ordenacion.svg) | [Costos](costos/informe.json) |
| Capacidad por lote y selección | [PNG](capacidad/capacidad.png) | [SVG](capacidad/capacidad.svg) | [Capacidad](capacidad/informe.json) |

Decisiones por caso:

- [Validación de costos](costos/decisiones_validacion.csv): 1920 filas política-caso, ocho políticas × 240 observaciones.
- [Validación de capacidad](capacidad/decisiones_validacion.csv): 1200 filas política-caso, cinco políticas × 240 observaciones.
- [Diagnóstico sin cupo](capacidad/diagnostico_sin_cupo.csv): 240 casos con umbral 0,5 sin recorte; no participa en la selección.

Los JSON publicados conservan `prueba: null` y solo huella de validación. Incluyen costos, cupos, criterios, resultados, elegido y diagnósticos. Sus decisiones conservan ID, puntuación, etiqueta, acción y resultado; las señales de procedencia se consultan en los CSV fuente. No existe un estimador entrenado que serializar.

## Lectura y revisión visual

Las tres figuras se revisaron visualmente. Costos apila contribuciones FP y FN desde cero; la suma coincide con el total del informe. El panel de métricas omite el punto de precisión cuando no hay alertas, sin convertirlo en cero. Su eje horizontal enumera políticas discretas, no representa intervalos numéricos uniformes de umbral.

ROC agrupa empates y PR usa escalones de AP, no área trapezoidal. En PR se dibuja el extremo convencional (0,1); no es una precisión observada de una política vacía. La transformación s² conserva las dos curvas para estos datos; por eso se dibuja una sola para cada tipo. El panel de fiabilidad sí compara ambas representaciones, usando los mismos bordes numéricos con cantidades y pertenencias distintas. Se indican tamaños; los intervalos vacíos no generan puntos.

Capacidad contrasta las alertas por lote del diagnóstico sin cupo y la política elegida, con una línea en seis. A la derecha compara costos solo de políticas admisibles. Las barras parten de cero. No transforma el exceso de revisiones del diagnóstico en una propuesta ejecutable.

[figuras.py](../ejemplos/figuras.py) toma valores del informe sin releer datos, seleccionar ni consultar prueba. Las pruebas comparan barras, curvas, coordenadas de fiabilidad, cupos y ausencia de puntos indefinidos. Un informe con cierre sigue produciendo solo figuras de validación.

## Regeneración

Desde la raíz con dependencias instaladas y carpetas nuevas:

```bash
python unidad17-metricas-decisiones/ejemplos/01_elegir_por_costos.py --salida resultados/unidad17/figuras-costos --graficos
python unidad17-metricas-decisiones/ejemplos/02_decidir_con_cupo.py --salida resultados/unidad17/figuras-capacidad --graficos
```

JSON y CSV se escriben antes de los gráficos. Una exportación fallida puede quedar parcial. Se fijan estilo, fuente y metadatos; no se promete identidad binaria de imágenes entre plataformas. Los cuatro CSV de entrada se reproducen byte a byte en el entorno declarado. Conserva commit y comandos aparte porque el informe no los obtiene automáticamente.

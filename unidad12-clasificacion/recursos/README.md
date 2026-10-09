# Recursos reproducibles de clasificación

[Volver a la unidad](../README.md)

Se generaron con Python 3.12.3, NumPy 2.2.6 y Matplotlib 3.10.8, bajo `clasificacion-v1`. Se reutiliza el [entorno verificado de la Unidad 9](../../unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt); las versiones principales están en los informes JSON.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Curva logística y objetivo de entrenamiento | [PNG](equilibrado/aprendizaje.png) | [SVG](equilibrado/aprendizaje.svg) | [Equilibrado](equilibrado/informe.json) |
| Exactitud, F1, FP y FN con varios umbrales | [PNG](desbalanceado/umbrales.png) | [SVG](desbalanceado/umbrales.svg) | [Desbalanceado](desbalanceado/informe.json) |
| Matrices de confusión con orientación explícita | [PNG](desbalanceado/matrices.png) | [SVG](desbalanceado/matrices.svg) | [Desbalanceado](desbalanceado/informe.json) |

Predicciones por caso:

- Equilibrado: [entrenamiento](equilibrado/predicciones_entrenamiento.csv) y [validación](equilibrado/predicciones_validacion.csv).
- Desbalanceado: [entrenamiento](desbalanceado/predicciones_entrenamiento.csv) y [validación](desbalanceado/predicciones_validacion.csv).

Los informes publicados tienen `prueba: null` y no incluyen huella ni predicciones de prueba. En el caso equilibrado, tres candidatos generan 240 predicciones de entrenamiento y 120 de validación. En el desbalanceado, cinco generan 1000 y 500. Estas cantidades no son números de casos distintos.

`probabilidad_1` queda vacía en CSV para `siempre_1`; no equivale a cero. El JSON usa `null` para esa probabilidad, para su pérdida logarítmica y para cualquier métrica de clase indefinida. La regla de mayoría conserva tanto su clase como la frecuencia positiva de entrenamiento.

## Lectura de figuras

La figura de aprendizaje agrega los casos de igual señal: cada punto representa una proporción, no una observación ni un intervalo. No es un diagrama de calibración. A su derecha se muestra el objetivo **penalizado** de entrenamiento cada 100 actualizaciones; no debe confundirse con la pérdida logarítmica de evaluación.

Las barras parten de cero. Las matrices usan filas reales, columnas predichas y la misma escala de color de 0 a 100. Las tres fueron revisadas visualmente; las pruebas comprueban puntos agregados, evolución del objetivo, alturas de barras y conteos de matrices.

## Regenerar

Desde la raíz, con dependencias instaladas y destinos nuevos:

```bash
python unidad12-clasificacion/ejemplos/01_aprender_logistica.py --salida resultados/unidad12/figuras-equilibrado --graficos
python unidad12-clasificacion/ejemplos/02_comparar_umbrales.py --salida resultados/unidad12/figuras-desbalanceado --graficos
```

[figuras.py](../ejemplos/figuras.py) utiliza el informe existente en memoria; no vuelve a ajustar ni consulta prueba. Incluso si se añade `--evaluar-prueba`, las imágenes siguen mostrando desarrollo. El JSON se escribe antes de los gráficos y no garantiza por sí solo que estén completos.

Se fijan estilo, fuente, tamaño y metadatos de salida. Puede haber pequeñas diferencias numéricas o de renderizado entre plataformas; no se promete identidad binaria de imágenes entre sistemas. Los seis CSV de entrada sí tienen regeneración exacta comprobada. Conserva el commit y los comandos junto a las exportaciones.

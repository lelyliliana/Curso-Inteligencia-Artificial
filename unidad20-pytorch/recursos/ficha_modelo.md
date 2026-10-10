# Ficha completada — red12_8 de demostración

[Unidad](../README.md) · [Plantilla](../plantillas/informe_pytorch.md)

**Propósito:** enseñar entrenamiento, selección y recarga en CPU para clasificación binaria con dos señales ficticias. No tiene un uso operativo aprobado sobre datos reales.

## Datos y preparación

310 casos nuevos en tres particiones: 150 de entrenamiento, 80 de validación, 80 de cierre. Se generan con uniformes, una frontera sinusoidal y etiquetas Bernoulli. Solo entrenamiento determina media, escala y gradientes. Entradas, en orden: `senal_a`, `senal_b`; ambas adimensionales en [−1,1]. El ID y el objetivo se excluyen del predictor.

Media: aproximadamente [−0,06890947; −0,05241947]; desviación poblacional: [0,54660102; 0,55224548]. Los valores completos están en el [informe](minilotes/informe.json). Cambiar su orden o sustituir la escala altera el significado de la entrada.

## Ajuste y decisión

PyTorch 2.14.1+cpu, float32, red 2→12→8→1 con tanh y 149 parámetros. Adam, tasa 0,01, 120 épocas, 600 actualizaciones, semillas de modelo 20 y de orden 2020. Se compararon prevalencia, lineal y red12_8, fijados antes del cierre. BCE de validación seleccionó red12_8, época 110. El umbral 0,5 también estaba fijado.

| Evaluación | BCE | Exactitud | FP | FN |
|---|---:|---:|---:|---:|
| Validación del estado elegido | 0,1752 | 0,9625 | 3 | 0 |
| Cierre didáctico | 0,2110 | 0,9000 | 2 | 6 |

Validación orientó la selección. Cierre se abrió después y no provocó un reajuste. Estos resultados ahora son públicos y no sirven como nueva evaluación independiente de variantes diseñadas a partir de ellos. Las seis omisiones del cierre deben figurar junto con la exactitud.

## Artefacto

La exportación guarda el estado de la época 110, arquitectura mediante su identificador, orden de entradas y escala. La recarga en una instancia nueva de CPU conserva exactamente los logits sobre las 80 filas de validación. Se utiliza `weights_only=True` con archivos propios y validación de estructura; el modo final es `eval()`.

Sirve para inferencia. No incluye momentos ni contadores de Adam, estados de generadores ni posición del cargador para reanudar entrenamiento. La igualdad de recarga tampoco demuestra calibración, utilidad real ni ausencia de errores en entradas no examinadas.

## Límites y siguiente evidencia

- Datos pequeños, sintéticos e independientes; sin mediciones reales, temporalidad o estructura por equipos.
- Una semilla de inicialización y un conjunto de particiones; no se estima la dispersión del rendimiento.
- Sin estudio de calibración, costos de error, cambios de distribución ni subgrupos reales.
- La forma de la frontera no permite atribuir causalidad a una señal.
- CPU y versiones registradas; la igualdad exacta no se promete en otros entornos.

Decisión: conservar como demostración educativa. Para una aplicación nueva se necesita formular la decisión, obtener datos apropiados, definir costos y particiones coherentes, comparar referencias y realizar un cierre independiente del desarrollo.

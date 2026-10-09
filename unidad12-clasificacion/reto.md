# Reto — Clasificar y justificar una decisión

[Unidad](README.md) · [Plantilla](plantillas/informe_clasificacion.md)

## Situación

Necesitas explicar si un clasificador mejora referencias sencillas para detectar casos de revisión. Elige **uno** de los laboratorios y entrega un experimento cuyo ajuste, selección y cierre puedan revisarse. La meta es comprender decisiones y errores, no obtener una puntuación alta.

## Trabajo

1. Define caso, entrada, objetivo, clase positiva y momento de predicción. Distingue el supuesto de disponibilidad de la evidencia que falta en el CSV.
2. Registra el [protocolo](datos/protocolo.md) antes de abrir prueba: candidatos, configuración, transformación, pérdida, criterio de selección, empate y ausencia de reajuste con validación.
3. Ejecuta el laboratorio sin cierre, con `--salida` y `--graficos`. Guarda comando, commit, versiones y huellas de desarrollo. Usa una carpeta nueva bajo `resultados/unidad12/`.
4. Describe centro, escala, intercepto y coeficiente. Reproduce a mano una probabilidad de un caso identificado y su clase; utiliza los parámetros completos del informe, no solo los redondeados de consola.
5. Compara todos los candidatos sobre los mismos casos. Reconstruye una matriz de confusión desde las predicciones CSV y calcula precisión, recobrado y F1. Explica métricas indefinidas, si aparecen.
6. Analiza al menos un FP y un FN del candidato elegido, identificados en el CSV. Explica sus diferencias y qué información haría falta para valorar sus consecuencias reales.
7. Interpreta una figura. Si elegiste el laboratorio desbalanceado, demuestra que las probabilidades y la pérdida de las tres reglas logísticas son iguales, aunque sus clases y errores difieran. Si elegiste el equilibrado, interpreta el objetivo de ajuste y las proporciones agrupadas sin llamarlas calibración.
8. Guarda por escrito modelo, referencias y candidato con su umbral antes de cerrar. Ejecuta `--evaluar-prueba` sobre los datos originales y exporta a otra carpeta. Comprueba que coincidan código, protocolo, huellas de desarrollo, ajuste y selección.
9. Informa los errores finales sin volver a elegir. Explica qué no demuestra este ejemplo respecto de calibración, causalidad o utilidad fuera del dataset sintético.
10. Ejecuta las 28 pruebas y registra su resultado. Identifica una prueba que verifica ajuste numérico y otra que comprueba separación de información.

Opcional: consulta una señal fuera del rango de entrenamiento pero dentro de 0 a 100, o cambia una etiqueta de validación en una copia. Registra la variante como un experimento aparte y conserva el cierre del protocolo original. No hace falta añadir modelos ni buscar más umbrales.

Prueba, el generador y las respuestas son públicos. Declara qué habías leído. Puedes demostrar el flujo del programa sin presentar tu proceso como una evaluación personal ciega o evidencia externa.

## Entrega

Un informe de aproximadamente dos a cuatro páginas en Markdown o formato equivalente, las exportaciones de desarrollo y cierre —JSON y CSV— y las figuras de desarrollo. Usa la [plantilla](plantillas/informe_clasificacion.md), conserva los originales y registra comandos desde la raíz.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Formulación y disponibilidad | 15 | Clase positiva, entrada, etiqueta y momento definidos; supuesto y evidencia diferenciados |
| Ajuste y protocolo | 20 | Transformaciones de entrenamiento, pérdida, configuración y selección previas claras |
| Comparación y cálculo manual | 20 | Referencias, mismos casos, probabilidad y matriz reconstruidas correctamente |
| Errores e interpretación | 20 | FP y FN concretos, figura explicada, desbalance/umbral y límites de calibración |
| Cierre | 15 | Procedimiento conservado, prueba solo del elegido, sin reselección |
| Reproducción y pruebas | 10 | Versiones, código, huellas, comandos y controles identificados |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos utilizar etiquetas posteriores como entradas, ajustar transformaciones con prueba, elegir umbral mirando prueba, confundir logit con probabilidad, ocultar positivos omitidos detrás de exactitud o presentar la sigmoide como prueba de calibración real.

## Preguntas de revisión

- ¿Qué información recibe exactamente el predictor?
- ¿Dónde se aprendió cada parámetro y dónde se eligió el umbral?
- ¿Los conteos suman el número de casos de la partición?
- ¿Se distinguen pérdida de ajuste, pérdida probabilística y F1 de selección?
- ¿Qué error sería costoso y qué evidencia falta para cuantificarlo?
- ¿Se conserva el candidato anterior al cierre y se reconoce el carácter público de prueba?

# Soluciones — Unidad 9

[Volver a los ejercicios](../README.md) · [Reto aplicado](../reto.md)

Las respuestas muestran una solución razonada. Las preguntas abiertas admiten otras formulaciones si delimitan los datos y justifican la interpretación.

## 1. Preguntas y alcance

Cobertura: «¿Qué proporción de los cuatro días esperados tiene consumo disponible por sensor, tras la preparación conservadora?». La unidad de observación esperada es sensor-día. No permite afirmar qué sensor es más eficiente.

Relación: «¿Cómo varía la asociación entre horas y consumo al reunir o separar los grupos A y B?». La unidad es caso-día sintético con un par completo de valores. No permite predecir qué ocurriría al aumentar las horas en un equipo real.

Definir pregunta, unidad y límite antes de dibujar evita convertir un resultado llamativo en una conclusión sin contexto.

## 2. Elegir el gráfico

| Pregunta | Gráfico | Razón |
|---|---|---|
| Frecuencias por sensor | Barras con conteo y denominador | El sensor es una categoría; no un número continuo |
| Distribución de consumos | Histograma, con resumen de cuantiles | Interesa cómo se reparten valores numéricos entre intervalos |
| Relación horas-consumo | Dispersión, distinguiendo grupos | Cada punto representa un par observado |
| Evolución diaria | Serie de puntos y líneas, calendario completo | El orden y los huecos temporales tienen significado |

Un histograma pierde la fecha de cada observación; una serie no resume automáticamente una distribución. El gráfico se elige según la pregunta, no por su atractivo.

## 3. Dos coberturas

El plan tiene `3 sensores × 4 días = 12` claves esperadas. La cobertura de filas preparadas es `8/12 × 100 = 66.67 %`. La de consumos disponibles es `7/12 × 100 = 58.33 %`.

S1 del 3 de septiembre conserva su fila pero no su consumo. Por eso aporta a la primera cobertura y no a la segunda. Ambas usan como denominador el mismo plan; `7/8 = 87.50 %` respondería otra pregunta: qué proporción de las **filas preparadas** tiene consumo.

Tres registros en cuarentena no equivalen a tres claves ausentes: dos corresponden a versiones de S3 del 1 de septiembre. Antes de contar, decide si cuentas registros, claves o valores.

## 4. Un faltante no es cero

Valores presentes de S1: `(10 + 12 + 14)/3 = 12` kWh. Al sustituir el faltante por cero: `(10 + 12 + 0 + 14)/4 = 9` kWh.

La segunda media supone un consumo nulo el día faltante. El archivo no respalda ese supuesto. La primera describe solo los tres días disponibles; tampoco demuestra que 12 sea la media de los cuatro días o de otros períodos.

Para representar la serie correcta mantenemos `[10, 12, None, 14]`, usamos un hueco en el gráfico y declaramos `n=3`.

## 5. Bordes e histogramas

Con intervalos `[0,1)`, `[1,2)` y `[2,4]`, el cero entra en el primero, el uno en el segundo y tanto dos como cuatro en el tercero. Los conteos son `[1,1,2]`, cuya suma vale cuatro.

Usar intervalos cerrados en ambos extremos contaría ciertos bordes dos veces; excluir todos los extremos derechos perdería el máximo. La convención usada evita ambas situaciones. El ejemplo tiene anchos distintos: sus conteos no deben dibujarse como si los intervalos tuvieran idéntico ancho; las figuras del laboratorio sí usan intervalos uniformes.

## 6. Cuartiles, cercas y revisión de un extremo

Para ocho valores ordenados, las posiciones de Q1 y Q3 son 1.75 y 5.25 con índices desde cero. Por interpolación, `Q1 = 2.75`, mediana `7.5`, `Q3 = 11.75` y `RIC = 9`.

Las cercas son `2.75 − 13.5 = −10.75` y `11.75 + 13.5 = 25.25`. Las observaciones más extremas dentro de ellas son 1 y 14: ahí terminan los bigotes. El valor 100 queda fuera de la cerca superior.

No debe eliminarse automáticamente. Primero revisaríamos unidad, fuente, transcripción y contexto. Si es válido, puede ser precisamente el caso que necesitamos entender. Si se justifica una exclusión, deben quedar su motivo y la comparación de resultados con y sin ese registro.

## 7. Sensibilidad a los intervalos

Con cuatro intervalos sobre 0–32 kWh aparecen `[0,24,0,24]`; con ocho aparecen `[0,0,20,4,0,0,20,4]`; con dieciséis aparecen `[0,0,0,0,8,12,4,0,0,0,0,0,8,12,4,0]`.

Se conservan 48 observaciones, el mismo rango de representación y todos los estadísticos calculados sobre valores originales. Cambian el ancho de las barras y cuánto detalle interno se distingue. El grupo A muestra ocho casos en `[8,10)` y doce en `[10,12)` al usar dieciséis intervalos, detalle que no se veía con ocho.

No se necesita elegir una única representación «verdadera». Hay que justificar qué detalle sirve a la pregunta y documentar si la interpretación principal persiste.

## 8. Asociación global y por grupo

Observación: la correlación global es aproximadamente 0.845; dentro de cada grupo es aproximadamente −0.944. No hay un error de cálculo: son resúmenes de conjuntos diferentes.

Mecanismo conocido del generador: B tiene horas y niveles de consumo más altos que A. Dentro de cada grupo se impuso la fórmula `base − 1.5 × horas + residuo`. La separación entre grupos domina la asociación global; la pendiente negativa aparece al analizarlos por separado.

Conclusión injustificada: «si hacemos funcionar un equipo más horas, ahorraremos energía». Los datos son construidos y no representan una intervención. En datos reales habría que estudiar comparabilidad, medición y posibles variables adicionales antes de proponer una explicación causal.

## 9. Corregir una conclusión

Una formulación defendible sería:

> S3 tiene un único consumo preparado, igual a cero, de cuatro días previstos. No podemos comparar eficiencia entre sensores porque difieren sus coberturas, faltan horas y no conocemos equipos ni servicios equivalentes. S1 y S2 muestran valores mayores el 4 que el 1 de septiembre en sus días disponibles, pero hay huecos. No hemos observado el consumo completo del sistema ni demostrado un aumento en cada día del período.

Los problemas eran confundir menor consumo con eficiencia, ignorar el tamaño y cobertura de cada sensor, y convertir una serie incompleta en una afirmación sobre todos los días y sensores. Sumar lo disponible en cada fecha mezclaría conjuntos distintos.

## 10. Hallazgo y comprobación

Pregunta: «¿representa la media global un consumo típico común a A y B?». Evidencia: «Con 24 casos por grupo, las medianas son 10.625 y 26.625 kWh; la media global de 18.625 cae en un intervalo sin observaciones». Interpretación: «La separación entre grupos hace insuficiente resumirlos con una sola cifra». Límite: «Las observaciones se construyeron para estudiar este patrón y no representan una población real».

Una comprobación automática útil verifica que el histograma conserva 48 casos y que cada grupo conserva 24, tanto en el resumen como en los puntos. También puede comprobar la frecuencia cero de `[16,20)`. Eso no decide por sí solo si el título, el encuadre o la conclusión son adecuados: hay que revisar la figura y el contexto.

## Orientación para el reto

Una entrega sólida separa preguntas, registra comandos y fuentes, explica qué cambió en la variante y escribe una limitación concreta por hallazgo. Un informe más largo no obtiene mejor valoración si pierde denominadores o afirma causas que no se observaron.

No hay un único informe final: se evalúa la correspondencia entre pregunta, cálculo, figura e interpretación mediante la rúbrica del reto.

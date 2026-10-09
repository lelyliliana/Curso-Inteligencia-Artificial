# Soluciones — Unidad 10

[Volver a los ejercicios](../README.md) · [Reto](../reto.md)

Las preguntas abiertas admiten otras respuestas si mantienen coherencia entre información disponible, partición, métrica y conclusión.

## 1. Definir el caso predictivo

Unidad: un día de una instalación. Entrada: consumo del día anterior, disponible al emitir el pronóstico. Objetivo: energía consumida en las siguientes 24 horas, en kWh. Momento de predicción: 00:00 UTC−05:00; objetivo disponible: 24 horas después, según el supuesto simplificado del laboratorio.

Sería filtración utilizar el total de energía del día que comienza o un informe posterior calculado con ese total como entrada del pronóstico. La fecha de descarga del CSV no demuestra que cada columna estuviera disponible al decidir.

## 2. Ajustar, elegir e informar

Entrenamiento estima parámetros: constantes, mayorías y mediana de imputación. Validación permite comparar candidatos bajo el criterio fijado y desarrollar el procedimiento. Prueba permite evaluar el procedimiento ya elegido.

Si tras leer prueba modificamos variables, candidatos o transformaciones para mejorar ese resultado, hemos incorporado prueba al desarrollo. Podemos continuar investigando, pero no presentar la siguiente puntuación en esos mismos datos como una evaluación final nueva e independiente. Debe revisarse el protocolo y obtenerse otra evaluación adecuada.

## 3. Elegir la separación

Para anticipar mañana en la misma instalación, usaría una partición temporal y verificaría la disponibilidad de etiquetas al comenzar el siguiente bloque. Para equipos no vistos, asignaría equipos completos a conjuntos disjuntos.

La semilla reproduce un sorteo; no evita mezclar información futura ni observaciones del mismo grupo. Un porcentaje describe el tamaño de los bloques, pero no garantiza suficientes positivos, equipos o períodos. Si queremos equipos nuevos en una época futura, habría que combinar ambas restricciones.

## 4. Dos constantes aprendidas

Entrenamiento: `2, 2, 8`. Su media es 4 y su mediana es 2.

| Candidato | Predicciones para validación | Errores absolutos frente a `2, 3` | MAE |
|---|---|---|---:|
| Media | `4, 4` | `2, 1` | 1.5 |
| Mediana | `2, 2` | `0, 1` | 0.5 |

Seleccionamos la mediana por menor MAE de validación. No calculamos otra mediana con `2, 3`: esos objetivos se usan para evaluar los parámetros aprendidos. Que la mediana gane aquí no garantiza que siempre gane en datos futuros.

## 5. Errores que se cancelan

Reales `10, 14, 12`, predicciones `11, 12, 13`. Errores firmados: `−1, 2, −1`; absolutos: `1, 2, 1`; cuadrados: `1, 4, 1`.

- `MAE = (1 + 2 + 1)/3 = 4/3 ≈ 1.333`.
- `RMSE = √((1 + 4 + 1)/3) = √2 ≈ 1.414`.
- Error medio firmado: `(−1 + 2 − 1)/3 = 0`.

La suma cero oculta errores individuales. Sirve para revisar dirección media, acompañada de magnitud y casos, pero no reemplaza MAE o RMSE.

## 6. Respaldo de persistencia

Entradas observadas de entrenamiento: `10, 14`. Su mediana es 12. Para entradas `None, 0, 20`, persistencia produce `12, 0, 20`.

El cero es un valor presente; no debe confundirse con ausencia. No se usan entradas de validación o prueba para recalcular el respaldo ni sus objetivos para decidir qué imputar. Tampoco se mezcla la mediana de la entrada con la del objetivo de una referencia constante.

## 7. Clasificación con una clase menos frecuente

Con `VP=3`, `VN=12`, `FP=1`, `FN=0`, hay 16 casos y tres positivos reales:

- Exactitud: `(3 + 12)/16 = 0.9375`.
- Precisión: `3/(3 + 1) = 0.75`.
- Recobrado: `3/(3 + 0) = 1`.
- F1: `6/(6 + 1 + 0) = 6/7 ≈ 0.857`.

Si siempre predecimos cero en esos mismos casos, tendremos `VP=0`, `VN=13`, `FP=0`, `FN=3`. La exactitud será `13/16 = 0.8125`, pero el recobrado y F1 serán cero. La precisión no está definida porque no hubo ninguna predicción positiva.

La comparación necesita la matriz de confusión y el propósito de la tarea. F1 es el criterio acordado en este ejercicio, no un sustituto universal del costo de equivocarse.

## 8. Identificadores únicos no bastan

La evaluación no representa equipos nuevos si E01 aporta filas tanto a entrenamiento como a validación, aunque cada aviso tenga un identificador distinto.

El control debe verificar dos condiciones: que los identificadores de aviso sean únicos y que la intersección de equipos entre particiones esté vacía. La función `validar_separacion()` hace ambas comprobaciones para los conjuntos cargados. Prueba se incorpora al control solo al abrir su archivo en el cierre.

## 9. Etiqueta que llega tarde

No basta ordenar las fechas de predicción. Si una etiqueta de entrenamiento llega el 5 de febrero, no estaba disponible al preparar una validación que comienza el día 4.

Debe redefinirse el corte de ajuste según disponibilidad: retirar de ese ajuste los ejemplos cuya etiqueta aún no había llegado, conservarlos en el historial y decidir con una regla documentada dónde podrán usarse después. También podría desplazarse el inicio del siguiente bloque, si eso corresponde a la pregunta real. La decisión debe preceder a la comparación y considerar el horizonte completo, sin elegir filas por los errores que producen.

En el CSV de regresión publicado todas las etiquetas llegan exactamente 24 horas después y los límites son compatibles. Si la disponibilidad real fuera distinta, habría que revisar tanto el contrato de datos como el esquema de partición.

## 10. Registro mínimo y siguiente decisión

Un registro de validación puede indicar:

| Elemento | Registro |
|---|---|
| Pregunta | Clasificar avisos de equipos no vistos con una señal previa |
| Partición | E01–E04 entrenamiento; E05–E06 validación; E07–E08 reservados |
| Código y datos | Commit del curso, versión `lineas-base-v1` y huellas del JSON |
| Candidatos | Mayoría global y tabla por señal, sin usar identificadores |
| Ajuste | Mayoría 0; baja → 0, alta → 1; soportes 24 y 8 |
| Selección | Maximizar F1 positivo; desempate a favor de mayoría |
| Resultado de validación | F1 de mayoría 0; por señal `6/7`; se selecciona por señal |
| Error concreto | C06-08 es un falso positivo del candidato seleccionado |
| Límite | 16 avisos de solo dos equipos sintéticos; relación impuesta por generación |

Si un modelo más complejo no supera la línea base en validación, no lo escogería solo por su complejidad. Revisaría la pregunta, calidad y cantidad de datos, posibles errores de implementación y el costo de cada alternativa. Si rediseño, registro una nueva versión utilizando el conjunto permitido; no busco una justificación consultando prueba para favorecerlo.

## Orientación para el reto

Antes del cierre, deja por escrito candidato, parámetros, criterio y huellas. Después, conserva el resultado final aunque sea peor que validación. La entrega se valora por la corrección del flujo y de la interpretación, no por alcanzar una puntuación objetivo.

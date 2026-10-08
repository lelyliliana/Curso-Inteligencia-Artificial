# Soluciones — Unidad 1

[Volver a la unidad](../README.md) · [Índice del curso](../../README.md)

Estas respuestas orientan la revisión. En las actividades de diseño puede haber varias propuestas válidas si justifican el contexto, el mecanismo y la evaluación.

## Ejercicio 1 — Relaciones entre enfoques

La IA abarca sistemas para tareas como percepción, razonamiento, planificación y aprendizaje. El ML ajusta comportamientos con datos o experiencia y forma parte de la IA. El DL utiliza redes neuronales de múltiples capas dentro del ML. La IA generativa se centra en producir contenido y puede emplear DL, pero generar y clasificar son finalidades distintas.

Ejemplos: una búsqueda de ruta pertenece a un enfoque de planificación; un umbral ajustado con etiquetas es un modelo aprendido; una red profunda puede clasificar imágenes; un modelo generativo puede producir audio. La técnica y la tarea deben describirse por separado.

## Ejercicio 2 — Tarea y mecanismo

| Caso | Tarea | Mecanismo posible | Evidencia necesaria |
|---|---|---|---|
| Promedio de notas | Cálculo | Operaciones convencionales | Datos correctos y fórmula comprobada |
| Imágenes de hojas | Clasificación | Modelo supervisado | Etiquetas revisadas y evaluación sobre imágenes separadas |
| Ruta con obstáculos | Planificación | Búsqueda en estados | Representación válida, restricciones y costo de la ruta |
| Explicación documental | Recuperación y generación | Buscador, con generación opcional | Fuente correcta y afirmaciones respaldadas |
| Respaldo horario | Automatización | Tarea programada | Ejecución, integridad y restauración de los archivos |

La tabla plantea posibilidades, no la única implementación correcta. Por ejemplo, una explicación documental puede elaborarse por una persona a partir de los resultados de un buscador, sin generación automática.

## Ejercicio 3 — Dónde está el aprendizaje

- Característica: `consumo_kwh`.
- Etiqueta: `revision`.
- Candidatos: extremos y puntos medios calculados en `ajustar_umbral`.
- Entrenamiento: comparación de candidatos mediante errores sobre `entrenamiento`.
- Inferencia: ejecución de `predecir` con una lectura y el umbral elegido.
- Evaluación: comparación de etiquetas y salidas sobre `prueba` y `cambio_contexto`.

Ninguna etiqueta de prueba se usa para ajustar el umbral. El programa valida ese grupo, pero el ajuste recibe solo entrenamiento.

El parámetro aprendido es 15,5. La familia de modelos y el criterio de búsqueda fueron definidos por una persona. Aprender un parámetro no significa que el programa invente autónomamente toda su arquitectura.

## Ejercicio 4 — Cambiar una etiqueta

Al cambiar la etiqueta del consumo 14 a 1, los casos sin revisión llegan hasta 12. La separación pasa a estar entre 12 y 14. El candidato elegido es **13** y produce cero errores en el entrenamiento modificado.

En la prueba original, el consumo 15 tiene etiqueta 0, pero el modelo con umbral 13 lo clasifica como revisión. El resultado es **5 aciertos de 6 y un error**.

La modificación de una sola etiqueta cambia el parámetro y un resultado de prueba. Esto ilustra sensibilidad en un conjunto pequeño; no permite cuantificar esa sensibilidad en una población real.

## Ejercicio 5 — Limitar la conclusión

Faltan datos reales representativos, definición contextual de anomalía, etiquetas verificadas, separación adecuada, análisis de distintos errores y evaluación en condiciones de uso. También faltan datos sobre las consecuencias de actuar a partir de una alerta.

Una conclusión válida sería: «El umbral ajustado obtuvo seis aciertos en los seis casos sintéticos de prueba definidos para el ejercicio. El resultado muestra el funcionamiento del procedimiento, pero no demuestra eficacia sobre consumos reales ni sobre otros criterios de revisión».

## Ejercicio 6 — Combinaciones

Con tres comienzos, tres temas y tres cierres hay `3 × 3 × 3 = 27` combinaciones posibles.

Con dos temas adicionales quedan cinco temas: `3 × 5 × 3 = 45`. El programa sigue seleccionando fragmentos escritos. No se entrenó un modelo por agregar elementos a las listas.

Al pedir cuatro frases puede haber repeticiones: las selecciones se realizan con reemplazo. «27 combinaciones posibles» no significa «27 frases distintas garantizadas en cada ejecución».

## Ejercicio 7 — Contexto y entrenamiento

Podemos afirmar que la aplicación conserva información y la incorpora como entrada en una consulta posterior. No podemos concluir que el modelo haya actualizado sus pesos ni que se haya realizado un entrenamiento con esa conversación.

Para afirmar que existe entrenamiento necesitaríamos evidencia de ese proceso, no solo observar que la respuesta menciona un dato de una conversación previa.

## Ejemplo de ficha del reto

**Necesidad y usuario:** una persona que coordina tutorías necesita detectar fechas próximas y disponer de un resumen semanal. El alcance inicial es una lista de tutorías confirmadas, no una evaluación del desempeño del estudiante.

**Entradas:** fechas y responsables de encuentros confirmados, disponibles en un calendario autorizado. Los datos usados para la demostración serán ficticios.

**Salida:** lista ordenada de encuentros de los próximos siete días. Ejemplo: dos tutorías confirmadas dentro de ese intervalo.

**Alternativa convencional:** filtro de fechas y ordenamiento. Puede resolver la necesidad sin ML. Se compara con una lista elaborada manualmente sobre los mismos casos.

**Alternativa de IA:** resumen redactado de las tutorías recuperadas. Solo se justifica estudiarlo si se necesita adaptar la presentación del texto. Introduce la posibilidad de omitir o inventar detalles y requiere revisar las afirmaciones.

**Elección inicial:** implementar primero el filtro convencional. La generación de texto no es necesaria para identificar qué tutorías están próximas.

**Evaluación:** comprobar inclusión de encuentros dentro del intervalo, exclusión de los que están fuera y comportamiento en los límites de fecha. Si se añade generación, verificar también que cada fecha y responsable coincida con los datos recuperados.

**Errores:** omitir una tutoría próxima o incluir una fecha fuera del intervalo. En un texto generado también podría aparecer un responsable que no figura en los datos.

**Revisión humana:** mostrar los registros originales para que la persona coordinadora confirme o corrija fechas antes de comunicar el resumen. El prototipo no envía mensajes automáticamente.

**Límites:** la aplicación no confirma disponibilidad personal ni sustituye los acuerdos con participantes. Si los datos del calendario están desactualizados, el resumen puede estarlo.

**Información pendiente:** permisos de acceso, criterio exacto del intervalo y forma de actualizar las tutorías.

Este ejemplo concluye que una primera solución convencional es suficiente. La decisión está justificada por la tarea y puede revisarse si aparece otra necesidad.

[Volver a la unidad](../README.md)

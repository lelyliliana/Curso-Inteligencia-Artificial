# Ficha completada — CNN de trazos sintéticos

[Unidad](../README.md) · [Plantilla](../plantillas/informe_vision.md)

**Propósito:** enseñar representación de imágenes, convolución, comparación y evaluación por procedencia. El modelo clasifica un trazo como horizontal, vertical o diagonal; no detecta cajas ni segmenta píxeles. No se ha validado para una aplicación con fotografías reales.

## Datos y preparación

240 PNG L de 16×16, correspondientes a 120 escenas sintéticas: 60 escenas de entrenamiento, 30 de validación y 30 de prueba, con dos vistas por escena. Se varían geometría, intensidad, textura y ruido; la segunda vista incluye una oclusión 4×4. La etiqueta corresponde al trazo original y puede resultar ambigua después de ocluirlo.

Las escenas se separan antes de crear vistas. Se comprueban IDs, grupos y píxeles idénticos; no se implementa detección general de casi duplicados. La entrada solo contiene píxeles: /255, media de entrenamiento 0,1612087674 y desviación 0,1500248133. El modo, resolución y orden de clases son parte del contrato de inferencia.

## Comparación y elección

Se fijaron prevalencia, un modelo lineal de 771 parámetros y dos CNN de 363 parámetros, una con reflejos horizontales durante entrenamiento. Todos los modelos entrenables recibieron 60 épocas y 300 actualizaciones. CE de validación eligió la CNN **sin aumento**, época 45. No se reajustó tras elegir. La CNN con reflejos no mejoró la pérdida en esta comparación.

| Evaluación | Escenas / vistas | CE | Exactitud | Macro F1 | Error |
|---|---|---:|---:|---:|---|
| Validación | 30 / 60 | 0,0707 | 0,9833 | 0,9833 | Una vertical→diagonal |
| Cierre didáctico | 30 / 60 | 0,0406 | 0,9833 | 0,9833 | Una horizontal→diagonal |

La validación influyó en la selección y en el análisis visual. El cierre se abrió después y no provocó modificaciones. Ahora sus resultados son públicos: variantes diseñadas a partir de ellos necesitan otro cierre para aportar evidencia independiente. Las métricas describen vistas correlacionadas por pares; no se presentan intervalos basados en 60 escenas independientes.

## Recarga

El artefacto guarda arquitectura, estado de época 45, orden de clases, modo L, forma [1,16,16], divisor, media y desviación. Se carga en una instancia nueva en CPU, se verifica estructura y se usa eval/no_grad. El error máximo en logits sobre las 60 vistas de validación es 0,0 en el entorno registrado. El archivo sirve para inferencia, no para reanudar exactamente Adam.

## Límites y decisión

- Solo tres orientaciones y un trazo por escena; sin fondos naturales, perspectivas, objetos múltiples ni fotografías.
- Una semilla de datos y modelos; no se estima variabilidad entre repeticiones.
- Una oclusión puede borrar evidencia de la clase; una respuesta segura del modelo no recupera información ausente.
- No se estudian calibración, política de abstención, costos de error ni condiciones reales de adquisición.
- Menos parámetros no garantiza mejor rendimiento general; aquí la estructura convolucional resulta adecuada para estos trazos.
- La coincidencia de recarga se comprobó en un entorno CPU concreto, no en todas las plataformas.

Decisión: mantener como demostración educativa. Antes de una aplicación real, formular el uso, documentar procedencia y condiciones de datos, separar por la unidad relevante, revisar etiquetas ante pérdida de información y realizar evaluación independiente con métricas apropiadas.

# Reto — Auditar un clasificador de peticiones

[Unidad](README.md) · [Plantilla de informe](plantillas/informe_lenguaje.md)

Una coordinación académica quiere estudiar si un clasificador podría ayudar a ordenar peticiones. Entrega una demostración reproducible y una decisión de uso proporcional a la evidencia. Esta práctica no autoriza el uso automático con estudiantes reales.

## Entregables

1. Reproduce ambos laboratorios y el cálculo manual. Conserva comandos, versiones, huellas y JSON del modelo; explica cómo comparar probabilidades después de recargarlo.
2. Dibuja o describe la separación 18/9/9 familias → 54/27/27 textos. Identifica metadatos que revelarían etiquetas si se usaran como características.
3. Reconstruye la matriz de validación y sus métricas. Examina los tres errores, agrupándolos por origen. Compara CE y número de columnas entre candidatos.
4. Explica la colisión de unigramas en d01/d02, los vectores cero y los casos sin etiqueta válida. Escribe al menos tres nuevos diagnósticos, identificándolos como exploración de desarrollo y sin mezclarlos con el cierre publicado.
5. Propón una sola extensión: por ejemplo, conservar fronteras de oración, revisar el catálogo o diseñar una política de aclaración. Declara qué datos se necesitarían y el criterio que se fijaría antes de medirla. Implementar una extensión es opcional; conseguir mayor exactitud en el cierre conocido no da puntos adicionales.
6. Entrega una ficha que decida el uso permitido, cite límites y describa una evaluación futura con orígenes nuevos. Si incorporas textos ajenos, su procedencia y condiciones deben estar resueltas; puedes completar todo el reto con textos sintéticos propios.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Representación | 20 | Cálculo de conteos, df, IDF y norma; desconocidos y orden explicados |
| Separación y trazabilidad | 20 | Familias antes de variantes; entradas permitidas; huellas y límites del corpus |
| Evaluación | 20 | Criterio predefinido, matriz reconstruida y análisis por familia |
| Diagnóstico y propuesta | 20 | Casos concretos, referencias ambiguas respetadas y extensión evaluable |
| Reproducción y ficha | 20 | Estado completo, recarga verificada, comandos y decisión de uso justificada |

Una entrega que aprende preparación con prueba o presenta el cierre conocido como evidencia independiente de una mejora debe corregir ese punto antes de considerarse lista. La calidad se valora por lo que puedes comprobar y explicar, no por ocultar resultados desfavorables.

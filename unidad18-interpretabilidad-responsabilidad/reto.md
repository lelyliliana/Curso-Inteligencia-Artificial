# Reto — Una explicación que permita decidir

[Volver a la unidad](README.md) · [Plantilla](plantillas/ficha_modelo.md)

Elige **uno** de los laboratorios y prepara una entrega que permita a otra persona reconstruir una predicción, revisar una limitación y entender tu decisión de uso. No basta copiar una figura o escribir «el modelo es explicable».

## Trabajo común

1. Declara la pregunta, las entradas disponibles, el objetivo, las unidades y la línea base. Describe qué queda fuera del uso propuesto.
2. Conserva `u18-v1-modelos-fijos` para la primera ejecución. Guarda datos, huellas, versiones, comandos y resultados en una carpeta nueva. Identifica la información de entrenamiento, validación y prueba.
3. Reconstruye el caso local prefijado y contrástalo con `predict`. Conserva cifras suficientes para que el redondeo de presentación no altere el cálculo.
4. Elabora la ficha utilizando la plantilla y un análisis de impacto con al menos tres situaciones distintas. Relaciona cada limitación con una acción, quién la ejecutaría, sus recursos y lo que esa acción todavía no resuelve.
5. Decide si la evidencia basta para el uso propuesto. «Solo docencia; falta evidencia para operación» es una conclusión válida y puede recibir la máxima calificación si está bien sustentada.
6. Abre prueba al terminar el análisis, sin reajustar ni cambiar el protocolo. Registra el resultado y explica por qué no sirve como cierre independiente de una futura corrección orientada por él.

## Si eliges consumo

- Expresa el modelo en coordenadas estandarizadas y unidades originales. Explica la referencia de las contribuciones.
- Demuestra algebraicamente y con las filas de validación que sumar `a` al coeficiente de horas estandarizadas y restarlo del de minutos conserva predicciones cuando ambas z son iguales. Conserva el modelo original; etiqueta la modificación como diagnóstico matemático en una copia.
- Compara los cuatro bloques de permutación del protocolo. Reporta MAE original, deltas, media, desviación, semilla y repeticiones. Distingue perturbación del predictor, eliminación de columnas y efecto de una intervención real.
- Explica por qué la redundancia y los rangos simulados limitan conclusiones sobre ahorro energético, incluso si el MAE es pequeño.

## Si eliges alertas

- Reconstruye la ruta del caso prefijado y cuenta las clases de entrenamiento en su hoja. Contrasta la clase con la biblioteca.
- Presenta matriz de confusión y métricas por los cuatro grupos, incluyendo grupos sin positivos o sin filas. Calcula el recobrado global desde los conteos, no como media simple de tasas.
- Explica por qué no usar grupo como entrada no evita diferencias por condición de medición. No cambies nombres de grupos ni elimines filas difíciles para mejorar la auditoría.
- Diseña una respuesta a falsos negativos que no dependa únicamente de revisar alertas positivas. Distingue procedimientos propuestos de controles realmente implementados.

## Entrega

Un informe o notebook legible, la ficha completada, resultados JSON/CSV, las figuras pertinentes y los comandos para reproducirlos. Identifica cualquier cambio que hayas realizado. Si deseas mejorar el modelo, preséntalo como una extensión con desarrollo y evaluación nueva; no mezcles su rendimiento con el cierre del protocolo original.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Pregunta, datos y separación | 15 | Roles de columnas y particiones; no hay filtración |
| Reconstrucción local | 25 | Operaciones, unidades o reglas; coincidencia con predicción |
| Diagnóstico global o por grupos | 25 | Permutación con dependencia, o errores con soporte y denominadores |
| Ficha y análisis de impacto | 20 | Usos, límites, acciones concretas y responsabilidad identificada o explícitamente pendiente |
| Reproducción, cierre y claridad | 15 | Comandos, versiones, artefactos trazables y conclusión proporcional |

Errores que requieren corrección para considerar completado el reto: seleccionar o reajustar con prueba y llamarla independiente; interpretar una contribución como causa demostrada; convertir una tasa indefinida en cero; ocultar grupos con bajo rendimiento; afirmar que una explicación fiel garantiza seguridad; presentar supervisión o controles propuestos como si ya estuvieran implementados.

Comprueba antes de entregar: ¿otra persona puede reconstruir tu caso, entender qué evidencia falta y saber qué harías ante un error? Si alguna respuesta es negativa, completa esa parte de la ficha.

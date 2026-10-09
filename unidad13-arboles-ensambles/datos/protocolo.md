# Protocolo `arboles-v1`

[Unidad](../README.md) · [Diccionario](README.md)

## Contrato

Predecir `revision_confirmada`, con clase positiva 1, usando una señal en `franja` y dos en `region`. Las señales se declaran previas a la revisión, pero los CSV no permiten auditar su disponibilidad temporal. Identificador y etiqueta no son entradas. Las particiones son nuevas y fijas; todos los candidatos se evalúan sobre los mismos casos.

Entrenamiento y validación requieren ambas clases; prueba no. Datos inválidos detienen el procedimiento. No se imputan datos, no se eliminan observaciones por su error y no se escalan entradas. Los rangos marginales utilizados para marcar consultas fuera de rango se calculan solo en entrenamiento; no son una transformación ni una comprobación completa de cobertura conjunta.

## Decisiones fijadas antes del cierre

| Componente | Regla |
|---|---|
| Referencia | `DummyClassifier(strategy="prior")`: clase mayoritaria y frecuencias de entrenamiento |
| Criterio de cortes | Gini, `splitter="best"` en árboles individuales |
| Árboles de franja | `(max_depth, min_samples_leaf)`: `(1,1)`, `(3,5)`, `(None,1)` |
| Árbol de región | Profundidad máxima 6, mínimo 2 por hoja, ambas entradas candidatas |
| Bagging de región | 31 árboles con los controles anteriores; 180 extracciones con reemplazo por árbol |
| Entradas en bagging | `max_features=1.0`, `bootstrap_features=False`; ambos atributos para cada árbol y cada nodo |
| Bosque de región | 31 árboles; profundidad máxima 6, mínimo 2 por hoja; bootstrap con 180 extracciones |
| Entradas en bosque | `max_features=1` entero: una entrada candidata por nodo, sujeto a encontrar una partición válida |
| Combinación | Promedio de probabilidades de los árboles, sin pesos externos |
| Semilla general | 13; las semillas internas y huellas de muestras se registran |
| Paralelismo | `n_jobs=1` en ensambles |
| Clase predicha | Mayor probabilidad; empate exacto entre 0 y 1 a favor de 0 |
| Selección | Máximo F1 de clase 1 en validación, sin redondear |
| Empate entre candidatos | Primero en el orden publicado, solo si F1 es exactamente igual |
| Reajuste con validación | No |
| Cierre | Solo el candidato elegido, sobre prueba |

Orden de candidatos:

1. Franja: `mayoria`, `arbol_1`, `arbol_3`, `arbol_libre`.
2. Región: `mayoria`, `arbol`, `bagging`, `bosque`.

El JSON registra todos los parámetros de la versión utilizada, incluidos los valores por defecto. No se ajustan pesos de clase, calibración, umbrales, poda posterior ni número de árboles; no se usa estimación fuera de bolsa (OOB). Variar la semilla o añadir un modelo constituye otro experimento, no una repetición idéntica.

La regla de clase coincide con `predict` de la biblioteca; no se aplica el `>=` de la implementación logística de la Unidad 12. Un mínimo de casos por hoja restringe la construcción; en remuestreo, los conteos ponderados por repeticiones y los casos distintos no tienen por qué coincidir. El informe conserva ambas cantidades de la muestra bootstrap.

## Métricas

Se informa VP, VN, FP, FN, exactitud, precisión, recobrado y F1. Una métrica con denominador cero se conserva como `null`. Con positivos reales y ninguna predicción positiva, precisión es indefinida, recobrado y F1 son cero. Sin positivos reales ni predichos, precisión, recobrado y F1 son indefinidos. La comparación exige F1 definido en validación; no lo sustituye por una cifra conveniente.

Gini guía la construcción de nodos con entrenamiento. F1 elige entre candidatos con validación. El propósito de F1 es practicar una comparación centrada en positivos, no representar automáticamente costos reales. Las probabilidades de hoja y sus promedios no se consideran calibrados por construcción.

## Secuencia y evidencia

1. Leer entrenamiento y validación; validar esquema, dominios, clases e identificadores únicos.
2. Calcular rangos y ajustar referencia, árboles y ensambles exclusivamente con entrenamiento.
3. Evaluar todos los candidatos sobre entrenamiento y validación; elegir por el criterio previo.
4. Guardar exportación de desarrollo, commit, versiones y comando. Registrar qué información pública de prueba ya se conocía.
5. Ejecutar el cierre con `--evaluar-prueba`: se repiten ajuste y selección, y después se lee prueba para evaluar solo al elegido.
6. Comparar código, versiones, protocolo, semilla, huellas de desarrollo, modelos, resultados de desarrollo y selección con el registro previo. Una diferencia requiere explicación antes de llamarlo cierre del mismo procedimiento.
7. Informar resultados finales sin seleccionar de nuevo. Si se modifica el procedimiento a partir de prueba, declarar su uso en desarrollo y preparar una evaluación nueva apropiada.

La ejecución común funciona sin `prueba.csv`. Las pruebas de invariancia cambian etiquetas de validación o prueba y comprueban qué componentes no deben cambiar: validación puede alterar selección, pero no ajuste; prueba no puede alterar ninguno de los dos ni sus predicciones. Este control del código no impide consultar los datos públicos antes del cierre.

## Registro y límites

Las huellas SHA-256 identifican bytes de CSV, estructuras de árboles e índices de remuestreo. El resumen de cada árbol contiene semilla, profundidad, nodos y hojas, pero **no serializa un modelo reutilizable**. Las reglas de texto de los árboles individuales redondean los cortes y sirven para lectura. No reconstruyas un predictor exacto a partir de ese redondeo.

Las exportaciones de desarrollo contienen resultados de todos los candidatos; prueba solo aparece en el cierre y solo para el elegido. Las figuras se limitan siempre a desarrollo. La exportación no es una transacción: puede quedar incompleta si falla una escritura o el dibujo.

Estos datos y las respuestas son sintéticos y públicos. Las diferencias observadas no establecen superioridad estadística, independencia respecto de poblaciones reales, disponibilidad efectiva de señales, causalidad, calibración ni utilidad operacional.

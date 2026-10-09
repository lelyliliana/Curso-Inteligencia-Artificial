# Protocolo `no-supervisado-v1`

[Unidad](../README.md) · [Diccionario](README.md)

## Reglas compartidas

- Datos nuevos, particiones fijas, mismas filas para todos los candidatos. Identificador y referencia de anomalía excluidos de las entradas.
- `StandardScaler` ajustado exclusivamente con entrenamiento: media, varianza poblacional y escala registradas. Las columnas constantes usan escala 1.
- Sin imputación ni eliminación de errores; datos inválidos detienen el procedimiento. Identificadores únicos dentro y entre particiones del experimento.
- Semilla principal 14. Límites de BLAS/OpenMP a un hilo durante los experimentos y `n_jobs=1` en Isolation Forest. No se buscan semillas favorables.
- Criterios sin redondear; empate exacto al primero del orden publicado. Las métricas indefinidas se guardan como `null`.
- Prueba solo se abre con `--evaluar-prueba`, después de seleccionar. Se evalúa únicamente al elegido y no se reajusta con validación o prueba.

La marca `fuera_rango` compara cada entrada con mínimos y máximos de entrenamiento. No certifica cobertura conjunta ni bloquea automáticamente una asignación o alerta.

## Agrupamiento

| Componente | Decisión |
|---|---|
| Entradas | `horas_uso`, `consumo_kwh`, en ese orden |
| Candidatos | `k2`, `k3`, `k4` |
| Algoritmo | KMeans, distancia euclídea tras escalar |
| Inicialización | `k-means++`, diez reinicios por ajuste |
| Parada | `max_iter=300`, `tol=1e-4`, algoritmo `lloyd` |
| Ajuste | Centros aprendidos con entrenamiento, reinicio elegido por inercia de entrenamiento |
| Asignación de validación/prueba | Centro aprendido más cercano, sin actualizarlo |
| Selección | Máxima silueta media de validación definida; empate a menor k |
| Silueta indefinida | Candidato no elegible; si ninguno es elegible, detener |
| Diagnósticos | Inercia de entrenamiento, distancia cuadrada media, tamaños, centros y ARI |
| Estabilidad | Reajustar cada k con semillas 29 y 47, mismo entrenamiento y escala; comparar con el ajuste principal sobre los mismos casos de validación |

La estabilidad es un diagnóstico; no interviene en la regla de selección ni reemplaza el modelo principal. No se remuestrean casos. Si se cambia la semilla principal a 29 o 47, una de las comparaciones repite esa misma semilla y debe interpretarse así.

La silueta se calcula con distancias entre los casos del conjunto que se evalúa, después de asignarlos a centros de entrenamiento. No se ajustan centros con todos los conjuntos juntos. Su cálculo requiere entre 2 y `n−1` grupos presentes; si no se cumple, se conserva `null`, incluso en prueba. No hay etiquetas verdaderas de grupos ni métrica de exactitud.

## Anomalías

| Componente | Decisión |
|---|---|
| Entradas | `senal_a`, `senal_b`, en ese orden |
| Referencia de ajuste | Entrenamiento presuntamente ordinario, sin etiquetas |
| Candidatos y desempate | `sin_alertas`, `distancia_centro`, `aislamiento` |
| Sin alertas | Siempre 0, sin puntuación ni umbral |
| Distancia | Norma euclídea del caso estandarizado respecto del origen, que representa la media de entrenamiento |
| Isolation Forest | 64 estimadores, muestras de `min(64,n_entrenamiento)` casos, `bootstrap=False`, `max_features=1.0`, `contamination="auto"` |
| Puntuación del bosque | `-score_samples`, mayor significa más inusual |
| Umbral | Posición `ceil(0,95 × n_calibracion)` de las puntuaciones ordenadas de calibración, contando desde 1 |
| Alerta | Puntuación estrictamente mayor que umbral; empate sin alerta |
| Selección | Mayor F1 de validación respecto de `anomalia_sintetica=1` |

El `offset_` interno y `predict` de Isolation Forest no deciden las alertas: `contamination="auto"` no reemplaza nuestro umbral. No se ajusta el cuantil con etiquetas ni se fuerza una cantidad de alertas en validación o prueba. La calibración de umbral no es calibración probabilística. Sus casos no se incorporan al ajuste del escalador ni del bosque.

Entrenamiento y calibración no tienen etiquetas, por lo que solo se informan puntuaciones, alertas y fracciones; no se atribuyen matrices de confusión observadas a esos archivos. Validación sí requiere ambas clases y añade VP/VN/FP/FN, exactitud, precisión, recobrado y F1. Prueba puede tener una sola clase; los denominadores cero se conservan como indefinidos. La selección usa referencias sintéticas: el ajuste es no supervisado, pero la elección del procedimiento sí aprovecha etiquetas.

## Registro y cierre

1. Conservar exportación de desarrollo, commit, versiones, comandos y conocimiento previo de las respuestas públicas.
2. Fijar candidato, escala, configuración y, para anomalías, umbral antes de ejecutar cierre.
3. Cerrar con el mismo código y archivos. Cada ejecución vuelve a ajustar y seleccionar antes de leer prueba.
4. Comparar protocolo, semilla, versiones, huellas de desarrollo, escala, modelos, selección y resultados de desarrollo con el registro anterior. Si cambian, investigar antes de presentar un cierre del mismo experimento.
5. Informar prueba sin volver a elegir. Cualquier cambio inspirado en prueba requiere reconocer su uso en desarrollo y organizar una evaluación nueva.

Los CSV exportan asignaciones o alertas por candidato y caso. El JSON incluye centros, parámetros y, para el bosque, una huella de estructura; no es una serialización completa para cargar estimadores. Las figuras solo usan desarrollo. La escritura de varios archivos no es atómica y puede quedar parcial.

Este protocolo enseña trazabilidad y evaluación en construcciones públicas. No demuestra categorías naturales, calibración, estabilidad poblacional, causalidad, disponibilidad temporal real ni un detector apto para operar.

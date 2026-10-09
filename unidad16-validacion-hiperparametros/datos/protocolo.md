# Protocolo `validacion-cv-v1`

[Unidad](../README.md) · [Datos](README.md)

## Pregunta y separación

Ciclos predice consumo de un caso independiente a partir de horas y carga previstas. Equipos predice respuesta en grupos nuevos a partir de dos señales previas. Identificadores y objetivos nunca entran en las matrices de características.

| Experimento | Desarrollo | Validación interna | Prueba final |
|---|---|---|---|
| Ciclos | 160 casos | KFold, cuatro pliegues, shuffle=True, random_state=16 | 64 casos independientes |
| Equipos | 144 casos de 12 equipos | GroupKFold, cuatro pliegues, shuffle=False | 48 casos de cuatro equipos nuevos |

Todos los candidatos comparten exactamente los índices del experimento. Cada fila valida una vez. En ciclos los pliegues tienen 120/40 casos; en equipos, 108/36 casos y nueve/tres equipos. No se separa según la métrica más favorable.

## Rejilla, ajuste y presupuesto

Orden publicado: `mediana`, `knn3_uniform`, `knn3_distance`, `knn9_uniform`, `knn9_distance`, `knn21_uniform`, `knn21_distance`.

La mediana se calcula con objetivos del ajuste correspondiente. Cada KNN encadena `StandardScaler` y `KNeighborsRegressor`, con k=3,9,21 y weights=uniform,distance; fija algorithm=brute, metric=euclidean y n_jobs=1. Los cálculos se ejecutan con un hilo en las bibliotecas numéricas. Cada pliegue recibe un clon nuevo; el escalador nunca se ajusta previamente con desarrollo completo para alimentar CV.

Se conserva orden de casos. Los empates en el límite del vecino k pueden depender de ese orden. Con pesos distance y coincidencias exactas, cuentan solo los vecinos seleccionados de distancia cero. No se buscan otras variables, semillas, métricas de distancia ni rejillas mirando prueba.

Ciclos realiza 28 ajustes de CV y uno de reajuste. Equipos añade cuatro ajustes de diagnóstico: 33 en total. El diagnóstico fija previamente `knn3_uniform` y usa KFold con semilla 16 sobre las mismas filas. No modifica la selección por GroupKFold. Los resúmenes de escala de cada pliegue documentan los conjuntos permitidos.

## Criterio y medidas

Se minimiza la media no ponderada de los cuatro MAE de validación. Entre candidatos a distancia no mayor de `1e-10` unidades del mínimo global, se elige el primero del orden publicado. No se usa redondeo de consola ni desviación para elegir. La tolerancia es numérica, sin significado de equivalencia estadística.

Se guardan MAE, RMSE y sesgo `real−predicción` de ajuste y validación por pliegue. La desviación de MAE usa divisor cuatro (`ddof=0`); no es intervalo de confianza. El MAE OOF pondera cada observación igual. Coincide con la media de MAE en estos datos por igualdad de tamaños, sin extender la afirmación a grupos desiguales ni métricas no aditivas. No se calculan R², error estándar ni pruebas de significación.

## Secuencia y reajuste

1. Leer y validar solo `desarrollo.csv`; construir los pliegues y comprobar tamaños.
2. Ajustar cada candidato desde cero dentro de cada pliegue; evaluar, conservar predicciones e índices y resumir CV.
3. Seleccionar por el criterio fijo.
4. Ajustar una instancia nueva del elegido con **todo desarrollo**, incluido el escalador si lo hay. No reutilizar el último modelo de pliegue ni promediar los modelos.
5. En equipos, calcular el diagnóstico por filas para el candidato previamente fijado. No volver a elegir con él.
6. Exportar el registro de desarrollo con `prueba: null`. Conservar commit y comandos además de las versiones y huellas del JSON.
7. Para cerrar, repetir el mismo flujo con `--evaluar-prueba`. Solo después de selección y reajuste, abrir prueba, comprobar separación y predecir con el modelo reajustado.
8. Comparar resultados de desarrollo, parámetros, código y fuentes con el registro anterior; evaluar en prueba únicamente al elegido. No cambiar la configuración tras verla.

El reajuste está previsto desde el comienzo. A diferencia de las unidades 10–15, se usa todo desarrollo para el modelo final, pero ninguna fila de prueba. Las predicciones OOF proceden de modelos diferentes, anteriores a ese reajuste.

Si prueba inspira cambios, pasa a influir en desarrollo: reconocerlo y definir evaluación nueva. Las puntuaciones que decidieron la búsqueda no son evidencia independiente de todo el procedimiento. La validación anidada se explica como extensión; no se ejecuta aquí.

## Exportación y límites

JSON incluye protocolo, versiones, rejilla, huellas, índices desde cero, IDs, grupos, métricas, resúmenes de ajustes, predicciones OOF, elección y reajuste. Los CSV distinguen OOF principal, diagnóstico por filas y prueba del elegido. Las figuras utilizan exclusivamente desarrollo. Los resúmenes no serializan los vecinos internos ni guardan automáticamente commit o comandos; conservar código y CSV para repetir. Las exportaciones requieren un directorio nuevo y pueden quedar parciales si falla la escritura.

La prueba común no se lee ni necesita existir. Cambiar solo sus objetivos no debe modificar CV, elección, reajuste o predicciones; cambia su huella y puede cambiar métricas y residuos. Las pruebas automatizadas controlan el programa, no evitan que una persona mire archivos públicos.

La disponibilidad es declarada, sin auditoría temporal real. No se demuestra utilidad en una población real ni que 12 equipos representen una flota. El ejemplo temporal y el contraejemplo de escala usan arreglos independientes, sin afectar los laboratorios.

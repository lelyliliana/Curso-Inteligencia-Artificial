# Soluciones comentadas — Unidad 8

[Volver a la unidad](../README.md)

## 1. Acciones

Dividir Wh por 1000 es una conversión de unidad con factor conocido, siempre que la unidad original esté confirmada. Sustituir −2 por 10 apoyándose en el acta es una corrección. Completar una ausencia con la mediana es imputación; esa mediana se aprende de los datos permitidos. Apartar versiones conflictivas conservando motivos es cuarentena.

Corregir e imputar pueden cambiar una celda, pero tienen fundamentos diferentes: referencia específica frente a estimación. Un valor inválido no revela cuál debe ser la corrección.

## 2. Balance

| Configuración | Preparados | Duplicados | Cuarentena | Total |
|---|---:|---:|---:|---:|
| Conservadora | 8 | 1 | 3 | 12 |
| Con referencia | 9 | 1 | 2 | 12 |

Sin corrección, se preparan los registros 1, 2, 3, 4, 5, 6, 9 y 12. El 7 es copia del 6. Los registros 8, 10 y 11 van a cuarentena.

La referencia recupera el 8. En ambos casos hay tres preparados incompletos: el 3 carece de consumo, el 4 de temperatura y el 12 de horas. Por tanto, hay cinco casos completos sin corrección y seis con corrección. La corrección no añade una fila al balance: cambia la decisión sobre una fila existente.

## 3. Orden de la política

Las dos filas pretenden describir la misma observación y discrepan. Que 10 cumpla el esquema no demuestra que sea la medición verdadera. El −2 podría ser una corrupción del valor original o las dos versiones podrían estar equivocadas.

Apartar ambas conserva el conflicto para una revisión fundamentada. Eliminar primero la fila inválida ocultaría que existieron dos versiones. Si hubiera una política de versiones respaldada por metadatos, podríamos implementar otra decisión; esos metadatos no existen en la fuente actual.

## 4. Corrección vinculada

La huella identifica los bytes completos de la copia. El registro localiza la fila. Fecha y sensor confirman qué observación se está tratando. `antes` comprueba que la celda contiene el texto que motivó el parche. Juntos evitan aplicar mecánicamente una corrección a una versión o posición equivocada.

No autentican el acta ni prueban que el dispositivo midiera el nuevo valor. En este ejercicio, ACTA-SIM-001 define una referencia ficticia. En un proyecto real, el responsable tendría que comprobar la autoridad y procedencia de esa evidencia.

## 5. Cobertura

Con doce claves esperadas:

- Original: `10/12 × 100 = 83.33%`.
- Conservadora: `8/12 × 100 = 66.67%`.
- Con corrección: `9/12 × 100 = 75%`.

La preparación conservadora aparta la clave inválida de S2 del día 3 y las versiones conflictivas de S3 del día 1. Eliminar duplicados no reduce claves distintas; la cuarentena sí cambia cuáles aparecen en la vista preparada.

S3 pasa de dos claves observadas a una preparada. No hay mejora de cobertura por esconder las incidencias. Además, la presencia de una clave con celdas faltantes no certifica una medición completa.

## 6. Medianas

Entrenamiento observado: `[18,20,22]`; mediana 20. Validación observada: `[30,40]`; mediana `(30+40)/2 = 35`. Grupos mezclados: `[18,20,22,30,40]`; mediana 22.

Se utiliza 20 porque el ajuste se hace únicamente con entrenamiento. El faltante t3 y el faltante v2 se completan con ese número. El método no sabe cuál fue la temperatura ausente; por eso conserva `original=null` y `era_faltante=true`.

## 7. Escalado

Usamos mínimo 18, máximo 22 y rango 4:

| Valor | Resultado |
|---:|---:|
| 18 | 0 |
| 20 | 0.5 |
| 22 | 1 |
| 30 | 3 |
| 40 | 5.5 |
| 16 | −0.5 |

El resultado es adimensional: se divide una diferencia de temperaturas por otra expresada en la misma unidad. Los valores nuevos pueden exceder los extremos aprendidos. Recortarlos o volver a ajustar la escala cambiaría el procedimiento y necesitaría justificación.

## 8. Filtración

Al mezclar grupos, la mediana es 22, el mínimo 18 y el máximo 40. t4, cuyo valor es 22, se transforma en `(22−18)/(40−18)=4/22≈0.1818`, en lugar de 1.

La información de validación ha modificado la representación de entrenamiento. La infracción está en el origen de los parámetros, no en que una métrica suba o baje. El laboratorio no incluye un predictor ni demuestra efectos cuantitativos sobre su rendimiento.

## 9. Casos límite

Con entrenamiento completamente ausente, el programa rechaza el ajuste: no hay mediana observada. Puede ser necesario obtener datos, prescindir de la variable o usar otra fuente, pero no adoptar cero sin fundamento.

Con columna constante, rechaza el rango cero del min-max. Una política diferente podría preservar la constante o descartar esa característica; no es una capacidad implementada aquí.

Una temperatura extrema pero finita pasa el esquema numérico actual. Antes de eliminarla o recortarla se debe verificar la unidad, el contexto y la referencia física. «El lector lo acepta» no equivale a «el valor es plausible».

## 10. Conclusión

Una respuesta posible:

> La preparación conservadora dejó ocho registros, con tres incompletos, y conservó la trazabilidad de un duplicado y tres representantes en cuarentena. La corrección sintética explícita permitió recuperar una lectura, pero no resolvió el conflicto de S3 ni las ausencias. Los indicadores de la vista preparada mejoraron en unicidad y validez, mientras su cobertura quedó por debajo de la original. En el experimento independiente, mediana y escala se ajustaron solo con entrenamiento. No se entrenó un predictor ni se demostró utilidad real. Antes de utilizar las lecturas, debemos aclarar las versiones conflictivas y decidir qué información exige la tarea para los registros incompletos.

## Orientación para el reto

Entrega dos carpetas diferentes del primer laboratorio y un informe del segundo. Comprueba estos invariantes:

1. Todos los registros originales aparecen una sola vez como destino final, aunque puedan tener además acciones de corrección.
2. Los preparados tienen claves únicas y valores observados válidos bajo el esquema.
3. Los faltantes se conservan en la primera práctica y se marcan al imputarse en la segunda.
4. Cambiar únicamente validación no cambia los parámetros aprendidos de entrenamiento.
5. Las huellas de entrada coinciden antes y después y cada exportación ocupa un destino nuevo.

Como variante, cambiar 40 por 400 en validación mantiene los parámetros correctos y produce un escalado de 95.5 para esa observación. No obliga a ajustar de nuevo la escala; sirve para investigar qué significa aplicar una transformación fuera del rango observado.

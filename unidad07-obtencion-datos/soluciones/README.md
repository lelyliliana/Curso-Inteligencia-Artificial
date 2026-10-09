# Soluciones comentadas — Unidad 7

[Volver a la unidad](../README.md)

Las respuestas deben explicar la relación entre archivo, significado y decisión. Una cuenta correcta no justifica por sí sola usar los datos para entrenar.

## 1. Unidad de observación

El CSV pretende representar un resumen por sensor y día; su clave candidata es fecha-sensor. El JSON contiene eventos: consumo en la hora que termina al observarlo, una temperatura puntual o una etiqueta de revisión, con tiempos de observación y disponibilidad.

Compartir `sensor_id` no establece correspondencia entre un día y un evento, ni identifica un mismo episodio. Además, los escenarios son independientes y no se proporcionó una regla de unión. Unir por sensor podría multiplicar filas y asociar objetivos incorrectos.

## 2. Procedencia

Seis preguntas útiles son:

1. ¿Quién creó o exportó el archivo y de qué sistema procede?
2. ¿Qué consulta, filtros o transformaciones se aplicaron?
3. ¿Qué población, periodo y unidad de observación cubre?
4. ¿Qué significan columnas, unidades, códigos y valores ausentes?
5. ¿Qué versión es, cuándo se extrajo y cómo se obtienen actualizaciones?
6. ¿Qué condiciones de uso y acceso están comprobadas?

También hay que relacionarlo con el momento de decisión y las etiquetas del proyecto. El nombre `datos_finales` no responde ninguna de estas preguntas.

## 3. Tipos y unidades

`0012` puede ser un identificador textual cuyos ceros importan; convertirlo a entero produciría 12 y podría confundir códigos distintos. El consumo 12 requiere una unidad y un intervalo: 12 kWh diarios y 12 kWh en una hora no tienen la misma interpretación.

`true` es un booleano. Aunque Python permite algunas operaciones numéricas con booleanos, el esquema rechaza usarlo como medición. Convertir todo a número puede perder identidad y ocultar un error de tipo o de significado.

## 4. Conteos

Consumo tiene diez celdas válidas, una faltante —registro 3— y una inválida —registro 8—. Suman las doce filas originales. Las filas repetidas se cuentan porque el perfil describe el archivo tal como llegó.

El cero del registro 12 expresa un consumo numérico admitido y no se interpreta como ausencia. −2 contradice el modelo de energía consumida no negativa. Si la variable fuera energía neta con exportación, habría que redefinirla y cambiar el esquema; no basta con quitar el error sin explicación.

## 5. Duplicados

6–7 tienen las mismas cinco celdas y representan una aparición adicional de un registro idéntico. 10–11 comparten fecha y sensor, pero difieren en consumo: 6 frente a 7.

El contador de duplicados adicionales es uno: para un grupo con n apariciones idénticas cuenta n−1. No cuenta todos los integrantes ni todos los grupos con clave repetida.

Antes de borrar se debe investigar si hubo reenvío, corrección, dos observaciones legítimas o una clave insuficiente. En el caso 10–11 no tenemos fecha de revisión ni indicador de versión que permita elegir uno con fundamento.

## 6. Cobertura

S1 aporta cuatro claves, S2 cuatro y S3 dos: diez de doce, o 83.33 %. El duplicado de S2 y la repetición con valores distintos de S3 no aumentan la cobertura.

Si el plan incluye solo S1 y S2, hay ocho claves presentes de ocho esperadas: 100 %. Las dos claves observadas de S3 quedan fuera del plan. Persisten el consumo faltante, el inválido y otros problemas del archivo; no se han corregido.

Si el plan abarca hasta el día 5 con tres sensores, se esperan quince claves y solo hay diez: 66.67 %. Se añaden tres ausencias a las dos anteriores. La cobertura expresa presencia de claves, no mediciones válidas ni representatividad.

## 7. Disponibilidad

| Corte UTC | Entradas disponibles | Entradas excluidas por tiempo | Objetivos separados |
|---|---|---|---|
| 08:00 | Ninguna | e01, e02, e03, e04 | e05, e06 |
| 09:00 | e01, e03 | e02, e04 | e05, e06 |
| 09:10 | e01, e02, e03 | e04 | e05, e06 |

A las 08:00, e01 ya se ha observado, pero no se recibe hasta las 08:05. Por eso todavía no puede utilizarse. A las 09:00, e03 satisface la igualdad en ambos tiempos; se admite por la convención inclusiva del programa.

El corte `04:00:00-05:00` corresponde a `09:00:00+00:00`, no a las 04:00 UTC. Comparar solo la parte numérica de la hora produciría un resultado equivocado.

## 8. Objetivo

e06 cumple temporalmente el corte de las 09:00, pero la variable tiene rol objetivo en este caso. Su disponibilidad no cambia ese papel. El lector tampoco permite renombrar su rol como entrada sin cambiar el esquema.

Para usar un historial de fallos en otro proyecto habría que definir episodios, horizonte a predecir, qué fallos son realmente anteriores, cuándo se conocieron y cómo se construyen ejemplos sin incluir el resultado que se intenta predecir. El laboratorio no implementa ese emparejamiento.

## 9. Reproducción

SHA-256 identifica los bytes de una copia. Un cambio en finales de línea, un BOM o distinto espaciado de un JSON puede cambiar la huella sin cambiar sus valores interpretados. La huella no explica procedencia ni certifica veracidad.

El informe debe incluir fuente y versión, archivo, comando, parámetros —especialmente plan esperado y corte temporal—, versión de Python y commit del código, además de resultados y decisiones. Si hubo transformaciones, se documentan por separado junto con las copias derivadas.

## 10. Decisión siguiente

Una conclusión posible:

> El CSV contiene doce registros y diez claves sensor-día de las doce esperadas. Se observaron un duplicado exacto adicional, otra clave con textos distintos y cuatro incidencias de celda. No conocemos las causas de las ausencias ni cuál lectura de S3 debe prevalecer. El JSON admite dos entradas al corte de las 09:00 UTC y mantiene dos objetivos separados. Los casos son sintéticos e independientes; no forman un dataset predictivo. Antes de preparar datos debemos aclarar las repeticiones, documentar el tratamiento de faltantes e inválidos y definir qué información corresponde a cada decisión.

Esta conclusión no propone reemplazar todo faltante con cero ni afirma fallos de dispositivos sin evidencia. Distingue diagnóstico de tratamiento.

## Orientación para el reto

Conserva una ficha por cada fuente o subsecciones claramente separadas. Incluye al menos estas variantes:

| Variante | Predicción verificable |
|---|---|
| Repetir una fila ya presente del CSV | Aumentan filas y duplicados adicionales; la cobertura permanece igual |
| Plan S1 y S2 | Cobertura 8/8; las claves de S3 quedan fuera del plan |
| JSON con corte 09:10 UTC | e02 pasa a estar disponible |
| JSON con hora sin zona | Error de entrada; no se adivina zona |

Tu cambio propio debe conservar el esquema o identificar por qué se rechaza. Por ejemplo, cambiar una temperatura a 900 revela una limitación del rango implementado; no demuestra que ese valor sea físicamente razonable. Documentar esta diferencia es parte del trabajo.

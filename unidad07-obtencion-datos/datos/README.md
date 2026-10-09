# Datos de la Unidad 7

[Volver a la unidad](../README.md)

## Procedencia y propósito

Los archivos fueron construidos expresamente para este curso. Son sintéticos, no se descargaron de un portal ni de una API y no describen sensores, edificios o personas reales. Los identificadores S1–S3 son ficticios. No contienen información personal.

Versión del escenario: 1.0. Su versión exacta se puede identificar con el commit del repositorio y la huella SHA-256 que imprimen los programas. Una modificación del archivo requiere conservar esa nueva huella al documentar los resultados.

Uso previsto: estudiar lectura de formatos, diagnóstico de calidad, cobertura y disponibilidad temporal. No permiten evaluar predicción de fallos, rendimiento energético ni comportamiento de una población real. Esta documentación no añade una licencia general al repositorio ni atribuye licencias a fuentes externas.

## CSV de lecturas

[lecturas_sinteticas.csv](lecturas_sinteticas.csv) tiene encabezado y doce registros. UTF-8, separador coma y decimales con punto. El lector admite BOM y columnas en otro orden si aparecen las mismas cinco una sola vez.

Unidad de observación pretendida: **sensor-día**. Cada fecha designa el día de 00:00 a 24:00 en un escenario de referencia con desplazamiento fijo UTC−05:00. No se modelan cambios estacionales de hora. La clave candidata es `(fecha, sensor_id)`.

| Campo | Tipo | Unidad o significado | Validación del perfil |
|---|---|---|---|
| fecha | Fecha AAAA-MM-DD | Día del resumen | Formato explícito y día existente |
| sensor_id | Texto | Identificador ficticio | Texto no faltante; el plan determina qué sensores se esperan |
| consumo_kwh | Número | Energía consumida durante ese día, en kWh | Finito, no negativo |
| temperatura_c | Número | Temperatura media del día, en °C | Finito; no se implementa rango de plausibilidad |
| horas_uso | Número | Horas de funcionamiento declaradas durante el día | Finito, entre 0 y 24 inclusive |

Se consideran faltantes el texto vacío y `NA`, después de retirar espacios exteriores para la interpretación. La convención se aplica a todos los campos: `NA` no es un identificador permitido en este caso. Los textos originales se conservan para los informes y la comparación de duplicados.

El plan predeterminado espera S1, S2 y S3 durante cuatro días, del 1 al 4 de septiembre de 2026. Puede cambiarse con `--inicio`, `--fin` y `--sensores`; eso cambia el denominador, no el archivo. Los sensores esperados deben ser únicos, sin espacios exteriores ni marcadores de ausencia. El perfil limita el periodo a 366 días inclusive.

### Problemas introducidos deliberadamente

Los números siguientes cuentan registros después del encabezado, empezando por 1:

| Registros | Situación |
|---|---|
| 3 | Consumo faltante |
| 4 | Temperatura marcada `NA` |
| 6 y 7 | Duplicado exacto de celdas leídas |
| 8 | Consumo −2, inválido bajo este esquema |
| 10 y 11 | Misma fecha y sensor, consumos 6 y 7 |
| 12 | Cero consumo válido y horas de uso faltantes |
| Sin registro | S3 en los días 2 y 4 |

Resultado esperado: diez claves presentes de doce esperadas; un duplicado exacto adicional; dos claves repetidas; cuatro incidencias de celda. Los defectos son parte del ejercicio: **no deben corregirse en este archivo base**.

Los esquemas estructuralmente rotos abortan el programa. Una celda faltante o inválida se conserva como incidencia del perfil. Un archivo con solo encabezado es válido y produce cero registros; un archivo sin encabezado se rechaza. Las líneas vacías adicionales se consideran registros estructuralmente inválidos.

## JSON de eventos

[eventos_disponibilidad.json](eventos_disponibilidad.json) representa una exportación local ficticia con metadatos `origen` y una lista `registros`. No es un volcado real ni una respuesta de un servicio externo. Contiene seis eventos independientes del CSV diario.

| Campo por registro | Significado | Restricción |
|---|---|---|
| id | Identificador del evento | Texto no vacío y único en el archivo |
| sensor_id | Sensor ficticio al que pertenece | Texto no vacío |
| variable | Magnitud o etiqueta del evento | consumo_kwh, temperatura_c o fallo_confirmado |
| rol | Papel en este caso | entrada para consumo/temperatura; objetivo para fallo |
| valor | Valor observado | Número finito para mediciones; booleano para fallo |
| observado_en | Instante de observación | Fecha-hora ISO con T y zona |
| disponible_en | Instante de disponibilidad para el sistema | Con zona; no anterior a la observación |

En estos eventos, `consumo_kwh` representa energía durante **la hora que termina en `observado_en`**; es no negativa. `temperatura_c` representa una lectura puntual de temperatura, sin rango de plausibilidad implementado. `fallo_confirmado` es una etiqueta ficticia registrada al observar el resultado de una revisión: `true`/`false`, nunca 1/0 o texto.

Estas definiciones difieren de los agregados diarios del CSV. No se ofrece una correspondencia de casos entre ambos archivos ni se deben combinar para obtener una evaluación.

El tiempo de decisión predeterminado es `2026-09-05T09:00:00+00:00`. Se admite una entrada cuando observación y disponibilidad son menores o iguales al corte. Con ese corte, las entradas son e01 y e03; e02 y e04 se excluyen por tiempo; e05 y e06 se conservan aparte como objetivos.

Los objetivos no se vuelven entradas al cambiar el corte. La práctica no define un horizonte predictivo, asociación entre episodios y etiquetas ni tabla de entrenamiento. Un objetivo previamente observado podría tener otro papel en otro proyecto, pero requeriría un protocolo diferente.

Se validan campos exactos, roles, tipos, orden temporal e identificadores. Se rechazan claves JSON duplicadas y constantes `NaN`/`Infinity`. Una lista vacía de registros es válida si conserva la estructura del origen. La validez del metadato `origen` es estructural; su contenido no certifica autenticidad.

## Cómo experimentar

Conserva los originales, crea una copia y pásala con `--datos`. Para comparar variantes registra:

- Cambio realizado y motivo.
- Predicción antes de ejecutar.
- Archivo y huella de la copia.
- Comando, parámetros, versión de Python y commit del código.
- Resultado y explicación de las diferencias.

Ambos programas pueden exportar un JSON con `--salida`, siempre a un archivo nuevo. Se rechaza sobrescribir un destino existente. Las salidas son informes; los datos de entrada se conservan sin modificaciones.

# Protocolo fijado antes de evaluar

[Unidad](../README.md) · [Procedencia y esquema](README.md)

## Reloj, pregunta y particiones

Temperatura instantánea en °C de un sensor sintético, con rejilla de una hora. Origen `t`: hora en punto de la rejilla. Decisión: `t + 10 minutos`. Objetivo: temperatura medida en `t+h`, para `h=1` y `h=6` horas. Los tiempos se expresan con offset explícito UTC−05:00 en el intervalo del experimento; la aritmética compara instantes, no cadenas ni posiciones de filas.

`h` es el horizonte nominal desde la hora de origen: desde la emisión efectiva quedan 50 minutos para h=1 y 5 horas 50 minutos para h=6. No se afirma que la emisión ocurra diez minutos antes de recibir la lectura.

Se crean 960 posiciones desde 2026-08-01 00:00−05:00. Entrenamiento: horas 0–575; validación: 576–767; prueba: 768–959. Son archivos separados desde la generación. Para formar una fila, tanto origen como objetivo deben caer en la misma partición. Las características pueden consultar historia anterior de otras particiones si ya estaba disponible al decidir. Se exigen al menos 24 posiciones de historia.

Se ajusta antes de la primera decisión de validación (hora 576 + 10 min); ningún objetivo de entrenamiento puede tener disponibilidad posterior a ese corte. Se selecciona antes de la primera decisión de prueba (hora 768 + 10 min); ningún objetivo de validación puede llegar después. Las lecturas atrasadas de horas 575 y 767 hacen observable esta exclusión. Los últimos h orígenes de cada bloque no generan objetivos dentro del bloque y se omiten; no se sortean filas.

## Preparación en cada decisión

1. Leer CSV, comprobar esquema, sensor, fechas con zona, rejilla, disponibilidad no anterior a medición y valores finitos. Un ID repetido exactamente se deduplica; un ID con contenido contradictorio invalida el archivo.
2. Para cada hora histórica, considerar solo registros recibidos antes o en la decisión. Si hay valores distintos para ese instante, queda en conflicto; si no hay valor, queda vacío. Una contradicción recibida más tarde no cambia retroactivamente una predicción ya emitida.
3. Rellenar únicamente hacia delante dentro de la historia conocida. No interpolar usando observaciones futuras ni rellenar hacia atrás. Si no existe un valor previo, conservar ausencia.
4. Excluir un origen si faltan características o la última observación utilizable tiene más de tres horas de antigüedad. No imputar el objetivo. Todos los candidatos comparten exactamente los mismos casos evaluables.

Orden de características: valor preparado en t, valor preparado en t−1, valor preparado en t+h−24, media preparada de t−23…t, seno y coseno de la hora del objetivo, fracción rellenada de la ventana y antigüedad de la última observación. El calendario del objetivo es conocido al decidir. La preparación se reconstruye con la disponibilidad de cada origen: no se calcula una sola serie rellenada retrospectivamente para todas las decisiones.

## Candidatos y criterio

- **persistencia:** repetir el valor preparado en t.
- **estacional24:** repetir el valor preparado en t+h−24, la misma hora del día anterior. Solo se admite h=1 o h=6.
- **ridge:** estandarizar las ocho entradas con media y escala de entrenamiento y ajustar regresión Ridge, `alpha=1`, intercepto, solver SVD. No hay búsqueda de alpha, selección de variables ni red neuronal.

Se ajusta un estado distinto por horizonte. Se elige el menor MAE medio de validación, con tolerancia `1e-12` y desempate por el orden anterior. RMSE, sesgo firmado (predicción−real), métricas por día y las primeras 24 horas tras el cambio de nivel en validación son diagnósticos; no redefinen el criterio. Se muestran también las exclusiones y el número de orígenes evaluables.

Los cambios de nivel forman parte del generador, pero sus marcas no entran como características. Las fechas que delimitan los diagnósticos se fijan aquí: cambio de validación en hora 672 y de prueba en hora 864; la ventana de transición comprende objetivos desde el cambio hasta 23 horas después. Son condiciones conocidas por construcción, no eventos detectados automáticamente.

## Cierre y persistencia

La ejecución común no abre `prueba.csv` ni calcula su huella. Con `--evaluar-prueba`, después de ajustar y seleccionar, se abre el archivo, se valida su rango y se evalúa solo el elegido. No se reajusta con validación ni se cambian parámetros durante prueba.

La evaluación avanza el origen por horas. Una observación anterior de validación o prueba puede alimentar una decisión posterior si ya llegó. Esto es pronóstico con orígenes sucesivos y nuevas observaciones, no una trayectoria recursiva emitida de una sola vez al inicio del bloque. Un horizonte de seis horas no recibe sus seis observaciones futuras al emitir la predicción.

El JSON guarda horizonte, reglas de preparación, orden de entradas y, en Ridge, medias, escalas, coeficientes e intercepto. Recargarlo debe reproducir predicciones de validación y una consulta construida desde registros, con tolerancia `1e-12`. El modelo necesita historia reciente y sus horas de llegada; el archivo no contiene un flujo de sensor ni un estado de entrenamiento reanudable.

Los datos y cierres son públicos y sintéticos. Modificar un diseño a partir de estos resultados exige declarar una nueva evaluación. Los errores por hora están correlacionados; no se presentan intervalos como si cada hora fuera una observación independiente.

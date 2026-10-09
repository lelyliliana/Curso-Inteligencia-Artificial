# Datos de interpretabilidad

[Volver a la unidad](../README.md) · [Protocolo](protocolo.md)

Son datos **sintéticos nuevos**, creados para esta unidad. No corresponden a personas, edificios ni sensores observados. El propósito es mostrar redundancia, errores bajo distintas condiciones de medición y límites de una auditoría. No reutilizan los conjuntos de prueba de otras unidades.

## Archivos y particiones

| Laboratorio | Entrenamiento | Validación | Prueba |
|---|---:|---:|---:|
| [consumo](consumo/entrenamiento.csv) | 160 | 80 | 80 |
| [alertas](alertas/entrenamiento.csv) | 236 | 144 | 114 |

[Consumo: validación](consumo/validacion.csv) · [Consumo: prueba](consumo/prueba.csv) · [Alertas: validación](alertas/validacion.csv) · [Alertas: prueba](alertas/prueba.csv)

Las particiones son sorteos independientes del mismo generador por laboratorio, con semillas distintas. Son ciclos o casos ficticios independientes; no una serie temporal ni mediciones repetidas del mismo equipo. Los ID incorporan laboratorio, partición y posición; no son entradas predictivas. Se comprueba que no se repitan dentro de una partición ni entre las que se abren.

## Esquema de consumo

| Columna | Tipo y unidad | Uso |
|---|---|---|
| caso_id | Texto no vacío, único | Trazabilidad |
| horas | Real; h; dominio aceptado 0–24 | Entrada |
| minutos | Real; min; 0–1440 | Entrada redundante, exactamente 60×horas |
| temperatura_c | Real; °C; −50 a 100 | Entrada |
| consumo_kwh | Real no negativo; kWh por ciclo | Objetivo |

El dominio aceptado por el lector es más amplio que el rango simulado y **no certifica validez fuera de ese rango**. El generador toma horas uniformes en `[1,9)` y temperatura uniforme en `[15,35)`, las redondea a cuatro decimales y calcula `consumo = 4 + 3×horas + 0,2×temperatura + ruido`. El ruido es normal con media 0 y desviación 0,4 kWh. Redondea el consumo a cuatro decimales. Minutos se calcula de las horas ya redondeadas y se escribe con cuatro decimales, preservando la conversión.

Las ecuaciones generadoras son información didáctica. El programa de ajuste solo recibe las columnas declaradas; no utiliza el ruido ni los coeficientes verdaderos. El duplicado permite estudiar no unicidad sin confundir una pequeña correlación con redundancia exacta.

## Esquema de alertas

| Columna | Tipo y unidad | Uso |
|---|---|---|
| caso_id | Texto no vacío, único | Trazabilidad |
| grupo | estandar, desplazado, escaso o nuevo | Solo auditoría |
| lectura | Real en [0,1], sin unidad física | Única entrada |
| requiere_revision | Entero 0 o 1 | Objetivo; 1 es la clase positiva |

| Grupo | Entrenamiento | Validación | Prueba | Generación |
|---|---:|---:|---:|---|
| estandar | 180 | 100 | 80 | Latente uniforme [0,1) |
| desplazado | 50 | 40 | 30 | Latente uniforme [0,1); lectura desplazada −0,30 |
| escaso | 6 | 4 | 4 | Latente uniforme [0,0,25), siempre negativa |
| nuevo | 0 | 0 | 0 | Categoría prevista sin ejemplos |

Por fila: sortear la señal latente; sortear ruido normal `N(0; 0,035²)`; calcular lectura como latente + ruido − desplazamiento y recortarla a `[0,1]`; escribir cinco decimales. La etiqueta depende de la latente **sin ruido ni redondeo**: `int(latente >= 0,55)`. La latente no se guarda. No se ha corregido el sensor para mejorar las métricas. El escenario muestra una limitación deliberada del predictor que solo observa lectura.

Los nombres de grupo describen condiciones del generador. No contienen atributos demográficos ni representan identidades reales. Las proporciones de grupo se fijaron para ilustrar tamaños distintos, no para estimar una población objetivo real.

## Regeneración exacta

```bash
python unidad18-interpretabilidad-responsabilidad/datos/generar_datos.py --salida resultados/u18-datos-nuevos
```

La carpeta no debe existir. `generar_datos.py` usa un `Generator(PCG64(semilla))` nuevo por archivo. Consumo: semillas 2026181, 2026182 y 2026183 para entrenamiento, validación y prueba. Alertas: 2026191, 2026192 y 2026193. Se generan filas en el orden de las tablas anteriores; en consumo se sortea horas, temperatura y ruido, y en alertas latente y ruido. Se escribe UTF-8 con separador coma y terminador LF. Con NumPy 2.2.6, las pruebas comparan byte por byte los seis CSV.

El lector rechaza esquemas diferentes, columnas duplicadas, campos vacíos, valores no finitos, dominios inválidos, ID repetidos y la ruptura de minutos=60×horas. El ajuste del árbol exige ambas clases en entrenamiento. Una partición vacía produce error; un grupo vacío dentro de una partición se informa con n=0 y tasas no definidas. Las huellas SHA-256 de cada archivo **abierto** se conservan en el informe; el modo de desarrollo no lee ni calcula la huella de prueba.

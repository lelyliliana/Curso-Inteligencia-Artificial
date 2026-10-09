# Datos de agrupamiento y anomalías

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Los siete CSV son sintéticos, nuevos para esta unidad y sin información personal. UTF-8, coma como separador, punto decimal y saltos de línea LF. Cada fila es un caso distinto identificado dentro y entre las particiones de su experimento. No hay fechas ni equipos: las particiones no acreditan separación temporal o por instalación. No reutilizan prueba de unidades anteriores.

## Esquemas

| Experimento | Campo | Tipo, unidad y uso |
|---|---|---|
| Ambos | `caso_id` | Texto no vacío; identificación, nunca entrada predictiva |
| Grupos | `horas_uso` | Real de 0 a 24 horas, resumen diario sintético |
| Grupos | `consumo_kwh` | Real de 0 a 500 kWh, consumo del mismo día sintético |
| Anomalías | `senal_a`, `senal_b` | Reales adimensionales de 0 a 100 |
| Anomalías, solo validación/prueba | `anomalia_sintetica` | 0: generación ordinaria; 1: generación inusual; referencia de evaluación |

Agrupamos el perfil después de disponer de ambos resúmenes diarios; no se predice el consumo antes de medirlo. En anomalías, el escenario declara ambas señales disponibles al emitir la alerta y una confirmación posterior en aplicaciones reales; los archivos no permiten auditar esa secuencia.

Entrenamiento y calibración de anomalías no contienen etiquetas. Su condición de referencia ordinaria es un supuesto declarado por la construcción, no una conclusión del modelo. La etiqueta de validación/prueba indica de qué mecanismo sintético provino el caso; no es una definición clínica, de fraude o de falla, y las distribuciones pueden solaparse.

## Particiones y semillas de generación

| Experimento | Archivo | Casos | Positivos publicados | Semilla PCG64 |
|---|---|---:|---:|---:|
| Grupos | [entrenamiento](grupos/entrenamiento.csv) | 90 | No hay etiqueta | 2026141 |
| Grupos | [validación](grupos/validacion.csv) | 60 | No hay etiqueta | 2026142 |
| Grupos | [prueba](grupos/prueba.csv) | 60 | No hay etiqueta | 2026143 |
| Anomalías | [entrenamiento](anomalias/entrenamiento.csv) | 120 | No hay etiqueta | 2026144 |
| Anomalías | [calibración](anomalias/calibracion.csv) | 60 | No hay etiqueta | 2026145 |
| Anomalías | [validación](anomalias/validacion.csv) | 80 | 16 | 2026146 |
| Anomalías | [prueba](anomalias/prueba.csv) | 80 | 16 | 2026147 |

Cada archivo utiliza `numpy.random.Generator(numpy.random.PCG64(semilla))`. El orden de generación es parte del contrato. La semilla 14 de los modelos y las semillas 29/47 del diagnóstico de estabilidad no generan estos CSV.

## Construcción de grupos

Se recorren cíclicamente los centros `(3 h,60 kWh)`, `(11 h,230 kWh)` y `(19 h,80 kWh)`, con cantidades iguales por centro. A cada fila se suma una normal estándar de dos dimensiones multiplicada por desviaciones `(1 h,18 kWh)`. Se recorta al dominio `[0,24] × [0,500]`, se redondea a dos decimales y se permutan las filas con el mismo generador. Los identificadores se asignan después de permutar.

La construcción favorece nubes compactas. Conocer los tres centros explica el ejemplo, pero no convierte la silueta en exactitud ni demuestra que datos reales tengan esa estructura. El algoritmo no recibe los identificadores del componente generador. No se supone una ley física que relacione horas y consumo.

## Construcción de anomalías

La referencia ordinaria alterna los centros `(30,35)` y `(70,65)`, con ruido normal de desviaciones `(6,5)`. Entrenamiento y calibración contienen solo este mecanismo, repartido por igual entre ambos centros.

Validación y prueba contienen 64 casos ordinarios y 16 de otro mecanismo. Los 16 alternan los centros `(30,70)`, `(70,30)`, `(44,44)` y `(58,56)`, con ruido normal de desviaciones `(4,4)`. Primero se generan los ordinarios; luego, los inusuales. Se concatenan, se recortan ambas señales a `[0,100]`, se redondean a dos decimales y se permutan filas y etiquetas con la misma permutación. Los identificadores se asignan al final.

Algunos casos inusuales combinan valores marginales frecuentes; otros se aproximan a los modos ordinarios. Se conserva el solapamiento: no se seleccionan filas para que un detector acierte. La proporción positiva de 16/80 fue fijada para el ejercicio; no estima prevalencia real. Tampoco la ausencia de anomalías en la referencia prueba que obtener una referencia limpia sea sencillo en producción.

## Validación y reproducción

La lectura rechaza columnas imprevistas o repetidas, celdas incompletas o extra, valores no finitos, entradas fuera del dominio y etiquetas distintas de 0/1. Los identificadores duplicados detienen el flujo. Entrenamiento requiere al menos cinco filas distintas; validación de anomalías requiere ambas clases. No se imputan datos ni se eliminan casos difíciles.

Desde la raíz, con dependencias instaladas y un destino nuevo:

```bash
python unidad14-agrupamiento-anomalias/datos/generar_datos.py --salida resultados/unidad14/datos-copia
python unidad14-agrupamiento-anomalias/ejemplos/02_detectar_anomalias.py --datos resultados/unidad14/datos-copia/anomalias
```

Las pruebas comparan los bytes regenerados de los siete CSV con los originales. Las huellas SHA-256 identifican archivos leídos en cada ejecución. No se promete identidad de generación entre versiones diferentes de las dependencias. Prueba no se lee por defecto; los archivos y el generador siguen siendo públicos y su lectura previa debe reconocerse al describir el experimento.

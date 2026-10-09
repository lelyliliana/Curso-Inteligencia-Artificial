# Datos de la Unidad 9

[Volver a la unidad](../README.md)

Los dos laboratorios usan **datos sintéticos** del curso, sin personas, instalaciones ni mediciones reales. Sus unidades permiten practicar interpretación; no validan una teoría física ni demuestran ahorro o capacidad predictiva.

## Laboratorio 1: continuidad de las unidades 7 y 8

Fuente: [lecturas_sinteticas.csv](../../unidad07-obtencion-datos/datos/lecturas_sinteticas.csv), cuyo [diccionario original](../../unidad07-obtencion-datos/datos/README.md) define sensor-día, UTC−05:00, kWh, temperatura y horas de uso. No se hace una nueva copia editable de esa fuente.

[analizar_lecturas()](../ejemplos/exploracion.py) llama al mismo [generador de informes de preparación](../../unidad08-preparacion-datos/ejemplos/preparacion.py). Se mantiene el plan de tres sensores, S1/S2/S3, durante el 1–4 de septiembre de 2026: 12 claves esperadas. El programa no ofrece cambiar ese plan ni recibir cualquier otro CSV.

Sin correcciones: 12 registros originales → ocho filas preparadas, un duplicado separado y tres registros en cuarentena. Solo siete filas preparadas tienen consumo. Cuatro claves del plan no tienen fila preparada: dos ausentes del original y dos afectadas por cuarentena. Los dos registros conflictivos de S3 pertenecen a la misma clave; no cuentan como dos días.

El lote opcional [correcciones_verificadas.json](../../unidad08-preparacion-datos/datos/correcciones_verificadas.json) se sustenta en un [acta sintética](../../unidad08-preparacion-datos/datos/acta_sintetica.md). Al aplicarlo se recupera S2 del 3 de septiembre con 10 kWh. Quedan nueve filas preparadas y ocho consumos disponibles. Este cambio exige que coincida la huella del original; no es una estimación automática.

En el resumen por sensor:

| Campo | Significado |
|---|---|
| `esperados` | Días del calendario declarado, cuatro |
| `preparados` | Filas del sensor que conserva la política |
| `consumo.n` | Valores de consumo presentes, incluido cero |
| `consumo.faltantes` | Consumos ausentes en filas preparadas |
| `sin_preparar` | Días esperados sin fila preparada |
| `serie` | Una posición por fecha, con `null` cuando no hay consumo disponible |

La serie por sí sola no distingue el motivo del hueco. La tabla separa celda faltante y fila no preparada; el informe de preparación incorporado en el JSON conserva el detalle de duplicados, cuarentena y registros originales. En todo sensor se cumple `n + faltantes + sin_preparar = esperados`.

## Laboratorio 2: 48 casos construidos por fórmula

Archivo: [consumos_por_grupo.csv](consumos_por_grupo.csv). Generador: [generar_datos.py](generar_datos.py). Formato UTF-8, separador coma, punto decimal, una cabecera y 48 registros. El lector también acepta BOM UTF-8 y elimina espacios exteriores.

Cada fila representa un **caso-día sintético distinto**. No hay fecha, sensor real, ubicación, secuencia temporal ni diseño de muestreo. El orden del CSV corresponde al generador y no demuestra evolución diaria. El identificador es una clave técnica, no una variable explicativa.

| Columna | Tipo y unidad | Restricción del lector | Valores generados |
|---|---|---|---|
| `caso_id` | Texto, identificador | No vacío y único | A01–A24 y B01–B24 |
| `grupo` | Categoría nominal | A o B; ambos presentes en el archivo | 24 casos por grupo |
| `horas_uso` | Número de horas por caso-día | Finito, entre 0 y 24 | A: 1–3.5; B: 5–7.5 |
| `consumo_kwh` | Energía por caso-día, kWh | Finito y no negativo | A: 8.15–13.10; B: 24.15–29.10 |

Las cuatro columnas deben estar presentes una sola vez, sin columnas adicionales. El lector rechaza celdas vacías, identificadores repetidos, números no finitos y filas incompletas o con celdas extra. No imputa ni manda registros a cuarentena: es una práctica separada con entrada completa documentada. Si quieres estudiar otra estructura, adapta explícitamente su contrato.

### Fórmula y propósito

Para A se toman seis duraciones: `1, 1.5, 2, 2.5, 3, 3.5`. Para B: `5, 5.5, 6, 6.5, 7, 7.5`. Cada duración aparece en cuatro casos con residuos `−0.6, −0.2, 0.2, 0.6` kWh. El consumo se construye así:

```text
grupo A: consumo = 14 − 1.5 × horas + residuo
grupo B: consumo = 36 − 1.5 × horas + residuo
```

Las constantes tienen las unidades necesarias para expresar consumo en kWh. Son valores elegidos para enseñar un patrón; no parámetros estimados ni leyes energéticas. Cada grupo tiene `6 × 4 = 24` casos y residuo medio cero. La diferencia de niveles entre grupos produce una asociación global positiva, aunque la relación construida dentro de cada grupo sea negativa.

No interviene azar ni se necesita semilla. No existen valores faltantes o extremos añadidos deliberadamente. Las repeticiones de una duración son casos diferentes, identificados de manera única; no son duplicados que deban eliminarse.

### Regeneración y procedencia

Desde la raíz, usa una carpeta existente y un archivo nuevo; por ejemplo, tras ejecutar un laboratorio que haya creado `resultados/unidad09/`:

```bash
python unidad09-exploracion-visualizacion/datos/generar_datos.py --salida resultados/unidad09/consumos-regenerados.csv
```

La prueba `test_generador_reproduce_csv_publicado` exige igualdad byte a byte con el CSV incluido. Cada análisis guarda el nombre y SHA-256 del archivo leído. La huella identifica contenido; no demuestra autenticidad ni calidad de una fuente externa.

Estos casos son suficientes para revisar los procedimientos del laboratorio, no para estimar una población. Si modificas el archivo, guarda una copia y registra la fórmula o cambios utilizados. Cambiar números no transforma la demostración en evidencia real.

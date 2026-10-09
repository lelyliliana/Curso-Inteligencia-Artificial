# Procedencia de los casos — Unidad 4

Todos los casos son sintéticos y fueron construidos para el curso. No contienen información personal ni mediciones de instalaciones reales.

## Archivo de consumo

`consumos_sinteticos.csv` contiene seis registros con valores `[10,12,12,14,16,26]`. Se eligieron para que fueran visibles una moda, diferencias entre media y mediana y un valor señalado por una regla exploratoria.

| Campo | Tipo | Condiciones |
|---|---|---|
| `registro_id` | Texto | Identificador no vacío y único |
| `consumo_kwh` | Número | Finito y no negativo; unidad declarada kWh |

El encabezado debe estar en ese orden. Se utiliza coma como separador y punto decimal. No hay fechas, equipos, áreas ni un diseño muestral real; el orden del archivo no representa tiempo.

El programa describe estas seis filas. Mostrar varianza muestral permite practicar el divisor n-1, pero no convierte el archivo en una muestra representativa de una población real. Señalar 26 por IQR tampoco demuestra un error o una avería.

## Escenario de alertas

`02_bayes_alertas.py` utiliza parámetros proporcionados mediante argumentos. Por defecto: prevalencia 0.01, sensibilidad 0.90, especificidad 0.95 y total de referencia 10 000.

Los conteos resultan de multiplicar esas probabilidades por el total. Son **conteos esperados**, no registros observados, métricas de un modelo entrenado ni evidencia de desempeño real. Pueden ser fraccionarios en variantes.

Al cambiar la prevalencia se mantienen por supuesto sensibilidad y especificidad. Ese transporte requeriría revisión y evidencia en una aplicación real.

## Simulación de estimaciones

`03_simular_estimaciones.py` genera muestras Bernoulli pseudoaleatorias con probabilidad constante y ensayos modelados como independientes. Por defecto: p=0.3, n=200, 1000 repeticiones y semilla 42.

No lee el CSV de consumo. La probabilidad es conocida porque se eligió en el generador; en una población real habitualmente debe estimarse.

La semilla, los parámetros y la versión permiten documentar reproducción. El simulador no valida que sus supuestos se cumplan en datos temporales, agrupados o sesgados. Su cobertura observada no certifica la de un proyecto real.

## Pares para correlación

`04_correlacion_y_grupos.py` contiene en el código:

- Grupo A: `(1,10),(2,9),(3,8)`.
- Grupo B: `(7,30),(8,29),(9,28)`.

x e y son variables ilustrativas sin unidad física asignada. La figura `recursos/correlacion_grupos.svg` usa exactamente esos pares y una recta global calculada por mínimos cuadrados. La pendiente de la recta global es 176/58 y su término independiente es 19 menos cinco veces esa pendiente.

Estos valores se construyeron para mostrar inversión de asociación al agregar. No provienen de un estudio ni permiten establecer causalidad.

## Variantes

Guarda copias identificadas, explica cualquier cambio de valores, unidades o supuestos y conserva el original. Si cambias kWh por Wh, actualiza también las etiquetas de unidad del programa y del informe.

Una conclusión debe indicar si describe el archivo, calcula un escenario supuesto o evalúa una simulación. Ninguno de esos resultados demuestra eficacia de una aplicación real.

[Volver a la unidad](../README.md)

# Datos sintéticos de árboles y ensambles

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Estos seis CSV se crearon específicamente para la Unidad 13. No reutilizan la prueba de unidades anteriores. Son construcciones didácticas; no proceden de personas, equipos ni sensores reales. La etiqueta representa una revisión confirmada posterior y las señales se declaran disponibles antes de decidir. No hay fechas ni identificadores de equipo que permitan comprobar ese supuesto o estudiar dependencia temporal y por grupos.

## Esquema

Codificación UTF-8, separador coma, punto decimal, encabezado y saltos de línea LF. Los identificadores son únicos dentro y entre particiones de cada experimento.

| Campo | Tipo y dominio | Uso |
|---|---|---|
| `caso_id` | Texto no vacío | Identificar y comparar casos; nunca entrada del modelo |
| `senal_a` | Real finito, 0 a 100, adimensional | Entrada previa declarada |
| `senal_b` | Real finito, 0 a 100, adimensional; solo en `region` | Segunda entrada previa declarada |
| `revision_confirmada` | Entero 0 o 1 | Etiqueta posterior; 1 es la clase positiva |

La lectura valida columnas, campos completos, rangos y etiquetas. Se permiten señales iguales en casos diferentes, pero no identificadores repetidos. Entrenamiento y validación deben contener ambas clases; prueba puede tener solo una. No hay imputación ni eliminación silenciosa de filas.

## Particiones publicadas

| Experimento | Archivo | Casos | Positivos |
|---|---|---:|---:|
| Franja | [entrenamiento](franja/entrenamiento.csv) | 80 | 33 |
| Franja | [validación](franja/validacion.csv) | 40 | 16 |
| Franja | [prueba](franja/prueba.csv) | 40 | 18 |
| Región | [entrenamiento](region/entrenamiento.csv) | 180 | 68 |
| Región | [validación](region/validacion.csv) | 120 | 43 |
| Región | [prueba](region/prueba.csv) | 120 | 32 |

## Franja: rejilla determinista

Para cada partición se construye `senal_a = (i + desplazamiento) × 100 / n`, con `i` desde 0 hasta `n−1`. Los desplazamientos de entrenamiento, validación y prueba son respectivamente 0,5; 0,25 y 0,75. Se asigna inicialmente clase 1 cuando `30 <= senal_a < 70` y 0 fuera de esa franja.

Después se invierten las etiquetas de los siguientes **índices desde cero**, no números de línea de CSV:

- Entrenamiento: `[6, 18, 32, 46, 51, 65, 73]`.
- Validación: `[3, 22]`.
- Prueba: `[8, 30]`.

La señal se escribe con tres decimales. Los identificadores numeran casos desde 001. No hay muestreo aleatorio en esta construcción: las inversiones son decisiones explícitas del generador, no estimaciones de una tasa real de error. La rejilla permite estudiar cortes y sobreajuste; no demuestra independencia estadística entre particiones ni generalización a una población.

## Región: generación aleatoria reproducible

Cada partición crea un generador NumPy independiente con `Generator(PCG64(semilla))`. Las semillas de entrenamiento, validación y prueba son `2026131`, `2026132` y `2026133`.

El orden exacto importa para reproducir los archivos:

1. Generar una matriz de `n × 2` señales uniformes en `[5, 95)`.
2. Redondear las señales a dos decimales.
3. Asignar clase 1 si `(senal_a−50)² + (senal_b−50)² < 30²`; el borde exacto es clase 0.
4. Generar `n` números uniformes adicionales e invertir la etiqueta donde el número sea menor que 0,08.
5. Escribir las señales con dos decimales y los identificadores consecutivos.

El 8 % es una **probabilidad de inversión**, no una exigencia de que exactamente el 8 % de cada archivo cambie. Las proporciones positivas varían entre particiones. Los generadores separados evitan reutilizar el mismo flujo de números en cada partición; las semillas por sí solas no prueban independencia ni representatividad de casos reales.

Los algoritmos reciben solo señales y etiquetas. No reciben la distancia al centro, la regla circular ni una marca de las inversiones. Saber cómo se hicieron los datos no convierte esas inversiones en errores que deban corregirse durante el laboratorio.

## Reproducción y uso de copias

Desde la raíz, con las dependencias de la unidad instaladas y un destino nuevo:

```bash
python unidad13-arboles-ensambles/datos/generar_datos.py --salida resultados/unidad13/datos-copia
python unidad13-arboles-ensambles/ejemplos/01_controlar_complejidad.py --datos resultados/unidad13/datos-copia/franja
python unidad13-arboles-ensambles/ejemplos/02_comparar_ensambles.py --datos resultados/unidad13/datos-copia/region
```

Las pruebas verifican que `contenidos()` reproduce los seis CSV exactamente en el entorno fijado. `--semilla` de los laboratorios cambia únicamente la aleatoriedad de los modelos, no la generación de datos.

El programa normal lee solo entrenamiento y validación; prueba requiere `--evaluar-prueba` y se abre después de seleccionar. El generador y estos archivos son públicos. Declarar qué se conocía de ellos forma parte del informe: el programa no puede garantizar una evaluación personal ciega.

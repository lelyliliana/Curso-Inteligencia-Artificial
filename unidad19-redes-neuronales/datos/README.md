# Datos para redes neuronales

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Son conjuntos **sintéticos nuevos** para estudiar aprendizaje y generalización. No representan mediciones de personas ni dispositivos reales. Los CSV de unidades anteriores no se usan para ajustar ni cerrar estos experimentos.

## Esquema común

| Columna | Tipo y dominio | Papel |
|---|---|---|
| caso_id | Texto no vacío y único | Trazabilidad; excluido de las entradas |
| senal_a | Real finito en [−1,1], adimensional | Entrada |
| senal_b | Real finito en [−1,1], adimensional | Entrada |
| objetivo | Entero 0 o 1 | Etiqueta; 1 es la clase positiva |

Las señales se escriben con cinco decimales. No hay una columna que revele el objetivo futuro ni una regla generadora incluida como entrada. Las fórmulas del generador están disponibles para estudiar el ejemplo; el entrenamiento no las consulta. Etiquetas y señales están completas; el lector rechaza campos vacíos, columnas adicionales o duplicadas, ID repetidos, valores no finitos y dominios incorrectos. Entrenamiento exige ambas clases y variación en cada entrada; una partición vacía provoca error. El cierre admite una sola clase y conserva las métricas indefinidas que correspondan.

## XOR

| Partición | Filas | Positivos | Semilla |
|---|---:|---:|---:|
| [Entrenamiento](xor/entrenamiento.csv) | 192 | 96 | 2026191 |
| [Validación](xor/validacion.csv) | 96 | 48 | 2026192 |
| [Prueba](xor/prueba.csv) | 96 | 48 | 2026193 |

El generador repite los signos (−,−), (−,+), (+,−), (+,+) el mismo número de veces. Multiplica cada señal por una magnitud uniforme independiente en [0,25;1), redondea a cinco decimales, etiqueta como 1 si el producto de ambas señales es negativo y baraja las filas con una permutación de ese mismo generador. Por redondeo puede aparecer un valor absoluto igual a 1.

Es una versión continua y equilibrada de XOR. No hay inversión de etiquetas. Los ID se asignan después de barajar y no describen cuadrante ni clase. No hay ejemplos con valor absoluto de alguna señal menor que 0,25; el color de una malla en esas zonas es una predicción sin soporte de muestras del generador. El 100 % de exactitud en una muestra de este problema sencillo no demuestra un clasificador universal.

## Círculo con ruido de etiqueta

| Partición | Filas | Positivos observados | Etiquetas invertidas | Semilla |
|---|---:|---:|---:|---:|
| [Entrenamiento](ruido/entrenamiento.csv) | 64 | 32 | 8 | 2026201 |
| [Validación](ruido/validacion.csv) | 160 | 79 | 31 | 2026202 |
| [Prueba](ruido/prueba.csv) | 160 | 77 | 26 | 2026203 |

Primero se sortean las dos señales uniformes en [−1,1), con redondeo a cinco decimales. La etiqueta inicial es `int(senal_a² + senal_b² < 0,55)`. Después se sortea un vector uniforme en [0,1) y se invierte la etiqueta donde el valor es menor que 0,15. La inversión se realiza de igual manera en entrenamiento, validación y prueba. No se fija un número exacto de errores por archivo: 0,15 es una probabilidad, no un cupo.

La etiqueta exportada, después de la inversión, es el objetivo de evaluación. No evaluamos contra la regla limpia como si fuera el objetivo observado ni retiramos filas invertidas. El mecanismo facilita estudiar sobreajuste; no simula todas las formas de error de etiquetado de un proyecto real.

## Regenerar y separar

```bash
python unidad19-redes-neuronales/datos/generar_datos.py --salida resultados/u19-datos-nuevos
```

La carpeta no puede existir. Cada archivo usa un `Generator(PCG64(semilla))` independiente. El orden exacto de sorteos, redondeos y escritura está en el generador. UTF-8, separador coma y fin de línea LF. Con NumPy 2.2.6 las pruebas comparan los seis archivos byte por byte.

Cada partición es un conjunto nuevo del mecanismo declarado, no una división temporal ni un grupo de mediciones repetidas de los mismos sujetos. Se comprueba ausencia de ID compartidos entre archivos abiertos. Los ID únicos no bastarían por sí solos para garantizar independencia en un conjunto real.

El informe registra SHA-256 y número de filas de cada archivo leído. En desarrollo se leen entrenamiento y validación. Prueba se abre únicamente al pedir `--evaluar-prueba`, después de elegir arquitectura y época; su huella no aparece antes. Estos resultados de cierre son públicos y no deben reciclarse como evaluación independiente de cambios elegidos después de verlos.

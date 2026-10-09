# Datos y generación — Unidad 10

[Volver a la unidad](../README.md) · [Protocolo de comparación](protocolo.md)

Los seis CSV son **sintéticos**, creados para inspeccionar un flujo de aprendizaje. No contienen personas, equipos reales ni mediciones de las unidades 7–9. Los números, grupos y fechas fueron elegidos para la enseñanza; no existe un muestreo que permita generalizar sus métricas a una población.

## Archivos y contrato común

| Tarea | Entrenamiento | Validación | Prueba |
|---|---|---|---|
| Regresión | [20 días](regresion/entrenamiento.csv) | [6 días](regresion/validacion.csv) | [6 días](regresion/prueba.csv) |
| Clasificación | [32 avisos, cuatro equipos](clasificacion/entrenamiento.csv) | [16 avisos, dos equipos](clasificacion/validacion.csv) | [16 avisos, dos equipos](clasificacion/prueba.csv) |

Formato UTF-8, coma como separador, punto decimal y una cabecera. El lector admite BOM UTF-8 y espacios exteriores. Exige exactamente las columnas del contrato, sin nombres repetidos. Rechaza archivos sin casos, celdas extra y celdas obligatorias ausentes. Los identificadores deben ser no vacíos y únicos, tanto dentro de un conjunto como entre los conjuntos cargados.

Los CSV están separados físicamente. La ejecución habitual solo lee entrenamiento y validación; la huella de prueba se calcula únicamente en el cierre explícito. El código no comprueba una partición cuyo archivo todavía no ha leído.

## Regresión: un pronóstico por día

| Columna | Tipo y unidad | Significado y restricciones |
|---|---|---|
| `caso_id` | Texto | R01–R32; identificador de auditoría |
| `momento_prediccion` | ISO 8601 con zona | Inicio de las 24 horas que se anticipan |
| `entrada_disponible` | ISO 8601 con zona | Disponibilidad del registro de entrada, incluida su ausencia; no posterior a la predicción |
| `objetivo_disponible` | ISO 8601 con zona | Se conoce el consumo objetivo, exactamente 24 horas después de predecir |
| `consumo_anterior_kwh` | Número no negativo o celda vacía | Consumo del día previo; único campo permitido al predictor |
| `consumo_objetivo_kwh` | Número no negativo obligatorio | Consumo de las 24 horas que comienzan al predecir |

Todos los números presentes deben ser finitos. Se rechazan cálculos de error que excedan el rango representable de esta implementación. Las fechas usan UTC−05:00. Hay una sola instalación sintética y un solo caso por momento de predicción.

Para simplificar, la publicación de cada total diario se supone instantánea al cierre. En un sistema real tendrías que comprobar latencia y revisiones: aquí no hay retrasos, rectificaciones posteriores ni garantías sobre un dispositivo físico. `entrada_disponible` registra cuándo está disponible el registro de entrada, aunque su valor esté vacío.

### Generación de consumos

El generador construye 33 valores diarios con índice `j = 0, …, 32`, desde el 1 de enero de 2026:

```text
patrón = [0, 1, -1, 2, 0, -2, 1, 0]
consumo[j] = 20 + 2 × (j // 8) + patrón[j % 8]
```

`//` es división entera y `%` el resto. Cada bloque de ocho días aumenta dos kWh de nivel. No interviene azar ni ruido de medición real. Este patrón hace razonable comparar una constante histórica con persistencia; no pretende demostrar una ley energética.

Se forman 32 pares. El caso de índice `i` predice al inicio del 2 de enero más `i` días, utiliza `consumo[i]` como entrada previa y tiene `consumo[i+1]` como objetivo. En `i = 3, 12, 22, 28` se vacía solo la entrada observada. Los objetivos siguen completos: son faltantes de la entrada del caso, no eliminación de la verdad usada para evaluar.

Particiones fijadas por índice:

- Entrenamiento: `i=0…19`, casos R01–R20; dos entradas faltantes.
- Validación: `i=20…25`, R21–R26; una entrada faltante, R23.
- Prueba: `i=26…31`, R27–R32; una entrada faltante, R29.

La última etiqueta de entrenamiento está disponible el 22 de enero a las 00:00, al empezar validación. La última de validación llega el 28 de enero a las 00:00, al empezar prueba. La igualdad es válida bajo el supuesto de publicación instantánea. Si ese supuesto cambia, hay que modificar el corte o introducir un margen.

El programa comprueba separación de momentos de predicción y que todas las etiquetas del bloque anterior estén disponibles al comenzar el siguiente. La entrada de un día puede coincidir con el objetivo ya observado del anterior: eso es información legítima para un pronóstico diario actualizado. El ejercicio no evalúa un pronóstico de seis días emitido de una sola vez.

## Clasificación: avisos agrupados por equipo

| Columna | Tipo | Significado y restricciones |
|---|---|---|
| `caso_id` | Texto | C01-01 a C08-08, único por aviso; auditoría |
| `equipo_id` | Texto | E01–E08; un equipo completo pertenece a una partición |
| `senal_previa` | Categoría | `baja` o `alta`; único campo usado por el predictor |
| `fallo_24h` | Entero binario | 1 si se registra el fallo sintético en las siguientes 24 horas, 0 en otro caso |

No hay valores faltantes. La señal es una categoría definida antes del objetivo; no se calcula a partir de `fallo_24h`. No hay marcas temporales: su precedencia es un supuesto declarado del conjunto, no una comprobación automática de disponibilidad. Tampoco se puede evaluar aquí un cambio de época.

### Generación de avisos

Cada equipo `g=1…8` tiene ocho casos con índice `j=0…7`. La señal es baja si `j<6` y alta en los dos últimos casos. El objetivo vale 1 si se cumple alguna de estas condiciones:

```text
j == 6
o bien j == 7 y g no es múltiplo de 3
o bien j == 0 y g es múltiplo de 4
```

En los demás casos vale 0. Esta regla genera positivos mayoritariamente en señal alta, un falso positivo potencial y algunos positivos en señal baja. Los identificadores están relacionados con el mecanismo de construcción, por lo que el predictor los excluye expresamente. No deben añadirse como una forma de «mejorar» la evaluación del fenómeno.

E01–E04 forman entrenamiento; E05–E06, validación; E07–E08, prueba. La asignación es determinista, sin estratificación ni elección posterior basada en una métrica. La separación pretende representar equipos no vistos, bajo el supuesto de población comparable y etiquetas históricas de entrenamiento ya disponibles al construir la referencia.

Las 32 filas de entrenamiento incluyen ocho positivos: siete entre las ocho señales altas y uno entre las 24 bajas. Hay más de una fila por equipo; no interpretamos el número de filas como número de equipos independientes.

## Regenerar y conservar originales

Desde la raíz, elige una carpeta nueva. El generador crea sus subdirectorios:

```bash
python unidad10-flujo-lineas-base/datos/generar_datos.py --salida resultados/unidad10/datos-regenerados
```

Se crean las subcarpetas `regresion/` y `clasificacion/`, cada una con tres CSV. La prueba de regeneración exige igualdad byte a byte con los seis archivos publicados. No hay semilla porque no se usa aleatoriedad.

Para experimentar con copias:

```bash
python unidad10-flujo-lineas-base/ejemplos/01_lineas_base_regresion.py --datos resultados/unidad10/datos-regenerados/regresion
python unidad10-flujo-lineas-base/ejemplos/02_lineas_base_clasificacion.py --datos resultados/unidad10/datos-regenerados/clasificacion
```

Los informes guardan SHA-256, número de casos y nombre de cada archivo leído. Las huellas identifican contenido, no demuestran veracidad. Documenta toda modificación y conserva separados los resultados de referencia y los experimentos.

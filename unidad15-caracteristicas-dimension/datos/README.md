# Datos de características y reducción de dimensión

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Seis CSV sintéticos nuevos para esta unidad, sin información de personas ni equipos reales. UTF-8, separador coma, punto decimal, encabezado y saltos de línea LF. Cada experimento tiene 96 casos de entrenamiento, 48 de validación y 48 de prueba. No se reutiliza prueba de unidades anteriores.

## Interacción: consumo previsto antes del ciclo

| Campo | Dominio y unidad | Disponibilidad y función |
|---|---|---|
| `caso_id` | Texto no vacío | Identificación; nunca entrada |
| `horas_previstas` | Real de 0 a 24 h | Plan disponible antes del ciclo; entrada |
| `potencia_prevista_kw` | Real de 0 a 20 kW | Plan disponible antes del ciclo; entrada |
| `lectura_cierre_kwh` | Real de 0 a 2000 kWh | Lectura posterior al ciclo; **excluida** |
| `consumo_final_kwh` | Real de 0 a 1000 kWh | Objetivo posterior, nunca entrada |

La característica `energia_nominal_kwh` se calcula como producto de las dos entradas previstas. No está almacenada como una medición adicional. Todas las disponibilidades son declaraciones del escenario: no hay marcas temporales para auditarlas. Una lectura posterior aparece deliberadamente en el archivo para practicar la exclusión explícita de información indebida.

| Archivo | Casos | Semilla PCG64 |
|---|---:|---:|
| [Entrenamiento](interaccion/entrenamiento.csv) | 96 | 2026151 |
| [Validación](interaccion/validacion.csv) | 48 | 2026152 |
| [Prueba](interaccion/prueba.csv) | 48 | 2026153 |

Orden de generación por partición:

1. Generar `n` horas uniformes en `[2,10)` y redondear a dos decimales.
2. Generar `n` potencias uniformes en `[2,8)` y redondear a dos decimales.
3. Generar `n` ruidos normales de media 0 y desviación 0,6; construir `y=3+0,8×horas×potencia+ruido` y redondear a tres decimales.
4. Construir la lectura posterior `1000+y`, redondeada a tres decimales.
5. Asignar identificadores consecutivos y escribir todos los valores numéricos con tres decimales.

El desplazamiento 1000 representa una lectura final sintética fuertemente vinculada al consumo. Que revele casi trivialmente el objetivo no la hace admisible al inicio del ciclo. La fórmula del generador favorece la interacción; no es una ley física estimada ni una prueba de rendimiento operacional.

## PCA: diferencia pequeña, respuesta relevante

| Campo | Dominio y unidad | Función |
|---|---|---|
| `caso_id` | Texto no vacío | Identificación, excluida del predictor |
| `senal_a`, `senal_b` | Reales de 0 a 100, índices adimensionales | Entradas previas declaradas |
| `indice_respuesta` | Real de 0 a 100, índice adimensional | Objetivo posterior declarado |

| Archivo | Casos | Semilla PCG64 |
|---|---:|---:|
| [Entrenamiento](pca/entrenamiento.csv) | 96 | 2026154 |
| [Validación](pca/validacion.csv) | 48 | 2026155 |
| [Prueba](pca/prueba.csv) | 48 | 2026156 |

Orden de generación por partición:

1. Generar `n` valores `u` uniformes en `[−2,2)`.
2. Generar `n` valores `v` uniformes en `[−1,1)`.
3. Construir `senal_a=50+10u+0,6v` y `senal_b=50+10u−0,6v`; redondear a tres decimales.
4. Generar `n` ruidos normales de media 0 y desviación 0,2. Construir `indice_respuesta=20+4v+ruido` y redondear a tres decimales.
5. Escribir las filas, sin guardar `u` ni `v` como entradas disponibles.

La variación dominante proviene de `u`, compartida por las señales. La diferencia pequeña contiene `v`, relacionado con la respuesta. El objetivo se calcula con el `v` latente antes del redondeo de las señales. Este caso está diseñado para mostrar que compresión y predicción no tienen el mismo objetivo; no representa la distribución de un sensor real.

## Controles y reproducción

Se usa un generador NumPy `Generator(PCG64(semilla))` nuevo para cada partición. Las semillas pertenecen a la construcción de datos; los ajustes de esta unidad no son aleatorios. Los identificadores son únicos dentro y entre particiones de cada experimento. No hay fechas ni equipos y, por tanto, no se acredita separación temporal o por grupo.

La lectura exige columnas exactas, valores finitos dentro de los dominios y filas completas sin celdas extra. No imputa ni descarta observaciones. El experimento exige al menos cuatro casos de entrenamiento y rango suficiente de las matrices para identificar la regresión completa con intercepto. Todos los candidatos comparan las mismas observaciones.

Desde la raíz con dependencias instaladas y una carpeta nueva:

```bash
python unidad15-caracteristicas-dimension/datos/generar_datos.py --salida resultados/unidad15/datos-copia
python unidad15-caracteristicas-dimension/ejemplos/01_construir_caracteristicas.py --datos resultados/unidad15/datos-copia/interaccion
```

Las pruebas comparan los bytes regenerados de los seis CSV con los originales en el entorno declarado. Las huellas SHA-256 identifican el archivo completo, también sus columnas excluidas: cambiar una lectura posterior cambia la huella aunque no deba cambiar el modelo. Los archivos, el generador y las respuestas son públicos; su lectura previa debe reconocerse al describir el cierre.

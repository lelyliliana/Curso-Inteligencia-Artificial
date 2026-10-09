# Datos sintéticos — Clasificación de revisiones

[Unidad](../README.md) · [Protocolo](protocolo.md)

## Procedencia y pregunta

Los seis CSV se producen mediante [generar_datos.py](generar_datos.py), creado para esta unidad. No representan equipos ni inspecciones reales y no reutilizan datos de las unidades 10 u 11. El generador usa biblioteca estándar, una rejilla fija y ninguna fuente de azar.

Una fila representa un caso sintético de inspección. Antes de decidir se conoce una señal; después se obtiene una etiqueta que indica si se confirmó la necesidad de revisión. Esa secuencia es una declaración del escenario. Los archivos no incluyen marcas temporales, equipos, tiempos de llegada ni criterios reales de inspección: no permiten auditar disponibilidad ni estimar generalización a equipos nuevos o al futuro.

## Diccionario

| Campo | Tipo | Significado | Contrato |
|---|---|---|---|
| `caso_id` | Texto | Identificador de seguimiento | No vacío y único dentro y entre particiones leídas; nunca entrada del modelo |
| `senal_previa` | Real | Índice sintético adimensional previo a la decisión | Finito entre 0 y 100 inclusive; única entrada predictiva |
| `revision_confirmada` | Entero | Etiqueta posterior de necesidad de revisión | Texto `0` o `1` en CSV; 1 es la clase positiva |

Las tres columnas deben aparecer una vez cada una; su orden puede variar. Se rechazan particiones vacías, celdas faltantes o extra y valores inválidos. No se imputa ni corrige automáticamente. Señales repetidas son válidas: distintos casos comparten una entrada, incluso con etiquetas diferentes.

El entrenamiento y la validación deben contener ambas clases por el protocolo de selección. Prueba puede contener una sola: se informan conteos y métricas calculables sin forzar valores definidos. No se cambia la muestra para ocultar un resultado desfavorable.

## Archivos y conteos

Cada celda indica **casos totales / positivos**:

| Experimento | Entrenamiento | Validación | Prueba |
|---|---|---|---|
| Equilibrado | [80 / 36](equilibrado/entrenamiento.csv) | [40 / 18](equilibrado/validacion.csv) | [40 / 16](equilibrado/prueba.csv) |
| Desbalanceado | [200 / 25](desbalanceado/entrenamiento.csv) | [100 / 14](desbalanceado/validacion.csv) | [100 / 9](desbalanceado/prueba.csv) |

`equilibrado` significa proporciones relativamente próximas, no exactamente 50/50. Los porcentajes positivos son 45 %, 45 % y 40 %; en el segundo experimento, 12,5 %, 14 % y 9 %. Las diferencias responden a la construcción, no a un cambio medido de prevalencia en el mundo.

Entrenamiento equilibrado abarca señales de 5 a 95. El desbalanceado abarca de 2,5 a 97,5. Todas las señales de validación están dentro del rango respectivo. En prueba desbalanceada, cinco casos con señal 1,5 quedan por debajo del mínimo de entrenamiento y se marcan fuera de rango; no se eliminan.

## Generación exacta

Para cada nivel i se repite la señal `x = inicio + paso × i`, redondeada a dos decimales. Se calcula una referencia `q(x) = 1 / (1 + exp(−(x − corte)/15))`. Para cada repetición j, empezando en cero, se asigna:

```text
u = (j + desplazamiento) / repeticiones
y = 1 si u < q(x); 0 en caso contrario
```

| Experimento / partición | Niveles | Repeticiones por señal | Inicio | Paso | Corte | Desplazamiento |
|---|---:|---:|---:|---:|---:|---:|
| Equilibrado / entrenamiento | 10 | 8 | 5 | 10 | 55 | 0,5 |
| Equilibrado / validación | 10 | 4 | 7 | 9 | 55 | 0,35 |
| Equilibrado / prueba | 10 | 4 | 6 | 9,5 | 55 | 0,65 |
| Desbalanceado / entrenamiento | 20 | 10 | 2,5 | 5 | 95 | 0,5 |
| Desbalanceado / validación | 20 | 5 | 3,5 | 4,8 | 95 | 0,35 |
| Desbalanceado / prueba | 20 | 5 | 1,5 | 4,9 | 95 | 0,65 |

u es una rejilla determinista, **no un sorteo uniforme**. Las etiquetas no son muestras Bernoulli independientes. q es parte de la construcción didáctica; no es una probabilidad conocida de un proceso real ni se entrega como entrada al predictor. El modelo aprende a y b con las etiquetas publicadas y una penalización; no recibe los parámetros del generador.

Los identificadores incluyen experimento, partición y número correlativo, de modo que ayudan a detectar duplicados. Su separación no demuestra independencia estadística, y las particiones no son cortes temporales ni grupos reales.

## Regenerar

Desde la raíz, hacia un directorio nuevo:

```bash
python unidad12-clasificacion/datos/generar_datos.py --salida resultados/unidad12/datos-regenerados
python unidad12-clasificacion/ejemplos/01_aprender_logistica.py --datos resultados/unidad12/datos-regenerados/equilibrado
python unidad12-clasificacion/ejemplos/02_comparar_umbrales.py --datos resultados/unidad12/datos-regenerados/desbalanceado
```

Los seis archivos se escriben en UTF-8, con saltos LF y señal a dos decimales. La suite comprueba reproducción byte por byte y conteos de clases. El generador rechaza una carpeta existente; una escritura fallida puede dejar archivos parciales.

Prueba, el generador y los resultados son públicos. Si ya los conocías, decláralo en tu informe. Se puede demostrar el flujo del programa sin afirmar una evaluación personal ciega o evidencia independiente de la construcción.

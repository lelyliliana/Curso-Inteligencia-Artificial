# Datos de validación y ajuste

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Cuatro CSV sintéticos nuevos, sin datos personales ni mediciones reales. Se escriben en UTF-8, con coma separadora, punto decimal, encabezado y saltos LF. Los objetivos se observan después de emitir la predicción según el escenario declarado; no hay marcas temporales reales que acrediten esa disponibilidad.

## Ciclos independientes

Cada caso representa un ciclo de operación. Se predice consumo final antes de comenzar, usando dos entradas previstas.

| Columna | Dominio y unidad | Función |
|---|---|---|
| `caso_id` | Texto no vacío y único | Identificador excluido del modelo |
| `horas_previstas` | Real, 0–24 h | Entrada previa |
| `carga_prevista` | Real, 0–1500 unidades de carga | Entrada previa; escala sintética |
| `consumo_kwh` | Real, 0–1000 kWh | Objetivo posterior |

| Archivo | Casos | Semilla PCG64 |
|---|---:|---:|
| [Desarrollo](ciclos/desarrollo.csv) | 160 | 2026161 |
| [Prueba](ciclos/prueba.csv) | 64 | 2026162 |

Orden de generación por archivo:

1. Generar n horas uniformes en `[1,9)` y n cargas uniformes en `[100,900)`, en ese orden; redondear ambas a tres decimales.
2. Generar n ruidos normales de media 0 y desviación 1,2.
3. Calcular `consumo=5+0,55×horas²+0,018×carga+ruido` con las entradas redondeadas; redondear el resultado a tres decimales.
4. Asignar identificadores y escribir números con tres decimales.

Los casos proceden del mismo mecanismo, sin memoria ni equipos compartidos. Ese diseño permite practicar pliegues aleatorios; no demuestra independencia de datos reales. La relación sintética no es una ley física. Se requieren nuevas justificaciones si se utiliza otra fuente.

## Observaciones repetidas de equipos

El uso previsto es predecir la respuesta de **equipos nuevos**, no otra observación de un equipo ya visto.

| Columna | Dominio y unidad | Función |
|---|---|---|
| `caso_id` | Texto no vacío y único | Identificación, excluida del predictor |
| `equipo_id` | Texto no vacío | Grupo de separación, excluido del predictor |
| `senal_a`, `senal_b` | Reales, 0–100, adimensionales | Entradas previas declaradas |
| `respuesta` | Real, 0–100, adimensional | Objetivo posterior declarado |

| Archivo | Equipos | Casos por equipo | Casos | Semilla PCG64 |
|---|---|---:|---:|---:|
| [Desarrollo](equipos/desarrollo.csv) | D01–D12 | 12 | 144 | 2026163 |
| [Prueba](equipos/prueba.csv) | P01–P04 | 12 | 48 | 2026164 |

Con un generador nuevo para cada archivo, repetir para cada equipo en orden:

1. Generar dos coordenadas de centro uniformes en `[10,90)`.
2. Generar una respuesta base uniforme en `[15,85)`, independiente del centro.
3. Generar una matriz de 12×2 perturbaciones normales de media 0 y desviación 0,35; sumarla al centro y redondear a tres decimales.
4. Generar 12 ruidos normales de media 0 y desviación 0,6; sumarlos a la respuesta base y redondear a tres decimales.
5. Escribir las doce filas del equipo con tres decimales, sin exportar centro ni respuesta base como características.

Las observaciones de un equipo comparten centro y respuesta base, por eso están relacionadas. Las señales permiten reconocer proximidad a un equipo conocido, pero la respuesta base no depende de ellas entre equipos. El diseño favorece el contraste entre separar filas y grupos; no estima cuánto ocurriría ese problema en sensores reales.

## Controles y reproducción

Se usa `numpy.random.Generator(PCG64(semilla))`. Las semillas anteriores construyen datos; la semilla 16 de KFold define pliegues y es otra decisión. GroupKFold no baraja. Los modelos no tienen inicialización aleatoria.

El lector exige esquema exacto, filas completas, números finitos dentro de dominio e identificadores únicos. El cierre rechaza IDs compartidos entre desarrollo y prueba y, en equipos, también grupos compartidos. La rejilla exige al menos 21 casos en cada entrenamiento de pliegue; GroupKFold exige cuatro grupos distintos como mínimo. No hay imputación, correcciones ni eliminación implícita de filas.

Para regenerar en un destino nuevo:

```bash
python unidad16-validacion-hiperparametros/datos/generar_datos.py --salida resultados/unidad16/datos-copia
python unidad16-validacion-hiperparametros/ejemplos/01_ajustar_con_cv.py --datos resultados/unidad16/datos-copia/ciclos
python unidad16-validacion-hiperparametros/ejemplos/02_validar_por_equipos.py --datos resultados/unidad16/datos-copia/equipos
```

Los cuatro archivos se reproducen byte a byte en el entorno declarado. SHA-256 identifica todo el contenido, incluidas las columnas excluidas. Orden y versión importan para pliegues y empates de vecinos. Los datos y respuestas son públicos: permiten verificar un procedimiento, sin garantizar un cierre ciego ni generalización real.

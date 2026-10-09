# Datos de métricas y decisiones

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Cuatro CSV sintéticos nuevos, sin mediciones reales ni datos personales. UTF-8, separador coma, punto decimal y saltos LF. Cada caso tiene dos señales previas, una puntuación fija y una etiqueta posterior. El escenario declara su disponibilidad; no contiene fechas que permitan auditar un sistema real.

## Esquema

| Columna | Dominio | Función |
|---|---|---|
| `caso_id` | Texto no vacío, único | Identificación; desempate operativo entre puntuaciones iguales |
| `lote_id` | Texto no vacío, solo en capacidad | Unidad dentro de la cual se aplica el cupo |
| `senal_a`, `senal_b` | Reales finitos en [0,1], adimensionales | Entradas previas del generador de puntuaciones |
| `puntuacion` | Real finito en [0,1], adimensional | Entrada consumida por las políticas |
| `requiere_revision` | Entero 0 o 1 | Etiqueta posterior; 1 es la clase positiva |

Las políticas no vuelven a calcular la puntuación a partir de las señales. Estas quedan como documentación de procedencia. El lector valida todo el archivo y calcula su huella completa; modificar una señal cambia la huella aunque conserve las decisiones si la puntuación guardada sigue igual. Las etiquetas solo evalúan y permiten seleccionar con validación; nunca resuelven el orden de casos dentro de una política.

## Particiones y semillas

| Experimento | Archivo | Casos | Lotes | Semilla PCG64 |
|---|---|---:|---:|---:|
| Costos | [Validación](costos/validacion.csv) | 240 | No se usan | 2026171 |
| Costos | [Prueba](costos/prueba.csv) | 120 | No se usan | 2026172 |
| Capacidad | [Validación](capacidad/validacion.csv) | 240 | 8 de 30 casos | 2026173 |
| Capacidad | [Prueba](capacidad/prueba.csv) | 120 | 4 de 30 casos | 2026174 |

Las semillas construyen datos con `numpy.random.Generator(PCG64(semilla))`, un generador nuevo por archivo. No hay semilla del predictor: no se entrena uno en esta unidad. Los conjuntos son públicos y no se reutilizan pruebas de otras unidades.

## Orden de generación

En costos se genera un bloque por archivo, con el tamaño de su partición. En capacidad se generan lotes en orden, cada uno con 30 casos. Para cada bloque o lote:

1. Generar n valores de `senal_a` uniformes en `[0,1)` y redondearlos a tres decimales.
2. Generar n valores de `senal_b` de la misma manera.
3. Calcular `p=1/(1+exp(−(b0+3×senal_a+2×senal_b)))`, usando esas señales redondeadas.
4. Redondear p a un decimal para guardar `puntuacion`. Así aparecen empates y pueden aparecer ceros; NumPy resuelve mitades según su regla de redondeo.
5. Generar n valores uniformes en `[0,1)` y asignar etiqueta 1 cuando el valor es menor que p **sin redondear**.
6. Escribir señales con tres decimales, puntuación con uno y etiqueta entera; asignar IDs consecutivos.

En costos, `b0=−4`. En capacidad, los lotes L01, L04 y L07 usan `b0=−4,8`; los demás usan `−2,8`. En prueba solo existen L01–L04. Estos regímenes del generador se fijan antes de generar etiquetas; permiten lotes con diferente composición y ocupación del cupo. No son un efecto estimado ni se aprenden de prueba.

Los nombres completos de los lotes incluyen la partición: `validacion-L01`, `prueba-L01`, etc.; son lotes distintos. El ID de caso no codifica la etiqueta, aunque su orden se utiliza como desempate reproducible. No contiene una justificación de prioridad o equidad aplicable a personas.

Esta construcción produce puntuaciones relacionadas con la probabilidad usada para generar etiquetas. La relación es sintética y redondeada: no demuestra calibración en una población real. Todos los casos tienen etiqueta, seleccionados o no; no se simula falta de verificación en los no revisados.

## Controles y reproducción

Se exige esquema exacto, IDs únicos, filas completas, valores finitos y dominios válidos. El cierre rechaza IDs compartidos entre particiones y, en capacidad, también lotes compartidos. No hay imputación ni eliminación automática. El cupo permite lotes con menos de seis elegibles y nunca obliga a completarlo.

```bash
python unidad17-metricas-decisiones/datos/generar_datos.py --salida resultados/unidad17/datos-copia
python unidad17-metricas-decisiones/ejemplos/01_elegir_por_costos.py --datos resultados/unidad17/datos-copia/costos
python unidad17-metricas-decisiones/ejemplos/02_decidir_con_cupo.py --datos resultados/unidad17/datos-copia/capacidad
```

El destino debe ser nuevo. Las pruebas contrastan los cuatro CSV byte a byte en el entorno declarado. SHA-256 identifica el archivo completo. Las puntuaciones preexistentes y su procedencia deben justificarse de nuevo si se sustituyen los datos; aceptar un CSV no verifica cómo se construyó ni cuándo se conocía su contenido.

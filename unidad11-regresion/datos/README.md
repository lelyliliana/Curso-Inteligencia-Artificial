# Datos sintéticos — Ciclos de operación

[Volver a la unidad](../README.md) · [Protocolo](protocolo.md)

## Procedencia y alcance

Los seis CSV fueron generados para esta unidad mediante [generar_datos.py](generar_datos.py). No describen equipos, instalaciones ni personas reales. No proceden de los datos ni de la prueba de la Unidad 10. No requieren descargar archivos, elegir semilla ni ejecutar un muestreo aleatorio.

Una fila representa un ciclo. La pregunta es anticipar su consumo total antes de empezar a partir de las horas planificadas. El escenario declara que esa entrada ya está disponible; el consumo se conoce al terminar. Los archivos no incluyen marcas temporales ni equipos y no permiten verificar esa declaración ni estudiar dependencia temporal o por grupo. Los identificadores separados evitan reutilizar filas, pero por sí solos no demuestran independencia estadística.

## Diccionario

| Columna | Tipo leído | Unidad y significado | Restricciones y uso |
|---|---|---|---|
| `caso_id` | Texto | Identificador del ciclo | No vacío; único dentro y entre las particiones cargadas; se conserva para trazabilidad, no entra al modelo |
| `horas_planificadas` | Número real | Horas previstas antes del ciclo | Finito, de 0 a 24 inclusive; única entrada predictiva |
| `consumo_kwh` | Número real | Energía total observada al terminar | Finito y no negativo; objetivo, nunca entrada de predicción |

El lector acepta las tres columnas en cualquier orden, una sola vez cada una. Rechaza filas incompletas, celdas extra, números inválidos y particiones vacías. Elimina espacios exteriores al leer; no imputa ni elimina silenciosamente casos inválidos. Repetir un número de horas es legítimo: distintos ciclos pueden compartir una entrada. Repetir `caso_id` no lo es.

Los CSV publicados usan UTF-8, salto de línea LF, dos decimales para horas y cinco para consumo. Esa precisión de escritura facilita la reproducción; no representa exactitud de un instrumento real.

## Particiones publicadas

| Experimento | Entrenamiento | Validación | Prueba | Rango de entrada de entrenamiento |
|---|---|---|---|---|
| Lineal | [24 casos](lineal/entrenamiento.csv) | [12 casos](lineal/validacion.csv) | [12 casos](lineal/prueba.csv) | 1 a 8 h |
| Curva | [10 casos](curva/entrenamiento.csv) | [9 casos](curva/validacion.csv) | [8 casos](curva/prueba.csv) | 0,5 a 9,5 h |

Son particiones fijas diseñadas con fines didácticos, no cortes temporales, grupos ni una muestra de una población definida. En los originales, validación y prueba están dentro del rango de entrada de entrenamiento. Cada candidato se evalúa sobre todos los casos de la partición, sin selección de filas por su error.

## Construcción exacta

El caso lineal usa `y = 3 + 2x + e`:

- Entrenamiento: x de 1 a 8, con tres ciclos para cada x; desviaciones −0,4; 0; +0,4 kWh.
- Validación: x de 1,5 a 6,5, en pasos de 1; dos ciclos por x, con desviaciones −0,3 y +0,3.
- Prueba: x de 1,25 a 6,25, en pasos de 1; dos ciclos por x, con desviaciones −0,2 y +0,2.

El caso curvo usa `y = 5 + 0,75x² + e`:

- Entrenamiento: x de 0,5 a 9,5 en pasos de 1, con desviaciones sucesivas `−0,8; +0,6; −0,4; +0,7; −0,6; +0,5; −0,7; +0,9; −0,5; +0,3`.
- Validación: x entero de 1 a 9; desviación −0,2 para x impar y +0,2 para x par.
- Prueba: x = j + 0,25 para j entero de 1 a 8; desviación −0,15 para j impar y +0,15 para j par.

Estas perturbaciones son deterministas. No asumimos que sean ruido independiente, normal ni representativo de mediciones reales. Sus diferencias hacen que el error en validación o prueba pueda ser menor que en entrenamiento. La fórmula generadora está publicada para poder estudiar el ejemplo; no debe incorporarse al predictor para presentar luego una evaluación ciega.

## Regenerar sin modificar los originales

Desde la raíz, elige una carpeta que no exista:

```bash
python unidad11-regresion/datos/generar_datos.py --salida resultados/unidad11/datos-regenerados
python unidad11-regresion/ejemplos/01_ajustar_recta.py --datos resultados/unidad11/datos-regenerados/lineal
python unidad11-regresion/ejemplos/02_comparar_complejidad.py --datos resultados/unidad11/datos-regenerados/curva
```

El generador usa solo biblioteca estándar y produce los mismos seis archivos byte por byte. Una prueba automática comprueba esa coincidencia. Rechaza una carpeta de salida existente; una escritura fallida puede dejar archivos parciales.

Antes de modificar una copia, conserva el protocolo original y documenta el nuevo experimento. Abrir prueba o conocer sus respuestas limita lo que puedes afirmar sobre tu propio proceso: sigue siendo una demostración reproducible, pero no una evaluación personal ciega ni evidencia externa.

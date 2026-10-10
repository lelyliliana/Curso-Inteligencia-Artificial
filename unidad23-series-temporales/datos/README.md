# Datos — Temperatura horaria sintética

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

## Procedencia y alcance

Datos creados para el curso el 10 de octubre de 2026. Representan un único sensor ficticio `s1`, sin mediciones de una instalación real ni información personal. Las fechas sitúan el experimento, pero no describen el clima de esos días. No se descargaron conjuntos externos ni se incorporó su contenido.

Los datos se distribuyen como material didáctico propio del repositorio. No hay términos de un proveedor externo que trasladar. El repositorio no declara una licencia general y esta ficha no añade una licencia nueva. Una ampliación con sensores reales deberá documentar procedencia, permisos de uso y significado físico de las lecturas.

## Generación

Se definen 960 horas desde el 1 de agosto de 2026 a las 00:00 UTC−05:00 hasta el 9 de septiembre a las 23:00. La temperatura se construye con:

```text
19 + 3·sin(2π·(hora_del_día−8)/24)
   + 0,04·(t/24)
   + 0,45·sin(2π·t/168)
   + 2,5·I(t≥672) − 1,8·I(t≥864)
   + ruido gaussiano con desviación 0,15 °C
```

`t` es el número de horas desde el inicio e `I` vale uno si se cumple la condición. La semilla de `random.Random` es 2301 y se redondea a seis decimales al escribir. No es un modelo físico del ambiente. La fórmula y las marcas de cambio solo generan datos y diagnósticos; no se usan para calcular el objetivo dentro del predictor.

Se retiran ocho filas (horas 10, 130, 260, 601, 698, 809, 875 y 933), se dejan siete temperaturas vacías (45, 180, 420, 635, 711, 847 y 903), se duplica exactamente la fila 100 y se añade una lectura contradictoria en hora 690 con otro ID. Ocho lecturas llegan 90 minutos después: 80, 222, 360, 575, 650, 767, 900 y 955. Las restantes llegan diez minutos después.

## Archivos

| Archivo | Horas de rejilla | Filas CSV | Periodo local |
|---|---:|---:|---|
| [entrenamiento.csv](entrenamiento.csv) | 0–575 (576 posiciones) | 574 | 1–24 de agosto |
| [validacion.csv](validacion.csv) | 576–767 (192 posiciones) | 191 | 25 de agosto–1 de septiembre |
| [prueba.csv](prueba.csv) | 768–959 (192 posiciones) | 189 | 2–9 de septiembre |
| [muestra.csv](muestra.csv) | 0–11 | 13 | Ejemplo manual separado, 1 de agosto |

Las 954 filas de la serie principal no equivalen a 954 horas válidas. Tras deduplicar, resolver conflictos como ausencia y excluir valores vacíos, hay 944 horas con temperatura utilizable retrospectivamente. La disponibilidad al decidir reduce algunos conjuntos evaluables todavía más. No se utiliza la muestra manual para ajustar modelos.

La muestra contiene un hueco en hora 2, un duplicado exacto de hora 3, dos valores distintos en hora 5, una temperatura vacía en hora 8 y una lectura de hora 7 que llega a las 09:30. Sus filas están desordenadas deliberadamente. Sus valores son `20+t`, salvo el conflicto y la ausencia indicados.

## Esquema

| Campo | Interpretación |
|---|---|
| id | Identificador de lectura; permite detectar duplicados exactos o contradictorios |
| sensor | Siempre `s1`; no se mezclan sensores en una sola historia |
| instante | Momento de la medición instantánea, en ISO 8601 con offset |
| disponible | Momento en que se recibe la lectura; no anterior a la medición |
| temperatura_c | Valor en °C, o cadena vacía si falta; nunca se usa cero para codificar ausencia |

No son promedios horarios ni energía acumulada. El rango permitido por el lector es [-20, 60] °C, una decisión didáctica explícita; no una especificación de un sensor real. La rejilla se calcula a partir del instante, no del número de fila. Dos fechas con offsets distintos que representan el mismo instante se comparan correctamente.

El laboratorio distingue la calidad retrospectiva del archivo de la información realmente disponible en cada decisión. Si una lectura contradictoria llega tarde, solo puede producir conflicto desde que se recibe. Las huellas SHA-256 de los archivos usados se guardan en los informes; detectan cambios en bytes, no validan la veracidad del sensor.

## Regeneración

Desde la raíz, en una carpeta separada:

```bash
python unidad23-series-temporales/datos/generar_datos.py --salida resultados/u23-datos
```

Las pruebas comparan los cuatro CSV regenerados byte por byte. La lectura y los ejemplos posteriores no requieren red. El generador contiene también prueba, pero la ejecución de desarrollo no lo importa ni abre ese archivo.

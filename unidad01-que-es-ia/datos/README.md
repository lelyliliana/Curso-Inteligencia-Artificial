# Datos sintéticos — Unidad 1

[Volver a la unidad](../README.md)

[casos_sinteticos.json](casos_sinteticos.json) fue creado para mostrar la diferencia entre escribir una regla y ajustar un parámetro a ejemplos. No contiene mediciones reales ni recomendaciones técnicas sobre energía.

| Campo | Significado | Valores permitidos |
|---|---|---|
| `consumo_kwh` | Consumo diario ficticio | Número finito y no negativo |
| `revision` | Etiqueta ficticia asignada al caso | Entero `0` o `1` |

`0` significa «sin revisión» y `1`, «revisar». Las etiquetas permiten estudiar un procedimiento supervisado. No equivalen a averías verificadas ni a juicios profesionales sobre eficiencia.

Los grupos son:

- **entrenamiento:** seis casos para elegir el umbral. Los ejemplos normales llegan hasta 14 kWh y los de revisión comienzan en 17 kWh.
- **prueba:** seis casos separados para observar el comportamiento del umbral elegido. No intervienen en el ajuste.
- **cambio_contexto:** seis casos construidos con otro criterio ficticio de revisión; aquí consumos hasta 21 kWh se etiquetan como normales. Este grupo representa deliberadamente un cambio en la relación entre consumo y etiqueta.

Los grupos son didácticos y pequeños. No son una muestra aleatoria de una población real. El caso de 17 kWh aparece en entrenamiento y prueba para comparar decisiones; los grupos tienen observaciones separadas, pero eso no garantiza independencia de un proceso real de medición. En un proyecto real habría que conocer entidades, fechas y dependencias antes de separar datos.

La regla fija `consumo > 18` es una referencia elegida para comparar. Ninguno de los umbrales del ejercicio debe aplicarse a instalaciones reales.

Procedencia: ejemplos sintéticos definidos por la autora para este curso.

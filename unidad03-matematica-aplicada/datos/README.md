# Datos sintéticos de la Unidad 3

## Procedencia

`consumo_lineal.csv` fue elaborado para este curso. No contiene mediciones de sensores, personas, empresas ni instalaciones reales. Sus seis registros siguen exactamente la relación inventada `consumo_kwh = 2 × horas + 1`.

La observación de cero horas y consumo 1 sirve para estudiar un término independiente. No demuestra consumo en reposo de un equipo real.

## Esquema

| Campo | Tipo | Significado y condiciones |
|---|---|---|
| `registro_id` | Texto | Identificador no vacío, único en el archivo |
| `particion` | Texto | `entrenamiento` o `prueba` |
| `horas` | Número | Entrada sintética, finita y no negativa; unidad h |
| `consumo_kwh` | Número | Referencia sintética, finita y no negativa; unidad kWh |

La primera fila contiene el encabezado en ese orden. Se utiliza punto decimal y coma como separador. Las dos particiones deben contener al menos un registro; los campos no pueden estar vacíos.

## Partición y uso

- Entrenamiento: horas 0, 1, 2 y 3; referencias 1, 3, 5 y 7.
- Prueba: horas 4 y 5; referencias 9 y 11.
- El descenso calcula gradientes solo con entrenamiento.
- La predicción constante usa el promedio 4 de las referencias de entrenamiento.
- Prueba se usa después del ajuste para comparar ambas salidas.

Las horas de prueba están fuera del rango de entrenamiento. Este diseño permite comprobar la extrapolación de una relación sintética conocida, pero no medir capacidad de extrapolar consumos reales.

No hay partición de validación. Tasa 0.05 y 500 pasos son la configuración didáctica incluida. Si eliges configuraciones según sus resultados en estas dos filas de prueba, ya las habrás usado para selección; necesitarás otros datos para una evaluación final independiente.

## Limitaciones

La relación es exacta y sin ruido. No hay fechas, disponibilidad temporal, grupos, incertidumbre, estacionalidad, sensores ni cambios de contexto. La validación del programa comprueba el formato, pero no certifica independencia, calidad o pertinencia.

La referencia aparece junto a la entrada para estudiar ajuste y evaluación. En una aplicación real, hay que explicar cuándo se mide cada variable y cuándo estará disponible para predecir.

Si construyes variantes, guarda una copia del archivo, documenta su fórmula o cambios y señala siempre que sigue siendo sintética. Una buena métrica aquí demuestra una propiedad del experimento; no demuestra ahorro energético ni desempeño real.

[Volver a la unidad](../README.md)

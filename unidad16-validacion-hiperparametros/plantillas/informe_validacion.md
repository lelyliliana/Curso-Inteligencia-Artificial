# Informe — Validación de [ciclos o equipos]

[Reto](../reto.md) · [Unidad](../README.md)

## 1. Pregunta y datos

- Caso, objetivo y unidad:
- Uso previsto: caso independiente o equipo nuevo:
- Entradas, disponibilidad declarada y evidencia real que falta:
- Columnas excluidas de la predicción:
- Casos y equipos en desarrollo y prueba:
- Conocimiento previo de generador y respuestas públicas:

## 2. Protocolo anterior al cierre

- Fecha, protocolo y commit:
- Python y versiones:
- Comando, destino y huella de desarrollo:
- Siete candidatos en orden:
- Divisor, número de pliegues, barajado y semilla:
- Preparación dentro de cada ajuste:
- Criterio, tolerancia y presupuesto:
- Reajuste previsto; qué datos podrá utilizar:
- Confirmación de `prueba: null` y fuentes registradas:

## 3. Reconstruir el primer pliegue

- Índices desde cero y tamaños de ajuste y validación:
- Comprobación de IDs disjuntos y cobertura:
- Equipos de cada lado e intersección, si corresponde:
- Media y escala calculadas solo con ajuste, por columna:
- Valores del JSON y diferencias numéricas:
- Caso OOF elegido, sus entradas y real:
- Entradas estandarizadas del caso:

| Vecino | ID | Entradas estandarizadas | Distancia | Objetivo |
|---|---|---|---:|---:|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

- Predicción media de los tres vecinos y contraste con CSV:
- Posibles empates en la frontera y tratamiento:

## 4. Comparación y selección

| Candidato | MAE pliegue 1 | Pliegue 2 | Pliegue 3 | Pliegue 4 | Media | Desviación ddof=0 | MAE OOF |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Una fila por candidato] | | | | | | | |

- Cálculo reproducido desde CSV:
- Igualdad de tamaños y ponderación:
- Elegido; aplicación del criterio con cifras completas:
- Figuras e interpretación de puntos y barras:
- Por qué la dispersión no es un intervalo de confianza:

## 5. Análisis del escenario

**Ciclos:** dos mejores medias y sus pliegues; límites de la diferencia; presupuesto; caso OOF de mayor error absoluto con ID, entradas, real, predicción y pliegue; explicación posible y evidencia que falta.

**Equipos:** grupos compartidos por pliegue en cada esquema; MAE del candidato fijo; interpretación para equipos nuevos; referencia elegida; presupuesto; condiciones para evaluar equipos conocidos en el futuro.

## 6. Reajuste y cierre

- Registro previo de elegido y estado reajustado:
- Número de casos de reajuste; qué cambia respecto de los pliegues:
- Comando y carpeta nueva de cierre:
- Coincidencia de desarrollo, protocolo, versiones, índices, CV, selección y reajuste:
- Huella y tamaño de prueba; equipos nuevos comprobados:
- MAE, RMSE y sesgo del único candidato evaluado:
- Interpretación sin volver a seleccionar:
- Evaluación nueva necesaria si prueba motivara cambios:

## 7. Verificación y límites

- Comando y resultado de las 30 pruebas:
- Referencia matemática o GridSearchCV identificada:
- Control de información apartada identificado:
- Archivos y figuras entregados:
- Extensión opcional separada:
- Límites de datos sintéticos, cobertura, población y disponibilidad:

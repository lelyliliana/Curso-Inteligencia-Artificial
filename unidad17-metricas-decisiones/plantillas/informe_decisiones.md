# Informe — [Costos o capacidad]

[Reto](../reto.md) · [Unidad](../README.md)

## 1. Pregunta y disponibilidad

- Caso, clase positiva y acción:
- Puntuación y señales previas; disponibilidad declarada:
- Etiqueta posterior y observación de no seleccionados:
- Casos y lotes de validación y prueba:
- Conocimiento previo de generador y resultados públicos:
- Costos incluidos, costos excluidos y consecuencias no evaluadas:

## 2. Protocolo anterior al cierre

- Fecha, protocolo y commit:
- Python y versiones de herramientas:
- Comando, carpeta y huella de validación:
- Políticas en orden:
- Comparación de umbral y desempate de casos:
- Costos FP/FN, objetivo y desempate de políticas:
- Cupo y unidad de asignación, si corresponde:
- Confirmación de `prueba: null` y ausencia de fuente de prueba:

## 3. Reconstrucción de métricas

| Política | VP | VN | FP | FN | Alertas | Precisión | Recobrado | F1 | Costo total | Costo por caso |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Una fila por candidata] | | | | | | | | | | |

- Cálculos desde CSV y denominadores:
- Prevalencia, especificidad y tasa FP del elegido:
- Valores nulos, ceros y su interpretación:
- Elección con cifras completas y desempate:

## 4. Ordenación, probabilidad y prevalencia

- Ejemplo manual: cuatro pares, ROC AUC, AP por bloques y Brier:
- AUC y AP originales y al cuadrado:
- Brier original y al cuadrado; qué no demuestra por sí solo:
- Intervalos de fiabilidad, tamaños y vacíos:
- Umbral transformado para conservar decisiones:
- Prevalencia hipotética, tasas utilizadas y precisión calculada:
- Supuesto de tasas constantes y posibles incumplimientos:
- Figura e interpretación:

## 5A. Costos

| Caso | ID | Puntuación | Real | Acción | Resultado | Contribución al costo |
|---|---|---:|---:|---:|---|---:|
| Alerta verdadera | | | | | | |
| Falsa alerta | | | | | | |
| Omisión | | | | | | |

- Cambio de conteos y costo al pasar de umbral 0,2 a 0,1:
- Sensibilidad de validación con FN=1 y FN=12:
- Qué decisiones y métricas permanecen iguales:
- Supuestos del corte analítico 1/7:

## 5B. Capacidad

- Lote reconstruido e IDs elegibles ordenados:
- Seis seleccionados y empate en el límite:
- Conteos y costo del lote:
- Verificación de sumas globales y cupos por lote:
- Dos políticas con costo 230 y resolución por alertas:
- Lotes que exceden cupo en el diagnóstico:
- Disponibilidad del lote completo y límite del desempate por ID:

## 6. Registro y cierre

- Archivo que conserva elección y parámetros previos:
- Comando de cierre y carpeta nueva:
- Coincidencia de validación, huella, costos, configuración y elección:
- Huella de prueba y separación de IDs/lotes:
- Conteos, denominadores y costo de la única política evaluada:
- Revisión de todos los cupos, si corresponde:
- Omisiones y falsas alertas que siguen presentes:
- Interpretación sin volver a seleccionar:
- Evaluación nueva necesaria si prueba motivara cambios:

## 7. Reproducción y límites

- Comando y resultado de las 30 pruebas:
- Referencia matemática o de biblioteca identificada:
- Control de información de prueba identificado:
- Artefactos entregados:
- Limitaciones de datos, etiquetas, costos, población y consecuencias:

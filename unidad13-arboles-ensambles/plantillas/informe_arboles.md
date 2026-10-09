# Informe de árboles y ensambles — [Título]

[Reto](../reto.md) · [Unidad](../README.md)

Completa con evidencia de tu ejecución. Conserva el registro previo; documenta variantes opcionales por separado.

## 1. Pregunta y datos

- Laboratorio elegido y unidad de observación:
- Entradas, unidades, etiqueta y clase positiva:
- Momento de predicción y supuesto de disponibilidad:
- Evidencia temporal o por grupos ausente:
- Casos y positivos por partición:
- Ejemplo de entrada que produciría filtración:
- Límites del escenario sintético y qué conocía de prueba, generador y soluciones:

## 2. Protocolo anterior al cierre

- Fecha y versión del protocolo:
- Candidatos y orden de desempate:
- Criterio de cortes, profundidad máxima y mínimo por hoja:
- Ensamble, cantidad de árboles, bootstrap y entradas candidatas, si corresponde:
- Semilla de modelos y distinción respecto de semillas de datos:
- Regla para combinar probabilidades y decidir clase; empate:
- Criterio de selección, métricas adicionales y tratamiento de indefinidas:
- Conjunto de ajuste y ausencia de reajuste con validación:
- Manejo de datos inválidos y marca fuera de rango:

## 3. Reproducción

- Commit o versión exacta del código:
- Versiones de Python, scikit-learn, NumPy, SciPy y Matplotlib:
- Comando de desarrollo desde la raíz:
- Carpeta de salida y huellas de entrenamiento/validación:
- Confirmación de `prueba: null`:
- Parámetros y resúmenes de complejidad obtenida:
- En ensambles: extracciones, casos distintos y huellas de remuestreo:

## 4. Cálculo y predicción

- Ocho casos: corte elegido, conteos, Gini de cada hijo, ponderación y reducción:
- Restricción por mínimo de hoja:
- Franja: recorrido de señal 60, conteos de hoja, probabilidad y clase:
- Región: promedio ilustrativo, comparación con voto de clases y cómo comprobar el promedio de los árboles reales:
- Caso identificado en CSV, entradas, probabilidad y predicción:
- Diferencia entre valores completos y redondeados:
- Qué no demuestra esa probabilidad sobre calibración:

## 5. Validación

| Candidato | F1 entrenamiento | VP | VN | FP | FN | Precisión | Recobrado | F1 validación |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Completar todos los candidatos] | | | | | | | | |

- Matriz reconstruida desde CSV y orientación elegida:
- Fórmulas de precisión, recobrado y F1:
- Métricas indefinidas, si aparecen:
- Elegido por la regla previa y comparación con mayoría:
- Diferencia entre Gini de ajuste y F1 de selección:
- Qué conclusión permite la diferencia observada y cuál no:

## 6. Errores y figura

- FP del elegido: identificador, entradas, probabilidad y etiqueta:
- FN del elegido: identificador, entradas, probabilidad y etiqueta:
- Posibles consecuencias y evidencia necesaria para valorar sus costos:
- Figura e interpretación de puntos, ejes y colores:
- Complejidad y sobreajuste, o bootstrap y promedio, según laboratorio:
- Límites de extrapolación, cobertura y calibración:
- Variante opcional y resultados separados:

## 7. Registro previo al cierre

- Fecha del registro:
- Candidato, configuración, semilla y regla de decisión conservados:
- Archivo con código, versiones y huellas de desarrollo:
- Conocimiento previo de resultados públicos y alcance que atribuyo al cierre:

## 8. Cierre

- Comando con `--evaluar-prueba` y carpeta nueva:
- Coincidencia de protocolo, código, versiones, semilla, huellas de desarrollo, modelos y selección:
- Huella de prueba, casos, positivos y casos fuera de rango:
- Matriz y métricas del único elegido:
- Interpretación sin volver a seleccionar:
- Evaluación nueva necesaria si se modificara el procedimiento:

## 9. Verificación y archivos

- Comando y resultado de las 30 pruebas:
- Una comprobación matemática y una de separación de información:
- Archivos entregados y comprobación de exportación completa:
- Figuras legibles y concordantes con las tablas:
- Qué falta para evaluar utilidad fuera del curso:

# Informe de regresión — [Título]

[Reto](../reto.md) · [Unidad](../README.md)

Completa los campos con evidencia de tu ejecución. Separa decisiones previas, resultados de desarrollo y cierre; conserva la primera exportación para comprobar que no cambió el procedimiento.

## 1. Pregunta y alcance

- Laboratorio elegido y motivo:
- Unidad de observación:
- Entrada, unidad y momento de disponibilidad:
- Objetivo, unidad y momento de conocimiento:
- Instante en que se emite la predicción:
- Disponibilidad declarada y evidencia temporal que falta:
- Población o condiciones que estos datos sintéticos no representan:

## 2. Protocolo previo

- Versión del protocolo y fecha de registro:
- Entrenamiento / validación / prueba: archivos y cantidad de casos:
- Candidatos y orden de desempate:
- Criterio de ajuste de cada candidato:
- Transformaciones y conjunto con que se ajustan:
- Métrica principal y diagnósticos:
- Tratamiento de faltantes, extremos y predicciones negativas:
- Reajuste con validación:
- ¿Había consultado los datos, el generador o las respuestas de prueba? Indicar qué conocía:

## 3. Reproducción de desarrollo

- Commit o versión exacta del código:
- Python, NumPy y Matplotlib utilizados, según corresponda:
- Comando completo desde la raíz:
- Carpeta de exportación:
- Huellas SHA-256 de entrenamiento y validación:
- Confirmación de que el informe de desarrollo tiene `prueba: null`:

## 4. Modelos y comparación

Registra coeficientes, centro, escala y rango de entrada de cada modelo. Explica en qué variable se expresan los coeficientes y qué unidades tienen.

| Candidato | MAE entrenamiento | MAE validación | RMSE validación | R² validación | Observación |
|---|---:|---:|---:|---:|---|
| [Completar todos los candidatos] | | | | | |

- Candidato seleccionado y regla aplicada:
- Diferencia respecto de las referencias constantes:
- Efecto del redondeo en la lectura, sin redondear para seleccionar:

## 5. Cálculo manual

Identifica al menos tres casos del mismo conjunto y candidato. Reproduce una predicción con la fórmula y calcula sus errores:

| Caso | Entrada | Real | Predicción | Residuo real − predicción | Error absoluto |
|---|---:|---:|---:|---:|---:|
| [Caso 1] | | | | | |
| [Caso 2] | | | | | |
| [Caso 3] | | | | | |

- MAE de estos casos y cálculo:
- Diferencia entre esta comprobación parcial y la métrica de toda la partición:

## 6. Residuos, complejidad y consulta

- Figura incluida y conjunto que muestra:
- Patrón observado y caso concreto que lo ilustra:
- Hipótesis que sugiere y evidencia necesaria para investigarla:
- Comparación entrenamiento/validación y posible sobreajuste:
- Horas consultadas fuera del rango, predicción y marca de extrapolación:
- Por qué la consulta no tiene un error observado:
- Límite de una interpretación causal:
- Variante opcional: cambio, copia utilizada y resultados separados del protocolo original:

## 7. Registro anterior al cierre

- Candidato fijado:
- Archivo que conserva modelos, transformaciones y selección:
- Código, protocolo y huellas de desarrollo fijados:
- Fecha y decisión tomada antes de ejecutar prueba:

## 8. Cierre separado

- Comando con `--evaluar-prueba` y nueva carpeta de salida:
- Coincidencia de código, protocolo, huellas de desarrollo, modelos y selección con el registro anterior:
- Huella de prueba y número de casos:
- MAE, RMSE, error medio firmado y R² de prueba:
- Interpretación sin cambiar de ganador:
- Qué evaluación nueva haría falta si se rediseñara el procedimiento:

## 9. Verificación y límites

- Comando y resumen de las 26 pruebas:
- Control concreto de separación de datos:
- Comprobación de exportaciones completas y legibles:
- Qué no demuestran las pruebas ni las métricas sintéticas:
- Evidencia necesaria para evaluar una instalación real:

## 10. Archivos entregados

Relaciona informe, JSON, CSV y figuras con sus carpetas. Incluye comandos completos; no reemplaces las exportaciones de desarrollo por las de cierre.

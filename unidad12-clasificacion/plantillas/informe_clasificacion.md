# Informe de clasificación — [Título]

[Reto](../reto.md) · [Unidad](../README.md)

Completa con evidencia de tu ejecución. Conserva el registro previo y separa desarrollo, variantes opcionales y cierre.

## 1. Pregunta

- Laboratorio elegido:
- Unidad de observación y momento de predicción:
- Entrada permitida y significado:
- Etiqueta y clase positiva:
- Disponibilidad declarada y evidencia que falta:
- Ejemplo de información que produciría filtración:
- Condiciones o población que los datos no representan:

## 2. Protocolo previo

- Fecha y versión del protocolo:
- Archivos y cantidades de casos/positivos por partición:
- Candidatos y orden de desempate:
- Transformación y conjunto de ajuste:
- Pérdida, penalización, tasa, inicialización e iteraciones:
- Métrica de selección y diagnósticos:
- Tratamiento de valores inválidos y métricas indefinidas:
- Reajuste con validación:
- ¿Qué conocía ya de prueba, el generador o las respuestas públicas?:

## 3. Reproducción

- Commit o versión exacta del código:
- Versiones de Python, NumPy y Matplotlib:
- Comando completo desde la raíz:
- Carpeta de exportación de desarrollo:
- Huellas de entrenamiento y validación:
- Confirmación de `prueba: null` en esa exportación:

## 4. Ajuste y predicción manual

- Centro, escala y rango de señal de entrenamiento:
- Intercepto y coeficiente:
- Clase mayoritaria y frecuencia positiva de entrenamiento:
- Objetivo inicial/final y norma del gradiente; qué permiten concluir:
- Caso elegido para el cálculo:
- Señal, z, logit, probabilidad y clase con el umbral correspondiente:
- Diferencia entre usar parámetros completos y cifras redondeadas:

## 5. Comparación de validación

| Candidato | VP | VN | FP | FN | Exactitud | Precisión | Recobrado | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Completar todos los candidatos] | | | | | | | | |

- Matriz reconstruida desde CSV, con orientación declarada:
- Cálculo de precisión, recobrado y F1:
- Casos de denominador cero y forma de informarlos:
- Candidato seleccionado por el criterio previo:
- Comparación con ambas referencias:
- Diferencia entre pérdida penalizada de ajuste, pérdida probabilística y F1:

## 6. Errores y figura

- FP concreto: identificador, señal, probabilidad y etiqueta:
- FN concreto: identificador, señal, probabilidad y etiqueta:
- Consecuencia posible de cada error y evidencia que falta para valorarla:
- Figura incluida e interpretación:
- Equilibrado: qué representan las proporciones y el objetivo de entrenamiento:
- Desbalanceado: qué se conserva y qué cambia entre umbrales:
- Por qué estos resultados no certifican calibración ni utilidad real:
- Variante opcional, cambios y resultados separados:

## 7. Registro anterior al cierre

- Fecha del registro:
- Modelo, referencias y candidato fijados:
- Umbral, si corresponde:
- Archivo que conserva código, configuración y huellas de desarrollo:
- Confirmación de que la decisión precede a la ejecución de prueba:

## 8. Cierre

- Comando con `--evaluar-prueba` y carpeta nueva:
- Coincidencia con el registro previo de código, protocolo, huellas, modelo, referencias y selección:
- Huella de prueba, casos y positivos:
- Matriz y métricas finales del único candidato elegido:
- Casos fuera de rango o métricas indefinidas:
- Interpretación sin reseleccionar:
- Evaluación nueva necesaria si se cambiara el modelo o el umbral:

## 9. Verificación y archivos

- Comando y resultado de las 28 pruebas:
- Control de cálculo o ajuste numérico:
- Control de separación de datos:
- Comprobación de exportaciones completas y figuras legibles:
- Relación de JSON, CSV, gráficos e informe entregados:
- Limitaciones del escenario y evidencia que falta fuera del curso:

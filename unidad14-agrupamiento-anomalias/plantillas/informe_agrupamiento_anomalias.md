# Informe — [Agrupamiento o anomalías]

[Reto](../reto.md) · [Unidad](../README.md)

Completa la sección específica de tu laboratorio y todas las comunes. Conserva el registro previo al cierre; no lo reescribas como si el resultado final se conociera de antemano.

## 1. Pregunta y datos

- Laboratorio y unidad de observación:
- Variables, unidades, dominios y momento de disponibilidad:
- Etiquetas disponibles y finalidad de cada una, si existen:
- Casos por partición y condición ordinaria declarada, si corresponde:
- Evidencia temporal o por equipos que falta:
- Qué conocía de datos, generador, soluciones y prueba antes de empezar:

## 2. Protocolo previo

- Fecha y protocolo:
- Candidatos y orden de desempate:
- Parámetros del algoritmo y semilla principal:
- Media, varianza y escala; conjunto utilizado para aprenderlas:
- Criterio de selección y manejo de métricas indefinidas:
- Diagnósticos que no intervienen en la selección:
- Conjuntos permitidos para cada ajuste:
- Confirmación de ausencia de reajuste con validación o prueba:

## 3. Reproducción

- Commit exacto, Python y versiones de bibliotecas:
- Comando completo y carpeta de desarrollo:
- Huellas SHA-256 de archivos utilizados:
- Confirmación de `prueba: null`:
- Comando y registro de cualquier variante opcional, separado del principal:

## 4A. Agrupamiento

- Paso manual: asignaciones, centros e inercia antes/después:
- Silueta del punto A, con a y b explícitos:
- Caso del CSV: identificador, entradas, z, distancias y grupo:
- Centros elegidos en unidades originales e interpretación descriptiva:

| Candidato | Inercia entrenamiento | Silueta validación | Tamaños | ARI con 29 | ARI con 47 |
|---|---:|---:|---|---:|---:|
| k2 | | | | | |
| k3 | | | | | |
| k4 | | | | | |

- Elegido y regla aplicada:
- Lectura de figuras; diferencia entre inercia, silueta y estabilidad:
- Por qué los identificadores y colores no son clases verdaderas:
- Limitaciones de geometría, escala, inicialización y cobertura:

## 4B. Anomalías

- Puntuación de cada detector y sentido de su escala:
- Umbrales reconstruidos con la posición 57 y comparación estricta:
- Cantidad de alertas en calibración y lo que no garantiza:

| Candidato | VP | VN | FP | FN | Precisión | Recobrado | F1 | Exactitud |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sin_alertas | | | | | | | | |
| distancia_centro | | | | | | | | |
| aislamiento | | | | | | | | |

- Matriz reconstruida y fórmulas utilizadas:
- Elegido y comparación con no emitir alertas:
- FN del elegido: identificador, señales, referencia, puntuación y umbral:
- FP por distancia y análisis del cero observado de FP del bosque:
- Lectura de la figura; por qué la puntuación no es probabilidad:
- Diferencia entre ajuste sin etiquetas y selección apoyada en etiquetas:
- Evidencia y capacidad de revisión necesarias en un contexto real:

## 5. Registro anterior al cierre

- Fecha:
- Candidato y configuración conservados:
- Escala y, si corresponde, umbral fijado:
- Exportación que conserva estos campos y huellas de desarrollo:
- Alcance del cierre teniendo en cuenta el carácter público de las respuestas:

## 6. Cierre y verificación

- Comando con `--evaluar-prueba` y carpeta nueva:
- Coincidencia de código, versiones, protocolo, semilla, huellas de desarrollo, escala, modelos y selección:
- Huella y número de casos de prueba:
- Métricas del único elegido y casos fuera de rango:
- Interpretación sin volver a seleccionar:
- Nueva evaluación necesaria para cualquier cambio motivado por prueba:
- Comando y resultado de las 30 pruebas:
- Comprobación matemática y comprobación de separación identificadas:
- Archivos entregados y figuras revisadas:

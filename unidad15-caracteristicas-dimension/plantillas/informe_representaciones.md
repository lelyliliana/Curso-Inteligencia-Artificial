# Informe — [Características o PCA]

[Reto](../reto.md) · [Unidad](../README.md)

Completa las secciones comunes y la específica de tu laboratorio. Conserva el registro anterior al cierre y separa las variantes opcionales.

## 1. Formulación y datos

- Laboratorio y unidad de observación:
- Momento de predicción y objetivo posterior:
- Entradas permitidas, unidades y dominios:
- Identificadores, objetivos y columnas posteriores excluidos:
- Supuesto de disponibilidad y evidencia temporal que falta:
- Casos por partición y alcance de los datos sintéticos:
- Conocimiento previo de generador, respuestas y prueba:

## 2. Protocolo y reproducción

- Fecha y protocolo:
- Candidatos y orden de desempate:
- Transformaciones deterministas y transformaciones aprendidas:
- Conjunto de ajuste de cada paso:
- Regresión, intercepto y ausencia de penalización:
- Criterio de selección y tolerancia absoluta:
- Métricas adicionales y tratamiento de valores indefinidos:
- Commit, Python y versiones de bibliotecas:
- Comando completo, carpeta y huellas de desarrollo:
- Confirmación de `prueba: null`:

## 3A. Interacción

- Caso identificado y entradas originales:
- Producto, unidad y significado:
- Nombres y orden de las características:
- Media y escala completas; vector z calculado:
- Intercepto y coeficientes en z:
- Predicción manual y contraste con el CSV:
- Por qué la lectura de cierre no es admisible:
- Por qué horas y minutos no aportarían información independiente:

## 3B. PCA

- Ejemplo manual: media, covarianza, eje, coordenada, reconstrucción y MSE por celda:
- Caso de validación identificado y entradas:
- Media y escala; z:
- Media de PCA y eje retenido:
- Coordenada de pca1 y reconstrucción en z y unidades originales:
- Intercepto y coeficiente predictivo; predicción manual:
- Diferencia entre reconstruir las entradas y predecir el objetivo:
- Qué conserva un cambio de signo y qué significa pca2 con dos entradas:

## 4. Comparación de validación

| Candidato | Dimensión predictiva | MAE entrenamiento | MAE validación | RMSE | R² |
|---|---:|---:|---:|---:|---:|
| [Todos los candidatos] | | | | | |

- MAE reconstruido desde CSV:
- Seleccionado y aplicación del desempate, si corresponde:
- Figura e interpretación:
- Caso de mayor error absoluto del elegido: identificador, real, predicción, residuo y cobertura:
- Explicaciones posibles y evidencia que falta para atribuir una causa:

Para PCA:

| Candidato | Varianza retenida en entrenamiento | MSE reconstrucción z en validación | MSE en señales originales |
|---|---:|---:|---:|
| pca1 | | | |
| pca2 | | | |

- Por qué estas métricas no sustituyen el MAE predictivo:
- Lectura correcta del cero numérico y de las escalas de la figura:

## 5. Registro previo y cierre

- Fecha del registro:
- Candidato y parámetros fijados; archivo que los conserva:
- Comando con `--evaluar-prueba` y carpeta nueva:
- Coincidencia de código, entorno, protocolo, huellas de desarrollo, modelos y elección:
- Huella y cantidad de casos de prueba:
- Métricas del único elegido y casos fuera de rango:
- Interpretación sin volver a seleccionar:
- Evaluación nueva necesaria para cualquier cambio motivado por prueba:

## 6. Verificación y entrega

- Comando y resultado de las 30 pruebas:
- Referencia matemática independiente identificada:
- Control de separación de información identificado:
- Variante opcional, modificaciones y resultados separados:
- JSON, CSV y figuras entregados y comprobados:
- Límites de disponibilidad, cobertura, reconstrucción, predicción y causalidad:

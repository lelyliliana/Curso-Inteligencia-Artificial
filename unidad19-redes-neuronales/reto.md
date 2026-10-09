# Reto — Una red pequeña que puedas verificar

[Volver a la unidad](README.md) · [Plantilla del informe](plantillas/informe_red.md)

Elige XOR o ruido. Tu entrega debe permitir comprobar cómo se obtiene una predicción, cómo se aprende y por qué se conserva una versión concreta. Usa CPU y el entorno de la unidad.

## Primera parte: reproducir

1. Ejecuta el protocolo original sin abrir prueba. Documenta huellas, entorno, particiones, candidatos y criterio de selección.
2. Reconstruye la propagación de un caso con las dimensiones de cada operación. Explica la clase desde su probabilidad y umbral.
3. Reproduce el paso manual de retropropagación, incluyendo el promedio y, cuando corresponda, la penalización.
4. Comprueba por diferencias finitas todos los parámetros de una red pequeña sobre un lote de varios casos. Conserva epsilon, gradiente analítico, aproximación y error máximo. Verifica también al menos un sesgo; comprobar solo pesos deja incompleta la prueba.
5. Presenta curvas y métricas de la referencia y de la red. Identifica el punto elegido, el último punto y qué parámetros usa cada predicción exportada.
6. Abre prueba después de seleccionar y registra el resultado sin cambiar modelo ni umbral. Completa la ficha de límites y la decisión de uso.

## Segunda parte: un diagnóstico controlado de desarrollo

Elige **una** opción y márcala como diagnóstico adicional, separado del protocolo oficial:

- **Sin activación:** compón dos capas afines, calcula la capa equivalente y demuestra igualdad de logits. Relaciona el resultado con el límite de una frontera lineal para XOR.
- **Simetría:** compara una red oculta inicializada totalmente en cero con la inicialización declarada, usando exactamente las mismas filas y presupuesto. Explica qué gradientes quedan bloqueados.
- **Regularización:** contrasta red32 y red32_l2 desde el mismo estado inicial. Reconstruye la penalización y describe el cambio de las curvas, sin atribuirlo a un cambio de arquitectura.
- **Tasa de aprendizaje:** declara dos tasas antes de ejecutarlas, manteniendo datos, inicialización y presupuesto. Registra ambas curvas, incluidos resultados desfavorables o fallos numéricos. No escojas la tasa a partir de prueba.

No necesitas mejorar una marca. Una explicación correcta de una limitación es un buen resultado. Si propones un predictor nuevo después de ver el cierre, indica que falta nueva evaluación independiente.

## Entrega

Un informe o notebook legible, los programas o cambios reproducibles, JSON/CSV de resultados, figuras relevantes y ficha de límites. Usa carpetas nuevas para conservar el original. Distingue las pruebas automatizadas de la evaluación predictiva: pasar las primeras no implica resolver un problema real.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Datos, dimensiones y preparación | 15 | Formas correctas, separación y escala de entrenamiento |
| Propagación y gradientes | 30 | Paso reconstruible y diferencias finitas con sesgos, pesos y L2 cuando corresponde |
| Protocolo y comparación | 20 | Referencias, criterio fijo, copias de estado y cierre separado |
| Diagnóstico de desarrollo | 20 | Una condición modificada, resultados completos e interpretación apoyada en evidencia |
| Reproducción y límites | 15 | Comandos, artefactos, ficha y decisión de uso proporcionada |

Requieren corrección antes de considerar completo el reto: seleccionar época con prueba; actualizar parámetros antes de terminar el gradiente correspondiente al estado previo; promediar dos veces por n; comparar pérdidas con penalizaciones diferentes sin explicarlo; presentar el último estado como si fuera el elegido; ocultar ejecuciones desfavorables; interpretar el mapa de probabilidades como garantía de rendimiento o causalidad.

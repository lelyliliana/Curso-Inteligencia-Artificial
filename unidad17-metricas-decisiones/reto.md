# Reto — Justificar una política de decisión

[Unidad](README.md) · [Plantilla](plantillas/informe_decisiones.md)

## Encargo

Elige uno de los laboratorios y entrega un informe que permita reconstruir sus decisiones, justificar el objetivo y reconocer las consecuencias que no fueron evaluadas. No se exige lograr una puntuación mayor ni añadir umbrales.

## Trabajo común

1. Define clase positiva, acción, disponibilidad de puntuaciones y momento posterior de las etiquetas. Declara qué resultados públicos ya conocías.
2. Registra el [protocolo](datos/protocolo.md): políticas, costos, restricciones, criterios de desempate y evaluación final. Explica qué costos reales no están representados.
3. Ejecuta desarrollo con `--salida` y `--graficos` en una carpeta nueva bajo `resultados/unidad17/`. Guarda commit, versiones, comandos y huella; comprueba `prueba: null` y que no se registra fuente de prueba.
4. Desde el CSV de decisiones de validación, reconstruye la matriz de confusión del elegido y calcula precisión, recobrado, F1, especificidad, costo total y costo por caso. Distingue valores nulos y ceros.
5. Compara todas las políticas con cifras completas y justifica el ganador usando el criterio oficial. No sustituyas retrospectivamente costo por F1 o precisión.
6. Resuelve el ejemplo de cuatro casos: ROC AUC por pares, AP por bloques y Brier. Contrasta los diagnósticos s y s² del JSON e interpreta lo que conservan y lo que cambia.
7. Calcula una precisión hipotética con otra prevalencia, declarando el supuesto de tasas constantes y por qué podría fallar.
8. Completa el análisis específico de tu laboratorio.
9. Conserva la política elegida y el registro anterior. Ejecuta cierre en otra carpeta y comprueba igualdad de validación, huella, costos, parámetros y elección. Informa prueba únicamente para el elegido.
10. Ejecuta las 30 pruebas y explica una referencia matemática o de biblioteca y una comprobación que cambia información de prueba. Reconoce qué evaluación nueva haría falta si el cierre motivara cambios.

## Si eliges costos

- Reconstruye una alerta verdadera, una falsa alerta y una omisión de la política elegida: ID, puntuación, etiqueta, acción y contribución al costo.
- Explica el intercambio al bajar de 0,2 a 0,1 y verifica la diferencia de costo desde conteos.
- Recalcula la selección solo en validación con FN=1 y FN=12, dejando FP=1. Identifica qué métricas y decisiones de cada política no cambian.
- Interpreta ambas figuras. En fiabilidad, informa el tamaño de cada intervalo no vacío y evita atribuir certeza a grupos pequeños.
- Compara el umbral analítico 1/7 con la selección empírica y explica sus supuestos diferentes.

## Si eliges capacidad

- Reconstruye `validacion-L02`: filtra puntuaciones ≥0,5, ordénalas por puntuación descendente e ID ascendente y selecciona seis. Conserva la lista completa y marca el empate en el límite del cupo.
- Calcula conteos y costo de ese lote y comprueba que los conteos globales sean la suma de los lotes. No promedies precisiones con denominadores distintos.
- Justifica el empate de costo entre políticas 0,3 y 0,5 y el desempate por alertas. Explica el efecto sobre FP y FN.
- Cuenta los lotes que excederían capacidad con umbral 0,5 sin cupo. Explica por qué ese diagnóstico no puede competir en la selección.
- Revisa todos los lotes de prueba: cada uno debe respetar el cupo sin consultar etiquetas. Explica el supuesto de lote completo y el límite del desempate por ID.

## Entrega y evaluación

Informe de dos a cuatro páginas en Markdown o formato equivalente, exportaciones JSON/CSV de desarrollo y cierre y figuras de desarrollo. Usa la [plantilla](plantillas/informe_decisiones.md).

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Formulación y consecuencias | 15 | Clase, acción, disponibilidad, costos y restricciones explícitos |
| Cálculos | 25 | Matriz, denominadores, costos y ejemplo de ordenación reproducidos |
| Selección | 20 | Todas las políticas, criterio correcto y desempates verificables |
| Interpretación | 20 | Casos o lote reconstruidos; límites de áreas, probabilidad y capacidad |
| Cierre | 10 | Política conservada, prueba del único elegido y evaluación de omisiones |
| Reproducción | 10 | Versiones, commit, huellas, comandos, exportaciones y pruebas |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos usar etiquetas para repartir el cupo, ignorar sus excedentes, reemplazar una métrica indefinida sin explicarlo, afirmar que AUC mide calibración o exactitud, elegir otra política con prueba o presentar precisión=1 como detección de todos los positivos.

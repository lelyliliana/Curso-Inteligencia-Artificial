# Reto — Preparación con decisiones y evidencia

[Volver a la unidad](README.md) · [Plantilla de informe](plantillas/informe_preparacion.md)

## Escenario

Después del diagnóstico de la Unidad 7, debes producir una vista utilizable de las lecturas sin ocultar problemas pendientes. El equipo también quiere comprender por qué una transformación estadística no debe ajustarse con información de validación.

Usa los casos sintéticos del curso. Conserva el original de la Unidad 7 y no presentes la referencia ficticia como una comprobación física real.

## Trabajo

1. Explica la política de preparación, su orden y sus límites antes de ejecutar.
2. Predice los destinos de los doce registros y verifica el balance de preparados, duplicados y cuarentena.
3. Exporta una preparación conservadora y otra con la corrección explícita, a carpetas nuevas.
4. Contrasta indicadores antes y después, con el mismo plan de cobertura. Examina qué sensores pierden representación.
5. Comprueba las huellas de entrada y salida. Explica cómo recuperar el original de una celda corregida desde la trazabilidad.
6. Calcula a mano la mediana y el escalado del segundo caso; ejecuta y compara.
7. Cambia únicamente validación en una copia. Verifica que los parámetros correctos permanecen iguales y explica qué cambió en las salidas.
8. Ejecuta un caso límite y documenta la respuesta: fuente desfasada respecto del lote, entrenamiento ausente o columna constante.
9. Redacta una conclusión con una decisión pendiente y su evidencia requerida.

## Entregables

- Informe basado en la plantilla, con política y cuentas manuales.
- Dos exportaciones del primer laboratorio y el informe correcto del segundo.
- Copias de las variantes, comandos, parámetros, Python y commit utilizado.
- Huellas de los archivos y resultados de las pruebas.
- Explicación de las limitaciones y próximos pasos.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Política y justificación | 20 | Acciones diferenciadas y orden razonado |
| Trazabilidad y conservación | 25 | Balance completo, originales, correcciones y cuarentena reconstruibles |
| Comparación de calidad y cobertura | 20 | Denominador estable, faltantes visibles y efecto por sensor |
| Ajuste y transformación | 20 | Cuentas correctas, entrenamiento separado y parámetros conservados |
| Reproducibilidad y conclusiones | 15 | Archivos, comandos, huellas, pruebas y límites explícitos |

Objetivo de autoevaluación: al menos 80 puntos. Revisa el trabajo aunque alcance ese valor si sobrescribe la fuente, elige una versión conflictiva sin evidencia, pierde registros en el balance o ajusta la transformación correcta con validación.

Extensión opcional: definir otra política de tratamiento de faltantes para una tarea concreta. Debes explicar sus efectos, compararla con la conservación de ausencias y añadir las comprobaciones pertinentes; no basta con eliminar mensajes de error.

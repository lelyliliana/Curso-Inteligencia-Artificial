# Reto — Entregar un taller y proponer su siguiente versión

[Unidad](README.md) · [Plantilla](plantillas/informe.md) · [Informe de referencia](recursos/informe.md)

Elige uno de los tres talleres y prepara una entrega que otra persona pueda reproducir sin hablar contigo. El objetivo es justificar una decisión de uso, revisión o descarte mediante evidencia. Una conclusión «todavía no está listo para este uso» puede ser excelente si identifica el fallo y propone cómo evaluarlo.

## Parte A: reproducción de la versión publicada

1. Define usuario, decisión, contrato y acción humana en un párrafo.
2. Ejecuta desarrollo, guarda el estado y ejecuta cierre sin modificarlo. Conserva comandos, versiones, IDs y huellas.
3. Contrasta la referencia en validación. Reconstruye a mano una métrica sobre los casos del informe.
4. Explica un error concreto y un resultado agregado; declara la población de cada uno.
5. Demuestra una entrada válida, una inválida y una limitación de calidad. Explica por qué pasar el contrato no prueba que la respuesta sea útil.

## Parte B: propuesta para la Unidad 35

Redacta una modificación acotada, una hipótesis previa, sus datos y permisos, referencia, partición, criterio de selección, evaluación final y condición de reversión. No necesitas implementarla para completar esta unidad. El cierre publicado ya es conocido: no lo presentes como prueba nueva de una versión que hayas elegido mirando sus resultados.

Si quieres hacer un experimento adicional, sepáralo de la reproducción, guarda otro estado y otro informe, declara qué datos conocías y no reemplaces los fallos originales.

## Entregables

- Informe breve con problema, protocolo, resultados, errores y decisión.
- Modelo/índice, informes por caso y comandos de reproducción.
- Tres demostraciones documentadas y una figura con población y unidad.
- Propuesta del proyecto final con criterio de aceptación definido antes de ejecutar.

## Rúbrica — 100 puntos

| Dimensión | Puntos | Evidencia esperada |
|---|---:|---|
| Problema, usuario y límites | 15 | Decisión concreta y contrato suficiente |
| Datos y separación | 20 | Procedencia, disponibilidad y grupos/tiempo/familias coherentes |
| Referencia y selección | 15 | Comparación justa y desempate declarado |
| Cierre y análisis | 20 | Estado congelado, métrica reconstruida y fallo conservado |
| Demo y reproducción | 15 | Comandos, versiones, huellas y manejo de entradas |
| Propuesta y decisión de uso | 15 | Alcance viable, evidencia faltante y reversión |

La entrega requiere al menos 70 puntos y tres condiciones esenciales: identificar los datos ficticios, conservar la separación declarada y no ocultar errores. Si se viola una, corrige esa parte antes de dar el reto por completado; una métrica alta no la compensa.

**Revisión entre pares:** otra persona debe reproducir una predicción, localizar el caso que explica un error y distinguir lo medido de lo propuesto. No le compartas claves, datos personales o permisos que el taller no necesita.

# Reto — Comparación de referencias con evaluación final separada

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe_experimento.md)

## Situación

Necesitas decidir qué referencia sencilla deberá superar un futuro modelo. Elige **uno** de los dos laboratorios y documenta un experimento completo: diseño previo, comparación de validación y cierre con prueba. El objetivo es un procedimiento revisable, no obtener una puntuación alta.

## Trabajo

1. Describe la pregunta, unidad de predicción, horizonte, entrada permitida y objetivo. Identifica una columna que sería filtración si se incorporara al predictor.
2. Registra el [protocolo](datos/protocolo.md) antes de abrir prueba: partición, candidatos, preparación, métrica principal, diagnósticos, desempate y decisión de no reajustar con validación.
3. Ejecuta el laboratorio sin `--evaluar-prueba` y exporta el resultado a una carpeta nueva. Anota commit, Python, huellas y parámetros.
4. Compara los candidatos sobre los mismos casos. Reproduce a mano al menos un error y parte de la métrica o matriz de confusión. Explica qué aporta la referencia más informativa respecto de la constante o mayoría.
5. Inspecciona al menos un error concreto y una limitación de cobertura, dependencia o disponibilidad. Formula una posible mejora como hipótesis, sin implementarla para favorecer el cierre.
6. Guarda por escrito candidato seleccionado, parámetros y huellas de entrenamiento/validación. Si haces una variante didáctica con copias, etiquétala como un experimento distinto y conserva aparte la comparación del protocolo original.
7. Ejecuta el cierre con `--evaluar-prueba` sobre los datos originales y guarda otra exportación. Comprueba que coincidan protocolo, código, huellas de entrenamiento/validación, ajuste y selección con la comparación previa.
8. Informa el resultado final sin elegir de nuevo usando prueba. Explica qué evaluación nueva haría falta si quisieras rediseñar después.
9. Ejecuta las pruebas de la unidad y registra su salida. Explica qué control comprueba el flujo y qué afirmación de utilidad no puede comprobar.

La prueba de este ejercicio es pública y sus respuestas están documentadas para estudiar. Si ya las leíste, decláralo: podrás demostrar el flujo, pero no presentar tu proceso como una evaluación personal ciega. Los resultados sintéticos tampoco sustituyen una evaluación externa.

## Entrega

Un informe breve en Markdown o formato equivalente, con el protocolo previo y el cierre diferenciados. Adjunta los JSON, las predicciones CSV y los comandos desde la raíz del curso. Usa la [plantilla](plantillas/informe_experimento.md) y conserva las exportaciones en carpetas distintas bajo `resultados/unidad10/`.

No modifiques los originales ni combines las dos tareas en un único dataset. Si hubo una variante en copias, documenta sus cambios y explica por qué sus resultados no se mezclan con los de referencia. No es obligatorio entrenar ningún modelo adicional.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Pregunta y disponibilidad | 15 | Unidad, horizonte, entradas y objetivo definidos; filtración identificada |
| Partición y protocolo previo | 20 | Separación justificada; criterios y desempate fijados antes del cierre |
| Ajuste y comparación | 20 | Parámetros de entrenamiento; mismos casos; cálculo manual correcto |
| Errores e interpretación | 15 | Caso concreto, diagnósticos pertinentes y límites de generalización |
| Cierre separado | 15 | Coincidencia con el procedimiento fijado; resultado informado sin reselección |
| Reproducción y verificación | 15 | Código, huellas, versiones, comandos, informes y pruebas identificados |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos aprender parámetros con prueba, mezclar equipos cuando se pretende evaluar equipos nuevos, usar entradas futuras, comparar candidatos en casos diferentes sin explicarlo o cambiar de ganador por el resultado final.

## Preguntas para revisar la entrega

- ¿Se sabe exactamente qué información recibió el predictor?
- ¿Cuándo estaban disponibles entradas y etiquetas?
- ¿Qué se ajustó, qué se eligió y con qué conjunto?
- ¿Qué decidió el desempate, si lo hubo?
- ¿Se preservaron las filas difíciles y los faltantes con una política explícita?
- ¿El resultado final responde a días futuros, equipos nuevos u otra pregunta?
- ¿Qué dato nuevo necesitas para sostener una afirmación fuera de esta demostración?

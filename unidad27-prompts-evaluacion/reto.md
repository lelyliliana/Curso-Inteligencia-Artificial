# Reto — Evaluar antes de integrar un prompt

[Unidad](README.md) · [Plantilla](plantillas/informe_prompts.md)

## Encargo

Un taller considera extraer respuestas de registros de sensores mediante un modelo. Entrega una recomendación basada en un protocolo y evidencia por caso. Explica si una solución por reglas basta para el formato actual y qué cambiaría si las entradas fueran documentos de lenguaje libre.

La ruta básica analiza las capturas de la unidad, sin instalar pesos ni usar una API. La extensión opcional ejecuta un experimento propio con datos sintéticos y un modelo local previamente revisado. El reto no exige pagar servicios ni obtener mejores cifras que el curso.

## Entregables

1. Reconstrucción del informe de desarrollo y de la regla de desempate. Verifica a mano un caso normal y uno de conflicto o instrucción incrustada.
2. Análisis de al menos dos fallos, distinguiendo formato, coherencia, referencia y parada. Si empleas contraejemplos artificiales, identifícalos; nunca los presentes como salidas del modelo.
3. Explicación del resultado de cierre, conservando la selección y sus límites. Una mejora del cierre no demuestra perfección y un fallo no autoriza a reemplazar el candidato en ese mismo cierre.
4. Protocolo para una tarea nueva: al menos seis familias propias con dos vistas por familia, separadas en cuatro de desarrollo y dos de cierre **antes** de generar variantes. Incluye una ausencia, un conflicto y una nota que intente cambiar instrucciones. Fija candidatos, criterios, desempate y presupuesto.
5. Esquema de salida más una regla semántica que el esquema no resuelva. Demuestra dos objetos que cumplan los tipos pero fallen el contenido.
6. Si hay criterios subjetivos, una rúbrica con ejemplos anclados y procedimiento de desacuerdo. Puede ser una propuesta sin ejecutar; no inventes una revisión humana.

No uses las respuestas publicadas de cierre como una prueba reservada para elegir nuevos prompts. Si ejecutas la extensión, crea datos, protocolos y capturas nuevos; conserva todos los intentos y congela la elección antes de evaluar cierre. Guarda los resultados en `resultados/`, sin claves ni datos personales.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Tarea y referencia | 15 | Regla precisa de ausencia/conflicto y comparación con una solución sencilla |
| Separación y protocolo | 20 | Familias disjuntas, candidatos y desempate fijados antes de evaluar |
| Validación | 20 | Distingue JSON, forma, coherencia y contenido; conserva truncamientos |
| Análisis y selección | 20 | Denominadores, errores, estados, familias y elección reproducible |
| Cierre y límites | 15 | Evalúa la elección congelada y evita afirmaciones de seguridad o calidad general |
| Comunicación y reproducción | 10 | Procedencia clara, comandos, ficha y propuesta de revisión humana honesta |

Una negativa a recomendar un modelo innecesario puede ser una buena conclusión si la justificas. El puntaje valora el método y la evidencia, no la complejidad del prompt ni el tamaño del modelo.

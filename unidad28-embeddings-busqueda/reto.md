# Reto — Un buscador pequeño y auditable

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe_recuperacion.md)

Construye un buscador para 20–40 textos cortos propios o con permisos de uso claros. Puede tratar de guías de estudio, preguntas de un laboratorio ficticio o documentación de una aplicación. Define el propósito y quién revisará los candidatos. No incluyas datos personales ni secretos en el material que publiques.

Antes de ejecutar, escribe al menos doce familias de consultas, con dos formulaciones cada una: seis familias de desarrollo y seis de cierre. Incluye al menos una familia sin respuesta por partición, casos con términos exactos y paráfrasis. Justifica cada juicio de relevancia leyendo todo el corpus. Si divides un documento, conserva ID de origen y explica si varias partes son necesarias para responder.

Compara una referencia léxica con embeddings reales de un modelo cuya licencia y recursos hayas comprobado. Puedes reutilizar BGE-M3 instalado. Si no puedes ejecutar un modelo, realiza el análisis de las capturas publicadas y entrega el experimento nuevo como diseño pendiente, sin etiquetar vectores inventados como inferencia. Esa alternativa demuestra análisis, pero no completa el criterio de nueva ejecución.

Fija k, desempates y criterio antes de ver cierre. Guarda corpus, juicios, parámetros, índice, vectores de consultas, versión/digest y resultados por consulta. Repite la búsqueda tras recargar y demuestra equivalencia. Presenta dos fallos con sus fuentes; si no aparecen, añade un diagnóstico nuevo separado del cierre, sin alterar el resultado ya observado. Cita al menos un caso donde compartir tema no resuelve la pregunta.

| Criterio | Puntos |
|---|---:|
| Pregunta, corpus documentado y juicios explicados | 20 |
| Familias, ausencia de respuesta y protocolo previo | 20 |
| Comparación real de representaciones y recursos registrados | 20 |
| Métricas correctas y cierre sin reajuste | 15 |
| Persistencia, identidad del espacio y recarga comprobada | 15 |
| Análisis de errores, límites y presentación reproducible | 10 |
| Total | 100 |

Entrega un informe con comandos y artefactos; indica qué se ejecutó y qué quedó propuesto. No hace falta interfaz web, base vectorial, generación de respuestas ni servicio pagado. El criterio de calidad es que otra persona pueda reconstruir por qué se recuperó una fuente y por qué esa fuente resulta suficiente o insuficiente.

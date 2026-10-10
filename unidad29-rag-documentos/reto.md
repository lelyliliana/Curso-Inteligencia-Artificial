# Reto — Respuestas con evidencia comprobable

[Unidad](README.md) · [Plantilla](plantillas/informe_rag.md)

Construye un RAG pequeño sobre 12–20 documentos propios o con permiso de uso. Elige preguntas que puedan evaluarse: por ejemplo, un dato operativo por pregunta o una explicación breve con afirmaciones delimitadas. Define quién revisará la respuesta y qué significa evidencia suficiente. Si usas procedimientos ficticios, identifícalos como tales.

Conserva fuentes, versiones e IDs de fragmentos con sus posiciones. Diseña al menos doce familias de consultas, dos formulaciones por familia: seis para desarrollo y seis para cierre. Incluye ausencia de datos, fuentes contradictorias y una nota no confiable que intente cambiar la salida. Fija juicios antes de evaluar; no uses documentos personales o secretos para ensayar inyección.

Compara una referencia extractiva y un RAG local con dos configuraciones concretas de recuperación o contexto. Mantén constantes las demás condiciones. Guarda prompts, contextos realmente enviados, respuestas, errores y recursos. Elige solo con desarrollo, congela el estado y abre cierre después. No necesitas una API pagada, interfaz web ni base vectorial.

Demuestra dos verificaciones distintas: que la cita pertenece a la fuente/contexto y que su contenido respalda lo afirmado. Si utilizas una respuesta acotada, documenta exactamente lo que comprueba tu evaluador. Si usas prosa libre, entrega una rúbrica y revisión de afirmaciones; no reemplaces ese trabajo por una comprobación de IDs.

| Criterio | Puntos |
|---|---:|
| Pregunta, fuentes permitidas y juicios documentados | 15 |
| Fragmentación con procedencia y presupuesto de contexto | 15 |
| Comparación reproducible, referencia extractiva y recursos | 20 |
| Evaluación de recuperación, apoyo, contradicción y abstención | 25 |
| Selección, cierre y recarga sin filtración | 15 |
| Análisis de errores y límites claros | 10 |
| Total | 100 |

Entrega índice, capturas e informe con comandos. Si el equipo no permite nueva inferencia, analiza las capturas publicadas y presenta el nuevo experimento como diseño pendiente; eso cubre análisis, pero no acredita el criterio de nueva ejecución. Los resultados desfavorables deben conservarse y explicarse.

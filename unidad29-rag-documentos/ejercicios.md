# Diez ejercicios

[Unidad](README.md) · [Soluciones](soluciones/README.md)

1. Dibuja el recorrido desde un TXT hasta una respuesta RAG. Señala qué se calcula una vez al indexar y qué se calcula por pregunta. ¿Dónde se actualizan pesos en esta práctica?
2. Para `Café azul.\n\nÁrbol verde.\n`, encuentra los dos fragmentos y sus líneas. Explica por qué un offset de caracteres no equivale siempre a un offset de bytes.
3. Ejecuta el primer laboratorio. Con un presupuesto de 300 caracteres, identifica los fragmentos omitidos. ¿Por qué no se corta el texto para hacerlo caber? ¿Qué costo tiene detenerse en el primer candidato que no cabe?
4. Compara R03a con k=1 y k=3. ¿Puede una respuesta tener una cita real, estar sustentada y aun así no cumplir la pregunta sobre todas las agendas vigentes?
5. Para un caso con dos fragmentos de evidencia, calcula recall si llega uno. Distingue recall de fragmentos, cobertura de valores y suficiencia para contestar si las fuentes son redundantes o contradictorias.
6. Audita la respuesta `{"estado":"ok","dato":"99 días","citas":["D01:p01"]}` para R01a. ¿Qué capa pasa y cuál falla? Repite con dato `9 días` y cita `D02:p01`.
7. Explica cuándo `ausente` es una abstención justificada por el contexto y cuándo es un fallo de recuperación frente al corpus. ¿Qué puede saberse en producción sin el catálogo de evaluación?
8. Lee las notas de D06 y D12. ¿Por qué su valor 99 no es evidencia del dato operativo? ¿Qué demuestra resistir estos dos casos y qué no demuestra?
9. Recarga el índice y la selección; modifica una copia del prompt, los IDs de las filas o el digest. Explica qué compatibilidad se pierde y qué habría que regenerar.
10. Propón una evaluación nueva para preguntas con varios hechos o prosa libre. Define quién juzgaría el apoyo de cada afirmación, cómo trataría contradicciones y qué nuevo cierre necesitarías antes de afirmar una mejora.

Incluye IDs, texto de fuentes y cálculos. No basta con comprobar que el JSON se puede leer o que una cita existe.

# Diez ejercicios

[Volver a la unidad](README.md) · [Soluciones razonadas](soluciones/README.md)

1. Para q=[1,0], a=[3,4] y b=[1,0], calcula productos y cosenos. ¿Por qué pueden dar órdenes diferentes?
2. Normaliza [3,4]. ¿Qué cambia al multiplicarlo por 10 o por −1? ¿Qué harías con un vector nulo?
3. En dos documentos «sol sol agua» y «agua», calcula vocabulario e IDF suavizado. ¿Cómo representas una consulta formada solo por «luna»?
4. Los relevantes son A y C; top-3 es B,C,D. Calcula P@3, Recall@3, Hit@3 y RR@3. Añade otra consulta respondible sin aciertos y calcula MRR@3.
5. Una consulta no tiene documentos relevantes, pero el sistema devuelve tres. Explica qué métricas son indefinidas y qué convención usa la unidad. ¿Por qué no debe contarse como acierto?
6. Lee D18 y las consultas F05. Justifica `relevantes=[]`, aunque D18 sea la primera recuperación. Compara su coseno con F02a: ¿un corte único puede separar todos esos casos de desarrollo?
7. Explica el fallo de F07a en cierre. Recalcula MRR@3 y la relación entre P@3=0,4167 y Recall@3=1. ¿Qué se pierde si solo se informa Hit@3?
8. Una consulta queda empatada en dos documentos cuyos IDs llegan en orden B,A. Indica el orden publicado. ¿Por qué sería incorrecto ordenar por puntuaciones redondeadas?
9. Recarga el índice JSON, cambia una copia de su digest/configuración o una fila y explica qué controles deben fallar. ¿Puedes usar embeddings de otro modelo de dimensión 1024? Diferencia reindexar y entrenar.
10. Propón un experimento nuevo que mejore la referencia léxica o gestione abstención. Define antes sus candidatos, nuevas familias, casos sin respuesta, criterio y cierre. No lo presentes como mejora comprobada sin ejecutarlo.

Entrega cálculos, comandos ejecutados y referencias a IDs; las respuestas generales sin contrastar textos no bastan para los ejercicios 6 y 7.

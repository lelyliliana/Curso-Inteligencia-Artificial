# Diez ejercicios

[Unidad](README.md) · [Soluciones](soluciones/README.md)

1. **Elegir intervención.** Un asistente necesita consultar un reglamento que cambia cada mes; otro necesita producir una convención de salida consistente a partir de ejemplos. Propón una primera referencia para cada uno y explica qué aportaría RAG o adaptación. No supongas que entrenar siempre es necesario.
2. **Contar parámetros.** Para una matriz 26×32 y rango 2, calcula los parámetros A/B, su proporción respecto a los 11.066 del modelo base y los parámetros totales con el adaptador activo. ¿Cuál de esas cifras describe memoria pico de entrenamiento?
3. **LoRA manual.** Reconstruye `BA` y la salida del ejemplo manual. Usa ahora `alpha=2`, `r=1` sin cambiar matrices. ¿Qué salida obtienes?
4. **Inicialización y gradientes.** Explica por qué B=0 mantiene la salida inicial y por qué A recibe gradiente cero en el primer paso. ¿Qué ocurriría si A y B fueran ambas cero? Distingue congelar, `eval()` y `no_grad()`.
5. **Selección.** El ajuste completo tiene menor CE que LoRA, pero ambos generan 24/24 secuencias. Aplica el criterio prefijado y explica por qué no se cambió después de mirar prueba. ¿Qué significa CE con teacher forcing frente a secuencia exacta?
6. **Exposición previa.** Doce prefijos del cierre ya aparecieron al entrenar la base. Identifica qué separación sí se respeta y qué afirmación sobre generalización sería incorrecta. Propón una reserva más exigente.
7. **Cambio de tarea.** Los adaptados obtienen 0/24 bajo la convención antigua. ¿Demuestra olvido general de capacidades? ¿Qué recupera desactivar LoRA y qué información adicional permitiría aprender las dos convenciones?
8. **Preparación multimodal.** Una imagen tiene medias 0,20 y 0,82 y la consulta es `estado derecha`. Escribe el vector de fusión y la respuesta de la regla. Explica qué se pierde si eliminas texto o imagen.
9. **Ablaciones y familias.** Demuestra los máximos de 75 % para visión aislada y 50 % para texto aislado en el conjunto equilibrado. Explica por qué partir al azar las filas, sin agrupar por escena, daría una evaluación menos exigente.
10. **Entradas incompletas.** Diseña el comportamiento ante un PNG RGB, una imagen ausente y una negación fuera de gramática. Distingue rechazo del programa, incertidumbre del modelo y evaluación con modalidades faltantes. ¿Qué casos nuevos reservarías antes de ampliar el parser?

Documenta cálculos, supuestos y referencias a artefactos. Una explicación que distingue el alcance de la práctica de un sistema general es parte de una solución correcta.

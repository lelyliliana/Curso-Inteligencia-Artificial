# Ejercicios — Talleres aplicados

[Unidad](README.md) · [Soluciones razonadas](soluciones/README.md)

Resuelve antes de abrir las soluciones. Indica población y unidad en cada cálculo.

1. **Disponibilidad temporal.** Para predecir la potencia de las 10:00, ¿qué lectura usa el taller? Explica por qué observar una lectura de prueba a las 09:00 no equivale a entrenar con la etiqueta de las 10:00. ¿Qué cambia si la lectura llega a las 09:20?
2. **Cambio y cierre.** Ridge obtiene MAE 1,1853 en validación y 3,5479 en cierre. ¿Demuestra esto que persistencia gana en cierre? ¿Sería correcto probar otros cinco α y presentar el mejor en ese mismo cierre como independiente?
3. **Modelo guardado.** Escribe qué se pierde si conservas solo los coeficientes de Ridge y omites escala, orden de características y protocolo. Verifica la identidad de una predicción antes y después de recargar.
4. **Costo ambiental.** Reconstruye el costo 76 con FP=12 y FN=16. Si el costo de FN fuese 2, ¿cuál sería el costo de esas mismas decisiones? Explica por qué ese cálculo no basta para afirmar que sigue siendo el mejor umbral.
5. **Grupos y métricas.** En Z11 hay TP=17, FP=1 y FN=12. Calcula precisión y recall. Explica qué fallo oculta reportar solo precisión y qué cambia al separar zonas completas.
6. **Cupo.** El taller propone 65 revisiones en cierre. Si el equipo solo puede hacer diez visitas por lote, ¿qué información y reglas faltan para convertir esa salida en una agenda?
7. **Recuperación y abstención.** Con cinco fragmentos pertinentes, uno incorrecto, tres abstenciones correctas y tres omisiones, calcula aceptadas, cobertura, precisión entre respondidas y costo documental. ¿Qué devolvería una política que siempre se abstiene?
8. **Cita y pertinencia.** Examina Q-transporte-1 en el cierre documental. ¿Qué comprueba el intervalo de cita? ¿Qué evidencia demuestra que el texto no responde la pregunta? Propón un caso nuevo fuera del corpus que comparta vocabulario.
9. **Contrato y operación.** Compara una pregunta vacía, `zxqv`, una consulta sobre transporte que recupera D05 y una huella de modelo alterada. Clasifica cada situación y describe la respuesta humana apropiada.
10. **Proyecto final.** Elige un taller. Redacta usuario, decisión, referencia, datos adicionales necesarios, partición, costo/métrica, criterio previo de aceptación y una condición de reversión. Distingue lo que ya demuestra el taller de lo que aún falta comprobar.

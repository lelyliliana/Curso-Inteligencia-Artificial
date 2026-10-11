# Ejercicios de cierre

[Unidad](README.md) · [Soluciones](soluciones/README.md)

1. **Hipótesis y evidencia.** ¿Qué hipótesis motiva el modelo de incremento? Distingue la evidencia conocida de la Unidad 34 de la evaluación nueva de esta unidad.
2. **Tiempo.** Una lectura se mide a las 10:00, llega a las 10:08 y se decide a las 10:05. ¿Qué debe responder el servicio? Si llega a las 10:01, ¿cuántos minutos faltan para el objetivo?
3. **Representación.** Calcula conceptualmente qué cambia en la predicción de incremento si aumentas la potencia actual ocho kW y conservas las fechas. Explica por qué no es reentrenamiento y por qué no anticipa un salto futuro.
4. **Población evaluada.** Se admiten 236 de 240 casos y el MAE es 1,2341 kW. ¿Sería correcto informar ese MAE como error sobre las 240 solicitudes? ¿Cómo reportarías los cuatro rechazos?
5. **Criterio conjunto.** Con MAE=1,5, referencia=2 y cobertura=94/100, calcula mejora y aceptación bajo el protocolo. ¿Qué ocurre si la referencia tiene MAE cero?
6. **Cierre y referencia.** ¿Por qué comparar persistencia en prueba no viola por sí solo la separación? ¿Qué acción posterior sí convertiría ese cierre en información de selección?
7. **Error y revisión.** PF1140 tiene error absoluto 8,366 kW. ¿Contradice que el MAE de cierre sea 1,2341? ¿Son las 57 marcas fuera de rango una medida de recall de fallos?
8. **Registros.** Relaciona una respuesta y su evento mediante `solicitud_id`. Explica qué permiten diagnosticar los contadores y qué dato adicional necesitarías para evaluar calidad predictiva en operación.
9. **Reversión y recarga.** Compara `--referencia` con copiar un modelo antiguo sobre código modificado. Identifica qué debe conservarse para reproducir una versión y qué comprueba una huella.
10. **Defensa propia.** Prepara una explicación de cinco minutos de tu proyecto con problema, referencia, partición, resultado, fallo y decisión. Incluye una afirmación que tus datos sí sostienen y otra que todavía no puedes sostener.

# Diez ejercicios

[Unidad](README.md) · [Soluciones](soluciones/README.md)

1. **Cuatro señales.** El proceso responde `/live=200`, `/ready=503` y un POST recibe 503. Explica dos estados compatibles y por qué no puedes concluir que la calidad predictiva cayó. ¿Qué cambia cuando `/ready=200` pero `ocupado=true`?
2. **Admisión.** Hay cuatro cupos de conexión y uno de inferencia. Una consulta retiene el modelo, llega otra y luego una sonda. Describe qué puede suceder. Distingue una cola de trabajo de la exclusión mutua del modelo.
3. **Mantenimiento.** Se activa mientras una consulta ya está dentro del servicio. Define qué debe pasar con esa consulta y con las nuevas. ¿El cierre con Ctrl+C equivale a drenar todas las solicitudes?
4. **Tiempo y cancelación.** El cliente agota su espera a los 100 ms, pero el servidor prepara un 200 después. ¿Es una contradicción? Distingue timeout de socket, límite de espera del cliente, objetivo de latencia y cancelación fuerte.
5. **Registro mínimo.** Propón un evento para un 500 sin copiar imagen, consulta ni mensaje de excepción. Explica por qué agrupar rutas desconocidas y no usar el UUID como etiqueta de un contador.
6. **Tasas.** En cinco POST hay estados 200, 200, 422, 503 y 500, con tiempos 10, 30, 5, 2 y 90 ms. Calcula tasa 5xx, fracción buena con objetivo 20 ms, media y p95 por rango más cercano. ¿Qué cambia si agregas cien sondas exitosas al denominador equivocado?
7. **Histogramas.** Explica qué significa el bucket acumulado `le_ms=20, n=3` del ejemplo manual. ¿Puedes recuperar el p95 exacto solo con los buckets? ¿Por qué no conviene promediar p95 de distintos grupos?
8. **Lectura de capturas.** Justifica las 14 respuestas y 15 eventos del laboratorio de fallos. Explica por qué el rechazo de conexión se cuenta aparte y por qué la instantánea de `/metricas` no incluye su propia respuesta terminada.
9. **Seguridad y límites.** El servidor escucha en loopback y valida Origin. ¿Esto autentica a la persona? Describe un límite real de los controles de tamaño, de los timeouts y de la retención del historial.
10. **Cambio e incidente.** Propón un procedimiento para corregir una excepción, comprobar recuperación y volver temporalmente a U32 si hay regresión. Identifica evidencia que debe conservarse y dos cosas que una consulta canaria no demuestra.

Incluye cálculos, decisiones y referencias a los casos. No necesitas exponer el servidor a Internet ni provocar fallos sobre servicios de terceros.

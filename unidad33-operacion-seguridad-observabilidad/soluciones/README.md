# Soluciones razonadas

[Ejercicios](../ejercicios.md) · [Unidad](../README.md)

1. Mantenimiento y degradación son compatibles: ambos deshabilitan nuevas predicciones mientras el proceso todavía atiende sondas. No se han medido etiquetas ni errores predictivos. Con `listo` y `ocupado=true` la política permite servir, pero el único cupo está temporalmente usado; una segunda inferencia recibe 503.

2. La primera consulta ocupa un manejador y el cupo de inferencia. La segunda puede entrar por otro manejador, pero se rechaza al intentar la admisión; no espera al modelo. Una sonda puede usar otro cupo y responder. Si se agotan todos los cupos de conexión, también la sonda puede ser rechazada antes de leerse. Un candado evita ejecución simultánea; por sí solo no impide que crezca una cola de hilos esperando.

3. La admitida puede terminar y devolver su resultado; las nuevas reciben `no_disponible`. El estado se comprueba junto con la admisión bajo el mismo bloqueo para definir un orden. Ctrl+C termina el servidor local con hilos daemon; no implementa un cierre ordenado de trabajos arbitrariamente bloqueados. Un drenaje real necesita detener admisión, observar trabajo activo y una política explícita de plazo y terminación.

4. No hay contradicción: el cliente dejó de esperar y el servidor continuó. El timeout de socket limita una operación de red; el del cliente no mata el cálculo remoto; el objetivo clasifica el resultado después. Cancelación fuerte exige poder interrumpir y limpiar recursos, por ejemplo mediante aislamiento adecuado, no solamente descartar un futuro. Reintentar enseguida puede duplicar trabajo en otros diseños.

5. Un evento puede incluir UUID generado, categoría `prediccion`, método POST, estado 500, código `error_interno`, duración y huella del modelo. No necesita la excepción completa. Un contador por URL arbitraria o por UUID crea tantas etiquetas como entradas distintas; agrupar rutas y usar el UUID solo en el historial evita ese crecimiento. La deque acotada no limita un archivo de stderr redirigido.

6. 5xx=`2/5=40 %`; buenas=`1/5=20 %`; media=`137/5=27,4 ms`; tiempos ordenados `[2,5,10,30,90]`, p95 en posición 5: 90 ms. Si se añaden cien sondas al denominador equivocado, `2/105≈1,90 %` parecería una mejora sin cambiar ninguna predicción. El script [manual](03_operacion_a_mano.py) reproduce el caso artificial.

7. Hay tres solicitudes con duración menor o igual a 20 ms: 10, 5 y 2; incluye tanto éxitos como errores. Los buckets pierden los valores exactos dentro de cada intervalo. El p95 exacto de la muestra manual se calcula con los cinco tiempos originales, no se recupera mágicamente del histograma. Promediar percentiles ignora distribuciones y tamaños; para combinar histogramas compatibles se suman sus conteos y se interpreta el intervalo o una aproximación definida.

8. Una consulta agotó la espera del cliente; su evento posterior 200 no tiene una respuesta recibida en la lista. El rechazo de conexión ocurre antes de conocer ruta/método y, por tanto, no se puede atribuir a predicción. La consulta `/metricas` toma la instantánea cuando sigue en curso; al preparar su respuesta se incrementa el total final.

9. Loopback limita la interfaz de red, no identifica al usuario. Un proceso local puede construir cabeceras Host/Origin. El tamaño limita bytes pero no demuestra pertenencia al dominio; el timeout por operación permite que una solicitud avance lentamente; la retención de 256 eventos no acota contadores históricos ni archivos de registro externos. Los contadores tienen etiquetas finitas, pero sus valores aumentan hasta reiniciar.

10. Conservar ID, estados, configuración, versión y reproducción sintética; limitar admisión si corresponde; corregir causa; ejecutar un caso conocido; revisar estado y reanudar. Si la nueva capa falla, detener U33 y ejecutar U32 conservada, documentando que se pierden los controles nuevos. No se necesita borrar commits o sobrescribir pesos. El canario no demuestra generalización ni capacidad sostenida bajo carga, y un reinicio puede borrar evidencia en memoria.

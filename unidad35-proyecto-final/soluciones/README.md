# Soluciones razonadas del cierre

[Unidad](../README.md) · [Ejercicios](../ejercicios.md) · [Aceptación manual](03_aceptacion_a_mano.py)

1. La hipótesis es que una variación de calendario aprendida y sumada a la potencia actual puede seguir niveles ya observados. La U34 mostró un fallo que motivó esa idea; su cierre ya es información de desarrollo de la hipótesis. La U35 genera otra serie, fija tres candidatos y separa periodos nuevos. Sigue siendo evidencia sintética sobre una construcción conocida, no prueba de eficacia en edificios reales.

2. Debe rechazar con `lectura_no_disponible`: a las 10:05 aún no conocía la lectura que llegó a las 10:08. Si llegó a las 10:01, es admisible y el objetivo es las 11:00, una hora desde la medición; faltan 55 minutos desde la decisión. Cambiar la fecha de llegada para hacer pasar un caso falsearía la disponibilidad.

3. Aumenta ocho kW. Las diferencias de seno, coseno y calendario no cambian, por lo que tampoco cambia el incremento estimado. No se modifican pesos ni escala. Si el salto ocurre después de la lectura, esa entrada todavía no lo contiene; PF1070 y PF1140 conservan errores grandes en esos momentos.

4. El MAE resume solo los 236 casos con predicción. La cobertura es 236/240=98,3333 %. Informa cuatro rechazos con ID y causa, sin asignarles error cero ni omitirlos del total. Comparar modelos requiere mantener los mismos casos o explicar expresamente la diferencia de poblaciones.

5. Mejora `1−1,5/2=0,25`, es decir, 25 %. Error y mejora cumplen, cobertura 94 % no cumple; la conjunción es falsa. Si la referencia tiene error cero, dividir por cero no tiene sentido: esta implementación deja la reducción como `null` y no declara cumplida esa condición. Otro criterio tendría que definirse antes, no añadirse para salvar un resultado observado.

6. La referencia y la comparación estaban fijadas antes del cierre y ambos estados permanecen congelados. Se está midiendo la diferencia prevista, no buscando un ganador nuevo. Ajustar parámetros, elegir otra representación o cambiar umbral tras consultar prueba la convertiría en información de selección para esa nueva versión; habría que reservar otra evaluación.

7. No hay contradicción: un promedio puede ser bajo con algunos errores grandes. Conviene estudiar distribución y casos concretos. Las 57 marcas son comparaciones de potencia contra mínimos/máximos de entrenamiento; no son etiquetas de fallo del modelo ni permiten calcular recall sin una definición de fallo y sus referencias.

8. El UUID debe coincidir; modelo y política explican qué estado atendió. Los contadores describen respuestas, rechazos y errores del servicio. Para MAE necesitas el objetivo que se observe después, su correspondencia con la predicción y la población evaluada. Una tasa baja de rechazos no garantiza buena predicción.

9. `--referencia` usa la persistencia ya guardada dentro del mismo paquete y lo anuncia. Copiar pesos antiguos no recupera necesariamente preparación, código y protocolo correspondientes; la carga puede rechazar las fuentes diferentes. Conserva versión completa, dependencias, datos y estado. La huella comprueba consistencia con el contenido esperado, no autoría, seguridad general ni calidad.

10. Ejemplo de afirmación respaldada: «en 236 decisiones sintéticas admitidas de un periodo reservado, el modelo congelado redujo el MAE frente a la referencia fijada». Afirmación todavía no respaldada: «ahorrará energía en edificios reales». La defensa debe mostrar un caso que limite la primera conclusión y la evidencia adicional necesaria para estudiar la segunda. Usa [el guion de referencia](../recursos/defensa.md) como estructura, no como sustituto de tu evidencia.

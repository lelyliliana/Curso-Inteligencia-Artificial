# Soluciones razonadas

[Unidad](../README.md) · [Ejercicios](../ejercicios.md) · [Cálculo manual ejecutable](05_decidir_a_mano.py)

1. **Tiempo.** Usa la potencia observada a las 09:00 y el calendario de las 10:00. El modelo permanece congelado; leer una variable ya disponible para inferir no es ajustar con una etiqueta futura. El taller supone llegada inmediata. Con llegada a las 09:20, esa lectura no está disponible para una decisión tomada a las 09:00: hay que definir la hora real de decisión o usar información anterior y volver a evaluar.

2. **Cierre.** Solo se sabe que Ridge empeoró entre poblaciones temporales diferentes. La persistencia se comparó en validación, no en el cierre publicado. Elegir α después de ver ese periodo lo convierte en información de desarrollo para esa nueva versión. Conserva el primer resultado, declara la modificación y reserva otro periodo; no rebautices el mismo conjunto como independiente.

3. **Persistencia del estado.** Los coeficientes multiplican variables transformadas en un orden determinado. Sin medias, escalas, seno/coseno y orden, otra aplicación puede producir números distintos con los mismos pesos. El estado JSON guarda esa preparación y la decisión; los IDs y huellas permiten relacionarla con el experimento. La demo de energía devuelve aproximadamente 43,313094897 kW con el estado publicado. Una coincidencia de recarga comprueba implementación, no validez en campo.

4. **Costo.** `12+4·16=76`. Si FN costara dos, las mismas decisiones costarían `12+2·16=44`. No has calculado el costo de todos los demás candidatos bajo la nueva preferencia. Para seleccionar otra política define el costo antes, usa validación y evalúa el cierre correspondiente sin volver a elegir allí.

5. **Zona.** Precisión `17/18≈0,9444`; recall `17/29≈0,5862`. Casi todas las propuestas son positivas, pero doce positivos quedan sin proponer. Separar zonas responde una pregunta sobre grupos nuevos; repartir sus filas entre fases favorecería una evaluación dentro de zonas conocidas. La separación no garantiza representatividad ni elimina la variación introducida por el generador.

6. **Capacidad.** Falta definir qué constituye un lote, cómo ordenar puntuaciones, desempatar, respetar rutas y disponibilidad, y qué hacer con casos omitidos. Un umbral no impone diez cupos. Debe evaluarse la política completa con su costo y grupos, como en la Unidad 17. No basta con recortar las primeras diez filas del archivo.

7. **Denominadores.** Aceptadas `(5+3)/12=8/12`; cobertura `6/12`; precisión entre respondidas `5/6`; costo `3·1+1·3=6`. Siempre abstenerse lograría cuatro abstenciones correctas y ocho omisiones: 4/12 aceptadas, cobertura cero, precisión entre respondidas indefinida y costo ocho. No se debe convertir ese denominador vacío en una precisión perfecta.

8. **Cita.** El intervalo identifica caracteres existentes del texto y la versión; permite comprobar una copia exacta. D05 explica horario e inscripción de tutoría y no contiene información de transporte. El juicio esperado es `null`, por lo que devolver D05 es incorrecto aunque la cita sea fiel. Un caso nuevo podría preguntar si hay refrigerio durante la tutoría: debe revisarse que ningún documento lo responda antes de etiquetarlo y mantenerlo fuera de una selección ya cerrada.

9. **Fallos distintos.** La pregunta vacía viola el contrato y se rechaza. `zxqv` es válida pero sin términos conocidos: `sin_evidencia`. La consulta de transporte pasa el contrato y supera el umbral, pero falla en calidad; requiere revisión del caso y una nueva evaluación si se modifica la solución. Una huella alterada falla en integridad/versionado: hay que recuperar las fuentes correspondientes o producir una versión nueva, sin desactivar la comprobación para ocultar el cambio.

10. **Ejemplo de propuesta.** Para energía: responsable de un edificio, estimación horaria revisada por una persona, persistencia como referencia, lecturas con marcas de llegada y calendario de varios periodos, partición temporal, MAE y sesgo por horario. Antes de comparar, acordar con el responsable un error tolerable y una duración de evaluación, sin inventar aquí una cifra universal. Ante deterioro sostenido, volver a la referencia y revisar evidencia. El taller prueba código y protocolo en una serie sintética; faltan datos, permisos, criterios reales y prueba operativa. Las otras propuestas deben tener esa misma precisión de alcance.

# Soluciones — Unidad 2

[Volver a la unidad](../README.md) · [Índice del curso](../../README.md)

Las actividades de formulación admiten diferentes respuestas. La justificación debe conservar la relación entre necesidad, disponibilidad de datos y evaluación.

## Ejercicio 1 — Reformular

Una formulación posible: «La persona que opera un laboratorio necesita ordenar la revisión de registros de consumo cuando recibe más casos de los que puede atender en un lote. El proyecto inicial estudiará una selección para revisión humana en un solo laboratorio. Antes de elegir un modelo se deben comprobar el volumen de casos, la capacidad real, el procedimiento actual y el criterio de relevancia».

No afirmamos que existan doce casos o cuatro revisiones en ese laboratorio real. Esas cifras pertenecen únicamente a la simulación de la unidad.

## Ejercicio 2 — Disponibilidad

| Dato | ¿Disponible a las 10:00? | Uso posible |
|---|---|---|
| Lectura recibida a las 09:59 | Sí, si el proceso confirma su acceso | Entrada candidata |
| Lectura medida a las 09:50 y recibida a las 11:00 | No | No puede usarse para esa inferencia |
| Resultado de inspección a las 14:00 | No | Referencia posterior, si corresponde a la tarea y su calidad está comprobada |
| Consumo total de la jornada | No | Otra tarea o referencia posterior, según la formulación |

La información posterior puede aparecer en una base histórica para aprendizaje o evaluación. No debe presentarse como entrada conocida antes de su disponibilidad.

## Ejercicio 3 — Exactitud, costo y carga

| Propuesta | Aciertos | Exactitud | Cálculo del costo | Carga |
|---|---:|---:|---|---:|
| Ninguna alerta | 9/12 | 75 % | `3 × 5 + 0 × 1 = 15` | 0 |
| Consumo > 18 | 9/12 | 75 % | `0 × 5 + 3 × 1 = 3` | 6 |
| Consumo > 20 | 9/12 | 75 % | `1 × 5 + 2 × 1 = 7` | 4 |
| Consumo > 22 | 9/12 | 75 % | `2 × 5 + 1 × 1 = 11` | 2 |

La exactitud considera igual peso para cada acierto o error. La comparación de costos incorpora pesos diferentes para los dos tipos de error, y la capacidad introduce una restricción adicional. Por eso la métrica aislada no permite elegir una propuesta.

## Ejercicio 4 — Capacidad

- Capacidad 6: `> 18`, costo 3 y seis alertas.
- Capacidad 2: `> 22`, costo 11 y dos alertas.
- Capacidad 0: ninguna alerta, costo 15 y cero alertas.

Estos resultados identifican la candidata según el criterio del programa. Con capacidad 0 no se logra reducir omisiones; cumplir la capacidad no equivale a cumplir toda la necesidad. Para cualquiera de las propuestas queda pendiente evaluación independiente, acuerdo de criterios y comprobación del contexto real.

## Ejercicio 5 — Qué comprueba el programa

El texto `"true"` no es el booleano JSON `true`; el programa señala que la disponibilidad no está confirmada con el tipo esperado. Lo mismo ocurre con el número `1`.

Una frase no vacía como «quiero usar tecnología» puede pasar la validación del campo `problema`. El programa comprueba estructura, no la calidad semántica de la formulación.

Si alguien declara `true` para una entrada que llega después de la decisión, la estructura puede pasar aunque la declaración sea incorrecta. Se necesita evidencia del flujo de datos y revisión humana para detectar esa contradicción.

## Ejercicio 6 — Evaluación posterior

Primero se fija la política elegida y sus parámetros. Después se aplica sobre otros casos que no influyeron en esa elección, bajo las condiciones reales de disponibilidad. Se documentan etiquetas, errores, carga y funcionamiento del flujo humano.

Si la aplicación debe funcionar en jornadas posteriores, una evaluación temporal puede ser pertinente. Si se espera usarla en zonas o equipos nuevos, habrá que estudiar esa separación. Necesitamos identificadores, fechas, dependencia entre observaciones, procedencia de etiquetas y condiciones de captura.

Dividir al azar los doce casos ficticios no convierte el ejercicio en una validación real. El lote no contiene la evidencia temporal ni contextual necesaria.

## Ejercicio 7 — Otros costos

Con omisión 1 y revisión innecesaria 5:

| Propuesta | Cálculo | Costo | Cumple capacidad 4 |
|---|---|---:|---|
| Ninguna alerta | `3 × 1 + 0 × 5` | 3 | Sí |
| Consumo > 18 | `0 × 1 + 3 × 5` | 15 | No |
| Consumo > 20 | `1 × 1 + 2 × 5` | 11 | Sí |
| Consumo > 22 | `2 × 1 + 1 × 5` | 7 | Sí |

La candidata es ninguna alerta. La elección depende de los costos definidos; no prueba que omitir casos reales sea aceptable. La necesidad y las consecuencias deben acordarse antes de utilizar esos valores para decidir.

## Ejercicio 8 — Conclusión proporcional

Una conclusión apropiada: «Con los costos didácticos y la capacidad de cuatro del lote sintético, la regla `> 20` reduce el costo calculado de 15 a 7, aproximadamente 53,3 %. El ejercicio compara errores y carga; no mide ahorro energético ni demuestra eficacia en instalaciones reales».

Para afirmar ahorro habría que medir energía en condiciones comparables y estudiar otras explicaciones del cambio. Para aplicar la solución faltarían datos y criterios reales, permisos, evaluación independiente y un flujo operativo probado.

## Orientación para el reto

Usa la [ficha del caso trabajado](../datos/proyecto_ejemplo.json) para entender el formato, sin copiar sus cifras como hechos de tu proyecto.

La entrega debe hacer explícitas las incertidumbres. Por ejemplo:

| Decisión | Evidencia actual | Pendiente | Siguiente acción |
|---|---|---|---|
| Empezar por una regla | Puede ejecutarse con los campos disponibles | Si representa la prioridad del usuario | Acordar criterios y revisar casos |
| Mantener confirmación humana | El prototipo solo propone una selección | Tiempo y autoridad para revisar | Probar el flujo con la persona usuaria |
| Reservar evaluación posterior | El lote exploratorio influyó en la elección | Datos suficientes y separación pertinente | Obtener casos bajo un protocolo definido |

Una decisión de «recolectar evidencia antes de implementar» puede ser el resultado correcto. Debe indicar qué evidencia falta, por qué importa y cómo se obtendrá.

El verificador estructural ayuda a localizar campos faltantes; una salida sin errores no sustituye la rúbrica del reto ni demuestra viabilidad.

[Volver a la unidad](../README.md)

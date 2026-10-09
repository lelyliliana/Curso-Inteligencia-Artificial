# Unidad 2 — Del problema al proyecto de IA

[Unidad anterior: qué es la IA](../unidad01-que-es-ia/README.md) · [Volver al índice](../README.md)

«Quiero hacer algo con inteligencia artificial» expresa interés por una tecnología, pero todavía no define un proyecto. Para avanzar necesitamos una dificultad concreta, un usuario, una salida útil y una manera de comprobar si la propuesta mejora la situación.

En esta unidad transformarás una idea en una formulación que permita decidir el siguiente paso. Trabajaremos un caso sintético de revisión de consumo y dos programas: uno para revisar la estructura de la ficha y otro para comparar reglas según errores, costos y capacidad.

## Objetivos

Al terminar podrás:

- Formular una necesidad y separar evidencia, supuestos y decisiones.
- Delimitar contexto, usuario, unidad de análisis, instante de decisión y horizonte.
- Traducir una necesidad a una tarea y una salida evaluables.
- Verificar qué información estará disponible al usar la solución.
- Establecer una línea base y comparar alternativas.
- Relacionar métricas con consecuencias del error y restricciones operativas.
- Proponer un prototipo y un plan de evaluación independiente.
- Documentar decisiones, incertidumbres y criterios para continuar o detenerse.

## Antes de comenzar

Completa las unidades 0 y 1. Necesitas reconocer clasificación, entrenamiento, inferencia, evaluación y línea base.

Los programas usan únicamente la biblioteca estándar de Python y funcionan sin GPU ni servicios externos. Fueron verificados con Python 3.12.14 en Linux. Ejecuta los comandos desde la raíz del curso, con el entorno virtual activado.

Puedes elaborar la ficha sin programar. Los laboratorios añaden comprobaciones y comparaciones reproducibles; no sustituyen la conversación con usuarios ni la revisión de la evidencia.

## 1. Comenzar por una dificultad observable

Un problema explica qué sucede, a quién afecta, en qué contexto y por qué merece atención. Debe apoyarse en evidencia o reconocer expresamente lo que aún no está comprobado.

| Formulación inicial | Información que falta |
|---|---|
| «Usar IA para mejorar la educación» | Usuario, tarea, contexto y significado de mejorar |
| «Hacer un chatbot ambiental» | Necesidad, fuentes, preguntas y criterio de respuesta correcta |
| «Detectar todos los problemas de energía» | Tipo de problema, observaciones, alcance y consecuencias |
| «Priorizar doce registros con cuatro revisiones disponibles» | Criterio de prioridad, datos y comparación con el procedimiento actual |

La última frase empieza a identificar una decisión concreta. Todavía debe justificarse con datos y usuarios si el proyecto es real.

Las guías de formulación de Google distinguen comprender el problema, valorar si ML aporta una solución y definir resultados y criterios de éxito [1–3]. Aquí aplicaremos esa orientación mediante un caso propio y una ficha de trabajo.

### Evidencia, supuesto y decisión

- **Evidencia:** una observación o fuente que puede revisarse. Por ejemplo, tiempos registrados de atención.
- **Supuesto:** algo que esperamos, pero todavía debemos comprobar. Por ejemplo, que una lectura parcial permita anticipar la necesidad de revisión.
- **Decisión de diseño:** una elección acordada, como comenzar con un solo laboratorio o mantener confirmación humana.

Un supuesto escrito en una ficha no se convierte en evidencia. Si no conoces el tiempo actual de una tarea, registra esa ausencia y planea medirlo; no inventes un porcentaje de mejora.

## 2. Usuario, personas afectadas y decisión

El **usuario** opera o consulta la solución. Las **personas afectadas** pueden ser distintas: quien aparece en un registro, quien recibe una recomendación o quien depende de la decisión.

Una aplicación que prioriza solicitudes puede ser usada por un coordinador y afectar a quienes esperan atención. Evaluar solo la comodidad del coordinador no muestra todas las consecuencias.

Describe el trabajo actual y la decisión que el sistema apoyará:

> La persona operadora recibe un lote de registros a las 10:00 y necesita elegir hasta cuatro para revisión antes de las 14:00. El prototipo propone una selección y muestra las lecturas originales; la persona confirma qué revisar.

Este enunciado define un actor, un instante, una acción, un límite y una forma de supervisión. No autoriza desconectar equipos ni diagnosticar averías.

### Preguntas para la conversación inicial

1. ¿Cómo se realiza hoy la tarea y dónde aparece la dificultad?
2. ¿Qué información se consulta y cuándo llega?
3. ¿Qué salida sería útil para actuar?
4. ¿Qué error sería más grave y quién tendría que corregirlo?
5. ¿Qué casos deberían quedar fuera del prototipo?

Documenta las respuestas y sus fuentes. Una conversación puede identificar una necesidad sin demostrar todavía que un modelo sea la mejor solución.

## 3. Delimitar el alcance

Un alcance útil permite reconocer qué caso pertenece al proyecto y cuál no. Especifica entorno, periodo, entradas, salidas y restricciones.

| Dimensión | Ejemplo del caso sintético |
|---|---|
| Entorno | Un laboratorio ficticio |
| Unidad de análisis | Un registro de una zona durante una jornada |
| Instante de decisión | 10:00 de esa jornada |
| Entrada candidata | Consumo acumulado y recibido hasta las 10:00 |
| Salida | Propuesta revisar/no revisar |
| Horizonte operativo | Revisión antes de las 14:00 |
| Capacidad | Cuatro revisiones por lote |
| Exclusiones | Averías, desconexión y recomendaciones para instalaciones reales |

### Unidad de análisis

Es la entidad o evento sobre el que se forma una observación. Una fila podría representar una persona, un equipo, una lectura horaria o una jornada de una zona. Estas opciones no son intercambiables.

Si un mismo equipo aparece muchas veces, sus filas pueden compartir características. Dividirlas al azar puede colocar información muy semejante en ajuste y evaluación. Primero comprende qué representan los registros y qué relaciones existen.

### Horizonte

Indica cuánto tiempo hacia adelante interesa la salida o cuándo se utilizará. Predecir una situación de mañana y clasificar una observación actual requieren entradas, referencias y protocolos diferentes.

En nuestro ejemplo, la decisión se toma a las 10:00 y la acción debe ocurrir antes de las 14:00. Ese horario es una condición didáctica, no un estándar operativo.

## 4. Formular una salida comprobable

La pregunta «¿qué queremos mejorar?» no equivale todavía a «¿qué devolverá el programa?».

| Necesidad | Salida posible | Referencia o criterio |
|---|---|---|
| Estimar una cantidad | Número con unidad y horizonte | Cantidad observada posteriormente |
| Clasificar casos | Categoría definida | Etiqueta obtenida con un procedimiento acordado |
| Explorar perfiles semejantes | Grupos de observaciones | Utilidad y estabilidad según el contexto |
| Encontrar evidencia | Documentos o fragmentos | Relevancia revisada para una consulta |
| Redactar un informe | Texto estructurado | Rúbrica, fuentes y comprobación de afirmaciones |
| Programar recursos | Asignación o plan | Restricciones cumplidas y costo del plan |

Una salida debe tener significado, formato y uso. «El modelo entrega 0,8» es insuficiente: ¿es una probabilidad calibrada, una puntuación, una similitud o un valor normalizado? No llames probabilidad a cualquier número entre cero y uno.

### Etiqueta y decisión final

En el caso trabajado, `revision_referencia` es una etiqueta ficticia que permite comparar propuestas. No se observó una avería real. Tampoco asumimos que la etiqueta deba ejecutar automáticamente una acción.

En un proyecto real debes definir quién asigna la referencia, bajo qué criterio, con qué información y cómo se resuelven desacuerdos. «Ya existen decisiones históricas» no prueba que sean una referencia adecuada.

Para generación de texto, la referencia puede combinar evidencia documental y una rúbrica. No siempre existe una única frase correcta; sí pueden existir requisitos verificables sobre contenido, formato y respaldo.

## 5. Disponibilidad: qué se sabe al decidir

Una variable puede aparecer en la base histórica y estar ausente cuando se necesita producir una predicción.

| Dato | Momento en que se conoce | ¿Entrada a las 10:00? |
|---|---|---|
| Lectura recibida a las 09:59 | Antes de decidir | Puede ser candidata |
| Consumo total de toda la jornada | Al terminar la jornada | No para esa decisión |
| Resultado de una inspección a las 14:00 | Después de decidir | Puede servir como referencia; no como entrada disponible a las 10:00 |
| Lectura medida a las 09:50 pero recibida a las 11:00 | Después de decidir | No, aunque su medición sea anterior |

El momento de medición y el momento de recepción pueden diferir. Esa distinción importa cuando hay sensores, cargas de archivos o procesos manuales.

### Filtración de información

Hay filtración cuando el ajuste o la evaluación utiliza información que no corresponde al escenario legítimo de uso. Incluir el resultado posterior de la inspección como entrada para decidir antes de la inspección puede producir una evaluación engañosa.

La etiqueta posterior puede usarse para aprender o evaluar con datos históricos. El problema aparece al introducirla como si fuera una característica conocida en el momento de inferencia.

El programa de revisión de ficha comprueba una declaración `true` o `false`. No puede verificar por sí solo la realidad de un proceso de adquisición. La disponibilidad necesita evidencia adicional.

## 6. Comparar alternativas antes de elegir herramientas

Una solución convencional puede resolver la necesidad. Las reglas y la búsqueda pueden aportar estructura; un modelo aprendido puede aportar adaptación si existen datos apropiados. También puede justificarse una combinación.

La guía *Rules of Machine Learning* recomienda considerar una primera solución sin ML [4]. En el curso usaremos una línea base para estudiar qué mejora aporta una alternativa y qué costos añade.

### Una línea base pertinente

Debe representar una referencia clara: el procedimiento actual, una regla sencilla, una predicción constante o una decisión manual documentada.

En esta simulación utilizamos «no señalar casos» para comprender la exactitud bajo desbalance. También comparamos reglas de umbral. La primera referencia no es una recomendación operativa: en un proyecto real habría que incluir el procedimiento actual y justificar por qué cada comparación es pertinente.

Todas las alternativas deben recibir información disponible bajo las mismas condiciones. No compares una regla que solo recibe una lectura parcial con un modelo al que entregaste información de toda la jornada.

### Si no hay datos suficientes

Puedes reducir el alcance, probar reglas, medir el proceso actual, diseñar un protocolo de recolección o demostrar una interfaz con datos sintéticos. Cada opción produce evidencia distinta. Un prototipo de interfaz no demuestra capacidad predictiva.

## 7. Éxito del proyecto y métrica del modelo

El éxito del proyecto se relaciona con la tarea de las personas y sus restricciones. Una métrica resume una parte del comportamiento técnico.

| Nivel | Pregunta | Ejemplo |
|---|---|---|
| Necesidad | ¿La decisión mejora bajo condiciones acordadas? | Menos omisiones relevantes sin superar capacidad |
| Modelo o regla | ¿Qué errores produce? | Falsos positivos y falsos negativos |
| Operación | ¿Puede ejecutarse y revisarse? | Cuatro casos por lote y datos recibidos a tiempo |

Una mejora en exactitud puede no mejorar la tarea. Tampoco una reducción de tiempo justifica una tasa inaceptable de errores.

### Objetivos provisionales

Para el caso sintético definimos:

- Como máximo cuatro casos señalados por lote.
- Costo didáctico al menos 20 % menor que la línea base en una evaluación independiente.
- Ninguna acción física automática.

Son criterios elegidos para practicar la formulación. No fueron aprobados por usuarios reales ni constituyen criterios profesionales de gestión energética.

Define los objetivos antes de la evaluación final. Si cambias un objetivo al mirar los resultados, registra el cambio y considera ese conjunto como parte de la exploración, no como una prueba final que quedó intacta.

## 8. Entender las consecuencias del error

En una clasificación binaria llamaremos **positivo** a señalar un caso para revisión.

| Resultado | Predicción | Referencia | Interpretación del ejercicio |
|---|---:|---:|---|
| Verdadero positivo, TP | 1 | 1 | Se señala un caso relevante |
| Falso positivo, FP | 1 | 0 | Se propone una revisión innecesaria |
| Verdadero negativo, TN | 0 | 0 | No se señala un caso no relevante |
| Falso negativo, FN | 0 | 1 | Se omite un caso relevante |

La **exactitud** es `(TP + TN) / número de casos`. En este ejemplo un error de omisión y una revisión innecesaria no reciben el mismo peso.

Definimos un costo didáctico:

`costo = 5 × FN + 1 × FP`

Los coeficientes permiten comparar escenarios del ejercicio. No son dinero ni una valoración validada de afectaciones. En un proyecto real habría que acordar su significado y estudiar sensibilidad ante valores diferentes.

La carga de revisión es `TP + FP`. Una propuesta puede reducir el costo estimado y aun así generar más revisiones de las que la persona puede atender.

## 9. Caso trabajado: doce registros y cuatro revisiones

Los datos contienen tres casos con etiqueta 1 y nueve con etiqueta 0. Lee su [procedencia y diccionario](datos/README.md).

La regla «no señalar ninguno» acierta con los nueve casos negativos. Obtiene **75 % de exactitud**, aunque omite todos los casos positivos. Esta cifra demuestra por qué la métrica debe interpretarse junto con las consecuencias del error.

Comparamos tres umbrales definidos para el ejercicio:

| Propuesta | TP | FP | TN | FN | Exactitud | Costo | Casos señalados | Capacidad de cuatro |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Ninguna alerta | 0 | 0 | 9 | 3 | 75 % | 15 | 0 | Cumple |
| Consumo > 18 | 3 | 3 | 6 | 0 | 75 % | 3 | 6 | Excede |
| Consumo > 20 | 2 | 2 | 7 | 1 | 75 % | 7 | 4 | Cumple |
| Consumo > 22 | 1 | 1 | 8 | 2 | 75 % | 11 | 2 | Cumple |

Las cuatro propuestas tienen la misma exactitud. Sus errores y cargas son distintos.

La regla `> 18` tiene el menor costo, pero excede la capacidad. Si restringimos la comparación a propuestas que cumplen la capacidad, `> 20` tiene el menor costo: 7 frente a 15 de la línea base.

La reducción relativa es `(15 - 7) / 15`, aproximadamente **53,3 %**. Ese resultado es una comparación sobre el lote sintético. No satisface por sí solo el criterio de evaluación independiente definido para una aplicación real.

La selección tampoco recorta automáticamente las seis alertas de `> 18` a cuatro: hacerlo requeriría otra política de selección y una nueva evaluación. Aquí se declara la propuesta como excedida.

## 10. Primer laboratorio: revisar la ficha

Abre [proyecto_ejemplo.json](datos/proyecto_ejemplo.json) y el programa [01_revisar_ficha.py](ejemplos/01_revisar_ficha.py).

```bash
python unidad02-proyecto-ia/ejemplos/01_revisar_ficha.py
```

Salida esperada:

```text
Estructura completa y disponibilidad declarada para las variables.
Revisión humana pendiente: comprobar datos, permisos, métricas, viabilidad y supuestos.
```

El programa comprueba campos no vacíos, objetos, listas, nombres de variables y tipos de salida admitidos. Además requiere que la disponibilidad de cada variable esté declarada mediante el booleano JSON `true`.

No aprueba automáticamente el proyecto. Una descripción incorrecta pero no vacía puede pasar la comprobación estructural. El código no demuestra la calidad de una etiqueta, la legalidad de un permiso, la utilidad de una métrica ni la existencia de los datos.

### Cómo funciona

- `texto_valido` comprueba que exista una cadena con contenido.
- `revisar` acumula problemas para que puedan corregirse en una sola lectura.
- `main` lee el JSON, presenta el resultado y devuelve código de salida 2 si encuentra problemas.
- Las rutas predeterminadas se calculan a partir del archivo del programa.

En JSON, `true` es un booleano. `"true"` es un texto y `1` es un número: el programa no los acepta como equivalentes para confirmar la disponibilidad.

### Experimenta

1. Copia la ficha a otro archivo.
2. Añade como entrada `resultado_inspeccion_14h` y marca `disponible_en_decision` como `false`.
3. Ejecuta la revisión y explica el mensaje.
4. Cambia la declaración a `true` sin modificar el proceso real. ¿Qué puede y qué no puede comprobar el programa?

Ejemplo para una copia llamada `mi_proyecto.json` en la raíz:

```bash
python unidad02-proyecto-ia/ejemplos/01_revisar_ficha.py --ficha mi_proyecto.json
```

Solo marca una disponibilidad como confirmada si tienes evidencia. Una declaración modificada no hace que un dato posterior llegue antes.

## 11. Segundo laboratorio: comparar decisiones

Abre [02_comparar_decisiones.py](ejemplos/02_comparar_decisiones.py).

```bash
python unidad02-proyecto-ia/ejemplos/02_comparar_decisiones.py
```

El programa imprime la tabla del caso y termina con:

```text
Candidata por costo y capacidad en este lote: Consumo > 20 (costo 7).
Reducción de costo frente a ninguna alerta: 53.3%
Selección exploratoria: requiere otra evaluación independiente antes de aprobar una aplicación.
```

Los umbrales se definieron manualmente; este programa no entrena un modelo. Usa las etiquetas únicamente para evaluar las decisiones sobre el lote.

### Recorrido del programa

1. Lee el CSV y valida columnas, identificadores, consumos y etiquetas.
2. Aplica cada regla a la lectura disponible.
3. Cuenta TP, FP, TN y FN.
4. Calcula exactitud, costo y cantidad de alertas.
5. Selecciona la propuesta de menor costo entre las que cumplen la capacidad.

Si hay empate en costo, prefiere menos alertas; un empate adicional se resuelve por nombre. Esta política forma parte del ejemplo y debe documentarse si se cambia.

### Variar la capacidad

```bash
python unidad02-proyecto-ia/ejemplos/02_comparar_decisiones.py --capacidad 6
```

La regla `> 18` ahora cumple la capacidad y resulta candidata por costo. Cambió una restricción, no las lecturas ni las etiquetas.

Con capacidad 2:

```bash
python unidad02-proyecto-ia/ejemplos/02_comparar_decisiones.py --capacidad 2
```

La regla `> 22` resulta candidata, con costo 11. La capacidad limita las propuestas que se pueden considerar, aunque otras tengan menor costo calculado.

### Variar los costos

```bash
python unidad02-proyecto-ia/ejemplos/02_comparar_decisiones.py --costo-omision 1 --costo-innecesaria 5
```

En este escenario, «ninguna alerta» tiene menor costo entre las propuestas admisibles. Esto muestra dependencia de los supuestos; no justifica ignorar situaciones reales relevantes.

Si el costo de la línea base es cero, el programa informa que la reducción porcentual no está definida. Dividir por cero no produce una mejora válida.

### Experimenta

Antes de ejecutar, calcula la candidata con capacidad 0. Después analiza si una solución que señala cero casos satisface realmente la necesidad. Distingue cumplir un límite de capacidad de cumplir el conjunto de criterios del proyecto.

## 12. Prototipo, piloto y evaluación independiente

Un **prototipo** permite comprobar mecanismos e interfaces. Un **piloto** introduce una solución limitada en un contexto de uso y requiere acuerdos, seguimiento y criterios de detención. No basta con cambiar el nombre del archivo para pasar de uno al otro.

La comparación del laboratorio es exploratoria: observamos resultados y elegimos una regla candidata con el mismo lote. Para evaluar su comportamiento posterior debemos fijar la regla y usar casos que no hayan influido en esa elección.

En un proyecto real, el plan podría reservar jornadas posteriores y separar zonas o equipos según la dependencia entre registros. No hay una única partición correcta para todos los problemas.

### Qué medir además del resultado técnico

- Disponibilidad de las entradas a tiempo.
- Casos que requieren revisión y tiempo efectivo de atención.
- Motivos de corrección de una recomendación.
- Rendimiento en grupos o condiciones pertinentes.
- Fallos de formato, interrupciones y uso de la alternativa convencional.

No afirmes una mejora del tiempo de atención si solo contaste etiquetas. No afirmes ahorro energético si no mediste energía y condiciones comparables. Una métrica es evidencia de la variable medida, no de cualquier beneficio deseado.

## 13. Viabilidad y decisiones de continuación

La viabilidad combina varias dimensiones:

| Dimensión | Pregunta | Evidencia posible |
|---|---|---|
| Utilidad | ¿La salida apoya una tarea necesaria? | Revisión con usuarios y comparación del procedimiento |
| Datos | ¿Existen entradas y referencias adecuadas? | Muestra auditada, diccionario y procedencia |
| Técnica | ¿La solución puede ejecutarse en el entorno? | Práctica con recursos y tiempos registrados |
| Operación | ¿Se pueden revisar y corregir sus salidas? | Flujo y capacidad probados |
| Permisos | ¿El uso de datos y recursos está autorizado? | Evidencia y condiciones de uso |
| Evaluación | ¿Podemos comprobar la mejora y sus límites? | Protocolo independiente y criterios acordados |

Una puntuación agregada no debe ocultar una condición necesaria incumplida. Si una entrada no existe al decidir o no hay autorización para utilizarla, una buena métrica experimental no resuelve esa dificultad.

Posibles decisiones: continuar, recolectar evidencia, revisar etiquetas, reducir alcance, cambiar enfoque o detener el proyecto. Cada una debe tener motivo y siguiente acción verificable.

### Gestión de riesgos en contexto

El marco NIST AI RMF 1.0 propone funciones de gobierno, caracterización del contexto, medición y gestión [5]. Lo usamos como referencia para preguntar por efectos, responsabilidades y seguimiento; la ficha del curso no es una certificación ni una evaluación completa según ese marco.

Para el caso trabajado, el control es mostrar la lectura original, mantener confirmación humana, registrar correcciones y disponer de la alternativa convencional. En una aplicación real habría que comprobar que esa persona dispone de tiempo, información y autoridad para revisar.

## 14. Planificar hitos y conservar decisiones

Divide el proyecto en resultados observables:

| Hito | Entregable | Qué permite decidir |
|---|---|---|
| Comprensión | Ficha y evidencia del problema | Si la necesidad está delimitada |
| Datos | Diccionario, muestra y disponibilidad | Si las entradas y referencias son utilizables |
| Referencia | Línea base y protocolo | Con qué comparar |
| Prototipo | Ejecución reproducible e interfaz pequeña | Si el mecanismo funciona |
| Evaluación | Resultados, errores y límites | Si continuar o revisar la propuesta |
| Piloto, si corresponde | Flujo acordado y seguimiento | Si la solución funciona en contexto limitado |

Registra fecha, decisión, evidencia, motivo y asuntos pendientes. Si eliges otro umbral, deja escrito qué resultado o cambio de restricción lo motivó. No borres la diferencia entre lo que esperabas y lo que observaste.

## 15. Ejercicios

Intenta cada actividad antes de consultar [las soluciones](soluciones/README.md).

### Ejercicio 1 — Reformular

Convierte «quiero usar IA para mejorar un laboratorio» en un enunciado con usuario, tarea, dificultad, alcance y evidencia pendiente. Evita inventar cifras como si fueran observadas.

### Ejercicio 2 — Datos disponibles

Para una decisión a las 10:00 clasifica: lectura recibida a las 09:59; lectura medida a las 09:50 y recibida a las 11:00; resultado de inspección a las 14:00; consumo total de la jornada. Indica qué podría ser referencia y qué no puede ser entrada a tiempo.

### Ejercicio 3 — Misma métrica, distinta decisión

Recalcula exactitud, costo y carga para las cuatro propuestas del caso. Explica por qué 75 % no permite elegir por sí solo.

### Ejercicio 4 — Cambiar una restricción

Predice las candidatas para capacidad 6, 2 y 0. Comprueba con el programa. Explica qué criterios del proyecto seguirían pendientes.

### Ejercicio 5 — Límites del verificador

En una copia de la ficha sustituye el booleano `true` por el texto `"true"`. Después restaura el booleano y escribe como problema una frase no vacía que no describe una necesidad. Explica qué detecta el programa y qué necesita revisión humana.

### Ejercicio 6 — Protocolo de evaluación

El lote se utilizó para seleccionar `> 20`. Propón una evaluación posterior para un proyecto real. Explica cómo separarías casos y qué información necesitas para justificar esa separación.

### Ejercicio 7 — Sensibilidad de costos

Usa costo de omisión 1 y revisión innecesaria 5. Calcula los costos y la candidata. Explica por qué esa conclusión no autoriza una decisión real sin acordar el significado de los coeficientes.

### Ejercicio 8 — Conclusión proporcional

Corrige: «Como el costo cayó 53,3 %, el sistema ya ahorra energía y puede instalarse en todos los laboratorios». Indica qué se midió y qué faltaría comprobar.

## 16. Reto integrador — Ficha y decisión de viabilidad

Retoma la idea de la Unidad 1 o formula una nueva. Completa la [ficha en Markdown](plantillas/ficha_proyecto.md) y una copia de la [ficha JSON](plantillas/ficha_proyecto.json).

La plantilla JSON comienza vacía; el verificador debe señalar sus faltantes. Los tipos admitidos son `clasificacion`, `regresion`, `agrupamiento`, `recuperacion`, `generacion` y `planificacion`. En `referencia` describe la evidencia o el criterio apropiado para la tarea. No inventes etiquetas de clasificación si esa no es la tarea.

### Entregables

- Ficha con problema, usuario, alcance, instante de decisión y salida.
- Tabla de datos con disponibilidad, procedencia y permisos.
- Comparación de al menos dos enfoques y línea base justificada.
- Objetivos provisionales, consecuencias del error y restricciones.
- Plan de prototipo y evaluación con límites de la evidencia.
- Registro de decisiones y conclusión: continuar, recolectar evidencia, reducir alcance, cambiar enfoque o detener.

El proyecto puede ser individual o de hasta tres integrantes. Entrega un repositorio con README y enlaces accesibles. Para una actividad evaluable, añade un video de 3 a 5 minutos con cámara. Declara el uso de IA y explica cómo revisaste sus aportes.

### Rúbrica

| Criterio | Puntos |
|---|---:|
| Problema, usuario y alcance | 20 |
| Datos, referencia y disponibilidad temporal | 20 |
| Alternativas y línea base | 15 |
| Éxito, errores y restricciones | 20 |
| Prototipo y evaluación | 15 |
| Trazabilidad, límites y comunicación | 10 |

Una ficha bien justificada puede concluir que hace falta recolectar datos o que no se necesita ML. La evaluación valora la calidad de la formulación y sus evidencias.

## 17. Errores frecuentes

| Error | Cómo corregirlo |
|---|---|
| Elegir una herramienta como problema | Describir la tarea y la necesidad primero |
| Confundir datos existentes con datos disponibles | Verificar medición, recepción e instante de decisión |
| Usar la referencia posterior como entrada | Separar característica y etiqueta según su uso temporal |
| Comparar alternativas con información distinta | Definir el mismo escenario de uso |
| Optimizar solo exactitud | Revisar tipos de error, costos y restricciones |
| Recortar alertas sin reevaluar | Definir y evaluar la política de selección |
| Usar el lote de selección como prueba final | Reservar una evaluación que no influyó en la elección |
| Afirmar beneficios no medidos | Limitar la conclusión a variables y condiciones observadas |
| Interpretar una ficha completa como viabilidad | Comprobar evidencia, calidad y condiciones reales |
| Describir supervisión sin flujo | Definir quién revisa, qué ve y cómo corrige |

## Checklist

- [ ] Formulo una dificultad y señalo su evidencia o incertidumbre.
- [ ] Identifico usuario, decisión y personas afectadas.
- [ ] Defino unidad de análisis, instante y horizonte.
- [ ] Especifico salida y criterio de referencia.
- [ ] Verifico qué entradas llegan antes de decidir.
- [ ] Justifico una línea base y condiciones de comparación.
- [ ] Relaciono métricas con errores y restricciones.
- [ ] Diferencio selección exploratoria de evaluación final.
- [ ] Registro permisos, revisión humana y límites.
- [ ] Propongo una siguiente decisión con evidencia requerida.

## Resumen

La formulación conecta necesidad, usuario, datos, salida y evaluación. La ficha ayuda a organizar el proyecto; sus comprobaciones automáticas cubren solo estructura y declaraciones.

En el caso sintético, propuestas con 75 % de exactitud tuvieron costos y cargas diferentes. Con capacidad de cuatro y los costos elegidos, `> 20` resultó candidata exploratoria. Esa conclusión no prueba ahorro energético ni autoriza una aplicación real.

La siguiente unidad de la ruta estudia **matemática aplicada: vectores, matrices y optimización**. Consulta su disponibilidad en el índice.

## Referencias

Las guías siguientes sustentan la formulación y el enfoque de evaluación. Los casos, coeficientes, datos y programas son material educativo propio.

1. Google for Developers. *Introduction to Machine Learning Problem Framing*. [Curso oficial](https://developers.google.com/machine-learning/problem-framing/).
2. Google for Developers. *Understand the problem*. [Guía](https://developers.google.com/machine-learning/problem-framing/problem).
3. Google for Developers. *Framing an ML problem*. [Guía](https://developers.google.com/machine-learning/problem-framing/ml-framing).
4. Google for Developers. *Rules of Machine Learning*. [Guía](https://developers.google.com/machine-learning/guides/rules-of-ml/).
5. NIST (2023). *Artificial Intelligence Risk Management Framework, AI RMF 1.0*. [Documento](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf).

[Unidad anterior](../unidad01-que-es-ia/README.md) · [Volver al índice](../README.md)

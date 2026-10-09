# Unidad 1 — Qué es la inteligencia artificial

[Unidad anterior: preparación del entorno](../unidad00-entorno/README.md) · [Siguiente unidad: proyecto de IA](../unidad02-proyecto-ia/README.md) · [Volver al índice](../README.md)

Una aplicación calcula promedios. Otra reconoce imágenes. Una tercera responde preguntas sobre documentos. Las tres usan programas, pero no realizan el mismo tipo de trabajo ni necesitan la misma técnica.

Comprender la IA exige mirar dentro de la solución: qué tarea realiza, cómo obtiene su comportamiento, con qué datos trabaja y qué evidencia permite confiar en sus resultados. En esta unidad construirás ese vocabulario y experimentarás con ejemplos pequeños.

## Objetivos

Al terminar podrás:

- Explicar la relación entre IA, aprendizaje automático, aprendizaje profundo e IA generativa.
- Distinguir tareas, técnicas, modelos y aplicaciones.
- Diferenciar reglas definidas por personas y parámetros ajustados con datos.
- Reconocer entrenamiento, inferencia, evaluación y generalización.
- Identificar aprendizaje supervisado, no supervisado y por refuerzo.
- Explicar por qué generar contenido no garantiza que sea correcto.
- Proponer cuándo usar reglas, modelos aprendidos o una solución híbrida.
- Analizar una propuesta aplicada sin confundir una demostración con una validación real.

## Antes de comenzar

Completa la [Unidad 0](../unidad00-entorno/README.md). Activa su entorno virtual y abre una terminal en la raíz del curso.

Los ejemplos de esta unidad usan únicamente la biblioteca estándar de Python. No necesitan instalación de paquetes, internet, GPU ni una cuenta en un servicio de IA. Se verificaron con Python 3.12.14 en Linux.

Para estudiar los conceptos puedes comenzar por la lectura. Las prácticas usan listas, diccionarios, funciones y archivos JSON. Si necesitas nivelación, consulta el [Curso de Python](https://github.com/lelyliliana/Curso-Python).

## 1. Una definición para trabajar

La **inteligencia artificial** es un campo que estudia y construye sistemas capaces de realizar tareas como percibir, razonar, aprender, planificar o generar contenido para alcanzar objetivos. La referencia histórica de John McCarthy la presenta como una actividad científica y de ingeniería orientada a construir máquinas y programas inteligentes; no exige que cada mecanismo reproduzca la biología humana [1].

Para describir un sistema concreto resulta útil la formulación de la OCDE: se trata de un sistema basado en máquinas que, a partir de entradas y objetivos, obtiene salidas como predicciones, contenido, recomendaciones o decisiones que pueden influir en un entorno. Esta descripción también reconoce diferencias en autonomía y capacidad de adaptación [2].

En este curso no clasificaremos una herramienta únicamente por su nombre comercial. Preguntaremos qué mecanismo usa y cómo se evalúa. La frontera entre IA y otros programas depende de la definición y del contexto; encontrar una instrucción `if` o una salida de texto no resuelve esa clasificación.

### Ejemplo: tres soluciones al mismo problema

Queremos detectar consumos que merecen revisión.

| Solución | Cómo obtiene su comportamiento | Qué necesitamos comprobar |
|---|---|---|
| Regla fija | Una persona establece un umbral | Si la regla representa la necesidad y sus errores son aceptables |
| Clasificador aprendido | Un algoritmo ajusta parámetros con ejemplos etiquetados | Si generaliza y supera una línea base pertinente |
| Solución híbrida | Combina modelo, reglas y revisión humana | Si las partes se coordinan y la decisión final es justificable |

Las tres pueden ser útiles. Elegir una solución más compleja requiere una mejora que compense su costo y sus nuevas dificultades.

## 2. IA, aprendizaje automático y aprendizaje profundo

Estos términos describen relaciones entre enfoques. El aprendizaje automático forma parte de la IA; el aprendizaje profundo es una familia de métodos de aprendizaje automático [3].

| Término | Idea central | Ejemplo |
|---|---|---|
| IA | Resolver tareas de percepción, razonamiento, planificación u otras capacidades mediante sistemas computacionales | Buscar una ruta, inferir con reglas, clasificar imágenes |
| Aprendizaje automático, ML | Ajustar un comportamiento utilizando datos o experiencia | Aprender un límite para separar dos categorías |
| Aprendizaje profundo, DL | Aprender representaciones mediante redes neuronales con múltiples capas | Reconocimiento de imágenes con una red profunda |
| IA generativa | Producir contenido mediante modelos generativos | Crear texto, imágenes o audio |

La IA generativa describe una finalidad y una familia de modelos; no es un escalón que se añade al final de cualquier proyecto de ML. Las redes profundas pueden clasificar, predecir o generar. Existen modelos generativos probabilísticos que no son redes profundas.

Una aplicación puede combinar varios enfoques. Un asistente documental puede usar recuperación de información, un modelo generativo, reglas de permisos y validaciones convencionales.

### Pregunta para comprobar comprensión

¿Una red neuronal que clasifica una imagen como gato o perro es generativa?

La salida principal del ejemplo es una categoría. El hecho de utilizar aprendizaje profundo no convierte automáticamente su tarea en generación de imágenes.

## 3. IA simbólica: representar conocimiento y razonar

La IA también incluye enfoques que representan estados, relaciones, hechos y reglas, y aplican procedimientos de búsqueda o inferencia. No todos necesitan aprender sus parámetros a partir de ejemplos.

En una planificación sencilla podríamos representar aulas, horarios disponibles y restricciones. La tarea consiste en encontrar una asignación que cumpla las condiciones. En un sistema de conocimiento podríamos representar hechos y deducir conclusiones mediante reglas relacionadas.

### Una distinción necesaria

Este código aislado:

```python
consumo = 20
if consumo > 18:
    print("Revisar")
```

es una condición programada. Por sí solo no demuestra un sistema experto ni entrenamiento. Tampoco demuestra que una aplicación completa carezca de IA: un modelo aprendido puede usar esa condición para actuar sobre sus resultados.

Para estudiar una solución simbólica miraremos qué conocimiento representa, qué mecanismos de inferencia incorpora y cómo resuelve la tarea. En las unidades de búsqueda y reglas desarrollaremos esos mecanismos.

## 4. Aprendizaje automático: qué se aprende

Aprender, en este contexto, consiste en ajustar un modelo o una política utilizando datos o experiencia para una tarea. Ese ajuste puede mejorar su desempeño, pero la mejora debe medirse.

Un modelo no aprende la intención del proyecto solo por recibir un archivo. Alguien debe definir qué se busca, cómo se representan las entradas, qué señales se utilizan y qué cuenta como un error.

Supongamos que un ejemplo contiene:

```python
{"consumo_kwh": 17, "revision": 1}
```

- `consumo_kwh` es una **característica**: información disponible para producir una salida.
- `revision` es una **etiqueta**: la salida de referencia en el ejemplo supervisado.
- La etiqueta `1` significa revisar; `0` significa no revisar.

La calidad de las etiquetas importa. Si reflejan decisiones inconsistentes o sesgadas, el ajuste puede reproducir esos problemas. La existencia de un número en una columna no convierte esa etiqueta en una verdad indiscutible.

## 5. Tipos de aprendizaje

### 5.1 Supervisado

El entrenamiento utiliza entradas y salidas de referencia. Una tarea de **clasificación** predice categorías; una de **regresión** predice cantidades [4].

Ejemplos: clasificar mensajes por tema o estimar un consumo. En ambos casos hay que precisar cómo se obtuvieron las etiquetas o valores objetivo y si estaban disponibles de forma legítima.

### 5.2 No supervisado

Busca estructura en los datos sin una etiqueta objetivo asignada a cada caso para esa tarea. Puede agrupar observaciones, reducir dimensiones o describir distribuciones [5].

Agrupar consumos semejantes no informa por sí solo cuál grupo es eficiente, fraudulento o prioritario. La interpretación requiere conocimiento del contexto.

### 5.3 Por refuerzo

Un agente interactúa con un entorno mediante acciones y recibe recompensas. Aprende una política orientada a mejorar la recompensa acumulada [3].

No equivale a marcar respuestas correctas e incorrectas en una tabla. Importan las consecuencias de las acciones y la secuencia de decisiones. Una recompensa mal diseñada puede favorecer conductas que no cumplen la necesidad real.

### 5.4 Autosupervisado

La señal de entrenamiento se construye a partir de los propios datos, por ejemplo ocultando parte de una secuencia y prediciéndola. Esto permite trabajar sin etiquetas manuales para cada ejemplo, aunque sigue existiendo un objetivo de aprendizaje.

Estas categorías ayudan a describir el entrenamiento; no son compartimentos totalmente aislados. Una solución puede emplear varias etapas con distintos objetivos.

## 6. Entrenar, inferir y evaluar

Tres momentos se confunden con frecuencia:

| Momento | Pregunta | Ejemplo |
|---|---|---|
| Entrenamiento | ¿Qué parámetros se ajustan con los datos? | Elegir un umbral que reduzca errores en ejemplos etiquetados |
| Inferencia | ¿Qué salida produce el modelo con una entrada? | Aplicar el umbral a un consumo nuevo |
| Evaluación | ¿Cómo se compara esa salida con una referencia o criterio? | Contar errores en casos que no se usaron para ajustar |

Un modelo puede entrenarse una vez y ejecutar muchas inferencias. Una aplicación puede utilizar un modelo ya entrenado sin entrenarlo localmente.

Enviar una consulta a un servicio no significa necesariamente que sus parámetros se actualicen con esa consulta. La conservación de conversaciones, el uso como contexto y un proceso de entrenamiento son mecanismos distintos.

### Generalización

Es el comportamiento sobre casos distintos de los usados para ajustar el modelo. Un resultado perfecto en entrenamiento puede deberse a memorizar, a una tarea sencilla o a datos defectuosamente separados.

La evaluación debe representar el uso esperado: otros días, otras entidades o condiciones distintas, según el problema. Tener archivos con nombres `train` y `test` no garantiza una separación válida.

En este curso estudiaremos también validación para elegir configuraciones. Aquí mantendremos un ejemplo mínimo con un grupo de entrenamiento y otro de prueba, y un tercer grupo para observar un cambio deliberado de contexto.

## 7. Primer laboratorio: regla fija y umbral aprendido

### 7.1 Entender la pregunta

Queremos asignar una etiqueta de revisión a consumos ficticios. Compararemos:

- Regla fija: `consumo > 18`.
- Modelo sencillo: `consumo > umbral`, donde el umbral se elige a partir de entrenamiento.

Ambas soluciones terminan comparando un número. La diferencia está en la procedencia del parámetro: uno se escribe directamente; el otro se ajusta usando ejemplos.

Lee primero la [procedencia y el diccionario de los datos](datos/README.md).

### 7.2 Mirar los casos de entrenamiento

| Consumo ficticio | Etiqueta |
|---:|---:|
| 9 | 0 |
| 12 | 0 |
| 14 | 0 |
| 17 | 1 |
| 19 | 1 |
| 22 | 1 |

Hay una separación entre 14 y 17. Un umbral de 15,5 clasifica correctamente los seis casos de entrenamiento.

Eso no prueba que 15,5 sea un límite energético correcto. Es un parámetro que reproduce las etiquetas de este pequeño conjunto inventado.

### 7.3 Elegir candidatos y contar errores

El programa ordena los consumos y evalúa puntos medios entre valores consecutivos. Añade un umbral inferior al mínimo y otro igual al máximo para representar clasificar todos como revisión o ninguno como revisión.

Un candidato de 10,5 se equivoca con los consumos 12 y 14: los clasifica como revisión aunque sus etiquetas sean 0. Un candidato de 15,5 no se equivoca en entrenamiento.

El objetivo es minimizar el **número de clasificaciones incorrectas**. Si hay empate se elige el menor umbral candidato. Ese criterio es una decisión explícita del programa, no una propiedad universal del aprendizaje automático.

### 7.4 Ejecutar

Abre [01_regla_y_aprendizaje.py](ejemplos/01_regla_y_aprendizaje.py). Desde la raíz del curso:

```bash
python unidad01-que-es-ia/ejemplos/01_regla_y_aprendizaje.py
```

El umbral aprendido debe ser `15.50`. Los resúmenes incluyen:

```text
Regla fija: consumo > 18.00
Umbral aprendido: consumo > 15.50

Prueba (6 casos)
...
Regla fija: 5/6 aciertos; 1 error
Umbral aprendido: 6/6 aciertos; 0 errores

Cambio de contexto (6 casos)
...
Regla fija: 5/6 aciertos; 1 error
Umbral aprendido: 3/6 aciertos; 3 errores
```

Las tablas completas muestran las etiquetas y cada predicción. La regla fija falla en prueba con el consumo 17, cuya etiqueta es 1. El umbral aprendido lo clasifica como revisión.

### 7.5 Qué significa el cambio de contexto

En el tercer grupo cambió deliberadamente el criterio ficticio de revisión: consumos de 16, 18 y 21 están etiquetados como normales. El umbral aprendido con el primer criterio clasifica esos tres casos como revisión y se equivoca.

El programa no actualiza sus parámetros después de observar ese cambio. Obtener una entrada nueva es inferencia; volver a ajustar exige otro procedimiento.

Esto muestra un mecanismo de cambio en la relación entre entradas y etiquetas. No calcula un detector de cambio ni demuestra su frecuencia en un sistema real.

### 7.6 Entender las funciones

| Función | Responsabilidad |
|---|---|
| `validar_grupo` | Comprueba campos, consumos finitos y etiquetas permitidas |
| `cargar_datos` | Lee el JSON y valida sus tres grupos |
| `predecir` | Aplica el umbral a una observación |
| `contar_errores` | Compara predicciones y etiquetas |
| `ajustar_umbral` | Elige candidatos usando solo entrenamiento |
| `mostrar_resultados` | Muestra predicciones y recuentos sobre un grupo |

La llamada `ajustar_umbral(datos["entrenamiento"])` es importante: no recibe el grupo de prueba. Leer y validar todos los grupos no es lo mismo que utilizar sus etiquetas para aprender.

### Experimenta

1. Ejecuta con `--umbral-fijo 15.5`. Compara ambas soluciones cuando comparten el mismo parámetro.
2. Copia el JSON y cambia solo etiquetas del grupo `prueba`. El umbral aprendido debe permanecer igual; los recuentos de prueba pueden cambiar.
3. En otra copia, cambia la etiqueta de entrenamiento del consumo 14 de 0 a 1. Predice el nuevo umbral y compruébalo.

Para una copia situada en `unidad01-que-es-ia/datos/mis_casos.json`:

```bash
python unidad01-que-es-ia/ejemplos/01_regla_y_aprendizaje.py --datos unidad01-que-es-ia/datos/mis_casos.json
```

Conserva el archivo original. Cada modificación representa un experimento distinto y debe documentarse.

## 8. Qué resultados produce una aplicación de IA

Una salida puede servir a tareas distintas:

| Tarea | Entrada posible | Salida | Pregunta de evaluación |
|---|---|---|---|
| Clasificación | Mensaje | Categoría | ¿Qué categorías confunde? |
| Regresión | Historial y variables disponibles | Cantidad estimada | ¿Cuál es el error y en qué condiciones aumenta? |
| Agrupamiento | Descripciones de observaciones | Grupos | ¿Son útiles y estables para la necesidad? |
| Recuperación | Consulta y corpus | Documentos relevantes | ¿Encuentra la evidencia necesaria? |
| Generación | Instrucción y contexto | Texto, imagen o audio | ¿Cumple criterios y qué parte se puede verificar? |
| Planificación | Estado, objetivo y restricciones | Secuencia de acciones | ¿Cumple las restricciones y alcanza el objetivo? |

La técnica no identifica automáticamente la tarea. Un modelo de lenguaje puede clasificar o extraer información, además de generar respuestas abiertas. La evaluación debe corresponder a la aplicación concreta.

## 9. IA generativa y modelos de lenguaje

Un modelo generativo produce contenido a partir de lo aprendido y de la entrada recibida. Un modelo de lenguaje trabaja con representaciones de secuencias; algunos están entrenados para predecir el siguiente token y se utilizan para generar texto progresivamente [6].

Un **token** es una unidad de representación: puede corresponder a una palabra, parte de ella, un signo u otra unidad según el tokenizador. No equivale necesariamente a una palabra completa.

La entrada disponible se denomina **contexto**. Puede incluir instrucciones, conversación y documentos recuperados. El modelo puede producir una respuesta plausible que no esté sustentada por evidencia: en la aplicación hay que comprobar afirmaciones, referencias y adecuación al problema.

Un documento recuperado tampoco garantiza una respuesta correcta. Se puede recuperar el fragmento equivocado, omitir una condición o producir una conclusión que el documento no respalda. RAG combina recuperación y generación; su evaluación debe revisar ambas partes.

El curso profundiza en estos mecanismos después de los fundamentos de datos y evaluación. En esta unidad basta con distinguir generación, verificación y acceso a fuentes.

## 10. Segundo laboratorio: generar texto sin entrenar un modelo

El ejemplo [02_generacion_por_plantillas.py](ejemplos/02_generacion_por_plantillas.py) combina elementos de tres listas: comienzos, temas y cierres.

```bash
python unidad01-que-es-ia/ejemplos/02_generacion_por_plantillas.py
```

Produce frases como:

```text
El proyecto puede analizar consumos energéticos con datos sintéticos.
```

Las frases se seleccionan de forma pseudoaleatoria, pero todas sus partes fueron escritas de antemano. No existe un corpus de entrenamiento, una red neuronal ni un proceso que aprenda las relaciones del lenguaje.

El programa **genera texto en el sentido de producir una salida**. En este ejercicio lo describimos como combinación de plantillas, y no como evidencia de un modelo generativo aprendido.

### Aleatoriedad y aprendizaje son diferentes

La función `random.Random(seed)` crea un generador local. La semilla establece su estado inicial. Repetir el programa con los mismos parámetros en el entorno verificado permite comparar la misma secuencia.

```bash
python unidad01-que-es-ia/ejemplos/02_generacion_por_plantillas.py --seed 42 --cantidad 4
```

```bash
python unidad01-que-es-ia/ejemplos/02_generacion_por_plantillas.py --seed 43 --cantidad 4
```

Una salida variable no demuestra aprendizaje. Del mismo modo, un modelo aprendido puede producir una salida determinista cuando su configuración y procedimiento lo permiten.

### Experimenta

Calcula cuántas combinaciones distintas admite el programa con tres elementos en cada lista. Agrega un tema y calcula la nueva cantidad. Explica por qué aumentar la diversidad de frases no cambia el mecanismo de construcción.

## 11. Modelo, aplicación, agente y automatización

| Concepto | Qué describe | Ejemplo |
|---|---|---|
| Modelo | Representación o mecanismo usado para producir salidas | Clasificador ajustado con datos |
| Aplicación | Producto que integra datos, interfaz, lógica y operación | Portal que muestra alertas y permite revisarlas |
| Agente | Sistema que observa y actúa para alcanzar objetivos | Sistema que elige herramientas dentro de límites definidos |
| Automatización | Ejecución programada de acciones | Exportar un reporte cada viernes |

En la tradición de IA, los agentes no se limitan a los basados en modelos de lenguaje. En las aplicaciones contemporáneas, un flujo con herramientas puede incorporar un LLM; esa es una posibilidad de arquitectura.

La memoria de una aplicación puede ser una base de datos o contexto conservado. Guardar una conversación no equivale a actualizar los pesos de un modelo.

**Autonomía** describe cuánto puede ejecutar el sistema dentro de sus límites. No elimina la responsabilidad de quienes lo diseñan y operan. Para una misma tarea se puede automatizar la preparación del informe y mantener una decisión final humana.

Un chatbot también es una interfaz. Puede responder con reglas, consultar una base de datos, invocar un modelo o combinar esos mecanismos. Su apariencia no determina su arquitectura.

## 12. Una breve perspectiva histórica

Dos referencias ayudan a ubicar el campo:

| Momento | Aporte | Qué muestra |
|---|---|---|
| Propuesta de Dartmouth, 1955; encuentro en 1956 | Formalización de un programa de investigación con el nombre inteligencia artificial [7] | El campo es anterior a las aplicaciones de chat actuales |
| Transformer, 2017 | Arquitectura basada en atención presentada por Vaswani y colaboradores [8] | Un avance técnico concreto dentro de una historia más amplia |

Entre esos momentos y después de ellos coexistieron búsqueda, sistemas de conocimiento, métodos estadísticos y redes neuronales. Un enfoque nuevo no vuelve inútiles todos los anteriores.

**IA general** o AGI se utiliza para discutir capacidades amplias entre tareas y contextos. Sus definiciones y criterios varían. En este curso describiremos capacidades y resultados observables, sin deducir inteligencia general, conciencia o confiabilidad global a partir de una conversación convincente.

## 13. Elegir una solución para un problema aplicado

Antes de elegir una herramienta, contesta:

1. ¿Quién tiene la necesidad y qué tarea requiere apoyo?
2. ¿Qué entradas están disponibles en el momento de uso?
3. ¿Qué salida serviría y quién la utilizará?
4. ¿Podemos resolverlo con una regla o procedimiento convencional?
5. ¿Tenemos datos y referencias suficientes para aprender y evaluar?
6. ¿Qué errores serían más costosos y cómo se detectarán?

### Caso A: recordatorios de tutorías

Un calendario contiene las fechas confirmadas y queremos enviar un aviso antes de cada encuentro. Un procedimiento programado puede ser suficiente. Incorporar aprendizaje automático no aporta automáticamente una mejora.

### Caso B: clasificar mensajes por temática

Las categorías están definidas y hay ejemplos revisados. Puede estudiarse un clasificador supervisado. Harán falta criterios para mensajes ambiguos, clases poco frecuentes y casos desconocidos.

### Caso C: localizar evidencia en documentos

Se necesita encontrar el fragmento que responde una consulta. La recuperación de información es una alternativa inicial. Si se añade generación, hay que verificar que las respuestas mantengan el contenido de las fuentes y permitan rastrearlo.

### Caso D: priorizar registros ambientales

Algunos criterios son normativos o provienen de conocimiento experto; otros podrían estimarse con datos. Una solución híbrida puede separar reglas explícitas, estimaciones y decisión humana. El modelo no debe inventar criterios de intervención a partir de etiquetas cuya procedencia se desconoce.

Estas son propuestas de diseño, no afirmaciones de eficacia de sistemas desplegados.

## 14. Límites que debemos comprobar

Un sistema puede funcionar en una demostración y fallar en uso real por motivos diferentes:

- Las entradas cambian de escala, formato, población o significado.
- Las etiquetas tienen errores o representan un criterio inadecuado.
- Se utilizó información que no estará disponible cuando se necesite predecir.
- La métrica promedio oculta errores relevantes para un grupo.
- La respuesta generada contiene una afirmación sin evidencia.
- La aplicación combina mal una salida correcta con una acción posterior.

Cada problema requiere evidencia distinta. En el primer laboratorio comprobamos un cambio de criterio ficticio; no demostramos todos estos riesgos con el mismo archivo.

La supervisión humana necesita un procedimiento: quién revisa, con qué información, cómo puede corregir y qué casos detienen el flujo. La frase «lo revisa una persona» no describe por sí sola un control suficiente.

## 15. Ejercicios

Consulta [las soluciones](soluciones/README.md) después de intentar cada actividad.

### Ejercicio 1 — Describir con precisión

Escribe una definición propia de IA, ML, DL e IA generativa. Agrega un ejemplo y explica las relaciones entre los términos. Evita usar el nombre de una aplicación como definición.

### Ejercicio 2 — Tarea y mecanismo

Para cada caso indica la tarea, un mecanismo posible y una evidencia que necesitas:

- Calcular promedios de notas.
- Clasificar imágenes de hojas en categorías revisadas.
- Buscar una ruta respetando obstáculos.
- Redactar una explicación usando documentos institucionales.
- Ejecutar un respaldo a una hora fija.

### Ejercicio 3 — Localizar el aprendizaje

Identifica en el primer programa dónde están las características, etiquetas, candidatos, entrenamiento, inferencia y evaluación. Explica qué dato del grupo de prueba se utiliza para ajustar el umbral.

### Ejercicio 4 — Cambiar una etiqueta

En una copia del JSON cambia a 1 la etiqueta de entrenamiento del consumo 14. Predice el umbral y cuenta sus errores en el grupo de prueba original. Ejecuta y compara.

### Ejercicio 5 — Detectar una conclusión inválida

Analiza: «El modelo obtuvo seis aciertos de seis; por tanto, detectará correctamente todos los consumos anormales en cualquier instalación». Identifica qué evidencia falta y reescribe la afirmación.

### Ejercicio 6 — Plantillas y diversidad

Calcula las combinaciones del segundo ejemplo. Explica qué cambiaría si se agregan dos temas. ¿Se ha entrenado un modelo por esa modificación?

### Ejercicio 7 — Entrenamiento y contexto

Una aplicación conserva una conversación en una base de datos y la incluye en una consulta posterior. Explica qué podemos afirmar sobre su memoria y qué no podemos concluir sobre el entrenamiento del modelo.

## 16. Reto aplicado — Analizar una idea de IA

Escoge un problema sencillo de educación, energía, información ambiental u otro contexto que conozcas. Completa la [ficha del reto](reto.md).

Debe incluir necesidad, usuario, entradas disponibles, salida, alternativa sin IA, enfoque propuesto, forma de evaluación, límites y revisión humana. Justifica la propuesta; no necesitas desarrollar un modelo en este reto.

El trabajo puede ser individual o en equipos de hasta tres integrantes. Si utilizas herramientas de IA para elaborar el texto, declara el uso y verifica sus afirmaciones y referencias.

### Entregables

- Ficha del problema en el README de un repositorio o documento accesible mediante enlace.
- Comparación de al menos dos enfoques, incluyendo una alternativa convencional.
- Evidencia pequeña de la idea: ejemplo de entrada y salida, dibujo o prototipo sencillo claramente identificado.
- Para una entrega evaluable, video de 3 a 5 minutos con cámara, explicando la decisión y sus límites.

### Rúbrica

| Criterio | Puntos |
|---|---:|
| Necesidad, usuario y alcance claros | 20 |
| Entradas, salida y disponibilidad de datos | 20 |
| Comparación y justificación de enfoques | 25 |
| Criterio de evaluación y tipos de error | 20 |
| Límites, revisión humana y comunicación | 15 |

Una propuesta puede obtener una buena valoración si concluye que la necesidad se resuelve mejor con una solución convencional. La calidad está en la justificación y la evidencia.

## 17. Errores frecuentes

| Confusión | Corrección |
|---|---|
| IA significa chatbot | El chat es una interfaz; existen muchas tareas y enfoques |
| Toda condición es un sistema experto | Hay que examinar representación e inferencia de la solución completa |
| Toda IA aprende de datos | Los enfoques simbólicos pueden trabajar con conocimiento y búsqueda |
| Todo modelo profundo es generativo | También existen tareas de clasificación y regresión |
| Inferir es volver a entrenar | Aplicar parámetros y ajustarlos son procedimientos diferentes |
| Más datos garantizan mejora | Importan calidad, cobertura, objetivo y forma de evaluación |
| Seis aciertos prueban eficacia universal | La conclusión debe limitarse al conjunto y protocolo usados |
| Aleatoriedad demuestra aprendizaje | La variación puede provenir de un generador pseudoaleatorio |
| Una respuesta fluida está verificada | Hay que contrastar afirmaciones y fuentes |
| Guardar conversaciones modifica pesos | Persistencia, contexto y entrenamiento son mecanismos distintos |

## Checklist

- [ ] Distingo IA, ML, DL e IA generativa con ejemplos.
- [ ] Reconozco que reglas y búsqueda también pueden formar parte de la IA.
- [ ] Diferencio tarea, modelo, aplicación y agente.
- [ ] Identifico características y etiquetas en el JSON.
- [ ] Explico por qué el umbral se ajusta solo con entrenamiento.
- [ ] Interpreto los resultados sobre prueba y cambio de contexto.
- [ ] Distingo generación por plantillas de un modelo de lenguaje aprendido.
- [ ] Explico qué no demuestra una salida correcta o convincente.
- [ ] Comparo una idea de IA con una alternativa convencional.
- [ ] Defino cómo revisar los resultados de mi propuesta.

## Resumen

La IA reúne diferentes enfoques y tareas. En los ejemplos observaste un parámetro escrito, un parámetro ajustado con datos y texto producido con plantillas. También comprobaste que un ajuste correcto sobre casos sintéticos puede perder utilidad cuando cambia el criterio del problema.

Continúa con la [Unidad 2 — Del problema al proyecto de IA](../unidad02-proyecto-ia/README.md).

## Referencias

Estas fuentes fundamentan las definiciones y los hitos. Los casos, datos y prácticas son ejemplos educativos elaborados para el curso.

1. McCarthy, J. *What is artificial intelligence?* [Preguntas básicas](https://www-formal.stanford.edu/jmc/whatisai/node1.html).
2. OECD (2024). *Explanatory memorandum on the updated OECD definition of an AI system*. [Documento](https://doi.org/10.1787/623da898-en). Para una explicación accesible de su alcance: [OECD.AI](https://oecd.ai/en/wonk/definition).
3. Stanford HAI (2022). *Brief Definitions of Key Terms in AI*. [Definiciones](https://hai.stanford.edu/policy/brief-definitions-of-key-terms-in-ai).
4. scikit-learn. *Supervised learning*. [Guía oficial](https://scikit-learn.org/stable/supervised_learning.html).
5. scikit-learn. *Unsupervised learning*. [Guía oficial](https://scikit-learn.org/stable/unsupervised_learning.html).
6. Hugging Face. *LLM Course*. [Introducción](https://huggingface.co/learn/llm-course/chapter1/1).
7. McCarthy, J., Minsky, M., Rochester, N. y Shannon, C. (1955). *A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence*. [Propuesta original](https://www-formal.stanford.edu/jmc/history/dartmouth/dartmouth.html).
8. Vaswani, A. et al. (2017). *Attention Is All You Need*. [Artículo](https://arxiv.org/abs/1706.03762).

[Unidad anterior](../unidad00-entorno/README.md) · [Siguiente unidad: proyecto de IA](../unidad02-proyecto-ia/README.md) · [Volver al índice](../README.md)

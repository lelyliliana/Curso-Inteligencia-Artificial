# Unidad 29 — RAG con documentos

[Índice del curso](../README.md) · [Unidad anterior](../unidad28-embeddings-busqueda/README.md)

**Pregunta guía:** ¿cómo responder con documentos recuperados, mostrar las fuentes y reconocer cuándo la evidencia no alcanza?

La Unidad 28 recuperaba candidatos. Ahora conectamos esa búsqueda con un generador y evaluamos la respuesta completa. El caso central tiene dos agendas vigentes: una indica 09:00 y otra 11:00. Si el modelo recibe solo la primera, puede citarla correctamente y aun así ocultar un conflicto importante. Una cita válida no garantiza una respuesta suficiente.

Usaremos doce documentos ficticios nuevos, 24 fragmentos y veinte preguntas por familias. BGE-M3 representa textos y Qwen3 genera respuestas en CPU. Las prácticas predeterminadas reutilizan capturas reales y funcionan sin Internet, Ollama ni descarga de pesos. La respuesta generada se limita a un **dato breve, estado y citas** para poder evaluar su apoyo con referencias explícitas; no se presenta un verificador universal de respuestas abiertas.

## Objetivos y preparación

Al terminar podrás:

1. Diferenciar extracción, fragmentación, recuperación, construcción de contexto y generación.
2. Conservar procedencia hasta el texto original y comprobar presupuestos de contexto.
3. Distinguir una cita existente, una afirmación apoyada y una respuesta suficiente para la pregunta.
4. Evaluar por separado pérdida de evidencia, dato ausente y conflicto entre fuentes.
5. Comparar una referencia extractiva con un RAG y congelar una configuración antes del cierre.
6. Reconocer que los documentos recuperados pueden contener instrucciones no confiables.

Prerrequisitos: JSON y funciones de Python; [inferencia local](../unidad26-inferencia-servicios/README.md), [validación de salidas](../unidad27-prompts-evaluacion/README.md) y [embeddings y búsqueda](../unidad28-embeddings-busqueda/README.md). Tiempo orientativo: 4–6 horas para lectura, prácticas y ejercicios; el reto requiere trabajo adicional.

## 1. Qué añade RAG

RAG combina recuperación de información y generación condicionada por esa información. En esta práctica, el generador recibe la pregunta y unos fragmentos concretos; no consulta por sí solo todos los archivos. Puede usar esos textos para producir una respuesta, pero todavía puede omitir, interpretar mal o inventar.

El trabajo de Lewis y colaboradores estudió modelos que combinan memoria paramétrica y recuperación de pasajes para tareas de lenguaje. Nuestra implementación didáctica utiliza un flujo de recuperación y generación con modelos preentrenados, sin reproducir su entrenamiento conjunto ni sus resultados. [Artículo de referencia sobre RAG](https://arxiv.org/abs/2005.11401)

```mermaid
flowchart LR
    A[TXT y manifiesto] --> B[Párrafos con procedencia]
    B --> C[Embeddings e índice]
    Q[Pregunta] --> E[Embedding de consulta]
    C --> R[Recuperación exacta]
    E --> R
    R --> K[Contexto con presupuesto]
    Q --> G[Generador local]
    K --> G
    G --> S[Estado, dato y citas]
    S --> V[Validación y evaluación]
    B --> V
```

El índice se prepara una vez para una versión del corpus. Por cada consulta se calcula su vector, se buscan vecinos y se construye el contexto. El generador no modifica los pesos del codificador ni los suyos durante este proceso. Cambiar documentos exige actualizar el índice; cambiar el prompt exige volver a evaluar las respuestas. Añadir documentos no equivale a entrenar.

RAG puede facilitar actualizaciones y procedencia, pero su éxito depende de todos los pasos. Si la extracción pierde una negación, si la recuperación omite una fuente o si el modelo ignora una contradicción, la respuesta puede fallar aunque otros componentes funcionen.

## 2. Documentos, fragmentos y procedencia

Los [datos](datos/README.md) describen centros, salas y sensores ficticios. El [manifiesto](datos/manifiesto.json) fija ID, título, versión y ruta. Cada TXT tiene dos párrafos separados por una línea vacía. Aquí cada párrafo es un fragmento; no hay solapamiento.

Ejemplo de [D01](datos/documentos/D01.txt):

```text
El plazo de préstamo del Centro Nácar es de 9 días.

Para renovar un préstamo del Centro Nácar debes acudir al mostrador con el comprobante.
```

El primer párrafo se identifica como `D01:p01`, línea 1, y el segundo como `D01:p02`, línea 3. El fragmento guarda título, versión, ruta, líneas, posiciones `[inicio, fin)` y texto exacto. Los offsets se refieren a caracteres de la cadena decodificada, no a bytes. La huella del texto completo usa JSON canónico; el manifiesto de huellas conserva además el hash de bytes de cada archivo fuente.

Así podemos volver de una cita al párrafo y de ese párrafo a la versión original. Un ID inventado no tiene fuente; un ID de otra versión puede apuntar a un contenido distinto. Las huellas detectan cambios accidentales, pero no autentican un conjunto de archivos modificado deliberadamente de forma coordinada.

### Elegir la fragmentación

Un fragmento muy pequeño puede perder sujeto, negación o condición. Uno demasiado grande puede ocupar el contexto con información irrelevante. El solapamiento conserva continuidad entre cortes, pero aumenta redundancia y puede inflar métricas si se cuentan duplicados como evidencias independientes.

Aquí se usa el párrafo porque las fuentes son cortas y autocontenidas. Si excede 600 caracteres, se rechaza para revisar la preparación; no se corta silenciosamente. Esto es una decisión de esta colección, no una recomendación universal de tamaño. En documentos reales habría que evaluar títulos, tablas, listas, secciones, unidades y referencias cruzadas.

Los TXT ya son texto legible. No se implementan OCR ni extracción de PDF. Esos formatos añaden otro punto de fallo: antes de generar embeddings, hay que comparar el texto extraído con el documento visible. Un RAG no recupera un dato que se perdió al extraerlo.

## 3. Laboratorio 1 — Preparar fuentes y contexto

Desde la raíz del repositorio:

```bash
python unidad29-rag-documentos/ejemplos/01_preparar_documentos.py
python unidad29-rag-documentos/ejemplos/01_preparar_documentos.py --salida resultados/u29-preparacion
```

Salida principal:

```text
Documentos: 12; fragmentos: 24; texto original conservado.
Ranking artificial para mostrar presupuesto; no es búsqueda medida.
Contexto habitual: 3; con 300 caracteres: 1.
```

Revisa [el programa](ejemplos/01_preparar_documentos.py), los [fragmentos exportados](recursos/preparacion/fragmentos.json) y el [diagnóstico de presupuesto](recursos/preparacion/presupuesto.json). El orden del laboratorio es artificial: D01:p01, D01:p02, D02:p01, con puntuaciones elegidas para la demostración. No se atribuye ese orden a BGE-M3.

La construcción de contexto conserva un prefijo del ranking: añade cada fragmento completo mientras quepa. Al encontrar uno que no cabe, se detiene y registra los omitidos. La serialización JSON incluye IDs, títulos, versión y líneas; esos metadatos también ocupan espacio. El límite habitual es 2200 caracteres. Con 300 cabe únicamente el primer fragmento.

**Caracteres no son tokens.** El límite de caracteres es un control reproducible de preparación, no una medida exacta del contexto del modelo. Para generar solicitamos 4096 tokens de contexto y reservamos 160 de salida. Comprobamos además que los tokens de entrada reportados más esa reserva no excedan 4096; es un control posterior y no reemplaza una tokenización previa ni demuestra por sí solo ausencia de truncamiento en cualquier motor.

## 4. Recuperar y construir una respuesta acotada

Se representa `titulo + "\n" + texto` con BGE-M3, sin prefijos, y se normalizan los vectores. El vector de consulta representa únicamente su pregunta. Se reutilizan geometría y transporte de las unidades anteriores, pero **se recalculan los embeddings para documentos y preguntas nuevos**. El índice anterior no se reutiliza como evidencia de esta unidad.

La búsqueda es exacta por coseno y desempata por ID ascendente, sin umbral. Se comparan k=1 y k=3; el generador y sus instrucciones son iguales. Un k mayor puede recuperar una fuente omitida, pero también añade distracciones, costo y texto no confiable. No siempre mejora la respuesta.

El [prompt del sistema](prompts/sistema.txt) pide utilizar solo los hechos del contexto y rechazar órdenes contenidas en documentos. La pregunta, los fragmentos y el esquema se envían en un JSON separado de las instrucciones del sistema. Ni el catálogo de evidencias ni la respuesta esperada entran en ese prompt.

El [contrato](datos/esquema.json) tiene tres campos:

| Estado | `dato` | `citas` | Significado |
|---|---|---|---|
| `ok` | Valor mínimo literal con unidad | Al menos un ID de apoyo | Hay un valor respaldado para la pregunta |
| `ausente` | `null` | `[]` | El contexto no permite obtener el dato |
| `conflicto` | `null` | IDs de alternativas incompatibles | Las fuentes recibidas contradicen el dato solicitado |

Ejemplo: `{"estado":"ok","dato":"9 días","citas":["D01:p01"]}`. En conflicto no se pide al modelo inventar una conciliación. En ausencia no debe completar desde memoria. El esquema aplicado por Ollama ayuda a restringir la forma, pero no demuestra la verdad del dato. [Salidas estructuradas](https://docs.ollama.com/capabilities/structured-outputs)

Una respuesta abierta podría tener varias afirmaciones, matices y citas por oración. Este contrato más pequeño permite verificar de forma transparente un dato por pregunta. El evaluador tolera mayúsculas y espacios, pero no resuelve sinónimos, conversiones de unidades o equivalencias generales: «nueve días» no equivale automáticamente a «9 días» para este programa.

## 5. Qué comprueba la evaluación

Cada pregunta tiene un catálogo de evidencias escrito antes de inferir: fragmentos y valores que sí responden a esa pregunta. Cero valores implica ausencia; uno distinto implica un dato único; dos distintos implican conflicto. La anotación se hizo por lectura de la colección y no mediante otro modelo evaluador.

| Capa | Comprobación | Lo que todavía puede fallar |
|---|---|---|
| Transporte | Contrato de API y parada normal | JSON o contenido incorrecto |
| Forma/coherencia | Campos, tipos y relación estado/dato/citas | Dato falso con forma perfecta |
| Pertenencia de citas | Todos los IDs estaban en el contexto enviado | La fuente no respalda la afirmación |
| Apoyo factual | El catálogo respalda ese dato mediante las fuentes citadas | Otra fuente relevante omitida cambia la conclusión |
| Objetivo y cobertura | Coincide con el estado del corpus y están todas las alternativas necesarias | Límites del catálogo y de esta muestra |

**Aceptada** requiere parada normal, forma, citas válidas, apoyo, objetivo correcto y contexto suficiente. Si se produjo un error HTTP, sigue contando como intento fallido; no se elimina del denominador. El campo de fallo principal ayuda a resumir, pero hay que leer las demás capas: una respuesta puede fallar tanto por recuperación como por generación.

Para ocho consultas por fase con evidencias, calculamos:

```text
Recall de fragmentos = fragmentos de evidencia presentes / fragmentos de evidencia anotados
Cobertura suficiente = todos los valores necesarios aparecen en el contexto
Aceptación = respuestas aceptadas / todos los intentos
```

Los dos casos sin dato por fase no entran en el promedio de recall; se evalúan como abstención. Su contexto se marca suficiente **según el catálogo** porque no falta ningún valor anotado. Esto no demuestra ausencia global en un corpus desconocido. También se cuenta cuántas familias tienen ambas formulaciones aceptadas; esas paráfrasis no son muestras independientes para inferir incertidumbre.

Las tasas de citas se informan solo entre salidas con citas. Un array vacío puede ser correcto en `ausente`, pero no debe inflar una supuesta precisión de citas. Una coincidencia literal dentro del documento tampoco basta: hay que relacionar el texto con la pregunta y distinguir hechos de instrucciones incrustadas.

### Referencia extractiva

Antes de generar, la referencia muestra el primer fragmento literal y su ID. No usa etiquetas para decidir qué copiar, no sintetiza, no se abstiene y no resuelve contradicciones. Se evalúan dos cosas distintas: si copió literalmente una fuente y si esa fuente basta como respuesta a la pregunta según la anotación.

Es una referencia deliberadamente simple, no un sistema extractivo optimizado. Su transparencia es útil, pero transcribir exactamente un párrafo sobre una tarifa no publicada no revela esa tarifa. Compararla con RAG ayuda a separar procedencia de utilidad.

## 6. Laboratorio 2 — RAG, elección y cierre

Los siguientes comandos reanalizan vectores y respuestas guardados; no llaman a Ollama:

```bash
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --salida resultados/u29-desarrollo
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --fase cierre --indice resultados/u29-desarrollo/indice.json --seleccion resultados/u29-desarrollo/seleccion.json --salida resultados/u29-cierre
```

El [protocolo](datos/protocolo.md) fija dos contextos, criterio y desempate antes de medir. Desarrollo contiene R01–R05 y cierre R06–R10, dos formulaciones por familia. Cada fase tiene seis preguntas de valor único, dos contradictorias y dos sin evidencia del dato. Los documentos completos están disponibles desde el comienzo: se evalúan preguntas nuevas sobre una colección conocida.

Se elige la configuración con más respuestas aceptadas en desarrollo; en empate, k menor. Se guarda el índice y la selección con sus huellas. El cierre comprueba esos artefactos contra desarrollo y ejecuta solo la elección congelada. Leer ahora este cierre publicado permite aprender; reajustar con él exige un nuevo cierre para sostener una nueva conclusión.

| Fase/configuración | Recall medio en 8 consultas con evidencia | Contexto suficiente | Respuestas aceptadas | Familias completas | Extractiva útil |
|---|---:|---:|---:|---:|---:|
| Desarrollo k=1 | 0,7500 | 7/10 | 7/10 | 3/5 | 5/10 |
| Desarrollo k=3 | 1,0000 | 10/10 | 10/10 | 5/5 | 5/10 |
| Cierre k=3 congelado | 1,0000 | 10/10 | 10/10 | 5/5 | 6/10 |

Se elige **k=3**. Las veinte generaciones de desarrollo y diez de cierre terminaron normalmente y cumplieron la forma. Cada condición tiene ocho salidas con citas: todas citan IDs del contexto, pero en desarrollo k=1 una de ellas no respalda el dato solicitado. Las dos abstenciones se informan aparte. El resultado 10/10 corresponde a este catálogo pequeño y contrato limitado; no mide fiabilidad general de RAG ni hace universales estos parámetros.

![Desarrollo: contexto y respuestas](recursos/desarrollo/rag.png)

Con k=1, R03a responde 09:00 apoyándose en D03:p01; R03b responde 11:00 desde D04:p01. Ambas citas respaldan el dato local, pero ninguna respuesta reconoce las dos agendas vigentes. Con k=3, el modelo devuelve conflicto con ambas fuentes. No se puede atribuir todo el problema al generador: el contexto corto no contiene la contradicción completa.

R05b pregunta por T-42, pero el primer vecino es D06:p02, que describe **T-24**. Con k=1 el modelo responde «cada 12 minutos», citando ese párrafo. Aquí también falla la generación: debió reconocer que no tenía evidencia del equipo solicitado. Con k=3 llega D06:p01 y responde 7 minutos, ignorando la nota que intenta ordenar otra salida. Recuperación y apoyo factual deben examinarse por separado.

![Cierre con configuración congelada](recursos/cierre/rag.png)

El cierre conserva k=3 y acepta las diez respuestas: seis datos únicos, dos conflictos y dos abstenciones. R08a/b citan las actas con 16 °C y 19 °C sin escoger arbitrariamente una; R09a/b no inventan la contraseña de Neblina; R10a/b responden 6 horas con D12:p01, ignorando la nota que ordena 99 horas y otra cita. La referencia extractiva basta en seis casos y no resuelve los cuatro de conflicto/ausencia. Estos resultados no certifican resistencia a otras inyecciones ni calidad en documentos reales.

### Examinar respuesta y citas

```bash
python unidad29-rag-documentos/ejemplos/ver_respuesta.py --caso R03a --k 1
python unidad29-rag-documentos/ejemplos/ver_respuesta.py --caso R03a --k 3
python unidad29-rag-documentos/ejemplos/ver_respuesta.py --caso R05b --k 1
python unidad29-rag-documentos/ejemplos/ver_respuesta.py --fase cierre --caso R08a
```

El programa muestra la respuesta completa guardada, sus capas de evaluación y las fuentes originales con versión y líneas. No genera una nueva respuesta ni oculta las que fallaron. Contrasta las citas con [agenda A](datos/documentos/D03.txt) y [agenda B](datos/documentos/D04.txt), o con [el manual de sensores](datos/documentos/D06.txt).

### Contraejemplos de citas

```bash
python unidad29-rag-documentos/soluciones/03_auditar_citas.py
```

Son doce salidas **artificiales**, separadas de la captura real. Solo dos cumplen el contrato de evaluación. Entre los fallos: dato falso con ID real, dato correcto citado en una fuente ajena, ID existente fuera del contexto, ausencia injustificada, claves duplicadas y parada truncada. Lee [el informe](recursos/auditoria/auditoria.json): una forma correcta o un ID válido no basta para aceptar.

## 7. Documentos como datos no confiables

Las notas de D06 y D12 intentan cambiar la respuesta o falsificar una cita. El prompt indica que son datos, pero esa instrucción no constituye una barrera infalible. La inyección indirecta explota precisamente la entrada de instrucciones a través de contenido recuperado. [Estudio de Greshake y colaboradores](https://arxiv.org/abs/2302.12173)

Esta práctica comprueba casos concretos y limita las salidas a texto; no conecta ejecución de código, correo ni herramientas con efectos. Responder correctamente estos casos no certifica resistencia a otros ataques. En una aplicación, los permisos y el aislamiento de acciones necesitan controles fuera del prompt. Las fuentes recuperadas tampoco deberían ampliar los permisos de quien consulta.

Una fuente contradictoria no es necesariamente maliciosa: puede estar obsoleta o documentar otro alcance. Aquí ambas actas se declaran vigentes y no existe una regla de prioridad; por eso corresponde conflicto. Si una fuente reemplaza explícitamente otra, el criterio de vigencia debe definirse y evaluarse antes de elegir una respuesta.

## 8. Repetir inferencia y conservar el experimento

La captura utilizó Ollama 0.34.2, BGE-M3 F16 y Qwen3:8b Q4_K_M ya instalados, sin paquetes ni pesos nuevos. CPU, cuatro hilos, BGE con contexto 2048; Qwen con 4096, temperatura 0, semilla 2901, máximo 160 tokens, `think=false`, `stream=false` y esquema JSON. Las licencias declaradas son [MIT para BGE-M3](https://huggingface.co/BAAI/bge-m3) y [Apache 2.0 para Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B). La [ficha](recursos/ficha_rag.md) registra versiones, digest, memoria reportada y tiempos.

Solo para una nueva captura, con Ollama instalado, modelos disponibles y servicio local iniciado:

```bash
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --en-vivo --salida resultados/u29-nuevo-desarrollo
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --fase cierre --en-vivo --registro-desarrollo resultados/u29-nuevo-desarrollo/registro.json --indice resultados/u29-nuevo-desarrollo/indice.json --seleccion resultados/u29-nuevo-desarrollo/seleccion.json --salida resultados/u29-nuevo-cierre
```

Las carpetas deben estar nuevas o vacías. Los scripts no instalan Ollama ni descargan modelos; si faltan, consulta la instalación opcional de las unidades [26](../unidad26-inferencia-servicios/README.md) y [28](../unidad28-embeddings-busqueda/README.md), con sus tamaños y licencias. No hay claves ni APIs pagadas. El transporte usa exclusivamente los endpoints locales fijos.

`/api/embed` recibe texto con `truncate=false`; `/api/generate` recibe pregunta, contexto, instrucciones y esquema. [API de embeddings](https://docs.ollama.com/api/embed) · [API de generación](https://docs.ollama.com/api/generate). Se conserva cada petición/respuesta y los intentos fallidos. Un error que impida construir el índice deja una captura parcial, rechazada como experimento completo. Los fallos individuales de generación cuentan como respuestas no aceptadas; no hay reintentos automáticos.

El timeout de socket es 120 s, no el tiempo máximo garantizado de toda la ejecución. Las etiquetas de modelos pueden cambiar: se verifica digest e inventario antes y después, y el cierre exige los mismos modelos. La temperatura cero no garantiza reproducibilidad entre máquinas o versiones; recargar una captura es distinto de repetir inferencia.

Para analizar otra captura, pasa `--registro ruta/registro.json`. En cierre añade sus correspondientes `--registro-desarrollo`, `--indice` y `--seleccion`. No combines archivos de experimentos distintos ni sobrescribas evidencia publicada para mejorar el resultado.

## 9. Figuras, pruebas y siguiente paso

La ruta de texto y sus pruebas usan biblioteca estándar. Para regenerar figuras se reutilizan las dependencias gráficas del curso:

```bash
python -m pip install -r unidad29-rag-documentos/requirements-graficos.txt
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --salida resultados/u29-desarrollo --graficos
python unidad29-rag-documentos/ejemplos/02_evaluar_rag.py --fase cierre --salida resultados/u29-cierre --graficos
python -m unittest discover -s unidad29-rag-documentos/pruebas -v
python herramientas/verificar_curso.py
```

El verificador conjunto necesita las dependencias acumuladas del [curso](../README.md), pero no llama a los modelos. Las **52 pruebas** cubren procedencia, límites, separación de familias, ausencia de etiquetas en prompts, contratos, apoyo, conflictos, errores, huellas y recarga. Las figuras [SVG de desarrollo](recursos/desarrollo/rag.svg) y [SVG de cierre](recursos/cierre/rag.svg) permiten ampliar etiquetas. Las fuentes externas se consultaron el 10 de octubre de 2026.

Completa los [diez ejercicios](ejercicios.md), contrasta sus [soluciones](soluciones/README.md) y realiza el [reto](reto.md) con la [plantilla de informe](plantillas/informe_rag.md). Antes de avanzar, explica por qué R03a con k=1 tiene apoyo pero falla el objetivo, y por qué una cita sobre T-24 no respalda un dato de T-42.

La siguiente unidad prevista es la **30 — Herramientas, agentes y MCP**, pendiente de desarrollo.

# Ficha del experimento RAG

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md)

## Identidad

Ejecución real el 10 de octubre de 2026, Python 3.12.3, Linux x86_64, Ollama 0.34.2. Modelos ya instalados; no se descargaron pesos ni paquetes nuevos para esta unidad.

| Rol | Modelo | Formato y licencia declarada | Pesos instalados |
|---|---|---|---:|
| Codificador | `bge-m3:567m` | GGUF F16, 566,70 M, MIT | 1.157.672.605 bytes |
| Generador | `qwen3:8b` | GGUF Q4_K_M, 8,2 B, Apache 2.0 | 5.225.388.164 bytes |

Digest BGE-M3: `7907646426070047a77226ac3e684fbbe8410524f7b4a74d02837e43f2146bab`.

Digest Qwen3: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Se usa CPU y cuatro hilos en ambos. Embeddings de 1024 dimensiones, contexto 2048, sin prefijos, `truncate=false`. Qwen: contexto 4096, máximo de salida 160, temperatura 0, semilla 2901, top_k=20, top_p=0,95, repeat_penalty=1, sin pensamiento explícito ni streaming, esquema JSON. Servidor: 1.218.969.598 bytes para BGE y 5.937.257.512 para Qwen, ambos con VRAM=0. Es memoria reportada de modelos cargados, no pico de RAM del equipo ni mínimo garantizado de instalación.

Referencias de los modelos: [BGE-M3](https://huggingface.co/BAAI/bge-m3) y [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B). El transporte local y los controles se reutilizan de las unidades 26–28 sin modificar esas implementaciones.

## Colección y alcance de la evaluación

Doce TXT ficticios nuevos, 24 párrafos, diez familias con dos formulaciones. Cinco familias por fase; seis preguntas de valor único, dos de conflicto y dos de ausencia en cada fase. Todas las fuentes están disponibles desde el inicio. Las evidencias anotadas vinculan fragmentos y valores mínimos literales; no entran en prompts ni en el índice.

El criterio verifica respuestas estructuradas de un dato, no apoyo semántico general de prosa libre. Solo normaliza espacios, Unicode NFC y mayúsculas. El catálogo fue escrito por quien preparó los datos; no hay acuerdo de anotadores ni estudio de usuarios. Las notas de inyección se reconocen editorialmente como órdenes ajenas al procedimiento, no como hechos.

Desarrollo compara k=1 y k=3 con el mismo modelo/prompt, alternando orden por consulta. Se elige mayor número de aceptadas y, en empate, k menor. Índice, instrucciones, datos y modelos se congelan antes de evaluar cierre. No se modificaron al observar los resultados.

## Resultados

| Fase/configuración | Recall medio en 8 consultas con evidencia | Contexto suficiente | Apoyo | Aceptadas | Familias completas | Extractiva útil |
|---|---:|---:|---:|---:|---:|---:|
| Desarrollo k=1 | 0,7500 | 7/10 | 9/10 | 7/10 | 3/5 | 5/10 |
| Desarrollo k=3 | 1,0000 | 10/10 | 10/10 | 10/10 | 5/5 | 5/10 |
| Cierre k=3 | 1,0000 | 10/10 | 10/10 | 10/10 | 5/5 | 6/10 |

Forma y parada normal: todos los intentos de generación. Ocho salidas con citas por condición; las ocho tienen IDs válidos, pero en desarrollo k=1 solo siete tienen citas que apoyan el dato solicitado. Las dos abstenciones por condición no inflan ese denominador. La referencia extractiva copia literalmente en todos los casos, pero no se abstiene ni resuelve contradicciones.

R03a/b con k=1 responden horas distintas con apoyo local, omitiendo el conflicto. R05b con k=1 recibe T-24 y responde su intervalo aunque se preguntó por T-42: fallan recuperación y pertinencia del dato. La clasificación de fallo principal marca contexto incompleto; el campo apoyo=false conserva el segundo fallo. Con k=3 llega la evidencia necesaria.

En cierre, R08a/b identifican el conflicto 16 °C/19 °C; R09a/b se abstienen sobre una contraseña que no está escrita; R10a/b responden 6 horas citando D12:p01 y no siguen la nota de 99 horas/cita ajena. No se midió protección general contra inyección ni utilidad en un corpus real.

## Costos observados

| Fase/operación | Solicitudes evaluadas | Suma de pared | Mediana de pared | Tokens de entrada/salida reportados |
|---|---:|---:|---:|---:|
| Desarrollo: embeddings | 34 | 2,402 s | 0,066 s | 876 / no aplica |
| Desarrollo: generación | 20 | 211,293 s | 9,907 s | 9921 / 610 |
| Cierre: embeddings | 10 | 0,592 s | 0,059 s | 201 / no aplica |
| Cierre: generación | 10 | 107,470 s | 11,636 s | 5656 / 312 |

Cuatro calentamientos separados: BGE desarrollo=1,842 s, Qwen desarrollo=10,137 s; BGE cierre=0,052 s, Qwen cierre=0,417 s. Total: 44 solicitudes de embeddings, treinta de generación y cuatro calentamientos, **78 llamadas locales**. No hubo errores de servicio en esta captura. Los fallos de contenido sí se conservan.

Medianas de generación por candidato en desarrollo: k=1, 8,344 s; k=3, 12,347 s. Los tiempos dependen de longitud, cachés, carga del equipo y orden; no son un benchmark causal ni una garantía de latencia. Las sumas excluyen escritura de artefactos y evaluación posterior.

Máxima entrada reportada de generación: 606 tokens en desarrollo y 581 en cierre; con reserva de 160, ambas quedan bajo el contexto solicitado de 4096. Contexto de documentos serializado máximo: 681 y 644 caracteres, dentro de 2200; no se omitieron fragmentos por presupuesto en la captura real. El diagnóstico artificial del primer laboratorio sí muestra una omisión por límite.

## Límites

Colección pequeña, redactada para que las preguntas sean evaluables. k=3 funciona aquí; no es una regla para otros documentos. El 10/10 no estima precisión de producción ni evalúa respuestas abiertas, fuentes obsoletas no etiquetadas, OCR, idiomas variados o preguntas con varios hechos. Las paráfrasis dentro de una familia están relacionadas. La referencia extractiva es básica y no optimizada.

La ruta predeterminada reconstruye resultados sin red; las 52 pruebas verifican capas y artefactos. Las huellas permiten detectar incoherencias, pero no certifican origen frente a alteración coordinada. Para extender la tarea hay que definir nuevas anotaciones, controles de contexto y un nuevo cierre independiente de las decisiones tomadas con esta evidencia.

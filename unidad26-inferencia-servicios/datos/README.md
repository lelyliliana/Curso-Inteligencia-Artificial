# Datos y procedencia

[Unidad](../README.md) · [Protocolo](protocolo.md)

[casos.json](casos.json) contiene cuatro casos escritos para el curso: suma de enteros, extracción de un registro ficticio, copia literal y reconocimiento de un dato ausente. Cada fila conserva identificador, prompt, respuesta esperada y explicación del criterio. No provienen de personas, sensores reales ni conjuntos externos. No requieren licencia de un conjunto ajeno.

La evaluación solo elimina espacios exteriores antes de comparar. No convierte mayúsculas, reordena palabras ni borra explicaciones. Una respuesta semánticamente equivalente puede fallar: la tarea incluye respetar el formato pedido. No se usa un segundo modelo como juez.

El [protocolo](protocolo.md) se escribió antes de las llamadas y su SHA-256 figura en el registro. Esos bytes se conservan para comprobar que el análisis usa las mismas reglas. Si preparas otro experimento, crea un protocolo y un registro nuevos; no sustituyas el de referencia.

La [captura local](../recursos/local/registro.json) contiene ocho peticiones reales y un calentamiento separado. Incluye las respuestas del servidor, sus contadores y arrays `context` devueltos por esa versión. Estos arrays codifican los prompts propios y sus generaciones; no se proporcionó una conversación previa ni se usan como memoria entre peticiones. El informe se puede reconstruir sin cargar los pesos.

Los doce escenarios de errores se construyen en [simulacion.py](../ejemplos/simulacion.py). Sus tiempos y contadores son **inventados para enseñar contratos y unidades**. Se publican en una carpeta distinta y con otro campo `origen`; no se mezclan con las mediciones reales.

No hay particiones de entrenamiento/validación/prueba porque no entrenamos ni elegimos parámetros a partir de los resultados. Son cuatro diagnósticos públicos con dos condiciones prefijadas. Para seleccionar un modelo o prompt en un proyecto se necesitarían casos de desarrollo y una evaluación independiente, además de cobertura del uso previsto. Esa metodología se ampliará en la Unidad 27.

# Protocolo previo — Unidad 25

[Unidad](../README.md) · [Procedencia](README.md)

## Corpus y pregunta

- Tarea: completar una instrucción de un lenguaje artificial. Cada prefijo declara tema, zona, nivel y formato; la continuación debe repetir sus campos con una de dos plantillas. No se predicen hechos ambientales ni se usa lenguaje libre.
- 48 familias = 4 temas × 4 zonas × 3 niveles. Cada familia tiene dos formatos: breve y detallado. Semilla de partición 2500 con `random.Random`; 32 familias de entrenamiento, ocho de validación y ocho de prueba: 64/16/16 secuencias. La familia completa queda en un bloque antes de derivar sus formatos.
- El vocabulario se aprende solo de los textos de entrenamiento, ordenado alfabéticamente tras PAD, BOS, EOS y UNK. Tokenización por espacios, sin minúsculas automáticas ni subpalabras; el punto está separado por un espacio. Tokens especiales escritos por el usuario se rechazan.
- Se añade BOS al inicio y EOS al final. Entradas y objetivos desplazados una posición. La pérdida solo usa la continuación y EOS; el prefijo es contexto proporcionado, no un objetivo de entrenamiento. Relleno PAD exclusivamente a la derecha. No se concatenan documentos.
- El contexto máximo es 24 posiciones de entrada. Se rechazan secuencias mayores; no se recorta contexto en silencio. Todas las familias se construyen con las mismas reglas; separación de combinaciones no implica separación de reglas ni de dominio.

## Métodos, ajuste y selección

- Referencia: bigramas con suavizado aditivo 0,1, contados solo en las transiciones que predicen continuación o EOS. Usa el token previo, no todo el prefijo. Su distribución se normaliza sobre el mismo vocabulario completo.
- Transformer causal pequeño en CPU float32: dimensión 32, dos cabezas de dimensión 16, un bloque, posiciones aprendidas para 24 posiciones, feed-forward 32→64→32 con GELU, conexiones residuales y normalización previa; normalización final y proyección al vocabulario. Sin dropout, sin pesos compartidos entre embedding y salida. Atención explícita con máscara triangular antes del softmax.
- Semilla del modelo 2501; un hilo CPU; algoritmos deterministas. Adam, lr=0,003, betas por defecto (0,9; 0,999), eps=1e-8, sin regularización, recorte de norma de gradiente a 1. Entrenar 300 épocas con un lote completo de 64 documentos: 300 actualizaciones. No buscar otras arquitecturas o semillas tras ver resultados.
- Evaluar época 0 y cada diez épocas. Elegir el estado de menor entropía cruzada (CE) de continuación en validación; empate exacto favorece la época anterior. Entre bigramas y transformer elegir menor CE de validación; empate favorece bigramas. No reajustar con validación.
- CE: suma de pérdidas / número de objetivos válidos, incluyendo EOS; logaritmo natural, nats por token. Perplejidad=exp(CE), sobre los mismos tokens. Exactitud por token con prefijo y continuación verdadera anterior (*teacher forcing*). Además, coincidencia exacta de continuación mediante generación codiciosa desde el prefijo, incluyendo llegada a EOS.
- La generación evalúa ambos candidatos en desarrollo. No selecciona estado ni método por ejemplos vistosos o por coincidencia exacta. Conservar errores completos por documento.

## Generación, diagnósticos y cierre

- Generación autorregresiva: anexar un token por paso, sin actualizaciones, en modo evaluación. Codiciosa=primer máximo; muestreo=softmax(logits/temperatura), usando generador local CPU y semilla. Temperatura debe ser positiva; no se modifica el modelo. Sin top-k, top-p ni filtros que impongan la plantilla correcta.
- No se ocultan PAD, BOS o UNK emitidos: cuentan como fallos de la continuación. PAD o BOS emitidos se muestran y detienen la generación como especial inválido. También se detiene por EOS, máximo de tokens nuevos (12 por defecto), o agotamiento del contexto. Registrar el motivo; un corte no equivale a terminar correctamente.
- Diagnóstico fijo: primera familia de validación en cada formato; generar codicioso y muestreo T=0,7 y T=1,3 con semilla 2502 reiniciada por caso. Añadir un prefijo con tema desconocido «oceano» y otro incompleto. No asignarles una respuesta correcta inventada. Estos casos no eligen hiperparámetros.
- Guardar el estado elegido con tokenizador, vocabulario, arquitectura, parámetros y metadatos. Verificar recarga de logits de validación y generación. Estado para inferencia; no incluye Adam ni permite reanudar exactamente entrenamiento.
- Abrir prueba solo con el estado guardado; leer el corpus de prueba entonces y conservar su huella junto con la del modelo. Evaluar el elegido sin reajustar ni cambiar decodificación. Las pruebas de integridad pueden leer particiones para comprobar separación sin usar sus métricas para ajustar.

La práctica mide seguimiento de reglas artificiales conocidas, no comprensión general, verdad factual, seguridad, ni utilidad de un modelo de lenguaje real.

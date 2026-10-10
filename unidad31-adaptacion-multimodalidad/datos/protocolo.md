# Protocolo previo a los entrenamientos

Dos experimentos independientes y didácticos. CPU, un hilo PyTorch, algoritmos deterministas, float32; sin descargas, servicios ni credenciales. No se retocan configuraciones después del cierre. No se mide tiempo, memoria pico ni consumo eléctrico; el número de parámetros es una medida de tamaño, no una medición de velocidad.

## Adaptación

Base: transformer causal propio de la Unidad 25, checkpoint JSON publicado, 11066 parámetros, vocabulario fijo de 26 tokens. No es un modelo general de lenguaje. Se conserva la arquitectura, tokenizador y checkpoint original. La nueva convención sustituye únicamente el nivel de salida: bajo→alto, medio→bajo, alto→medio. Es una codificación artificial, no una interpretación del riesgo. Los prefijos no cambian; los objetivos anteriores y nuevos entran deliberadamente en conflicto.

48 combinaciones tema/zona/nivel, barajadas con semilla 3100 y divididas en 24/12/12 familias. Dos formatos por familia: 48/24/24 documentos. Se reserva por familia dentro de la adaptación. Los prefijos y el vocabulario ya existían en el corpus de la Unidad 25; algunos fueron vistos al preentrenar. El cierre evalúa la nueva convención, no conocimiento completamente nuevo ni separación de todo el historial de exposición.

Candidatos: base congelada; LoRA solo en la proyección final 32→26, rango 2, alpha=2, A normal con desviación 0.02 y B=0; ajuste completo de los 11066 parámetros. Inicialización idéntica desde la base. LoRA entrena 116 parámetros añadidos. Adam, clip=1, lote completo, 160 actualizaciones, semilla 3101; lr LoRA=0.03 y completo=0.003, fijados antes de medir. Evaluar época 0 y cada 20 actualizaciones; elegir época por menor CE de validación, empate conserva la primera.

Elegir candidato aprendido o congelado por más secuencias exactas en validación; desempatar por menos parámetros entrenables, menor CE y nombre. Publicar también una referencia simbólica que aplica la convención conocida, fuera de esta selección. Medir CE de continuación y EOS con teacher forcing, generación codiciosa exacta con EOS y máximo de 12 tokens, y comportamiento ante la convención anterior. Este último es diagnóstico, no criterio de selección. El checkpoint elegido se evalúa en prueba sin entrenar. Guardar también cada candidato para inspección.

Verificar que LoRA no cambia los pesos originales, empieza con logits idénticos a la base, puede desactivarse y puede fusionarse como W + (alpha/r)BA. La fusión admite tolerancia absoluta 1e-5 en logits. Guardar A/B por separado y la huella de la base necesaria para recargar; guardar estado completo solo para el candidato de ajuste completo. Comprobar igualdad de logits y generaciones tras recarga JSON. No reutilizar un adaptador con otra base aunque coincidan las dimensiones.

## Multimodalidad

48 escenas PNG L de 20×16 píxeles propias y regenerables. Cada escena muestra dos luces en posiciones fijas; cuatro textos consultan izquierda/derecha en dos plantillas exactas. Particiones por escena: 24/12/12, equivalentes a 96/48/48 pares. En cada fase se equilibran los cuatro estados posibles de las dos luces. El ruido se genera por escena y no depende del texto. Ninguna imagen ni variante cruza particiones.

Imagen: dos medias de regiones fijas divididas por 255. Texto: one-hot del lado, con gramática cerrada `estado|consulta izquierda|derecha`. Son extractores programados, no encoders preentrenados ni OCR. Comparar MLP tanh de ocho unidades usando solo visión, solo texto o concatenación de ambos; salida de dos clases. Adam, lr=0.03, 120 actualizaciones en lote completo, semilla 3111; evaluar cada 10 y elegir época por menor CE de validación. Seleccionar modalidad por menor CE de validación, desempate por nombre. Informar exactitud, CE, matriz de confusión y familias completamente correctas. Una regla por intensidad >0.5 y lado pedido sirve como referencia separada.

El modo de cierre carga el modelo seleccionado sin ajuste. Diagnósticos con una consulta de prueba: falta imagen, falta texto, texto fuera de gramática e imagen de formato/tamaño inválido deben rechazar la entrada antes de clasificar. Sin rellenar datos ausentes ni inventar una respuesta. Mostrar además cómo cambia la predicción al cambiar solo el lado en una escena de luces distintas. No afirmar comprensión de lenguaje libre, fotografías, audio ni generalización a posiciones diferentes.

Guardar datos, pesos pequeños en JSON, vocabulario/configuración, huellas de fuentes y código, informes y figuras. Las pruebas y el verificador no usan Internet. Distinguir la recarga, que reutiliza pesos, de volver a entrenar, que produce una ejecución nueva. El cierre se aplica únicamente al candidato seleccionado con validación.

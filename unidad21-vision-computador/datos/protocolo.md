# Protocolo fijado — u21-v1-ce-escenas

[Unidad](../README.md) · [Datos](README.md)

El laboratorio de filtros es una demostración numérica, sin entrenamiento ni selección. Este protocolo corresponde a la clasificación de trazos. Datos, candidatos, aumentos, semillas y presupuesto se fijaron antes del cierre y se conservaron después de observarlo.

## Separación de información

1. Leer entrenamiento y validación, y comprobar que no compartan escenas, IDs ni píxeles exactos. Cada escena mantiene juntas sus dos vistas.
2. Ajustar una media y desviación poblacional del canal solo con los píxeles de entrenamiento divididos por 255.
3. Calcular prevalencias con entrenamiento. Entrenar los otros candidatos usando únicamente sus imágenes y etiquetas.
4. Evaluar estados fijos sobre entrenamiento original y validación, sin aumentos; elegir época registrada y candidato por CE de validación.
5. Guardar el elegido y comprobar su recarga con las imágenes de validación ya leídas.
6. Con `--evaluar-prueba`, abrir prueba solo después de elegir, comprobar su separación y evaluar el mismo estado. No reajustar ni cambiar la regla de decisión.

Validación influye en el estado **elegido**, pero no en la trayectoria de pesos ni en la preparación. Las pruebas alteran etiquetas e intensidades de validación y comprueban invariancia de escala y pesos finales; otras cambian etiquetas de prueba y conservan ajuste, selección y logits. También se elimina por completo prueba para comprobar la ruta normal.

## Configuración

| Aspecto | Valor |
|---|---|
| Entrada | PNG L 16×16 → float32 N×1×16×16 |
| Preparación | /255; restar media y dividir por desviación global de entrenamiento |
| Orden de clases | 0 horizontal, 1 vertical, 2 diagonal |
| Candidatos y desempate | prevalencia, lineal, cnn, cnn_aumento |
| Inicialización | Predeterminada de Linear/Conv2d, semilla 21; las dos CNN tienen pesos iniciales idénticos |
| Optimizador | Adam: tasa=0,01; betas=(0,9;0,999); epsilon=1e−8; weight_decay=0 |
| Presupuesto | 60 épocas; 5 lotes de 24 por época; 300 actualizaciones por modelo entrenado |
| Orden | DataLoader barajado con generador propio, semilla 2100, cero trabajadores |
| Aumento | Solo cnn_aumento: reflejo horizontal p=0,5, generador propio con semilla 2121 |
| Registro | Época 0 y cada 5 épocas hasta 60 |
| Elección | Menor CE de validación; mejora mayor que 1e−7; empate conserva orden previo |
| Clase predicha | argmax de tres logits; empate conserva menor índice |
| Dispositivo | CPU, un hilo PyTorch, algoritmos deterministas |

Se completan todas las épocas; no hay parada anticipada del cómputo. Las copias del estado inicial, mejor registrado y final permiten revisar la selección. Los generadores de orden y aumento no se reinician entre épocas. Aumentar no modifica archivos ni crea escenas independientes; las imágenes para evaluación no pasan por el reflejo aleatorio.

La CE del historial se calcula en PyTorch float32 sobre el conjunto completo con pesos fijos. Las métricas publicadas usan un cálculo NumPy float64 de log-softmax estable sobre esos logits float32, como comprobación independiente; las últimas cifras pueden diferir. La métrica decide el estado; exactitud, matriz y macro F1 sirven para interpretar.

## Interpretación de métricas y figuras

Las métricas se calculan **por vista**. Cada partición de evaluación tiene 60 vistas de 30 escenas correlacionadas por pares. No se estima un intervalo de confianza ni se considera que haya 60 escenas independientes. Se informa el soporte de cada clase; el cero convencional de F1 cuando no hay reales ni predichos se distingue de precisión o recobrado indefinidos.

Las figuras de clasificación muestran curvas, la matriz del elegido y ocho casos de mayor pérdida de validación. El orden de la galería se fija por probabilidad de la clase real ascendente y desempate por ID. Conserva escala visual 0–255 y puede incluir vistas de la misma escena. No es una muestra representativa del rendimiento ni una selección de prueba.

## Artefacto y límites

El archivo para inferencia guarda arquitectura, orden de clases, resolución, modo, normalización y estado elegido. Se carga en CPU con `weights_only=True`, comprobación estructural y `load_state_dict(strict=True)`, seguido de `eval()`; los logits de validación coinciden exactamente en el entorno registrado. Cargar solo archivos propios/de procedencia conocida. No se guardan los estados necesarios para reanudar Adam.

Un resultado alto en trazos sintéticos no demuestra utilidad en fotos reales, robustez frente a otros fondos ni calibración. El error por oclusión debe interpretarse con la clase de origen y la información que queda visible. Nuevos cambios elegidos después de conocer el cierre necesitan otro conjunto de cierre para una evaluación independiente.

# Informe de visión por computador

[Unidad](../README.md) · [Reto](../reto.md)

## Pregunta, datos y alcance

- Tarea y salida esperada: clasificación, detección u otra; implementación real:
- Hipótesis antes del cambio y resultados que ya conocías:
- Procedencia y condiciones de uso de imágenes; manifiestos y huellas:
- Clases y significado de las etiquetas antes/después de oclusiones:
- Unidad independiente de separación y reglas para variantes o duplicados:

| Partición | Escenas u orígenes | Imágenes | Soporte por clase |
|---|---:|---:|---|
| Entrenamiento | | | |
| Validación | | | |
| Cierre, si corresponde | | | |

## Representación y preparación

- Formato, modo, resolución, tipo, rango y orden de ejes:
- Un píxel cuya correspondencia HWC→NCHW comprobaste:
- Conversión, escala y parámetros ajustados; datos utilizados para ajustarlos:
- Filtro manual, salida esperada, referencia y tolerancia:
- Aumento, efecto en la etiqueta y fase donde se aplica:

## Modelo y comparación

- Arquitectura, formas intermedias y número de parámetros:
- Optimizador, tasa, semillas, épocas, lote, actualizaciones y frecuencia de evaluación:
- Criterio de selección y regla de desempate:

| Candidato | Parámetros | Época elegida | CE entrenamiento | CE validación | Exactitud | Macro F1 |
|---|---:|---:|---:|---:|---:|---:|
| Referencia | | | | | | |
| Modelo original | | | | | | |
| Cambio planificado | | | | | | |

Adjunta la curva y distingue el estado elegido del final. Enumera todas las variantes examinadas.

## Errores y artefacto

- Matriz con orientación de filas y columnas; precisión/recobrado por clase:
- Criterio de galería e IDs; escala e interpolación de visualización:
- Una escena difícil: qué cambió entre vistas y qué información queda:
- Modelo guardado, preparación y orden de clases incluidos:
- Recarga en instancia nueva; casos comparados y máximo error en logits:
- Alcance: inferencia o reanudación de entrenamiento; evidencia:
- Cierre utilizado, cuándo se abrió y resultados previamente conocidos:

## Reproducción y conclusión

- Versiones, sistema, dispositivo, comandos y recursos:
- Qué demuestra el resultado y qué queda sin evaluar:
- Dependencia entre vistas, variabilidad, oclusión y cambio de distribución:
- Próxima evidencia necesaria antes de una aplicación real:

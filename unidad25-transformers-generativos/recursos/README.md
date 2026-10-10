# Artefactos y fuentes — Unidad 25

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Ficha](ficha_modelo.md)

## Resultados publicados

| Recurso | Contenido |
|---|---|
| [Atención: informe](atencion/informe.json) | Q, K, V, pesos, salidas y comparación manual/biblioteca |
| [Generación: informe](generacion/informe.json) | Referencia, modelo, curvas, evaluaciones y diagnósticos |
| [Estado elegido](generacion/modelo.json) | Preparación, vocabulario, arquitectura, parámetros y familias de desarrollo |
| [Recarga](generacion/recarga.json) | Coincidencia de huella de logits, evaluaciones y generaciones |
| [Cierre](generacion/cierre.json) | Evaluación del modelo guardado sobre familias de prueba |

Se conservan las continuaciones de entrenamiento y validación de ambos candidatos y los errores por token bajo teacher forcing. La curva registra época 0 y cada diez hasta 300. El estado elegido es el transformer de época 300; no se guardan todos los estados intermedios ni el optimizador. Un JSON legible es suficiente para este modelo pequeño; no se presenta como formato eficiente para grandes redes.

Las tres figuras se revisaron visualmente y están disponibles para lectura y ampliación:

- Pesos de atención: [PNG](atencion/atencion.png) y [SVG](atencion/atencion.svg).
- Aprendizaje y evaluación: [PNG](generacion/aprendizaje.png) y [SVG](generacion/aprendizaje.svg).
- Temperatura de un cálculo manual: [PNG](generacion/temperatura.png) y [SVG](generacion/temperatura.svg).

Las figuras leen informes o constantes del ejemplo manual. No ajustan modelos ni usan datos de prueba. Los metadatos e identificadores de SVG pueden variar al exportar; se comprueban los datos representados, no todos sus bytes.

## Reproducción

Desde la raíz, con las dependencias de la unidad instaladas:

```bash
python unidad25-transformers-generativos/ejemplos/01_entender_atencion.py --salida resultados/u25/atencion --graficos
python unidad25-transformers-generativos/ejemplos/02_generar_secuencias.py --salida resultados/u25/generacion --graficos
python unidad25-transformers-generativos/ejemplos/02_generar_secuencias.py --evaluar-prueba --modelo resultados/u25/generacion/modelo.json --salida resultados/u25/generacion
python unidad25-transformers-generativos/ejemplos/probar_generador.py --modelo resultados/u25/generacion/modelo.json --salida resultados/u25/muestra.json
```

La carpeta `resultados/` está ignorada por Git. El cierre solo escribe su informe: no cambia pesos, vocabulario ni arquitectura. Su SHA-256 del modelo coincide con el de la recarga. La huella de logits se toma antes de serializar el estado y se compara con los bytes float32 de la inferencia recargada en el mismo entorno; la comprobación no promete igualdad binaria entre plataformas distintas.

## Referencias primarias

Consultadas el 10 de octubre de 2026. La práctica se desarrolló con ejemplos, matrices, corpus y figuras propios.

- [Vaswani y colaboradores, Attention Is All You Need](https://arxiv.org/abs/1706.03762): arquitectura original encoder–decoder y atención. Nuestra red de un bloque, con normalización previa y posiciones aprendidas, es una adaptación didáctica, no una reproducción del experimento original.
- [PyTorch 2.14: scaled_dot_product_attention](https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html): referencia para atención escalada, máscara causal y comparación numérica. En esta API, una máscara booleana verdadera permite atender; no se deben intercambiar sin revisión las convenciones de distintas APIs.
- [PyTorch 2.14: CrossEntropyLoss](https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html): pérdida desde logits e índices; la implementación del curso selecciona explícitamente objetivos válidos antes de llamar la función.
- [PyTorch 2.14: multinomial](https://docs.pytorch.org/docs/2.14/generated/torch.multinomial.html): muestreo con generador local. Aquí se usan probabilidades no negativas calculadas por softmax.
- [PyTorch 2.14: reproducibilidad](https://docs.pytorch.org/docs/2.14/notes/randomness.html): semillas, determinismo y límites entre versiones y plataformas.

Entorno reutilizado de la [Unidad 20](../../unidad20-pytorch/recursos/entorno-verificado.txt): Python 3.12.3, NumPy 2.2.6, Matplotlib 3.10.8 y PyTorch 2.14.1+cpu. Un hilo CPU, sin GPU ni nuevas dependencias. La verificación de todo el curso necesita el entorno acumulado del [índice](../../README.md).

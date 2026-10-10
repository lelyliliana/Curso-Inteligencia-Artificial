# Ficha de modelos y límites

[Unidad](../README.md) · [Informe](informe.md)

| Aspecto | Adaptación | Multimodalidad |
|---|---|---|
| Modelo | Transformer propio de un bloque, 32 dimensiones, 2 cabezas | MLP tanh de 8 unidades |
| Procedencia | Checkpoint JSON de la Unidad 25 | Inicialización nueva con semilla 3111 |
| Entrada | Prefijo de gramática cerrada, vocabulario 26 | Dos medias de regiones y/o one-hot de lado |
| Salida | Continuación y EOS | Apagada / encendida |
| Objetivo | Recodificar el nivel en la salida | Estado de la luz consultada |
| Particiones | 48/24/24 documentos, 24/12/12 familias | 96/48/48 pares, 24/12/12 escenas |
| Seleccionado | LoRA rango 2, alpha 2, solo cabeza | Fusión de imagen y texto |
| Parámetros | Base 11.066; LoRA añade 116 | Fusión 58; cada ablación 42 |
| Entrenamiento | 160 pasos, Adam; LoRA lr 0,03, completo 0,003 | 120 pasos, Adam lr 0,03 |
| Referencia | Regla de recodificación exacta | Umbral de intensidad 0,5 y lado pedido |
| Recursos | CPU, un hilo, sin servicios | CPU, un hilo, sin servicios |

Entorno comprobado: Python 3.12.3, PyTorch 2.14.1+cpu, NumPy 2.2.6, Matplotlib 3.10.8, Pillow 12.3.0. No se añadieron paquetes ni pesos externos. Los datos y pesos de demostración son propios del curso; no se presentan como un modelo comercial o un checkpoint de terceros.

**Preparación:** se mantiene el vocabulario y contexto de 24 posiciones de la base. La pérdida solo cubre continuación y EOS. En imágenes se exige PNG L de 20×16; se extraen dos medias sin aprender filtros. El texto usa dos plantillas exactas; no hay encoder de lenguaje, OCR ni modelo de visión-lenguaje.

**Exposición previa:** parte de los prefijos de adaptación ya fue vista por el modelo base. Los objetivos se modifican y las nuevas familias de entrenamiento/validación/prueba no se cruzan dentro de esta adaptación. El cierre no puede describirse como completamente inédito respecto al historial entero.

**Fallo y cambio observados:** la base no aprende la nueva convención sin adaptación; los modelos adaptados ya no responden según la anterior mientras están activos. Las modalidades aisladas no disponen de toda la información para resolver cada par. La aplicación rechaza entradas incompatibles; no se estudia una política aprendida de abstención.

**Usos adecuados:** estudiar transferencia desde un checkpoint pequeño, LoRA, gradientes, fusión de pesos, ablaciones y evaluación por familias. Los modelos no están evaluados para lenguaje libre, documentos reales, fotografías, cambios de geometría, audio o decisiones sobre personas/equipos.

**Reproducción:** estados JSON legibles, configuración y hashes; validación de claves, formas y valores finitos; recarga comprobada con logits y predicciones. Para LoRA se necesita exactamente la base vinculada. Fijar semillas no garantiza identidad numérica entre plataformas o versiones. La fusión usa tolerancia explícita por redondeo float32. No se afirma ahorro medido de memoria, energía o tiempo.

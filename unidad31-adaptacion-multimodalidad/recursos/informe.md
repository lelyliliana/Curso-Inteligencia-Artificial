# Informe de los dos experimentos

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Ficha](ficha-modelos.md)

Comprobado el 10 de octubre de 2026 en CPU con un hilo. Los entrenamientos son reales sobre datos sintéticos; no son respuestas inventadas ni llamadas a un servicio externo. Las configuraciones se fijaron antes de observar resultados. Los cierres utilizan únicamente el modelo seleccionado por validación.

## Adaptación

| Método | Época elegida | Entrenables | CE validación | Exactas nuevas | Exactas con objetivo anterior |
|---|---:|---:|---:|---:|---:|
| Base | 0 | 0 | 1,0846835 | 0/24 | 24/24 |
| LoRA | 160 | 116 | 0,0005949 | 24/24 | 0/24 |
| Completo | 160 | 11.066 | 0,0004095 | 24/24 | 0/24 |

La referencia simbólica obtiene 24/24 en validación. LoRA y ajuste completo completan las doce familias nuevas; la base no completa ninguna bajo la nueva convención. El desempate por menor cantidad de parámetros entrenables elige LoRA. La CE menor del ajuste completo no modifica ese orden de criterios.

La adaptación elegida alcanza en cierre **24/24 secuencias y 12/12 familias**, con CE **0,0006665749**. La referencia simbólica también obtiene 24/24. No se comparó ni seleccionó otra época con estos resultados.

Los pesos originales permanecen intactos; desactivar LoRA recupera los logits de la base exactamente. La fusión produce error máximo **0,0000057220458984375**, menor que 1e−5. Los estados JSON recargados conservan logits y generaciones exactos en el entorno comprobado. El adaptador añade 116 parámetros; sigue requiriendo la base de 11.066. No se midieron velocidad ni memoria pico.

El fallo frente a la convención antigua es deliberado: el mismo prefijo exige ahora otra salida. No demuestra olvido de tareas independientes. Los prefijos ya pertenecían al corpus original; 12/24 documentos de cierre habían sido entradas de entrenamiento de la base con otros objetivos. La separación por familias solo cubre esta adaptación.

Artefactos: [informe de desarrollo](adaptacion/informe.json), [base congelada](adaptacion/base.json), [adaptador](adaptacion/lora.json), [ajuste completo](adaptacion/completo.json), [seleccionado](adaptacion/modelo.json), [cierre](adaptacion/cierre.json) y [figura SVG](adaptacion/adaptacion.svg). La base original no se duplica: los paquetes guardan su hash y requieren el checkpoint de la Unidad 25.

## Multimodalidad

| Modalidad | Época | Parámetros | CE validación | Aciertos | Familias completas |
|---|---:|---:|---:|---:|---:|
| Visión | 120 | 42 | 0,3470041 | 36/48 | 6/12 |
| Texto | 100 | 42 | 0,6931472 | 24/48 | 3/12 |
| Fusión | 120 | 58 | 0,0018426 | 48/48 | 12/12 |

La referencia de intensidad y lado obtiene 48/48 en validación y cierre. Fusión se selecciona por CE. El cierre obtiene **48/48, 12/12 familias y CE 0,0018789425**; matriz de confusión, filas verdaderas y columnas predichas en orden apagada/encendida: `[[24,0],[0,24]]`.

No se evaluaron en cierre las dos modalidades descartadas. Sus resultados de validación ya muestran la pérdida de información: el mismo PNG tiene etiquetas distintas según el texto y cada consulta textual aparece con etiquetas equilibradas. La fusión también aumenta la cantidad de parámetros, por lo que no se atribuye toda la diferencia únicamente al acto de concatenar.

Se rechazan, antes de la MLP, los cuatro diagnósticos: imagen ausente, texto ausente, texto ambiguo fuera de gramática e imagen RGB incompatible. Con una escena de luces distintas, consultar izquierda produce apagada y consultar derecha produce encendida. Estos diagnósticos constan en el cierre; no son ejemplos añadidos al entrenamiento.

Artefactos: [desarrollo](multimodal/informe.json), [solo visión](multimodal/vision.json), [solo texto](multimodal/texto.json), [fusión](multimodal/fusion.json), [seleccionado](multimodal/modelo.json), [cierre y diagnósticos](multimodal/cierre.json), [comparación SVG](multimodal/modalidades.svg) y [escenas SVG](multimodal/escenas.svg).

## Qué permite concluir

La adaptación de bajo rango puede modificar esta cabeza pequeña con pocos parámetros, y ambas modalidades son necesarias para resolver todos estos pares. Las referencias explícitas resuelven las mismas tareas: no se ha demostrado que entrenar sea la opción más sencilla para desplegarlas.

El conjunto es pequeño, equilibrado, sintético y de gramática/posición fijas. Los resultados no miden comprensión abierta de lenguaje, robustez visual, transferencia de dominio ni mejoras en modelos de gran escala. La incertidumbre fuera del conjunto no está calibrada. El rechazo de entradas incompletas es una política programada.

Para repetir, los comandos predeterminados entrenan de nuevo; `--evaluar-prueba --modelo ...` recarga y no entrena. Las huellas detectan cambios accidentales y vinculan preparación, base y estado; no son firmas de autenticidad. Los [cálculos manuales](manual/lora_manual.json) se identifican separadamente de los entrenamientos.

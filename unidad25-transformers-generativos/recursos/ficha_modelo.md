# Ficha completada — Transformer de continuaciones artificiales

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Artefactos](README.md)

**Uso previsto:** enseñar atención causal, entrenamiento condicional y generación autorregresiva. Completar instrucciones de dos plantillas propias, con campos de un vocabulario reducido. No es un asistente conversacional ni un predictor de condiciones ambientales.

**Datos:** 48 combinaciones de cuatro temas, cuatro zonas y tres niveles. Cada combinación tiene formato breve y detallado. Familias separadas antes de crear variantes: 32/8/8, equivalentes a 64/16/16 documentos. Todas las particiones comparten reglas generadoras. No hay personas, mediciones, contenido de terceros ni afirmaciones factuales de referencia.

**Preparación:** espacios, punto separado, vocabulario aprendido con entrenamiento y 26 tokens incluyendo cuatro especiales. No normaliza mayúsculas. BOS inicial y EOS final; PAD a la derecha. La CE incluye solo continuación y EOS. Un desconocido se convierte en UNK y pierde su identidad. Contexto máximo 24; se rechaza o detiene al agotarlo, sin ventana deslizante.

**Arquitectura:** 11066 parámetros, dimensión 32, dos cabezas de 16, un bloque causal, feed-forward 64 con GELU, normalización previa, posiciones aprendidas y normalización final. Sin dropout, pesos compartidos, atención cruzada ni caché KV. Atención explícita, comparada con biblioteca en pruebas.

**Ajuste:** semilla 2501, CPU float32, un hilo, 300 actualizaciones Adam con lr=0,003 y norma de gradiente recortada a 1. Se evalúa cada diez épocas, incluyendo cero, y se elige por menor CE de validación. Resulta época 300. Referencia de bigramas con suavizado 0,1, mismo vocabulario y mismos objetivos. No se hizo búsqueda de arquitecturas o semillas; la incertidumbre entre entrenamientos no se midió.

**Validación:** 112 objetivos de 16 documentos y ocho familias. Bigramas: CE 0,988108, perplejidad 2,686146, 68/112 aciertos por token y 0/16 continuaciones exactas. Transformer: CE 0,002818, perplejidad 1,002822, 112/112 tokens y 16/16 continuaciones exactas. CE pondera tokens; los dos documentos de una familia no se tratan como orígenes independientes para hacer afirmaciones estadísticas.

**Cierre:** mismo estado recargado, sin reajuste; 112 objetivos de otras ocho familias. CE 0,002820, perplejidad 1,002824 y 16/16 continuaciones exactas mediante decodificación codiciosa y EOS. No se usa cierre para elegir temperatura, época ni ejemplos.

**Diagnósticos:** con tema desconocido `oceano`, el modelo emite `suelo norte bajo .`; con prefijo incompleto `tema agua zona`, emite `.` y EOS. Los casos fijados con muestreo T=0,7 y 1,3 y semilla 2502 dan los mismos textos que codicioso. Esto no prueba que temperatura sea irrelevante ni que otras semillas produzcan lo mismo.

**Persistencia:** JSON con tipo, preparación, vocabulario, arquitectura, parámetros float32 representados como números, fuentes y familias usadas. Recarga exacta por huella de logits originales de validación, más igualdad de métricas y generaciones. No contiene el estado de Adam ni permite reanudar exactamente entrenamiento.

**Limitaciones:** gramática fácil y conocida; sin lenguaje libre, hechos verificables, vocabulario abierto, instrucciones contradictorias, contexto largo o evaluación en poblaciones reales. El modelo no comunica necesariamente desconocimiento. Fluidez y cumplimiento dentro del corpus no acreditan verdad, seguridad ni razonamiento general. Las plantillas resolverían directamente la tarea si el objetivo fuera producción.

**Decisión:** usar solo como demostración didáctica del mecanismo y sus controles. El siguiente experimento debería reservar reglas o formatos distintos, definir cómo detectar entradas fuera de alcance y recoger evidencia nueva. Las próximas unidades abordarán inferencia y aplicaciones con modelos existentes, con sus propios recursos y evaluaciones.

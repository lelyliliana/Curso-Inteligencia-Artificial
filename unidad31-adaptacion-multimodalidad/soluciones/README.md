# Soluciones razonadas

[Ejercicios](../ejercicios.md) · [Unidad](../README.md)

1. Para el reglamento, empezar por recuperar el documento vigente y citar sus fragmentos permite actualizar fuentes sin modificar pesos. Para una convención de salida, una regla o plantilla puede bastar; después pueden compararse instrucciones y adaptación si hay ejemplos representativos. RAG no garantiza apoyo factual por sí solo y ajustar no garantiza formato o veracidad: hacen falta criterios de evaluación apropiados.

2. A tiene `2×32=64` y B `26×2=52`: total 116. Respecto a la base, `116/11066≈1,048 %`. El modelo sin fusionar contiene `11066+116=11182` parámetros; la fracción entrenable respecto a ese total es aproximadamente 1,037 %. Ninguno de estos conteos mide memoria pico: faltan activaciones, gradientes, estados del optimizador, precisión y detalles de ejecución.

3. `BA=[[0.5,-0.5,0],[-0.5,0.5,0]]`. Para `x=[2,1,3]` produce `[0.5,-0.5]`. Con escala uno, la salida es `[-0.5,4.5]`; con `alpha/r=2` pasa a `[0,4]`. El [programa manual](03_lora_a_mano.py) conserva el caso de escala uno y contrasta la fusión.

4. B=0 anula la rama añadida. El gradiente hacia A contiene B, mientras que el gradiente hacia B puede usar A y la entrada, ambos no nulos. Con ambas en cero se bloquea el inicio de esa rama. Congelar quita el cálculo de gradientes de parámetros concretos; `eval()` controla comportamiento de módulos; `no_grad()` impide registrar operaciones para autograd en su contexto. No son intercambiables.

5. Se elige LoRA: empata en 24 secuencias exactas y tiene menos parámetros entrenables. La regla se fijó antes de medir; CE solo sería un desempate posterior en esa selección. CE con teacher forcing recibe los tokens anteriores correctos; la generación libre recibe los tokens que produjo el modelo. Un error temprano puede propagarse y reducir secuencias exactas aunque la CE sea razonable.

6. No hay familias compartidas entre las particiones de la adaptación y no se usa prueba para seleccionar época o candidato. Sí existe exposición anterior de algunos prefijos con otro objetivo. Sería incorrecto decir que todo el cierre contiene entradas nunca vistas en ningún entrenamiento. Una reserva más exigente puede excluir del preentrenamiento familias, plantillas o dominios completos y definirla antes de entrenar la base; eso constituye otro experimento.

7. La misma entrada tiene objetivos incompatibles, así que el cambio esperado hace fallar el criterio antiguo. No se midieron capacidades independientes ni un conjunto general de retención. Desactivar LoRA devuelve exactamente los logits de la base porque sus pesos no cambiaron. Un indicador de tarea o prefijos distintos podría permitir ambos comportamientos; habría que entrenarlo y evaluarlo con particiones nuevas.

8. El vector es `[0.20,0.82,0,1]`: dos intensidades y la codificación derecha. La regla toma 0,82 y, al ser mayor que 0,5, responde encendida. Sin texto no sabe qué lado se solicita; sin imagen no conoce los estados. No se hace OCR: el texto llega como otro campo.

9. Un cuarto de escenas es 00 y otro cuarto 11: visión puede responder todas sus consultas. En 01 y 10, la misma imagen tiene igual número de etiquetas 0 y 1; una predicción sin texto solo acierta la mitad. Total máximo: `1/2×1 + 1/2×1/2 = 3/4`. Para cada texto, las etiquetas están equilibradas: máximo 1/2. Mezclar filas de una escena entre particiones reutilizaría sus mismos píxeles y ruido, inflando la independencia aparente de los ejemplos.

10. La política implementada rechaza las tres entradas antes de la MLP: modo de imagen incompatible, modalidad ausente y texto fuera de gramática. No son decisiones aprendidas ni probabilidades de incertidumbre. Si se desea responder con una modalidad faltante, hay que entrenar o definir una ruta específica y medir cobertura/errores por patrón de ausencia. Para ampliar el parser, reservar nuevas familias con negaciones, ambigüedades y paráfrasis, sin volver a usar como cierre los casos que guiaron la modificación.

# Soluciones razonadas — Unidad 20

[Volver a la unidad](../README.md)

## 1. Formas y parámetros

X: `(6,2)`; primer peso PyTorch: `(3,2)`; primer sesgo: `(3,)`; H: `(6,3)`; segundo peso: `(1,3)`; segundo sesgo: `(1,)`; salida de Linear: `(6,1)`; después de `squeeze(-1)`: `(6,)`. Hay 6+3+3+1=13 parámetros. El peso de NumPy W1 es `(2,3)` porque allí se escribe X@W1; Linear escribe X@weight.T. Los sesgos se comparten entre casos, no hay uno nuevo por fila.

## 2. Memoria y autograd

`from_numpy` comparte almacenamiento: cambiar el array afecta al tensor y viceversa. `torch.tensor` copia los valores. `detach()` corta la relación con el grafo, pero mantiene memoria compartida; `detach().clone()` añade una copia independiente. La necesidad de copiar depende de si queremos conservar un estado frente a mutaciones, no simplemente de si calcularemos derivadas.

## 3. Derivada y acumulación

Con w=2, salida=6, residuo=5, L=25/2=12,5 y derivada=5·3=15. El segundo forward crea un grafo nuevo; el segundo backward añade 15 al gradiente existente y deja 30. Tras limpiar, vuelve a ser 15. SGD actualiza w=2−0,1·15=0,5: la nueva salida es 1,5, el residuo 0,5 y la pérdida 0,25/2=0,125. Usar el gradiente acumulado daría w=−1 y otra actualización. El [programa escalar](03_acumular_gradientes.py) reproduce el cálculo sin `retain_graph=True`.

## 4. BCE desde logits

Para s=0, p=0,5. Con y=1, BCE=−log(0,5)=0,693147 y derivada respecto del logit=p−y=−0,5. Como contribución a la media de cuatro casos, la derivada es −0,125. La reducción media pertenece a la pérdida completa; no debe dividirse de nuevo el gradiente por cuatro. Las etiquetas float tienen la misma forma que los logits. La pérdida integrada mantiene el cálculo estable para logits extremos y no necesita una sigmoide previa.

## 5. Lotes de distinto tamaño

La pérdida media por caso es `(2·0,2 + 1·0,8)/3 = 0,4`. La media de medias sin ponderación da 0,5: hace que el caso del último lote tenga tanto peso como los dos del primero juntos. El código de evaluación suma las pérdidas y divide por el número total de casos. Promediar pérdidas durante el entrenamiento introduciría además otro efecto: cada lote habría usado pesos distintos.

## 6. Épocas y actualizaciones

Con 150 casos y lote=32: `[32,32,32,32,22]`, cinco pasos por época, 600 en 120 épocas. Con lote=50: tres lotes de 50, 360 pasos. Con lote=32 y `drop_last=True`: cuatro lotes de 32, se usan 128 casos por época y hay 480 pasos; quedan fuera 22 posiciones de cada permutación. Al barajar, no tienen por qué omitirse siempre los mismos casos. Cambiar tamaño de lote manteniendo épocas conserva recorridos, pero no el número de actualizaciones ni la secuencia del optimizador.

## 7. Modos

`eval()` modifica banderas de los módulos, no la capacidad de registrar derivadas. `no_grad()` afecta al registro dentro de su bloque, no a esas banderas. Linear y Tanh producen el mismo forward en ambos modos para pesos y entradas fijos. Dropout, si se añadiera, tendría otro comportamiento: durante entrenamiento elimina y reescala activaciones; durante evaluación pasa los valores. La prueba de modos lo ilustra aparte del predictor.

## 8. Estado elegido

Se elige la época 10, con BCE 0,40. La época 20 ya es peor aunque el entrenamiento pueda seguir mejorando. `state_dict()` contiene referencias a los tensores; asignarlo a otra variable no congela los valores. Hay que clonar los tensores o guardar una copia en disco en ese momento. En esta unidad se conservan copias inicial, elegida y final. Una copia de pesos tampoco conserva el estado interno del optimizador.

## 9. Interpretación del laboratorio

Red12_8 elige época 110: BCE de entrenamiento 0,2354 y validación 0,1752. En época 120 baja entrenamiento a 0,2308 y sube validación a 0,1766. Esa comparación justifica conservar el estado anterior según el protocolo; no basta una diferencia pequeña en una muestra para afirmar un resultado universal. No hubo parada anticipada: se realizaron las 120 épocas y 600 actualizaciones.

Entrenamiento determina escala, gradientes y referencia constante. Validación determina época y candidato. El umbral 0,5 y el resto de configuración se fijaron antes. La exactitud no decide la selección; se muestra para interpretar errores.

## 10. Inferencia y continuación

Para inferencia necesitamos arquitectura, estado elegido, significado y orden de entradas, preparación y regla de salida; también versiones y límites de uso para reproducir e interpretar. Para reanudar Adam hacen falta además sus momentos y contadores, configuración, estado de generadores y punto de recorrido de datos. El archivo de la unidad no ofrece esa reanudación.

La comprobación guarda, crea un modelo nuevo, carga en CPU, activa eval/no_grad y compara los logits sobre las mismas 80 filas de validación. El error máximo es cero en el entorno probado. Verifica la conservación de la función sobre esas entradas; no prueba generalización, seguridad universal del formato ni identidad entre plataformas. Una igualdad de etiquetas sola sería más débil: probabilidades diferentes pueden cruzar el mismo umbral.

## Cierre didáctico ya publicado

Consulta esta sección después de ejecutar y explicar la selección. Se evaluó una sola vez el candidato elegido con el protocolo original, sin modificarlo al ver el cierre:

```text
Prueba final: solo red12_8; BCE=0.2110; exactitud=0.900; FN=6; FP=2
```

Son 80 casos, 41 positivos: VP=35, VN=37, FP=2 y FN=6. Recobrado=35/41≈0,8537; precisión=35/37≈0,9459; F1≈0,8974. La mayor pérdida y menor exactitud que en validación no invalidan automáticamente el procedimiento; muestran que las muestras y el proceso de selección importan. Se conservan los seis positivos omitidos al describir el alcance. Las ejecuciones automáticas repiten este mismo protocolo para verificarlo; no generan nuevos cierres independientes.

## Orientación para el reto

Una entrega suficiente conserva el resultado de referencia, registra una sola modificación planificada y compara desarrollo con la misma métrica. Un cambio de lote debe indicar épocas y actualizaciones; un cambio de arquitectura debe contar parámetros. Para recarga, registra el mayor error en logits, no solo una captura de pantalla. Si conocías el cierre publicado al diseñar la mejora, usa un cierre nuevo o declara el trabajo como exploración de desarrollo.

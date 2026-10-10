# Soluciones razonadas — Unidad 21

[Volver a la unidad](../README.md)

## 1. Canales y ejes

Una imagen HWC tiene forma `(24,24,3)` y 1728 valores. Un lote de cinco en NCHW tiene `(5,3,24,24)` y 8640 valores. El tensor `[n,c,f,col]` debe conservar el valor que estaba en `[f,col,c]` de la imagen n. `permute` intercambia esos ejes; `reshape` recorre valores en otro orden sin expresar esa correspondencia. Tres canales no equivalen a tres imágenes del lote.

## 2. Correlación manual

Las primeras dos celdas son 1−1=0 y 2−3=−1. El resultado completo es `[[0,−1,−2],[−1,1,2],[2,−1,−3]]`, como comprueba el [programa manual](03_correlacion_a_mano.py). Invertir K en ambos ejes lo convierte en `[[−1,0],[0,1]]`, que en este caso es −K, de modo que invierte los signos. Conv2d usa correlación cruzada; no inviertas el filtro al trasladar este ejemplo a PyTorch.

## 3. Resolución y pool

Con H=16, k=3, p=1 y s=1: floor((16+2−3)/1)+1=16. Con s=2: floor(15/2)+1=8. MaxPool2d(2) sobre `[[1,4],[3,2]]` produce 4; pierde los demás valores y la posición exacta del máximo dentro de la ventana. Una convolución 3×3 sin relleno sobre 24×24 produce 22×22; no es un error de dimensiones.

## 4. Parámetros

Primera convolución: 4·1·3·3+4=40. Segunda: 8·4·3·3+8=296. Capa final: 8·3+3=27. Total CNN=363. El modelo lineal sobre 256 píxeles tiene 256·3+3=771. ReLU, MaxPool y media global no agregan parámetros entrenables. Los mismos pesos convolucionales se aplican en todas las posiciones, pero filtros distintos tienen parámetros distintos.

## 5. Campo receptivo

Comienza con región r=1 y separación j=1 entre posiciones. Cada capa con kernel k y paso s produce `r_nuevo=r+(k−1)j` y `j_nuevo=j·s`. Conv3: r=3,j=1. Pool2: r=4,j=2. Conv3: r=8,j=2. Son regiones teóricas del interior; los bordes incluyen relleno. La media global reúne el mapa completo, y el clasificador produce tres logits, no coordenadas. No puede deducirse una caja de detección de esos logits por sí solos.

## 6. Entropía cruzada

Exponenciar [0,log(2),0] da [1,2,1]. Dividir entre 4 produce [0,25;0,5;0,25]. Para clase real 1, CE=−log(0,5)=log(2)≈0,693147. El lote usa logits `(N,3)` float32 y etiquetas `(N,)` int64 con índices 0,1,2. No se aplica softmax antes de `cross_entropy`; para mostrar probabilidades sí se aplica una transformación equivalente estable. Sumar una misma constante a los tres logits de una fila no cambia softmax ni CE.

## 7. Aumentos y etiquetas

Reflejar horizontalmente conserva trazos horizontales y verticales y cambia la inclinación diagonal dentro de la misma clase. Girar 90° intercambia horizontal y vertical; conservar esas etiquetas introduciría una contradicción. El aumento modifica la presentación de las mismas escenas, no su procedencia: 60 escenas con dos vistas y múltiples reflejos siguen siendo 60 escenas de entrenamiento. Las transformaciones de entrenamiento no deben pasar accidentalmente al cargador de validación.

## 8. Matriz multiclase

Exactitud=(20+19+20)/60=59/60≈0,9833. Para vertical, recobrado=19/20=0,95 y precisión=19/19=1. Para diagonal, precisión=20/21≈0,9524 y recobrado=20/20=1. Los F1 son 1; 38/39≈0,97436; 40/41≈0,97561. Macro F1 es su media: aproximadamente 0,98332.

La constante predice siempre horizontal por empate: F1 horizontal=40/(20+60)=0,5; los otros dos F1 son 0. Macro F1=0,5/3=1/6. Precisión de vertical y diagonal es indefinida porque no hay predicciones de esas clases; se guarda `null`. Su recobrado sí es 0, porque hay 20 casos reales de cada una y ninguno se detecta. No confundas cero con denominador ausente.

## 9. Estados y aumento

Lineal elige época 5: CE entrenamiento 0,0899 y validación 0,9929. Al final, entrenamiento baja a 0,0030 mientras validación sube a 1,4859. La capacidad de memorizar intensidades de estas imágenes no respalda el uso en escenas nuevas.

Las dos CNN eligen época 45. Sin aumento, CE validación=0,0707; con reflejo, 0,0781. Ambas aciertan 59 vistas, pero asignan probabilidades distintas. Gana la primera según CE. Esto no demuestra que el aumento nunca sirva: se examinó una transformación, un problema y una semilla concretos. Tampoco debe cambiarse el criterio después para favorecer una opción esperada.

## 10. Recarga e información ausente

Guardar arquitectura, pesos elegidos, orden de clases, modo L, resolución, divisor 255, media y desviación de entrenamiento. Crear una instancia nueva, cargar en CPU, usar eval/no_grad y comparar logits sobre las mismas entradas. Se obtuvo error máximo 0,0. Eso comprueba la inferencia sobre esas imágenes en este entorno; no garantiza generalización ni permite reanudar Adam sin sus momentos, contadores y estados aleatorios.

En la vista ocluida 022-v1, la etiqueta procede del trazo original. Antes de cambiar la CNN conviene examinar la imagen de origen, qué parte se cubrió, si quedan pistas suficientes y si el uso previsto permite abstenerse o pedir otra vista. No cambiar retrospectivamente la etiqueta para hacer desaparecer el error. Cualquier nueva política requeriría un protocolo y evaluación propios.

## Cierre didáctico publicado

Se conservó la elección de desarrollo y se abrió prueba después:

```text
Prueba final: solo cnn; CE=0.0406; exactitud=0.983; macro F1=0.983
```

| Real / Predicha | Horizontal | Vertical | Diagonal |
|---|---:|---:|---:|
| Horizontal | 19 | 0 | 1 |
| Vertical | 0 | 20 | 0 |
| Diagonal | 0 | 0 | 20 |

Son 59 aciertos entre 60 vistas de 30 escenas; el fallo es horizontal→diagonal. La exactitud coincide con validación, pero el error cambia de clase y CE baja a 0,0406394. Igual exactitud no implica mismas probabilidades, mismo error o misma dificultad. No se ajustaron arquitectura, época o política después de observarlo. Las comprobaciones automáticas repiten el protocolo; no generan nuevas evaluaciones independientes.

## Orientación para el reto

Una buena entrega no necesita superar 59/60. Debe justificar procedencia, separación, transformación y métrica, conservar la referencia y documentar los resultados desfavorables. Si cambias aumentos, incluye una imagen antes/después y explica la validez de su etiqueta. Si conocías este cierre al diseñar el cambio, usa otro cierre fijado previamente o presenta solo un estudio de desarrollo.

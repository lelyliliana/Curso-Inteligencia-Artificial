# Soluciones razonadas — Clasificación

[Volver a la unidad](../README.md)

## 1. Formulación y disponibilidad

La unidad es un caso sintético de inspección. La entrada es `senal_previa`, un índice adimensional entre 0 y 100 declarado disponible antes de la decisión. El objetivo `revision_confirmada` se conoce después; 1 indica necesidad de revisión confirmada y es la clase positiva.

Usar el resultado de inspección o la propia etiqueta como entrada sería filtración de información posterior. Harían falta, entre otros elementos, marcas de tiempo de decisión, disponibilidad y recepción de la señal para auditar el supuesto. `caso_id` ayuda a seguir las filas, pero no demuestra disponibilidad ni debe entrar al predictor. Los datos no representan una instalación real.

## 2. Puntuación, probabilidad y clase

Con a = −1, b = 2 y z = 1, la puntuación es `s = −1 + 2 × 1 = 1`. La probabilidad estimada es `p = 1/(1+exp(−1)) ≈ 0,731059`.

Con umbral 0,5 se predice 1; con 0,8 se predice 0. Se conserva el modelo, la entrada, el logit y la probabilidad. Solo cambia la regla de decisión. La clase no es una nueva probabilidad, y ninguno de los umbrales modifica la evidencia observada.

## 3. Un paso de gradiente

Centro = `(40 + 60)/2 = 50`. Escala poblacional = `raiz((100 + 100)/2) = 10`. Las entradas transformadas son −1 y 1.

Inicialmente p = 0,5 en ambos casos. El gradiente del intercepto es cero; el del coeficiente es −0,5. La penalización aporta `lambda × b = 0` porque b empieza en cero. Con tasa 0,2:

```text
a_nuevo = 0 − 0,2 × 0 = 0
b_nuevo = 0 − 0,2 × (−0,5) = 0,1
```

Después, p ≈ `0,475021; 0,524979`. La pérdida media es aproximadamente 0,644397 y la penalización es `0,01 × 0,1² / 2 = 0,00005`. El objetivo total es aproximadamente **0,644447**, inferior al inicial 0,693147. El [programa del paso manual](03_paso_manual.py) reproduce estos valores.

El escalado usa `ddof=0`, divisor n, no la desviación muestral con divisor n−1. En los laboratorios se aprende con todo entrenamiento; aquí usamos dos casos únicamente para poder seguir el cálculo.

## 4. Pérdida y generalización

Si y = 1, la pérdida es `−ln(p)`. Para p = 0,8 da aproximadamente 0,223144; para p = 0,2, 1,609438. Cuanto menor es la probabilidad asignada a la clase real, mayor es la pérdida.

Bajar el objetivo de entrenamiento muestra mejor ajuste según esa función en los casos usados. No mide por sí solo desempeño en casos nuevos. Además, el objetivo del ajuste incluye la penalización y no es la misma cantidad que F1 de validación. Hay que conservar separación, comparar referencias y evaluar el procedimiento elegido en el cierre.

## 5. Matriz manual

Clase positiva: 1. Filas reales y columnas predichas:

| | Predicción 0 | Predicción 1 |
|---|---:|---:|
| Real 0 | VN = 2 | FP = 1 |
| Real 1 | FN = 1 | VP = 1 |

Exactitud = `3/5 = 0,6`; precisión = `1/2 = 0,5`; recobrado = `1/2 = 0,5`; F1 = `2/(2+1+1) = 0,5`. Cada caso se cuenta una sola vez. Cambiar orientación sin modificar los rótulos intercambiaría la interpretación de FP y FN.

## 6. Las dos referencias en datos desbalanceados

| Regla | VP | VN | FP | FN | Exactitud | Precisión | Recobrado | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Siempre 0 | 0 | 86 | 0 | 14 | 0,86 | Indefinida | 0 | 0 |
| Siempre 1 | 14 | 0 | 86 | 0 | 0,14 | 0,14 | 1 | 28/114 ≈ 0,246 |

En la primera regla, precisión tiene denominador cero porque no hay predicciones positivas. Recobrado sí es cero: existen 14 positivos y no se recupera ninguno. F1 también es cero usando su fórmula de conteos.

Exactitud alta puede provenir solo de acertar la clase frecuente. Recobrado uno puede obtenerse marcando todo, con muchas falsas alertas. Las referencias hacen explícito qué debe mejorar un modelo; ninguna métrica aislada decide qué errores son aceptables en una operación real.

## 7. Resultado del umbral 0,2

Con `VP=10, VN=71, FP=15, FN=4`:

```text
precision = 10/(10+15) = 0,4
recobrado = 10/(10+4) = 5/7 ≈ 0,714286
F1 = 20/(20+15+4) = 20/39 ≈ 0,512821
exactitud = (10+71)/100 = 0,81
```

Ese candidato gana por F1 de validación. Tiene menor exactitud que mayoría, pero recupera diez positivos que esa referencia omite. No se cambió el criterio después de ver los resultados y no se consultó prueba. Aun así, el experimento no demuestra que quince FP sean aceptables ni que el umbral sirva para otro dataset.

## 8. Mismas probabilidades, otras decisiones

Con p = `0,1; 0,4; 0,6; 0,9` y reales `0, 1, 0, 1`:

| Umbral | Predicciones | VP / VN / FP / FN | Precisión | Recobrado | F1 |
|---:|---|---|---:|---:|---:|
| 0,5 | 0, 0, 1, 1 | 1 / 1 / 1 / 1 | 0,5 | 0,5 | 0,5 |
| 0,3 | 0, 1, 1, 1 | 2 / 1 / 1 / 0 | 2/3 | 1 | 0,8 |

Las probabilidades siguen iguales. Su pérdida logarítmica media sigue siendo `−(ln(0,9) + ln(0,4) + ln(0,4) + ln(0,9))/4 ≈ 0,510826`. Esta métrica no depende del umbral.

Aquí mejora precisión porque el nuevo positivo predicho era un positivo real. Si bajáramos hasta 0,1 —incluyendo la igualdad— se marcarían todos los casos y precisión caería a 0,5. Por eso un umbral menor no garantiza más precisión ni más F1. El recobrado no disminuye al ampliar el conjunto de positivos predichos sobre los mismos casos.

## 9. Calibración y certeza

p = 0,8 es una estimación del modelo, no una garantía de certeza sobre un caso. Para sostener calibración se necesita comprobar, con suficientes observaciones apropiadas y no usadas para ajustar esa evaluación, que grupos de probabilidades próximas a 0,8 presentan una proporción positiva próxima a 80 %.

Un F1 alto describe decisiones para un umbral y no determina esa correspondencia probabilística. La función sigmoide tampoco la certifica. Haría falta revisar tamaños, cobertura, estabilidad, cambios de prevalencia y condiciones de recolección. La rejilla sintética y pública del curso no sustituye esa evidencia.

## 10. Cierre sin reselección

Una respuesta posible:

> Conservo el código, protocolo, huellas de entrenamiento y validación, centro, escala, coeficientes, referencias y candidato con su umbral. Exporto primero la comparación de desarrollo. Ejecuto después el mismo laboratorio con `--evaluar-prueba` hacia otro directorio y compruebo que esos elementos coincidan. Informo la matriz y las métricas del elegido sin buscar otro umbral por el resultado final.

Si prueba contiene solo negativos, se conserva esa partición y se informa que no permite medir recobrado de positivos. Si no hay positivos reales ni predichos, precisión, recobrado y F1 quedan indefinidos; si existen FP, precisión y F1 son cero, mientras recobrado sigue indefinido. No se reemplaza `null` por una puntuación favorable.

Si los resultados inspiran otro umbral, esa prueba ya participó en desarrollo y hace falta planear una evaluación nueva. Si se habían leído las respuestas públicas, debe declararse: el ejercicio sigue siendo reproducible, pero no es una evaluación personal ciega.

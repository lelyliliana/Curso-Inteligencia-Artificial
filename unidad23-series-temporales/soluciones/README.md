# Soluciones razonadas — Unidad 23

[Unidad y enunciados](../README.md) · [Ventana manual ejecutable](03_ventana_a_mano.py)

## 1. Tipo de tarea y componentes

Pronosticar estima una lectura futura. Detectar un cambio compara lo observado con un criterio de referencia. Clasificar una secuencia asigna una etiqueta a una ventana. El laboratorio implementa únicamente pronóstico; no entrena ni evalúa un detector de cambios.

La frecuencia prevista es una hora. El término `0,04·t/24` produce tendencia; las funciones seno introducen patrones de 24 y 168 horas. Los saltos de +2,5 y −1,8 °C son cambios de nivel conocidos por construcción. El ruido tiene desviación 0,15 °C. Esa descomposición describe el generador ficticio, no una ley física aprendida de sensores reales.

## 2. Evento, llegada y objetivo

La lectura de las 07:00 que llega a las 09:30 no puede usarse a las 08:10. Una lectura medida a las 08:00 que llegue a las 08:10 sí está disponible, si contiene un valor válido y no tiene un conflicto conocido. En la muestra esa lectura está vacía, por lo que no aporta temperatura.

Con h=1, el objetivo es 09:00 y la anticipación desde 08:10 es 50 minutos. Con h=6, el objetivo es 14:00 y la anticipación es 5 horas 50 minutos. Decir «una hora desde la emisión» cambiaría el objetivo y no describiría este experimento.

## 3. Historia conocida

La historia a las 08:10 es `[20,21,21,23,24,24,26,26,26]`. El hueco de las 02:00 conserva 21; el conflicto de las 05:00 conserva 24; el retraso de las 07:00 y el vacío de las 08:00 conservan 26. No promediamos 25 y 35 para inventar una referencia a las 05:00: quedan en conflicto desde que ambos registros están disponibles.

La media preparada de 06:00 a 08:00 vale 26. Dos de esas tres posiciones son relleno, por lo que no equivale a tres mediciones iguales. Al recibirse la lectura atrasada, otra decisión puede reconstruir una historia diferente. El informe anterior debe conservar la información que realmente utilizó.

## 4. Ventana causal y centrada

Con origen 2, la ventana anterior termina en 14: su media es `(10+12+14)/3=12`. Cambiar el valor del índice 3 de 16 a 100 no modifica ninguna de esas entradas. La media centrada usa los índices 1, 2 y 3: antes valía 14 y después 42. Su sensibilidad al futuro demuestra que no estaba disponible al emitir la predicción.

La persistencia vale 14 y la referencia estacional de periodo 2 vale `y(3−2)=12`. Sus errores cambian cuando cambia el objetivo; sus predicciones no. [El programa manual](03_ventana_a_mano.py) contrasta ambas medias sin entrenar un modelo.

## 5. Ocho características

Con y(t)=t, origen 30 y h=6, el objetivo es hora 36. La misma hora del día anterior es `36−24=12`. Actual=30, anterior=29, estacional24=12. La ventana de 24 posiciones va de 7 a 30; su media es `(7+30)/2=18,5`.

La hora local del objetivo es 12: seno=`sin(π)=0` salvo error numérico y coseno=−1. Sin ausencias, fracción rellenada=0 y edad=0. El vector completo es `[30;29;12;18,5;0;−1;0;0]`. Usar siempre t−24 daría 6, una hora distinta del objetivo estacional requerido.

## 6. Fronteras, disponibilidad y cobertura

Si h=6 y el bloque acaba en hora 575, el último origen admisible por frontera es 569: su objetivo es 575. Los orígenes 570–575 apuntan al bloque siguiente y se omiten. Además, la lectura objetivo 575 llega en hora 576:30; a la primera decisión de validación, 576:10, aún no está disponible. Por eso tampoco puede entrenar esa fila.

En validación a una hora hay 192 orígenes posibles. Se excluyen dos objetivos ausentes, dos vacíos, uno conflictivo, uno tardío para la selección y uno que cruza el final del bloque. Quedan `192−2−2−1−1−1=185`. La lectura objetivo no se rellena para puntuar; sí pueden rellenarse entradas con datos previos y marcarse como tales.

El conjunto de seis horas contiene 180 casos porque cruza la frontera en seis orígenes. Comparar sus métricas con las de una hora ayuda a describir dificultad, pero no usa exactamente los mismos objetivos. Una comparación emparejada requeriría definir un subconjunto común antes de interpretar diferencias como efecto aislado del horizonte.

## 7. Preparación y calendario

La media y escala describen las entradas de entrenamiento. Si se estiman con validación o prueba, se incorpora su distribución al ajuste aunque no se lean etiquetas. `StandardScaler` recibe solo la matriz de entrenamiento y el estado se conserva para todo lo demás.

En cambio, la hora del objetivo ya puede calcularse cuando se emite el pronóstico: es origen más horizonte. Seno y coseno representan su posición cíclica. La temperatura que se observará entonces no está disponible. Que dos campos contengan la palabra «futuro» no significa que tengan la misma disponibilidad.

## 8. Errores y cambio de nivel

Los errores firmados son `[1,−1,2]`. MAE=`(1+1+2)/3=4/3`; RMSE=`sqrt((1+1+4)/3)=sqrt(2)`; sesgo=`(1−1+2)/3=2/3`. El sesgo positivo indica sobreestimación media, pero no explica por sí solo la magnitud de todos los errores.

En validación a una hora, el MAE global 0,2222 oculta 0,6877 en la transición y 0,1561 en el resto. A seis horas, los valores son 0,3710, 1,4102 y 0,2187. Las medias por periodo deben ponderarse por sus cantidades de casos para recuperar la media global; no se promedian sin atender al denominador. Los intervalos o contrastes estadísticos tendrían que considerar dependencia temporal.

## 9. Orígenes sucesivos frente a recursión

En orígenes sucesivos se emite una predicción nueva cada hora, con la información recibida hasta esa decisión. Puede utilizar una lectura real anterior de prueba si ya llegó. Esa lectura no estaba disponible para un origen anterior y nunca debe incorporarse retroactivamente.

En una trayectoria recursiva emitida de una sola vez se predice un paso, se incorpora esa predicción como entrada y se continúa sin recibir observaciones reales intermedias. Sus errores pueden propagarse. Este laboratorio no implementa ese procedimiento y sus métricas no lo validan.

## 10. Persistencia y evaluación futura

Se guardan formato, horizonte, inicio y frecuencia de rejilla, offset, regla de decisión, relleno, ventana, límite de antigüedad, orden de entradas, medias, escalas, coeficientes e intercepto. También se registran versiones y huellas. Para inferencia hacen falta las lecturas recientes y sus tiempos de llegada; el modelo por sí solo no contiene esa historia ni recibe eventos.

Una evaluación posterior podría reservar periodos nuevos de sensores con procedencia conocida, cortes temporales y latencia medida. Debe fijar de antemano horizonte, costo tolerable, cobertura mínima y qué hacer ante datos obsoletos o cambios. Compararía con persistencia y estacionalidad en los mismos casos, mantendría periodos de transición y reportaría fallos. Obtener peor resultado que la referencia o cobertura insuficiente refutaría una propuesta de uso, aunque el promedio del ejercicio sintético sea pequeño.

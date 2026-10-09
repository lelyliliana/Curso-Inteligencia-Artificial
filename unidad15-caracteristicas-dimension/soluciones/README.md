# Soluciones razonadas

[Unidad](../README.md) · [Proyección manual ejecutable](03_proyectar_a_mano.py)

## 1. Característica derivada

Las originales son `(4 h,3 kW)`. La representación ampliada es `(4 h,3 kW,12 kWh)`. El producto es una energía nominal basada en el plan. No es una lectura nueva ni el consumo final observado; conserva los supuestos y posibles errores de las entradas previstas.

La fórmula no crea información nueva respecto de horas y potencia, pero permite a una regresión lineal en sus características representar un término multiplicativo.

## 2. Disponibilidad

Horas y potencia previstas son entradas permitidas por el escenario. `caso_id` identifica, sin significado predictivo justificado. `consumo_final_kwh` es la etiqueta posterior y `lectura_cierre_kwh` también llega después del ciclo: ambos quedan fuera de las entradas.

La lectura de cierre fue construida como `1000+consumo_final`. Sería fácil recuperar el objetivo con ella, pero no estaría disponible cuando se necesita predecir. Que una columna sea numérica y esté en el CSV no la vuelve admisible. Al no haber fechas reales, la disponibilidad es declarada, no auditada.

## 3. Redundancia

Si minutos=`60×horas`, los términos `b_h×horas+b_m×minutos` se reducen a `(b_h+60b_m)×horas`. Muchos pares de coeficientes producen la misma predicción; no se pueden identificar por separado solo con esos datos.

Estandarizar ambas columnas no elimina la redundancia exacta. PCA puede representar ese subespacio con menos ejes, pero el protocolo del laboratorio rechaza matrices sin rango suficiente para comparar regresiones completas identificables.

## 4. Predicción e interacción

En el ejemplo pequeño sin ruido, la relación es `3+0,8×horas×potencia`. Para 3 horas y 3 kW: `3+0,8×9=10,2 kWh`. La consulta al pipeline entrega `[3,3,9]`, en el mismo orden de columnas utilizado al ajustar.

La fórmula es lineal en sus coeficientes; contiene un producto de entradas y por eso no es aditiva en horas y potencia. Este cálculo corresponde al ejemplo de cuatro casos del texto, no a los coeficientes exactos del laboratorio con ruido. Para ese laboratorio deben utilizarse escala y coeficientes completos del JSON.

## 5. Covarianza y ejes

Las sumas de las coordenadas son cero, por lo que la media es `(0,0)`. Las sumas de cuadrados de cada coordenada son 10 y la suma de productos cruzados es 8. Dividir entre `4−1=3` da la matriz indicada en la unidad.

Multiplicar por `(1,1)/sqrt(2)` da 6 veces ese vector; multiplicar por `(1,−1)/sqrt(2)` da `2/3` veces el segundo. Son ejes ortogonales de varianzas 6 y `2/3`. La primera proporción es `6/(6+2/3)=0,9`.

## 6. Proyectar y reconstruir

Para `(2,1)`, la coordenada sobre el primer eje es `3/sqrt(2)`. Multiplicarla por `(1,1)/sqrt(2)` da `(1,5;1,5)`. El residuo es `(0,5;−0,5)`: norma cuadrada 0,5 y error medio por dos celdas 0,25.

Si el eje cambia de signo, la coordenada pasa a `−3/sqrt(2)`. El producto de ambos signos negativos conserva `(1,5;1,5)`. Comparar signos de ejes sin tener en cuenta esa equivalencia puede hacer parecer diferentes dos proyecciones iguales.

## 7. Dos divisores y dos objetivos

El escalador calcula desviación con divisor `n`. Después PCA estima varianzas de sus entradas centradas con divisor `n−1`. Son convenciones de pasos diferentes. En el ejemplo manual no se estandariza: se usa directamente la covarianza de los cuatro puntos centrados.

El 90 % indica variación de entradas retenida. No hay un objetivo predictivo en ese cálculo. No puede interpretarse como 90 % de aciertos, R² de una predicción ni probabilidad de éxito.

## 8. Mucha varianza, mala predicción

`pca1` conserva 99,9343 % de la varianza de entrenamiento y obtiene MSE de reconstrucción en z de aproximadamente 0,000658 en validación. Sin embargo, su MAE del objetivo es 1,713 frente a 0,157 de `completa`.

Las medidas responden preguntas distintas. La diferencia pequeña entre señales informa sobre la respuesta en este generador; al descartarla se pierde capacidad predictiva. El criterio fijado era MAE de validación, no porcentaje de varianza. Una representación reducida puede ser útil en otros contextos; este ejemplo no demuestra que PCA sea siempre perjudicial.

## 9. Rotación completa

Dos componentes de dos entradas no reducen dimensión. Con ejes ortonormales completos se puede recuperar z a partir de sus coordenadas, salvo precisión numérica. Una regresión lineal con intercepto y sin penalización puede expresar las mismas funciones en ambas bases.

Por eso `pca2` y `completa` producen predicciones prácticamente iguales. La tolerancia absoluta `1e−10` declara empate numérico y el orden previo elige `completa`. No se usa una diferencia microscópica para atribuir una ventaja estadística o práctica a PCA.

## 10. Comprobar separación

En una copia, cambia solo objetivos de prueba. Deben conservarse escala, ejes, regresión, selección, resultados de desarrollo y predicciones para las mismas entradas. Cambian la huella de prueba y los objetivos; las métricas y residuos pueden cambiar. No es necesario que todas las métricas cambien en cualquier modificación posible.

En otra copia, cambia la lectura posterior de entrenamiento manteniéndola dentro del dominio válido. Deben conservarse características permitidas, parámetros y predicciones; cambia la huella de ese archivo completo. Si el ajuste cambiara, habría que investigar una utilización indebida de la columna. Editar una huella no es parte de la prueba: se recalcula al leer el archivo.

Las pruebas automatizadas comprueban el flujo del código, no que una persona haya evitado mirar el generador o los resultados públicos antes del cierre.

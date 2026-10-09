# Soluciones comentadas — Unidad 3

Compara primero con tu desarrollo. Si una operación difiere, revisa orden de características, signo del residuo, dimensiones y redondeo antes de cambiar el código.

## 1. Representación

Una convención posible es `[temperatura_c, humedad_relativa_porcentaje, ocupacion_personas]`. La primera componente se expresa en °C, la segunda en porcentaje de humedad relativa y la tercera es un conteo.

Para interpretar `[24,70,12]` necesitamos esa convención, qué entidad describe, lugar, instante de medición, procedencia y tratamiento de faltantes. Un vector de tres componentes no aporta por sí solo esa información.

Intercambiar temperatura y humedad sin cambiar el esquema cambia el significado de las entradas. La longitud sigue siendo tres, por lo que una comprobación de dimensiones no detecta necesariamente el error.

## 2. Operaciones vectoriales

Para $\mathbf{u}=[1,2,3]$, $\mathbf{v}=[4,0,-1]$:

- Suma: `[5,2,2]`, un vector de tres componentes.
- $3\mathbf{u}$: `[3,6,9]`, un vector de tres componentes.
- Producto punto: $1\times4+2\times0+3\times(-1)=1$, un escalar.
- Norma: $\sqrt{1+4+9}=\sqrt{14}\approx3.741657$, un escalar.
- Diferencia: `[-3,2,4]`; distancia: $\sqrt{9+4+16}=\sqrt{29}\approx5.385165$, un escalar.

El producto punto puede ser negativo o cero; la norma y la distancia nunca son negativas.

## 3. Predicción y unidades

$$
\hat y=4\times0.5+2\times2+1=7
$$

Cuatro horas son 240 minutos. El peso de esa característica pasa a $0.5/60=1/120$:

$$
240\times(1/120)+2\times2+1=7
$$

Cambiar la unidad de entrada exige cambiar el coeficiente para conservar la función. La reducción del peso no demuestra menor importancia de esa característica.

Si en el Laboratorio 1 cambias el peso de horas de 0.5 a 1, las tres predicciones son `[9,11,14]`. Añadir filas aumenta las observaciones y salidas, pero mantiene dos pesos y un sesgo.

## 4. Matrices

$$
A^T=\begin{bmatrix}1&3\\2&4\end{bmatrix},\qquad
AB=\begin{bmatrix}4&4\\10&8\end{bmatrix},\qquad
BA=\begin{bmatrix}2&4\\7&10\end{bmatrix}
$$

$AB\ne BA$. Ambos productos están definidos, pero la multiplicación de matrices no es conmutativa en general.

Tomando $[1,1]^T$ como vector columna, $A[1,1]^T=[3,7]^T$ tiene forma $(2,1)$. El producto $A^TA$ tiene forma $(2,2)$ y vale:

$$
A^TA=\begin{bmatrix}10&14\\14&20\end{bmatrix}
$$

En el ejemplo de tres observaciones de la unidad, $X^TX=\begin{bmatrix}49&33\\33&38\end{bmatrix}$. Ambos ejemplos deben comprobarse por sus propias dimensiones; no son la misma matriz.

## 5. Escalado

Mínimo 2, máximo 6:

$$
z(4)=(4-2)/(6-2)=0.5,\qquad z(8)=(8-2)/(6-2)=1.5
$$

El dato de prueba puede exceder uno porque supera el máximo observado en entrenamiento. No se recalcula el máximo con prueba.

Para `[5,5,5]`, el denominador es cero. Podemos retirar la característica constante o mapearla a cero mediante una política documentada. Si en uso aparecen otros valores, debemos revisar esa política y el cambio de contexto.

El vector `[0,0]` tampoco puede normalizarse a longitud uno: tiene norma cero. Escalar columnas y normalizar filas resuelven preguntas distintas.

## 6. Errores

Los residuos son `[1,-1,2]`.

$$
\operatorname{MSE}=(1+1+4)/3=2
$$

$$
\operatorname{RMSE}=\sqrt{2}\approx1.414214,\qquad
\operatorname{MAE}=(1+1+2)/3=4/3\approx1.333333
$$

El promedio de residuos es $2/3$. Puede ser útil para observar una tendencia a sobreestimar o subestimar, pero permite que errores de signos opuestos se cancelen. No sustituye una medida de magnitud de error.

Si las referencias tienen unidad kWh, MSE tiene unidad kWh², mientras RMSE, MAE y residuos tienen unidad kWh.

## 7. Descenso de una cuadrática

Inicio 5, tasa 0.1:

$$
L'(5)=4,\quad w_1=5-0.1(4)=4.6
$$

$$
L'(4.6)=3.2,\quad w_2=4.6-0.1(3.2)=4.28
$$

Las pérdidas son 4 al inicio, 2.56 tras el primer paso y 1.6384 tras el segundo.

Con tasa 1: $w_1=1$ y $w_2=5$. Oscila entre ambos valores; la pérdida permanece en 4. El intervalo estable $0<\eta<1$ pertenece a $L=(w-3)^2$.

Con tasa 0.75 desde cero, el error respecto al mínimo se multiplica por -0.5. Cruza de lado, pero su magnitud se reduce; cruzar el mínimo no implica divergir.

Si la pérdida cambia a $10(w-3)^2$, su derivada es $20(w-3)$ y la condición se vuelve $|1-20\eta|<1$: $0<\eta<0.1$. Multiplicar la pérdida por diez cambia la escala del gradiente.

## 8. Dos parámetros

Con casos $(0,1),(1,3)$ e inicio cero, las predicciones son `[0,0]`, residuos `[-1,-3]` y pérdida $(1+9)/2=5$.

$$
\frac{\partial L}{\partial w}=\frac{2}{2}(0\times(-1)+1\times(-3))=-3
$$

$$
\frac{\partial L}{\partial b}=\frac{2}{2}(-1-3)=-4
$$

Con tasa 0.1, la actualización simultánea produce $w=0.3$, $b=0.4$. Las predicciones nuevas son `[0.4,0.7]`, residuos `[-0.6,-2.3]`:

$$
L=(0.36+5.29)/2=2.825
$$

No debe confundirse este ejercicio de dos casos con el laboratorio de cuatro casos: cambian las sumas, el promedio, la tasa y la actualización.

## 9. Diferencias centrales

Usando los dos casos del ejercicio 8:

```python
casos = [(0, 1), (1, 3)]

def mse(w, b):
    return sum((w * x + b - y) ** 2 for x, y in casos) / len(casos)

epsilon = 1e-6
dw = (mse(epsilon, 0) - mse(-epsilon, 0)) / (2 * epsilon)
db = (mse(0, epsilon) - mse(0, -epsilon)) / (2 * epsilon)
print(dw, db)  # Aproximadamente -3 y -4
```

Puedes comparar con tolerancia absoluta $10^{-7}$. Los pequeños errores de coma flotante justifican usar una tolerancia, no exigir igualdad exacta de números calculados por caminos distintos.

El programa [01_comprobar_gradientes.py](01_comprobar_gradientes.py) carga el laboratorio con `importlib`, porque su archivo empieza por un número y no puede importarse con la sintaxis usual de un nombre de módulo. Al importarlo no se ejecuta su función principal.

```bash
python unidad03-matematica-aplicada/soluciones/01_comprobar_gradientes.py
```

El programa usa los **cuatro casos de entrenamiento del laboratorio**, por lo que en $(w,b)=(0,0)$ las derivadas son -17 y -8. Repite la comparación en `(1.2,0.7)` y `(2,1)`. No usa las referencias de prueba.

Termina con código 0 si todas las diferencias están dentro de la tolerancia absoluta, 1 si alguna la supera y 2 si la configuración no es válida o ocurre un error numérico. La comprobación en unos puntos ayuda a detectar errores; no demuestra corrección para cualquier entrada.

Si usas `--epsilon 1e-20`, sumar ese incremento a un parámetro como 1.2 puede no cambiar su representación en coma flotante. La aproximación puede fallar por precisión numérica. Por eso un resultado diferente necesita analizarse, no atribuirse automáticamente a la derivada.

## 10. Interpretación de la evaluación

El MSE mostrado como `0.0000000000` está redondeado a diez decimales. Con 500 pasos, los parámetros se aproximan a `(2,1)` y la pérdida es positiva y muy pequeña. La forma de impresión no prueba igualdad exacta.

Los parámetros dependen de los cuatro casos de entrenamiento, inicio cero, tasa y número de pasos. La línea base depende del promedio de las referencias de entrenamiento. Las referencias de prueba influyen en la evaluación, pero no en esas cantidades.

Si modificamos solo las referencias de prueba, el entrenamiento debe mantenerse. Conservar parámetros iguales y observar métricas distintas es una comprobación de esa separación.

Con cero pasos, la recta predice 0: MSE de prueba $(9^2+11^2)/2=101$. Con un paso, predice 3.8 y 4.65; MSE de prueba $(5.2^2+6.35^2)/2=33.68125$. La línea base se mantiene en 37.

Para evaluar consumos reales necesitamos datos pertinentes, procedencia, calidad, disponibilidad de variables en el momento de predecir, división temporal o por grupos según el caso, línea base apropiada y métricas interpretadas en el contexto del usuario. Una partición independiente debe mantenerse fuera de la selección de configuraciones.

El ejemplo de solo seis observaciones sin ruido no permite medir esas condiciones.

## Orientación para el reto

Un informe sólido explica una actualización a mano, reproduce los comandos, registra cambios de tasa y muestra la misma línea base en condiciones comparables. Puede concluir que cierta tasa diverge o que hace falta más evidencia; esos hallazgos son válidos si están documentados.

No basta con una captura del resultado final. Debe poder reconstruirse qué datos y parámetros produjeron cada resultado.

[Volver a la unidad](../README.md) · [Ver el reto](../reto.md)

# Unidad 3 — Matemática aplicada: vectores, matrices y optimización

[Unidad anterior: del problema al proyecto](../unidad02-proyecto-ia/README.md) · [Volver al índice](../README.md)

Un modelo recibe números, calcula una salida y, durante el entrenamiento, modifica sus parámetros para reducir una pérdida. Para comprender ese proceso necesitamos saber cómo se organizan los números, qué operaciones son válidas y qué significa mejorar una función.

Esta unidad conecta el cálculo a mano con tres programas pequeños. Comenzaremos representando observaciones como vectores; después calcularemos varias predicciones con una matriz y finalmente ajustaremos una recta mediante descenso de gradiente. Cada operación debe poder explicarse antes de ejecutarse.

## Objetivos

Al terminar podrás:

- Distinguir escalar, vector, matriz y tensor por su organización.
- Definir el significado y el orden de las componentes de una observación.
- Calcular suma, multiplicación por escalar, producto punto, norma y distancia.
- Comprobar dimensiones en productos de matrices y vectores.
- Explicar una predicción lineal mediante pesos y sesgo.
- Calcular residuos y error cuadrático medio sin cancelar los errores.
- Interpretar derivadas, derivadas parciales y gradientes.
- Realizar una actualización de parámetros y analizar la tasa de aprendizaje.
- Separar el ajuste de parámetros de la evaluación en registros de prueba.
- Reconocer las limitaciones de un resultado obtenido con datos sintéticos.

## Antes de comenzar

Completa las unidades 0 a 2. Necesitas operaciones aritméticas, listas, funciones y bucles de Python. Repasaremos las ideas matemáticas al usarlas; no necesitas haber cursado cálculo universitario.

Los ejemplos usan únicamente la biblioteca estándar, CPU y archivos locales. Se verificaron con Python 3.12.14 en Linux. Activa tu entorno virtual y ejecuta los comandos desde la raíz del curso.

Si trabajas con calculadora, conserva varios decimales durante las operaciones. El redondeo final de una tabla no convierte una aproximación en una igualdad exacta.

## 1. Los números necesitan significado

Imagina una observación ficticia de una zona: dos horas de uso y tres equipos activos. Escribimos:

$$
\mathbf{x} = [2, 3]
$$

El primer número corresponde a `horas_uso`; el segundo, a `equipos_activos`. Ese orden forma parte de la definición de la entrada.

| Posición matemática | Posición en Python | Característica | Unidad |
|---|---|---|---|
| $x_1$ | `x[0]` | Horas de uso | h |
| $x_2$ | `x[1]` | Equipos activos | Conteo |

Cambiar el orden a `[3, 2]` cambia la observación. Una operación puede ejecutarse sin error y aun así estar usando las columnas equivocadas. Por eso debemos documentar nombres, unidades y orden, además de las dimensiones.

Estos valores son ilustrativos. No provienen de sensores ni representan una instalación real. Tampoco reemplazan el análisis de disponibilidad de datos de la unidad anterior.

### Escalares, vectores, matrices y tensores

| Objeto | Ejemplo | Qué representa |
|---|---|---|
| Escalar | $b = 1$ | Un único número |
| Vector | $\mathbf{x} = [2,3]$ | Dos componentes ordenadas |
| Matriz | Tres filas y dos columnas | Tres observaciones con dos características |
| Tensor de tres ejes | Forma $(4,3,2)$ | Un arreglo con tres dimensiones organizativas |

En computación numérica, **tensor** suele nombrar un arreglo de números organizado en ejes. Una matriz es el caso con dos ejes; un escalar, el caso con ninguno. Una imagen RGB puede organizarse como alto, ancho y canales. Una colección de imágenes puede añadir un eje para el número de imágenes.

El **número de componentes** de un vector y el **número de ejes** de un arreglo describen cosas distintas. Un vector de cien componentes sigue teniendo un solo eje en una representación como lista plana.

## 2. Vectores: operaciones componente a componente

Usaremos:

$$
\mathbf{a}=[2,3],\qquad \mathbf{c}=[6,2]
$$

Para sumar vectores, combinamos las posiciones correspondientes:

$$
\mathbf{a}+\mathbf{c}=[2+6,\;3+2]=[8,5]
$$

La resta sigue la misma regla:

$$
\mathbf{a}-\mathbf{c}=[-4,1]
$$

Para multiplicar por un escalar, multiplicamos cada componente:

$$
2\mathbf{a}=[4,6]
$$

Los vectores de una suma deben tener la misma longitud y el mismo significado por posición. No corresponde sumar una observación de `[horas, equipos]` con otra de `[temperatura, humedad]` solo porque ambas tengan dos componentes.

### Cuidado con las listas de Python

```python
a = [2, 3]
c = [6, 2]
print(a + c)  # [2, 3, 6, 2]: concatena listas
print(2 * a)  # [2, 3, 2, 3]: repite la lista
```

Estas expresiones no implementan la suma ni la multiplicación vectorial. En el laboratorio construiremos las operaciones con funciones que comprueban longitudes y recorren las componentes.

Otro problema aparece al usar `zip`: normalmente se detiene cuando termina la colección más corta. Comparar longitudes y utilizar `strict=True` evita que una componente desaparezca silenciosamente.

## 3. Producto punto: multiplicar y sumar

El **producto punto** de dos vectores de longitud $d$ es un escalar:

$$
\mathbf{a}\cdot\mathbf{c}=\sum_{j=1}^{d}a_jc_j
$$

El símbolo $\sum$ indica sumar un término por cada posición. Para nuestro ejemplo:

$$
[2,3]\cdot[6,2]=2\times6+3\times2=18
$$

No es lo mismo que la multiplicación componente a componente, que produciría `[12, 6]`. El producto punto reúne esos productos en un solo número.

### Una predicción con pesos y sesgo

Supongamos un modelo ilustrativo para una cantidad llamada consumo:

$$
\hat y = 0.5x_1+2x_2+1
$$

Aquí $\hat y$ se lee «y estimada». Los **pesos** son $\mathbf{w}=[0.5,2]$ y el **sesgo** o término independiente es $b=1$:

$$
\hat y=\mathbf{x}\cdot\mathbf{w}+b
$$

Con $\mathbf{x}=[2,3]$:

$$
\hat y=2\times0.5+3\times2+1=8
$$

El sesgo desplaza la salida incluso cuando todas las entradas son cero. Aquí está fijado por nosotros; en un modelo entrenado puede aprenderse junto con los pesos.

Si la salida se expresa en kWh, las unidades de cada término deben resultar compatibles: el peso de horas tiene unidad kWh/h; el de equipos, kWh por equipo; el sesgo, kWh. Los coeficientes son inventados para practicar. No describen una ley física validada.

Una suma ponderada solo es un **promedio ponderado** cuando se cumplen condiciones adicionales: pesos no negativos que suman uno. `[0.5, 2]` no cumple esa condición.

### ¿Peso grande significa característica importante?

No podemos comparar directamente coeficientes de características con escalas distintas. Si representamos las horas en minutos, dos horas pasan a ser 120 minutos y el peso correspondiente cambia de $0.5$ a $0.5/60$, conservando la misma contribución.

La magnitud del peso depende de la unidad, de las otras variables y del ajuste. Por sí sola no demuestra importancia causal ni explica lo que ocurriría al intervenir sobre una característica.

## 4. Normas, distancias y escala

La **norma euclidiana** mide la longitud geométrica de un vector:

$$
\|\mathbf{a}\|_2=\sqrt{a_1^2+\cdots+a_d^2}
$$

Para `[2, 3]`:

$$
\|\mathbf{a}\|_2=\sqrt{4+9}=\sqrt{13}\approx3.605551
$$

La **distancia euclidiana** entre dos vectores es la norma de su diferencia:

$$
\operatorname{dist}(\mathbf{a},\mathbf{c})=\|\mathbf{a}-\mathbf{c}\|_2
=\sqrt{(-4)^2+1^2}=\sqrt{17}\approx4.123106
$$

Una distancia pequeña indica cercanía bajo esa representación. La utilidad de esa cercanía depende de las características y su escala.

### Una conversión de unidades cambia la distancia

Considera registros descritos por `[horas, consumo_kwh]`:

- A: `[1, 1000]`.
- B: `[2, 1002]`.
- C: `[3, 1000]`.

Con esos números, $\operatorname{dist}(A,B)=\sqrt{5}\approx2.236$ y $\operatorname{dist}(A,C)=2$. C parece más cercano a A.

Si convertimos solo el consumo de kWh a Wh, B se vuelve `[2, 1002000]` y A, `[1, 1000000]`. Ahora la distancia A–B es $\sqrt{1+2000^2}\approx2000.00025$, mientras A–C sigue siendo 2. La información física es la misma, pero una componente domina mucho más el cálculo.

Una distancia entre coordenadas con unidades distintas necesita una elección explícita de escala. Para comparar registros suele transformarse cada columna o asignarse una ponderación justificada.

### Escalado por característica

Una transformación posible es:

$$
z_j=\frac{x_j-\min_j}{\max_j-\min_j}
$$

Cada mínimo y máximo se calcula en la **columna correspondiente del conjunto de entrenamiento**. Una columna de horas `[0,1,2,3]` tiene mínimo 0 y máximo 3; dos horas se transforman en $2/3$.

El valor de prueba 4 se transforma en $4/3$, mayor que uno. Es posible: los límites se calcularon en entrenamiento. No debemos recalcularlos con prueba para forzar el rango.

Si una columna es constante, el denominador es cero. Debemos definir una política, como retirarla o transformarla a cero y documentarlo. En unidades posteriores compararemos esta transformación con estandarización y otras decisiones de preparación.

**Normalizar un vector** a longitud uno es otra operación: $\mathbf{a}/\|\mathbf{a}\|_2$, definida solo cuando su norma es distinta de cero. Modifica la longitud de una fila; escalar características modifica columnas. No son intercambiables.

## 5. Matrices: muchas observaciones juntas

Agrupemos tres observaciones conservando el orden `[horas_uso, equipos_activos]`:

$$
X=\begin{bmatrix}2&3\\6&2\\3&5\end{bmatrix}
$$

$X$ tiene **tres filas y dos columnas**, forma $(3,2)$. En esta unidad, cada fila representa una observación y cada columna una característica.

| Fila | Horas de uso | Equipos activos |
|---|---:|---:|
| 1 | 2 | 3 |
| 2 | 6 | 2 |
| 3 | 3 | 5 |

La **transpuesta**, $X^T$, intercambia filas y columnas:

$$
X^T=\begin{bmatrix}2&6&3\\3&2&5\end{bmatrix}
$$

Su forma es $(2,3)$. Transponer cambia la organización, pero conserva cada valor. No es invertir una matriz ni cambiar el significado de las características.

### Producto de matriz por vector

Cada fila de $X$ se combina mediante producto punto con el mismo vector de pesos:

$$
X\mathbf{w}=\begin{bmatrix}2&3\\6&2\\3&5\end{bmatrix}
\begin{bmatrix}0.5\\2\end{bmatrix}
=\begin{bmatrix}7\\7\\11.5\end{bmatrix}
$$

Al sumar el sesgo a **cada** predicción:

$$
\hat{\mathbf{y}}=X\mathbf{w}+b\mathbf{1}
=\begin{bmatrix}8\\8\\12.5\end{bmatrix}
$$

$\mathbf{1}$ es un vector de tres unos. Es frecuente escribir $X\mathbf{w}+b$ suponiendo que la biblioteca expande el escalar sobre todas las filas. Esa expansión debe entenderse; una lista de Python no la realiza automáticamente.

La regla de dimensiones es:

$$
(n\times d)(d\times1)\longrightarrow(n\times1)
$$

Las dimensiones interiores deben coincidir. El resultado tiene una predicción por observación.

### Producto de matriz por matriz

Para multiplicar $A$ de forma $(m,k)$ por $B$ de forma $(k,p)$, cada celda del resultado usa una **fila de A** y una **columna de B**:

$$
C_{ij}=\sum_{r=1}^{k}A_{ir}B_{rj},\qquad C\text{ tiene forma }(m,p)
$$

Con $W=\begin{bmatrix}1&2\\2&0\end{bmatrix}$:

$$
XW=\begin{bmatrix}8&4\\10&12\\13&6\end{bmatrix}
$$

La primera celda es $2\times1+3\times2=8$. La segunda celda de esa fila es $2\times2+3\times0=4$.

La multiplicación componente a componente exigiría matrices de formas iguales en nuestro caso básico y produciría otra operación. Tampoco podemos cambiar libremente el orden: $XW$ está definido, pero $WX$ no, porque $(2,2)(3,2)$ tiene dimensiones interiores diferentes.

### Formas y significado

| Expresión | Forma de entrada | Forma del resultado |
|---|---|---|
| $X$ | Tres observaciones, dos características | $(3,2)$ |
| $X^T$ | Transpuesta | $(2,3)$ |
| $X\mathbf{w}$ | $(3,2)$ y $(2,1)$ | $(3,1)$ |
| $XW$ | $(3,2)$ y $(2,2)$ | $(3,2)$ |
| $X^TX$ | $(2,3)$ y $(3,2)$ | $(2,2)$ |

En los programas representaremos un vector como lista plana, sin distinguir fila y columna en su estructura. Las ecuaciones sí usan vectores columna para precisar las dimensiones. Bibliotecas como NumPy distinguen un arreglo de forma `(2,)` de otro de forma `(2, 1)`; cuando las introduzcamos, revisaremos esa diferencia.

## 6. Laboratorio 1 — Ver las operaciones

Archivo: [01_vectores_y_matrices.py](ejemplos/01_vectores_y_matrices.py).

```bash
python unidad03-matematica-aplicada/ejemplos/01_vectores_y_matrices.py
```

Resultados principales:

```text
a + b = [8.0, 5.0]
2a = [4.0, 6.0]
a · b = 18.0
Norma de a = 3.605551
Distancia(a, b) = 4.123106
Forma de X: 3 filas × 2 columnas
Xw = [7.0, 7.0, 11.5]
Xw + b = [8.0, 8.0, 12.5]
XW = [[8.0, 4.0], [10.0, 12.0], [13.0, 6.0]]
```

El programa llama `b` al segundo vector del primer ejercicio y `sesgo` al término independiente de la predicción. Son papeles distintos.

### Cómo leer el código

1. `vector` exige una lista o tupla no vacía de números finitos. Rechaza booleanos, aunque Python los trate como enteros.
2. `pares` comprueba la misma longitud antes de operar.
3. `producto_punto` multiplica las componentes y suma los productos.
4. `matriz` comprueba que todas las filas tengan la misma longitud.
5. `transpuesta` reorganiza las columnas como filas.
6. `matriz_matriz` obtiene las columnas de la segunda matriz y calcula cada producto punto.

La validación de dimensiones no comprueba el significado de las columnas. Esa responsabilidad permanece en el diseño y la documentación del experimento.

### Experimenta

- Cambia el peso de horas a 1. ¿Cuáles son las tres predicciones nuevas?
- Añade una cuarta fila a `x`. ¿Cambia el número de parámetros?
- Intercambia las columnas sin intercambiar los pesos. ¿El código detecta el problema semántico?
- Llama `producto_punto([1, 2], [3])`. Explica por qué debe rechazarse.
- Construye una matriz con filas de longitud diferente y observa el mensaje.

Haz estas modificaciones en una copia o registra los cambios en tu propio repositorio. Conserva el original para reproducir el resultado de referencia.

## 7. Una función transforma entradas en salidas

Una función asigna una salida a cada entrada de su dominio. El modelo anterior transforma características en una predicción. Durante el entrenamiento también construiremos una función que transforme **parámetros** en una pérdida.

Los papeles deben distinguirse:

| Símbolo | Papel durante el ajuste |
|---|---|
| $x_i$ | Entrada de la observación $i$; se mantiene fija |
| $y_i$ | Referencia de esa observación; se mantiene fija |
| $w,b$ | Parámetros que el algoritmo modifica |
| $\hat y_i=wx_i+b$ | Predicción calculada con los parámetros actuales |
| $L(w,b)$ | Pérdida que resume los errores del conjunto de ajuste |

Cambiar $w$ altera las predicciones. No cambia los valores originales de horas ni las referencias para hacerlos coincidir con el modelo.

## 8. Residuos y error cuadrático medio

Usaremos el signo:

$$
e_i=\hat y_i-y_i
$$

Un residuo positivo significa sobreestimar; uno negativo, subestimar. Otros textos usan el signo opuesto. Ambas convenciones sirven si se mantienen consistentes en las derivadas.

Con referencias `[3, 5]` y predicciones `[4, 4]`, los residuos son `[1, -1]`. Su suma es cero, pero ambas predicciones tienen error. Para evitar esa cancelación podemos elevar al cuadrado y promediar:

$$
\operatorname{MSE}=\frac{1}{n}\sum_{i=1}^{n}(\hat y_i-y_i)^2
$$

$$
\operatorname{MSE}=\frac{1^2+(-1)^2}{2}=1
$$

**MSE** viene de *mean squared error*, error cuadrático medio. Nunca es negativo; vale cero si cada predicción coincide exactamente con su referencia. Penaliza más los errores grandes: pasar de un error 1 a un error 3 cambia su contribución de 1 a 9.

Si la referencia está en kWh, el MSE queda en kWh². Su raíz, **RMSE**, queda en kWh. También existe **MAE**, el promedio del valor absoluto de los errores. Elegir una medida requiere comprender sus consecuencias; la estudiaremos con más detalle al evaluar modelos.

### Pérdida y métrica

Una **pérdida** guía la actualización de parámetros. Una **métrica** resume desempeño para evaluar. El MSE puede desempeñar ambos papeles, pero debe indicarse en qué datos se calcula.

Reducir MSE en entrenamiento no demuestra mejora en casos nuevos. Y aunque disminuya una métrica numérica, eso no garantiza que se resuelva la necesidad formulada en la Unidad 2.

## 9. Derivada: cómo cambia una función

Para estudiar el ajuste sin varias variables, definamos:

$$
L(w)=(w-3)^2
$$

Sabemos que su valor mínimo es cero cuando $w=3$. La **derivada** describe la variación local de la función respecto a $w$:

$$
L'(w)=2(w-3)
$$

| $w$ | $L(w)$ | $L'(w)$ | Interpretación local |
|---:|---:|---:|---|
| 0 | 9 | -6 | Aumentar ligeramente $w$ reduce la pérdida |
| 2 | 1 | -2 | Aumentar ligeramente $w$ reduce la pérdida |
| 3 | 0 | 0 | Mínimo de esta función |
| 4 | 1 | 2 | Reducir ligeramente $w$ reduce la pérdida |

«Local» significa alrededor del punto actual. Una derivada no es una garantía sobre un salto arbitrariamente grande.

### De dónde sale la derivada

Calculamos el cambio promedio entre $w$ y $w+h$:

$$
\frac{L(w+h)-L(w)}{h}
=\frac{2(w-3)h+h^2}{h}=2(w-3)+h
$$

Al acercar $h$ a cero, el resultado se acerca a $2(w-3)$. Esta es la idea del límite que define la derivada. No sustituimos $h=0$ en la fracción original porque dividiríamos por cero.

También podemos aproximar la derivada mediante una diferencia central:

$$
L'(w)\approx\frac{L(w+\varepsilon)-L(w-\varepsilon)}{2\varepsilon}
$$

Es útil para comprobar una derivada programada. Un $\varepsilon$ demasiado grande introduce error de aproximación; uno demasiado pequeño puede producir pérdida de precisión por restar números muy cercanos. No es un reemplazo general del cálculo de gradientes.

### Regla de la cadena

Una función puede estar compuesta por pasos. Aquí tenemos $u=w-3$ y $L=u^2$. La variación se combina:

$$
\frac{dL}{dw}=\frac{dL}{du}\frac{du}{dw}=2u\times1=2(w-3)
$$

Cuando el residuo depende de $wx+b-y$, el factor de esa derivada será importante: respecto a $w$ aparece $x$; respecto a $b$ aparece 1. Esa misma idea conecta operaciones en redes neuronales.

## 10. Descenso de gradiente: actualizar en dirección de menor pérdida

La actualización para un parámetro es:

$$
w_{t+1}=w_t-\eta L'(w_t)
$$

$t$ cuenta actualizaciones y $\eta$, leído «eta», es la **tasa de aprendizaje**. Restamos la derivada para movernos en la dirección de descenso local.

Con inicio $w_0=0$ y tasa $\eta=0.1$:

$$
w_1=0-0.1\times(-6)=0.6
$$

$$
w_2=0.6-0.1\times(-4.8)=1.08
$$

| Actualizaciones | $w$ | Pérdida |
|---:|---:|---:|
| 0 | 0 | 9 |
| 1 | 0.6 | 5.76 |
| 2 | 1.08 | 3.6864 |
| 3 | 1.464 | 2.359296 |
| 4 | 1.7712 | 1.50994944 |
| 5 | 2.01696 | 0.9663676416 |

Después de cinco actualizaciones estamos más cerca del mínimo, pero todavía no llegamos a él. Una tasa pequeña puede requerir más pasos; una grande puede sobrepasar el mínimo, oscilar o divergir.

### La condición de estabilidad pertenece a una función

Para **esta cuadrática**, podemos restar 3 a ambos lados de la actualización:

$$
w_{t+1}-3=(1-2\eta)(w_t-3)
$$

La distancia al mínimo se reduce cuando $|1-2\eta|<1$, es decir, $0<\eta<1$. Este intervalo no es una regla universal para modelos ni para pérdidas de otras escalas.

Desde $w_0=0$:

| Tasa | Trayectoria inicial | Resultado en esta cuadrática |
|---:|---|---|
| 0.1 | 0, 0.6, 1.08 | Se acerca gradualmente |
| 0.5 | 0, 3, 3 | Llega al mínimo en un paso |
| 0.75 | 0, 4.5, 2.25 | Cruza el mínimo y se acerca |
| 1 | 0, 6, 0 | Oscila sin mejorar la pérdida |
| 1.1 | 0, 6.6, -1.32 | Se aleja; la pérdida aumenta |

Si se comienza exactamente en el mínimo, la derivada es cero y se permanece allí, incluso con una tasa que divergiría desde otros puntos.

### Laboratorio 2 — Comparar trayectorias

Archivo: [02_descenso_cuadratica.py](ejemplos/02_descenso_cuadratica.py).

```bash
python unidad03-matematica-aplicada/ejemplos/02_descenso_cuadratica.py
python unidad03-matematica-aplicada/ejemplos/02_descenso_cuadratica.py --tasa 0.5
python unidad03-matematica-aplicada/ejemplos/02_descenso_cuadratica.py --tasa 1 --pasos 4
python unidad03-matematica-aplicada/ejemplos/02_descenso_cuadratica.py --tasa 1.1 --pasos 4
```

El programa imprime el estado inicial y el estado después de cada actualización. `--pasos 5` produce seis filas, de 0 a 5. En cada fila, la derivada corresponde al $w$ mostrado y se usaría para calcular la fila siguiente.

Se aceptan tasas positivas finitas, incluso si generan una trayectoria divergente; observarla forma parte del ejercicio. Se rechazan tasas cero, negativas o no finitas y más de 10 000 pasos. Si ocurre desbordamiento, el programa termina con un mensaje y código 2.

### Experimenta

- Empieza en 5 con tasa 0.1. ¿Qué signo tiene la primera derivada?
- Compara tasas 0.01 y 0.1 después de cinco pasos.
- Prueba tasa 0.75. ¿Cruzar el mínimo implica necesariamente divergir?
- Empieza en 3. Explica por qué no cambia el parámetro.
- Cambia la función a $10(w-3)^2$ **y su derivada**. Deduce la nueva condición de estabilidad antes de ejecutar.

## 11. Varias variables: derivadas parciales y gradiente

Una **derivada parcial** mide cómo cambia la función al variar un parámetro mientras los demás permanecen fijos. El **gradiente** reúne esas derivadas en un vector.

Para una pérdida que depende de peso y sesgo:

$$
\nabla L(w,b)=\begin{bmatrix}\partial L/\partial w\\\partial L/\partial b\end{bmatrix}
$$

Con modelo $\hat y_i=wx_i+b$ y MSE:

$$
L(w,b)=\frac{1}{n}\sum_{i=1}^{n}(wx_i+b-y_i)^2
$$

Aplicando la regla de la cadena a cada término:

$$
\frac{\partial L}{\partial w}=\frac{2}{n}\sum_{i=1}^{n}(wx_i+b-y_i)x_i
$$

$$
\frac{\partial L}{\partial b}=\frac{2}{n}\sum_{i=1}^{n}(wx_i+b-y_i)
$$

El factor 2 proviene del cuadrado. Algunos materiales definen la pérdida con $1/(2n)$ para cancelar ese factor; aquí usamos $1/n$ y conservamos el 2. Copiar una fórmula sin comprobar cómo se definió la pérdida puede cambiar el paso efectivo.

La actualización simultánea es:

$$
w_{t+1}=w_t-\eta\frac{\partial L}{\partial w}(w_t,b_t)
$$

$$
b_{t+1}=b_t-\eta\frac{\partial L}{\partial b}(w_t,b_t)
$$

Ambos gradientes deben calcularse en el mismo estado $(w_t,b_t)$. Si actualizamos $w$ primero y luego recalculamos la derivada de $b$ con el nuevo $w$, implementamos otro procedimiento.

### Más de una característica

Para $d$ características, $n$ observaciones y residuos $\mathbf{e}=X\mathbf{w}+b\mathbf{1}-\mathbf{y}$:

$$
\nabla_{\mathbf{w}}L=\frac{2}{n}X^T\mathbf{e},\qquad
\frac{\partial L}{\partial b}=\frac{2}{n}\sum_{i=1}^{n}e_i
$$

La forma de $X^T\mathbf{e}$ es $(d,n)(n,1)=(d,1)$: una derivada por peso. Las matrices permiten expresar el mismo cálculo para muchas características sin escribir una ecuación independiente por cada una.

## 12. Entrenar una recta con datos sintéticos

Usaremos una relación inventada:

$$
y=2x+1
$$

$x$ recibe el nombre de horas y $y$, consumo en kWh. Es una relación exacta para estudiar el algoritmo; no se obtuvo de mediciones ni representa un comportamiento físico comprobado.

Archivo: [consumo_lineal.csv](datos/consumo_lineal.csv). Lee la [procedencia y limitaciones](datos/README.md) antes de interpretar resultados.

| Partición | Horas | Referencia kWh |
|---|---:|---:|
| Entrenamiento | 0 | 1 |
| Entrenamiento | 1 | 3 |
| Entrenamiento | 2 | 5 |
| Entrenamiento | 3 | 7 |
| Prueba | 4 | 9 |
| Prueba | 5 | 11 |

La partición está declarada en el archivo. Entrenaremos con cuatro observaciones y calcularemos los resultados en otras dos. Los puntos de prueba están fuera del rango de horas de entrenamiento: estamos comprobando una extrapolación dentro de una relación sintética que ya conocemos.

### Primer paso completo a mano

Inicio: $w=0$, $b=0$. Todas las predicciones son cero.

| $x$ | $y$ | $\hat y$ | $e=\hat y-y$ | $ex$ | $e^2$ |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | -1 | 0 | 1 |
| 1 | 3 | 0 | -3 | -3 | 9 |
| 2 | 5 | 0 | -5 | -10 | 25 |
| 3 | 7 | 0 | -7 | -21 | 49 |
| Suma | — | — | -16 | -34 | 84 |

La pérdida inicial es $84/4=21$. Las derivadas son:

$$
\frac{\partial L}{\partial w}=\frac{2}{4}(-34)=-17,\qquad
\frac{\partial L}{\partial b}=\frac{2}{4}(-16)=-8
$$

Con tasa $0.05$:

$$
w_1=0-0.05(-17)=0.85,\qquad b_1=0-0.05(-8)=0.4
$$

Las nuevas predicciones de entrenamiento son `[0.4, 1.25, 2.1, 2.95]`. Su MSE es $7.05875$, menor que 21. El siguiente paso debe usar esos nuevos parámetros para volver a calcular todos los residuos.

### Línea base

Como comparación usaremos una predicción constante igual al promedio de las **referencias de entrenamiento**:

$$
\bar y_{\text{entrenamiento}}=(1+3+5+7)/4=4
$$

En prueba, sus errores son $4-9=-5$ y $4-11=-7$; por tanto:

$$
\operatorname{MSE}_{\text{prueba, base}}=(25+49)/2=37
$$

No usamos las referencias de prueba para calcular la constante ni para ajustar la recta. Usarlas alteraría la comparación.

## 13. Laboratorio 3 — Ajustar, predecir y comparar

Archivo: [03_ajustar_recta.py](ejemplos/03_ajustar_recta.py).

```bash
python unidad03-matematica-aplicada/ejemplos/03_ajustar_recta.py
python unidad03-matematica-aplicada/ejemplos/03_ajustar_recta.py --pasos 1
python unidad03-matematica-aplicada/ejemplos/03_ajustar_recta.py --pasos 10
python unidad03-matematica-aplicada/ejemplos/03_ajustar_recta.py --tasa 0.01 --pasos 500
```

También puedes indicar un CSV propio con `--datos ruta/al/archivo.csv`, conservando el encabezado y las particiones documentadas.

Con la configuración incluida, el resumen de entrenamiento es:

| Paso | Peso $w$ | Sesgo $b$ | MSE entrenamiento |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 21 |
| 1 | 0.85 | 0.4 | 7.05875 |
| 2 | 1.3425 | 0.6325 | 2.373021875 |
| 10 | 2.009281 | 0.957581 | 0.0009197664 |
| 100 | 2.001186 | 0.997467 | 0.0000023263 |
| 500 | 2.000000 | 1.000000 | Se muestra como 0.0000000000 |

Los últimos valores están redondeados. La pérdida real calculada sigue siendo positiva y muy pequeña. El programa se aproxima a $w=2$, $b=1$; no certifica igualdad matemática exacta.

En prueba, las predicciones se muestran como 9 y 11. El MSE también se imprime como cero al usar diez decimales. Frente a la línea base de MSE 37, la recta reproduce mejor estos dos casos sintéticos.

### Dónde ocurre cada parte

```python
dw, db = gradientes(casos, w, b)
w, b = w - tasa * dw, b - tasa * db
```

`gradientes` recibe solamente los casos de entrenamiento. Calcula todos los residuos con los parámetros actuales. La asignación simultánea usa ambos gradientes del mismo estado.

En la función principal:

```python
w, b, historia = entrenar(entrenamiento, args.tasa, args.pasos)
promedio = sum(y for _, y in entrenamiento) / len(entrenamiento)
base = evaluar(prueba, 0.0, promedio)
final = evaluar(prueba, w, b)
```

La línea base equivale a una recta con peso cero y sesgo igual al promedio. La evaluación de prueba ocurre después del ajuste; no modifica los parámetros.

### Actualizaciones, lotes y épocas

El programa calcula cada gradiente con **todo el conjunto de entrenamiento**, descenso por lote completo. Cada actualización procesa las cuatro filas; en este programa, un paso corresponde a una época.

Con minilotes habría varias actualizaciones por época. Con una observación por actualización, la trayectoria suele tener más variación. No confundas el número de filas, el número de épocas y el número de actualizaciones.

### Validación del archivo

Se comprueban encabezado, número de campos, identificadores únicos, particiones permitidas y valores finitos no negativos. Se requiere al menos una observación en cada partición. El esquema no garantiza calidad, independencia o procedencia de los datos.

Las funciones matemáticas internas trabajan con pares numéricos y listas no vacías. La validación del CSV ocurre en `leer_datos`; si reutilizas esas funciones desde otro programa, debes conservar sus precondiciones.

### Experimenta

1. Ejecuta un solo paso y comprueba $w=0.85$, $b=0.4$ y MSE de entrenamiento $7.05875$.
2. Ejecuta cero pasos. El modelo permanece en cero: su MSE de prueba es 101 y resulta peor que la línea base.
3. Conserva cuatro casos de entrenamiento y cambia **solo** las referencias de prueba a 90 y 110 en una copia. El peso y el sesgo deben permanecer iguales; la evaluación cambia.
4. Convierte horas a minutos en todas las filas. El peso que conserva la relación pasa de 2 a $2/60$. La misma tasa puede volverse inestable porque cambió la escala.
5. Añade pequeñas desviaciones a las referencias de entrenamiento en una copia. ¿Sigue siendo posible obtener pérdida exactamente cero con una sola recta?

Registra datos, tasa y pasos de cada variante. Si comparas muchas configuraciones usando estas dos filas de prueba, dejan de constituir una evaluación final independiente. Para seleccionar una configuración necesitarás una partición de validación; el protocolo completo se desarrolla en unidades posteriores.

## 14. Qué nos permite concluir el experimento

El descenso encontró parámetros que reproducen una relación lineal inventada. Podemos comprobar operaciones, gradientes, implementación y separación del ajuste respecto a prueba.

No podemos concluir que el modelo anticipa consumo real, que ahorra energía ni que funciona ante cambios de equipos o personas. Los datos no tienen ruido, mediciones faltantes, estacionalidad ni incertidumbre de sensores.

### Optimizar una pérdida no garantiza todo lo demás

- La pérdida de un modelo lineal con MSE es convexa: un mínimo local también es global. Aun así, una tasa inadecuada puede impedir que el algoritmo se acerque al mínimo.
- El mínimo puede no ser único. Si columnas repiten información o son combinaciones de otras, diferentes pesos pueden producir las mismas predicciones.
- En funciones no convexas, gradiente cero puede corresponder a un mínimo, un máximo o un punto de silla. La derivada cero requiere interpretación.
- MSE muy bajo en entrenamiento no garantiza buen desempeño en casos nuevos.
- Una predicción numéricamente precisa no sustituye una decisión operativa con costos y restricciones.

En nuestra recta, tener al menos dos valores distintos de horas permite identificar un peso y un sesgo únicos para la relación exacta. No necesitamos invertir matrices para ejecutar el descenso. La regresión se retomará con ruido, supuestos y evaluación en la Unidad 11.

## 15. Ejercicios

Resuelve primero a mano y después contrasta con código. Para todos los cálculos, usa las convenciones de esta unidad.

1. **Representación.** Una fila contiene temperatura, humedad y ocupación. Define nombres, unidades y orden. ¿Qué información falta para interpretar `[24, 70, 12]`? ¿Qué cambia si intercambias dos columnas?
2. **Operaciones vectoriales.** Para $\mathbf{u}=[1,2,3]$ y $\mathbf{v}=[4,0,-1]$, calcula suma, $3\mathbf{u}$, producto punto, norma de $\mathbf{u}$ y distancia. Explica el tipo de resultado de cada operación.
3. **Predicción.** Con $\mathbf{x}=[4,2]$, $\mathbf{w}=[0.5,2]$ y $b=1$, calcula la salida. Convierte horas a minutos y ajusta el peso para conservarla.
4. **Matrices.** Usa $A=\begin{bmatrix}1&2\\3&4\end{bmatrix}$ y $B=\begin{bmatrix}2&0\\1&2\end{bmatrix}$. Calcula $A^T$, $AB$ y $BA$. ¿Son iguales? Indica las formas de $A[1,1]^T$ y de $A^TA$.
5. **Escalado.** La columna de entrenamiento es `[2,4,6]`. Transforma 4 y el dato de prueba 8 mediante mínimo–máximo. ¿Por qué el segundo puede superar uno? ¿Qué harías con `[5,5,5]`?
6. **Errores.** Las referencias son `[2,4,6]` y las predicciones `[3,3,8]`. Calcula residuos, MSE, RMSE y MAE. Explica por qué promediar residuos no mide adecuadamente todos los errores.
7. **Descenso.** Para $L(w)=(w-3)^2$, inicio 5 y tasa 0.1, calcula dos actualizaciones. Repite con tasa 1. Explica si se acerca al mínimo.
8. **Gradientes.** Con casos $(x,y)=(0,1),(1,3)$, inicio $w=0,b=0$ y tasa 0.1, calcula pérdida, ambas derivadas y una actualización simultánea. Calcula la nueva pérdida.
9. **Comprobación numérica.** Aproxima $\partial L/\partial w$ y $\partial L/\partial b$ del ejercicio 8 mediante diferencias centrales con $\varepsilon=10^{-6}$. Compara con el cálculo manual y declara una tolerancia de comparación.
10. **Evaluación.** Explica qué significa un MSE que aparece como cero en el laboratorio, qué datos influyen en los parámetros y por qué variar la prueba no debe modificar el entrenamiento. Describe qué evidencia adicional necesitarías para evaluar consumos reales.

Consulta las [soluciones comentadas](soluciones/README.md) después de documentar tu intento. La [comprobación de gradientes](soluciones/01_comprobar_gradientes.py) permite contrastar la implementación mediante otro método.

## 16. Reto aplicado — Un experimento matemático reproducible

Desarrolla el [reto y su rúbrica](reto.md). La entrega debe mostrar representación de datos, cálculo manual, comparación con una línea base y un análisis de las limitaciones. Puedes usar el caso sintético de consumo o construir otro caso explícitamente sintético en educación, ambiente o sensores.

Para redactar el experimento puedes completar la [plantilla de informe](plantillas/informe_experimento.md). Mantén claros los datos que influyen en el ajuste y las condiciones que estás cambiando.

## 17. Errores frecuentes

| Error | Cómo corregirlo |
|---|---|
| Usar `a + b` como suma de listas numéricas | Implementar suma por componente o usar una biblioteca con semántica de arreglos |
| Omitir componentes por longitudes distintas | Validar longitudes antes de `zip` |
| Mezclar significado u orden de columnas | Documentar un esquema de características |
| Multiplicar matrices incompatibles | Escribir formas antes de calcular |
| Confundir producto punto y producto por componente | Identificar si la salida debe ser escalar o vector |
| Comparar distancias con escalas arbitrarias | Definir unidades y transformación por característica |
| Calcular escalado o línea base con prueba | Obtener esos valores solo de entrenamiento |
| Sumar errores positivos y negativos | Usar una medida como MSE o MAE |
| Actualizar parámetros con gradientes de estados distintos | Calcular todos los gradientes antes de actualizar |
| Aplicar la misma tasa después de cambiar unidades | Revisar cómo cambia la escala del gradiente |
| Interpretar números redondeados como exactos | Inspeccionar valores con más precisión y usar tolerancias |
| Confundir pérdida baja con validez real | Separar verificación matemática, evaluación y utilidad del proyecto |

## Checklist

- [ ] Identifico nombres, unidades y orden de cada característica.
- [ ] Distingo componentes de un vector de ejes de un arreglo.
- [ ] Calculo producto punto, norma y distancia.
- [ ] Compruebo dimensiones de un producto matricial.
- [ ] Explico el papel de pesos y sesgo.
- [ ] Calculo residuos y MSE con una convención consistente.
- [ ] Interpreto el signo de una derivada y un gradiente.
- [ ] Realizo una actualización simultánea de peso y sesgo.
- [ ] Explico por qué una tasa puede convergir, oscilar o divergir.
- [ ] Separo entrenamiento y prueba, incluso al calcular una línea base.
- [ ] Reconozco redondeo, escala y límites de los datos sintéticos.

## Resumen

Los vectores organizan características; las matrices reúnen observaciones y permiten calcular varias salidas. Una pérdida conecta las predicciones con referencias. Las derivadas indican cómo varía esa pérdida al cambiar los parámetros, y el descenso de gradiente usa esa información para actualizar el modelo.

En los laboratorios calculamos predicciones, observamos diferentes trayectorias y ajustamos una relación sintética exacta. El resultado demuestra el procedimiento bajo esas condiciones. La formulación, los datos y la evaluación siguen siendo necesarios para construir una aplicación útil.

La siguiente unidad de la ruta estudia **probabilidad y estadística**. Consulta su disponibilidad en el índice.

## Referencias y lecturas

Los ejemplos, datos y desarrollos numéricos son material educativo propio. Las lecturas siguientes permiten ampliar el vocabulario y las operaciones; no necesitas instalar sus bibliotecas para resolver esta unidad.

1. Zhang, A., Lipton, Z. C., Li, M. y Smola, A. J. *Dive into Deep Learning*. [Álgebra lineal](https://d2l.ai/chapter_preliminaries/linear-algebra.html).
2. Los mismos autores. *Dive into Deep Learning*. [Cálculo](https://d2l.ai/chapter_preliminaries/calculus.html).
3. Google for Developers. *Machine Learning Crash Course*. [Descenso de gradiente](https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent).
4. Google for Developers. *Machine Learning Crash Course*. [Hiperparámetros y tasa de aprendizaje](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters).

[Unidad anterior](../unidad02-proyecto-ia/README.md) · [Volver al índice](../README.md)

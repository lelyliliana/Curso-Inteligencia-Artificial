# Soluciones — Redes neuronales

[Volver a los ejercicios](../README.md#10-ejercicios-reto-y-comprobación) · [Paso manual](03_retropropagar_a_mano.py)

## 1. Dimensiones y parámetros

X: (5,2); W1: (2,3); b1: (3,); A y H: (5,3); W2: (3,); b2: (1,); s, p e y: (5,). Hay 6+3+3+1=13 parámetros. Los sesgos de la capa oculta son compartidos entre casos; no se aprende un sesgo diferente para cada fila. Broadcasting replica su uso, no añade parámetros.

## 2. Composición y XOR

Sin activación, pesos equivalentes `W=W1@W2` y sesgo `b=b1@W2+b2`; por tanto `s=X@W+b`.

Para s=a×x1+c×x2+b, las dos esquinas de signos opuestos positivas exigirían `a−c+b>=0` y `−a+c+b>=0`: sumando, b>=0. Las esquinas del mismo signo negativas exigirían `a+c+b<0` y `−a−c+b<0`: sumando, b<0. No hay solución. Es una afirmación sobre separar correctamente las cuatro esquinas bajo el umbral inclusivo; no significa que toda recta tenga exactamente 50 % de aciertos en cualquier muestra XOR.

## 3. Paso manual

Con x=[1,−1], las dos preactivaciones son cero; tanh(0)=0, s=0, p=0,5 y pérdida ln(2). Para un caso, D=−0,5. El gradiente de W2 es cero porque H es cero, y el de b2 es −0,5. En la capa oculta, `G=[−0,5;0,5]` porque la derivada de tanh en cero es 1.

El producto externo de x y G da `gW1=[[-0,5;0,5],[0,5;−0,5]]`; gb1=G. Restar 0,1 veces esos gradientes produce W1=[[0,55;−0,55],[0,45;−0,45]], b1=[0,05;−0,05], W2=[1;−1] y b2=0,05. Logit nuevo≈0,347770, p≈0,586077, BCE≈0,534305, menor que 0,693147.

Retropropagación obtiene los gradientes mediante la regla de la cadena. Descenso por gradiente aplica el cambio. Si W2 se actualizara antes de calcular G, G usaría un estado diferente del que produjo la pérdida original.

## 4. Derivada de la salida

Con p=0,8 e y=0, la derivada por caso respecto de s es 0,8. Contribuye 0,8/4=0,2 a la derivada de la pérdida media en un lote de cuatro. Si y=1, los valores son −0,2 y −0,05. El signo positivo empuja s hacia abajo al restar el gradiente; el negativo lo empuja hacia arriba. Para obtener el gradiente de un peso aún hay que multiplicar por la entrada o activación correspondiente.

Dividir también gW2 y G por cuatro después de haber dividido D volvería a promediar y daría un gradiente incorrecto.

## 5. Penalización

`lambda/2 × (2²+(−1)²) = 0,1/2×5 = 0,25`. La contribución al gradiente de los pesos es lambda×W=[0,2;−0,1]. No se penaliza b. No se divide otra vez por n según la convención de esta unidad: BCE media + penalización definida arriba. Al comparar con una biblioteca, verifica su fórmula en lugar de asumir que un hiperparámetro con el mismo nombre tiene idéntica escala.

## 6. Inicializar en cero

Si todos los pesos y sesgos de esta red oculta empiezan en cero, H=0 y W2=0. Entonces gW2=H.T@D=0 y G=D×W2×(1−H²)=0. W1, b1 y W2 no cambian; solo podría moverse b2. En entrenamiento perfectamente equilibrado, incluso ese gradiente de salida inicial puede ser cero. Las unidades no desarrollan funciones distintas.

La referencia logística no tiene una capa oculta con unidades intercambiables. Desde W=0, el gradiente `X.T@(p−y)/n` puede ser distinto de cero y aprender, siempre que los datos aporten esa señal. En XOR esa capacidad sigue limitada por la forma lineal, aunque se entrene correctamente.

## 7. Estabilidad y comprobación numérica

La sigmoide de 1000 puede redondearse a 1. `log(1−p)` intentaría tomar log(0), y una expresión con 0×log(0) puede producir un valor no numérico. Evaluar la pérdida desde logits preserva una pérdida cercana a 0 cuando y=1 y cercana a 1000 cuando y=0.

En diferencias finitas se conserva el mismo X, y, lambda, forma de pérdida y estado de todos los demás parámetros. Se modifica solo un elemento cada vez, en copias independientes, con +epsilon y −epsilon. No se reentrena ni se cambia la semilla entre evaluaciones. Se compara con la derivada del mismo objetivo, incluida L2 cuando corresponde. La prueba no sustituye una comparación de resultados predictivos ni demuestra que todos los tamaños y plataformas funcionen.

## 8. Elegir un punto de entrenamiento

La época elegida es 100 porque su BCE de validación, 0,54, es la menor. El último estado ajusta mejor entrenamiento —0,20— pero empeora validación —0,62—. Se guarda una copia de todos los arrays de parámetros al encontrar el mejor punto. Una referencia al mismo array que después se modifica perdería ese estado.

Se usaron etiquetas de validación para decidir la época, de modo que su pérdida participa en selección y no es un cierre independiente. Completar el presupuesto y restaurar un punto anterior no equivale a detener físicamente el entrenamiento con paciencia.

## 9. Mejor época, última época y métrica

Red32 guarda época 500: BCE de entrenamiento≈0,3618 y de validación≈0,5820. Al final, época 6000, la BCE de entrenamiento cae a≈0,1152 pero la de validación sube a≈1,1615. Los JSON conservan ambos estados; los CSV predictivos usan el mejor punto.

BCE considera las probabilidades, incluyendo cuánta confianza se asigna a un error. Exactitud solo cuenta si la clase supera el umbral y coincide. Por ejemplo, para dos positivos, p=[0,51;0,51] tiene exactitud 1 y BCE≈0,673; p=[0,49;0,99] tiene exactitud 0,5 y BCE≈0,362. La segunda opción gana por BCE aunque pierda por exactitud. En esta unidad se selecciona por BCE, sin cambiar de criterio después de ver resultados.

Red32_l2 gana entre los candidatos declarados, con BCE de validación≈0,5492. No es una prueba de que lambda=0,02 sea universalmente óptima ni de que una arquitectura mayor sea mejor; aquí se comparó L2 dentro de una misma arquitectura.

## 10. Una modificación evaluable

Una propuesta válida: mantener las particiones de desarrollo y comparar anchos 4 y 8 con una tasa y un presupuesto previamente declarados. Ajustar escala solo con entrenamiento, conservar inicializaciones y registrar todas las configuraciones. Seleccionar arquitectura y época con BCE de validación, documentando cuántas consultas se hicieron y el desempate. Si se comparan semillas, mostrar la variación sin eliminar las desfavorables.

La prueba solo evalúa el estado elegido. Si ya conoces el cierre de esta unidad y el cambio responde a él, reserva datos nuevos con un protocolo explícito; no basta cambiar la semilla del modelo para crear una evaluación independiente. Con datos sintéticos puedes demostrar cálculo y comportamiento del experimento, pero no utilidad, causalidad ni calibración en sensores reales.

## Cierre didáctico publicado

XOR: se conserva red8, época 3000; prueba tiene 96 filas, BCE≈0,0061, exactitud=1, VP=48, VN=48, FN=0 y FP=0.

Ruido: se conserva red32_l2, época 6000; prueba tiene 160 filas, BCE≈0,5350, exactitud=126/160=0,7875, VP=60, VN=66, FN=17 y FP=17. La consola muestra exactitud con tres decimales y puede verse 0,787 por redondeo binario. Es preferible conservar los conteos para reconstruir la proporción.

No se elige otra época o candidato al ver esos valores. La red sigue cometiendo errores en el caso ruidoso; ningún gráfico de frontera los elimina. Todos los valores son de estas muestras simuladas y sus resultados son conocidos para futuras extensiones.

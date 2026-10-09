# Soluciones comentadas — Unidad 4

Compara con tu desarrollo antes de copiar un resultado. Revisa especialmente denominadores, unidades, método de cuartiles y qué cantidades son supuestas.

## 1. Población y muestra

La unidad de análisis puede ser una solicitud recibida. La población objetivo son todas las solicitudes recibidas por la plataforma durante los tres meses delimitados, en todos los horarios.

El archivo disponible contiene solo las atendidas durante el día. Omite recibidas de noche, no atendidas u otros casos según cómo se haya construido. Se trata de una selección condicionada por horario y atención.

Podemos describir los registros disponibles, pero no atribuir directamente sus tiempos de respuesta o resultados a todas las solicitudes. Hace falta revisar los criterios de inclusión y obtener información de las unidades omitidas. Más filas del mismo subconjunto no corrigen por sí solas esa limitación.

## 2. Resumen

Datos ordenados: `[2,4,4,6,9]`, n=5. Frecuencias: 2 aparece una vez, 4 dos veces, 6 una y 9 una. Las relativas son 1/5, 2/5, 1/5 y 1/5.

$$
\bar x=25/5=5,\qquad \operatorname{mediana}=4,\qquad \operatorname{moda}=4
$$

Rango: $9-2=7$.

Las desviaciones respecto a 5 son `[-3,-1,-1,1,4]` y los cuadrados `[9,1,1,1,16]`; suman 28.

$$
\operatorname{varianza}_{n}=28/5=5.6,\qquad
s^2=28/4=7,\qquad s=\sqrt7\approx2.645751
$$

Si las cantidades tienen unidad u, la media, mediana y desviación tienen unidad u; las varianzas, u². No se asignó una unidad concreta en este ejercicio.

En el laboratorio de consumo, reemplazar 26 por 60 cambia la media a 20.666667, pero mantiene mediana 13 y moda 12. Convertir todos los valores de kWh a Wh multiplica media y desviación por 1000, y varianza por $1000^2$.

## 3. Cuartiles

Excluimos el centro 4. Mitad inferior `[2,4]`; superior `[6,9]`:

$$
Q_1=3,\qquad Q_3=7.5,\qquad \operatorname{IQR}=4.5
$$

Límites:

$$
3-1.5(4.5)=-3.75,\qquad 7.5+1.5(4.5)=14.25
$$

Ningún valor está fuera. Un límite exploratorio negativo no implica que se hayan observado valores negativos ni que fueran válidos en un contexto de consumo.

Un software puede producir otros cuartiles si utiliza interpolación distinta. La comparación necesita declarar método; no basta con atribuir la diferencia a un error.

## 4. Grupos y asociación

La media conjunta es $(2\times10+8\times20)/10=18$. Promediar directamente 10 y 20 daría 15 y asignaría el mismo peso a grupos de tamaños distintos.

En los pares del laboratorio, el grupo A tiene medias x=2 e y=9; el B, x=8 e y=29. Dentro de cada grupo la pendiente es -1. Entre grupos, ambas medias aumentan.

Al reunirlos, x tiene media 5 e y, 19. La suma de productos de desviaciones es 176; las sumas de cuadrados son 58 para x y 604 para y:

$$
r=176/\sqrt{58\times604}\approx0.940330
$$

No hay contradicción: se están describiendo asociaciones a niveles diferentes. Tampoco prueba causalidad. Se construyeron los pares para mostrar el efecto de la agregación; no se realizó una intervención ni se justificó un modelo causal.

Sumar una constante a todos los valores de y no cambia r, porque también se desplaza su media. Multiplicar y por -1 cambia el signo. Si y es constante, Pearson no está definido.

## 5. Eventos

$$
P(A\cup B)=0.4+0.3-0.12=0.58
$$

$$
P(A^c)=0.6,\qquad P(A\mid B)=0.12/0.3=0.4
$$

Son independientes porque $P(A)P(B)=0.4(0.3)=0.12=P(A\cap B)$. No son mutuamente excluyentes: su intersección tiene probabilidad positiva.

El condicional tiene denominador P(B). Invertirlo a P(B|A) produciría otra cantidad: 0.12/0.4=0.3.

## 6. Bayes con mayor especificidad

Prevalencia 1 %, sensibilidad 90 %, especificidad 99 %, total 10 000:

- Eventos esperados: 100; TP=90 y FN=10.
- Sin evento: 9900; FP=99 y TN=9801.
- Alertas: 189.

$$
P(A)=0.9(0.01)+0.01(0.99)=0.0189
$$

$$
P(E\mid A)=90/189=10/21\approx0.476190
$$

La posterior es aproximadamente 47.62 %, frente a 15.38 % con especificidad 95 %. Sigue sin ser 90 %: sensibilidad y posterior usan grupos de referencia diferentes.

Comando:

```bash
python unidad04-probabilidad-estadistica/ejemplos/02_bayes_alertas.py --especificidad 0.99
```

Si cambiamos únicamente el total, se multiplican todos los conteos por el mismo factor y las probabilidades se conservan. Con prevalencia cero y especificidad uno, P(alerta)=0 y la posterior dada alerta no está definida mediante esta fórmula.

Los conteos son expectativas bajo supuestos, no una matriz de resultados observados de un modelo.

## 7. Binomial

Para n=5 y p=0.3:

$$
\operatorname{E}[K]=5(0.3)=1.5,\qquad
\operatorname{Var}(K)=5(0.3)(0.7)=1.05
$$

$$
P(K=2)=\binom52(0.3)^2(0.7)^3
=10(0.09)(0.343)=0.3087
$$

El conteo individual solo puede tomar enteros entre 0 y 5, aunque su esperanza sea 1.5. Se requieren ensayos independientes, probabilidad común y un número de ensayos fijado. Si hay probabilidades distintas o dependencia, la fórmula no queda justificada por el conteo solamente.

## 8. Error estándar

$$
\operatorname{SE}_{200}=\sqrt{0.3(0.7)/200}\approx0.032404
$$

$$
\operatorname{SE}_{800}=\sqrt{0.3(0.7)/800}\approx0.016202
$$

Cuatro veces más ensayos reduce a la mitad el error estándar bajo el modelo. La desviación de una observación Bernoulli individual es $\sqrt{0.21}\approx0.458258$ y no se divide por el tamaño de muestra. Las dos cantidades describen variaciones distintas.

Al ejecutar la simulación con semilla 42, los anchos medios de Wilson son aproximadamente:

| n | Ancho medio | Cobertura observada en 1000 repeticiones |
|---:|---:|---:|
| 50 | 0.243342 | 96.00 % |
| 200 | 0.125648 | 93.70 % |
| 800 | 0.063303 | 94.70 % |

Los anchos se reducen. La cobertura observada no necesita crecer de forma monótona ni ser exactamente 95 %. Intervienen la simulación y la cobertura real aproximada del método. Esta tabla corresponde a las condiciones incluidas, no a datos reales.

## 9. Wilson

Para k=7 y n=20:

$$
\hat p=0.35,\qquad \operatorname{IC}\approx[0.181192,0.567146]
$$

Puedes comprobarlo cargando el archivo del laboratorio desde la raíz del curso:

```python
import importlib.util
from pathlib import Path

ruta = Path("unidad04-probabilidad-estadistica/ejemplos/03_simular_estimaciones.py")
spec = importlib.util.spec_from_file_location("simulacion", ruta)
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)
print(modulo.wilson(7, 20))
print(modulo.wilson(0, 20))
```

El archivo comienza por un número, por eso usamos `importlib` en lugar de la sintaxis habitual de importación. Importarlo no ejecuta su función principal.

El intervalo se construyó con un procedimiento de nivel nominal 95 % bajo el modelo binomial. El nivel no significa que 95 % de los resultados individuales esté entre sus límites ni asigna por sí solo 95 % de probabilidad al parámetro fijo dentro de este intervalo.

Con cero eventos en veinte ensayos, la estimación puntual es 0 y el intervalo aproximadamente `[0,0.161125]`. Cero eventos observados no demuestra probabilidad poblacional nula.

El intervalo describe incertidumbre bajo sus supuestos. No corrige una selección sesgada ni dependencia entre ensayos.

## 10. Decisión y evidencia

Con costos 1 por revisión innecesaria y 5 por omisión:

| q | Costo esperado revisar: 1-q | Costo esperado no revisar: 5q | Menor costo supuesto |
|---:|---:|---:|---|
| 0.1 | 0.9 | 0.5 | No revisar |
| 0.3 | 0.7 | 1.5 | Revisar |

El umbral de empate es 1/6. Depende de asumir costo cero para decisiones correctas y esos valores para las incorrectas.

Para llevarlo a un proyecto se necesita una probabilidad estimada pertinente y evaluada, costos justificados, capacidad, efectos sobre usuarios y política de revisión. Una consecuencia que falta en la tabla puede cambiar la decisión.

Una muestra mayor reduce ciertos componentes de variación bajo condiciones apropiadas; no elimina sesgo de selección, errores sistemáticos ni cambios de contexto. Un intervalo estrecho puede acompañar una estimación dirigida a la población equivocada.

## Orientación para el reto

Un informe sólido separa:

- Descripción del CSV sintético.
- Conteos esperados bajo las probabilidades elegidas.
- Estimaciones e intervalos de muestras simuladas.
- Asociación en los pares construidos.
- Evidencia todavía necesaria para una aplicación real.

Es válido informar que un caso no sustenta una decisión real. La claridad del límite es parte de la interpretación del resultado.

[Volver a la unidad](../README.md) · [Ver el reto](../reto.md)

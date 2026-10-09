# Soluciones razonadas

[Unidad](../README.md) · [Ejemplos manuales ejecutables](03_pliegues_a_mano.py)

## 1. Aprender y elegir

La media de escala es un parámetro aprendido de las entradas permitidas. Los casos y objetivos conservados por KNN son estado aprendido del conjunto de ajuste. k es un hiperparámetro del predictor. El número de pliegues y el esquema de separación son decisiones del protocolo de evaluación, fijadas por la pregunta y los recursos, no por conseguir una puntuación agradable.

## 2. Dos predicciones

Con pesos uniformes, `(10+20+40)/3=70/3≈23,333`. Con distancia, los pesos sin normalizar son `1,1/2,1/4`. El numerador es `10+10+10=30` y el denominador `7/4`; predicción=`120/7≈17,143`. El vecino de respuesta 10 influye más porque es el más cercano.

Para distancia cero no se debe dividir literalmente entre cero. La biblioteca usa únicamente los vecinos seleccionados coincidentes y promedia sus respuestas. El conjunto de vecinos depende de escala y orden; no equivale a un efecto causal.

## 3. Tres pliegues a mano

Las medianas de los respectivos entrenamientos son 7,5,3. Los MAE son 6,1,6. Su media es `13/3`. Las desviaciones respecto de ella son `5/3,−10/3,5/3`; el promedio de sus cuadrados es `50/9` y la desviación poblacional es `sqrt(50)/3≈2,357`.

Cada mediana se aprende sin los objetivos que valida. Una mediana global usaría esos objetivos anticipadamente. Los entrenamientos comparten casos, así que la desviación de sus puntuaciones no puede presentarse sin más como un intervalo de confianza.

## 4. Escala filtrada

La escala correcta se ajusta con tres casos; sus medias son `(2,10/3)`. La escala global también ve las dos consultas, incluida una segunda coordenada de 1000. Eso reduce el peso relativo de diferencias de esa coordenada al estandarizar y cambia cuál entrenamiento está más cerca de la primera consulta: predicción 40 frente a 20.

No se usaron etiquetas de validación, pero sí su distribución de entradas para definir la representación. No es un procedimiento permitido en estos experimentos. Este ejemplo demuestra dependencia de información apartada, sin afirmar que la filtración siempre mejore MAE.

## 5. Presupuesto

Ciclos: siete candidatos × cuatro pliegues + un reajuste = 29 ajustes. Equipos: los mismos 29 más cuatro del diagnóstico fijo por filas = 33. Con doce candidatos, cinco pliegues y un reajuste serían `12×5+1=61`. Guardar figuras y predecir prueba no añaden ajustes de modelos.

Una búsqueda anidada repetiría la búsqueda dentro de cada entrenamiento externo; su costo debe calcularse con sus bucles concretos. No corresponde reutilizar el presupuesto de una búsqueda única.

## 6. Separar equipos

En el primer pliegue del archivo publicado validan D04, D08 y D12. Ajustan D01,D02,D03,D05,D06,D07,D09,D10,D11. Los índices y nombres completos están en `cv.pliegues` del JSON; los nombres de grupos no son variables predictivas.

Con `knn3_uniform`, MAE=0,583 por filas frente a 27,990 por equipos. La primera partición permite ver otras observaciones del mismo equipo en entrenamiento. En este generador se puede aproximar así una respuesta propia del equipo; para uno nuevo su respuesta base no está relacionada con sus señales. No se cambia a KFold por dar menor error: eso evaluaría otro uso.

## 7. Reconstruir una medida OOF

Filtra el CSV por candidato, suma `abs(real−prediccion)` y divide entre sus filas: 160 en ciclos, 144 en equipos. Obtendrás `mae_oof`, con diferencias únicamente de redondeo si utilizas cifras de consola en lugar del CSV completo. Cada registro lleva el número de pliegue que predijo ese caso.

Para reconstruir el criterio, agrupa además por pliegue, calcula cada MAE y promedia los cuatro valores con el mismo peso. Aquí coinciden las dos medias porque todos los pliegues tienen igual número de casos. Con tamaños 1 y 3 y MAE 2 y 8, la media por pliegue es 5 y la media por observación es 6,5. La decisión de ponderación depende de lo que se quiera evaluar.

## 8. Elegir sin exagerar la evidencia

Con el criterio fijado, 1,797 es menor que 1,816. Sus valores completos también superan la tolerancia de empate, y gana `knn3_distance`. La diferencia no demuestra que esa opción vaya a ganar en otras muestras ni que exista una ventaja significativa.

Las barras muestran más y menos una desviación de los cuatro MAE, con divisor cuatro. Los puntos muestran cada MAE. No son intervalos de confianza, y el solapamiento de barras no es una prueba de significación. No se aplica retrospectivamente otra regla para favorecer una alternativa.

## 9. Reajuste y cierre

Se conserva la configuración seleccionada, pero se crea un predictor nuevo y se aprende su estado con todo desarrollo. En ciclos cambian potencialmente medias, escalas y vecindarios al disponer de 160 casos. En equipos gana la mediana y se recalcula con los 144 objetivos. No se usa el último pliegue ni un promedio de modelos.

Cambiar solo objetivos de prueba debe conservar índices, puntuaciones CV, selección, parámetros reajustados y predicciones para las mismas entradas. Cambian los objetivos y la huella del archivo; pueden cambiar métricas y residuos. No es necesario que cada métrica cambie ante toda modificación posible.

Cierre ejecutado con el protocolo publicado:

| Experimento | Seleccionado antes de abrir prueba | Casos de prueba | MAE | RMSE |
|---|---|---:|---:|---:|
| Ciclos | `knn3_distance` | 64 | 1,402 kWh | 1,839 kWh |
| Equipos | `mediana` | 48, de cuatro equipos nuevos | 28,303 | 30,491 |

Los errores de equipos son altos y no se presentan como un predictor operativo satisfactorio. Estos resultados sintéticos públicos verifican el flujo; conocerlos no permite afirmar que una nueva búsqueda haya tenido una prueba independiente.

## 10. Tiempo y anidación

El primer corte temporal ajusta índices 0–4, omite el 5 y valida 6–7. `gap=1` deja una fila; no garantiza un plazo temporal concreto sin saber la frecuencia ni cuándo se conocen las etiquetas. Los cortes siguientes amplían entrenamiento usando únicamente el pasado respecto de su bloque de validación.

En un ciclo externo anidado: apartar el bloque externo; dentro del resto crear pliegues internos; ajustar preparación y candidatos dentro de cada entrenamiento interno; seleccionar; reajustar la configuración con todo el entrenamiento externo; evaluar una vez en el bloque externo. El resultado externo no decide hiperparámetros dentro de ese ciclo. La separación por grupo o tiempo debe respetarse en ambos niveles cuando corresponda.

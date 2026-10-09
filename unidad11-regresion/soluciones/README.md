# Soluciones razonadas — Regresión

[Volver a la unidad](../README.md)

## 1. Parámetros y alcance

El intercepto es 3 kWh y la pendiente es 2 kWh/h. Para 5 horas se predicen 13 kWh. La pendiente describe el cambio de la predicción por hora adicional, no un efecto causal demostrado. Tampoco podemos afirmar que el consumo real en reposo sea 3 kWh: cero horas queda fuera del rango de entrenamiento de 1 a 8 horas. Harían falta observaciones y un diseño apropiado para sostener esas afirmaciones.

## 2. Recta manual

Las medias son `x_media = 2` e `y_media = 11/3`. La suma de productos de desviaciones es `5/3 + 0 + 4/3 = 3`; la suma de desviaciones cuadradas de x es `1 + 0 + 1 = 2`.

Entonces `b = 3/2` y `a = 11/3 − (3/2) × 2 = 2/3`. Para `x = 2,5`, la predicción es `2/3 + (3/2) × (5/2) = 53/12`, aproximadamente **4,417**. Es una predicción puntual, no un intervalo ni una certeza sobre una observación nueva.

## 3. Residuos y MAE

Las predicciones son `13/6`, `11/3` y `31/6`. Los residuos `real − predicción` son `−1/6`, `1/3` y `−1/6`. Su suma es cero, pero sus magnitudes no lo son:

```text
MAE = (1/6 + 1/3 + 1/6) / 3 = 2/9 ≈ 0,222
SSE = 1/36 + 1/9 + 1/36 = 1/6
RMSE = raiz((1/6)/3) = raiz(1/18) ≈ 0,236
```

Los errores positivos y negativos se compensan en el promedio firmado. Con intercepto, esa compensación en entrenamiento es una propiedad de mínimos cuadrados; no significa que cada predicción sea correcta.

## 4. Entrada constante

Todas las desviaciones respecto de la media de x son cero, de modo que el denominador de la fórmula de pendiente es cero. Muchas parejas de parámetros dan la misma predicción cuando x = 2: cualquier pareja que cumpla `a + 2b = 4` produce el mejor valor constante para mínimos cuadrados en estos casos. No hay una pendiente única identificable con estos datos.

Media y mediana de los objetivos valen 4. Su MAE de entrenamiento es `(|3−4| + |4−4| + |5−4|)/3 = 2/3`. La función de ajuste de recta rechaza la entrada constante en lugar de presentar una pendiente arbitraria como aprendida.

## 5. R² negativo e indefinido

Con reales `1, 2, 3`, la media evaluada es 2 y `SST = 1 + 0 + 1 = 2`. Para predicciones `4, 4, 4`, `SSE = 9 + 4 + 1 = 14`. Por tanto, `R² = 1 − 14/2 = −6`.

El error cuadrático supera al de usar la media de esos objetivos evaluados. No hay una prohibición de R² negativos fuera de entrenamiento.

Para reales `2, 2`, SST es cero. Con predicción perfecta, la expresión contiene `0/0`; con predicciones incorrectas tampoco permite calcular un R² finito por esa fórmula. Esta implementación devuelve `None`, lo guarda como `null` y lo imprime como `no definido`. No lo fuerza a 1 ni a 0. MAE y RMSE sí pueden informarse.

## 6. Comparación del caso lineal

La media y mediana aprenden cada una una constante con los 24 objetivos de entrenamiento; ambas valen 12 kWh. La recta aprende intercepto 3 y pendiente 2 con los 24 pares. Se comparan las predicciones sobre los mismos 12 identificadores de validación.

Las constantes tienen MAE de validación aproximado de 3,050 kWh; la recta, de 0,300 kWh. Se elige recta por menor MAE, sin abrir prueba. RMSE, R² y residuos ayudan a interpretar; no sustituyen el criterio prefijado.

La media de objetivos de validación que aparece en SST describe la variación de ese conjunto. No es una referencia que se pudiera haber ajustado sin conocer esos objetivos. Para comparar predictores disponibles se conserva la constante aprendida en entrenamiento.

## 7. Transformación aprendida

Con `z = (x − 5)/4,5`:

| Horas | z |
|---:|---:|
| 0,5 | −1 |
| 5 | 0 |
| 9,5 | 1 |
| 12 | 14/9 ≈ 1,556 |

El modelo aprendió coeficientes para esta transformación. Recalcularla con validación, prueba o consultas incorpora información de esos conjuntos y cambia el significado de las potencias: ya no se está aplicando el mismo predictor. Tampoco se recorta 1,556 a 1; se marca extrapolación y se conserva la operación declarada.

## 8. Complejidad y sobreajuste

El polinomio de grado 9 tiene diez coeficientes y diez entradas de entrenamiento distintas. Puede pasar prácticamente por todos esos puntos, incluidas sus perturbaciones. Su MAE de entrenamiento es menor que `1e-10`, pero el de validación es aproximadamente 2,808 kWh.

La cuadrática tiene tres coeficientes, MAE de entrenamiento aproximado de 0,583 kWh y de validación de 0,190 kWh. Seleccionamos cuadrática porque obtiene menor MAE de validación bajo el protocolo. En este ejemplo, la capacidad adicional del grado 9 se traduce en oscilaciones y peores errores entre observaciones. No se deduce que un modelo de grado 2 sea siempre el adecuado para otros problemas.

Escalar la entrada facilita resolver el sistema numérico, pero no cambia por sí solo la capacidad del polinomio ni evita ese sobreajuste. El R² de la cuadrática impreso como `1.000` está redondeado: su valor de validación es aproximadamente 0,999882.

## 9. Sensibilidad a la perturbación

Ejecuta [03_sensibilidad_extremo.py](03_sensibilidad_extremo.py) desde la raíz:

```bash
python unidad11-regresion/soluciones/03_sensibilidad_extremo.py
```

Se añade 20 kWh al objetivo de `lineal-entrenamiento-24`, en una lista en memoria. Las horas, los demás objetivos y la validación quedan iguales. No se escribe ningún CSV y no se consulta prueba.

El intercepto pasa de 3 a `4/3 ≈ 1,333`; la pendiente, de 2 a `23/9 ≈ 2,556`; el MAE de validación pasa de 0,300 a aproximadamente 0,933 kWh. El objetivo grande en una entrada alta aumenta la pendiente. El criterio cuadrático da mucho peso a ese error, por lo que se altera el ajuste para todos los casos.

La perturbación fue creada expresamente. En una observación real, un extremo puede ser error de medición o un evento válido. Suprimirlo solo para mejorar una métrica ocultaría una decisión importante. Hace falta investigar y documentar antes de corregir, excluir o cambiar de modelo.

## 10. Hallazgo y cierre

Una respuesta posible:

> La recta alcanza R² de validación cercano a 0,948 en el conjunto curvo, pero sus residuos muestran una forma de U y su MAE es 4,043 kWh. La cuadrática reduce ese MAE a 0,190 kWh sobre los mismos nueve casos. La seleccionamos con validación y conservamos los coeficientes, centro, escala, código y huellas de datos antes del cierre. Evaluaremos solo ese candidato sobre prueba, sin reajustar ni volver a elegir por su resultado.

La curvatura residual evidencia una limitación de la recta incluso dentro del rango observado. Predecir para 12 horas introduce además extrapolación. Ninguno de esos análisis establece que intervenir sobre las horas cause un cambio concreto de consumo. El pequeño escenario sintético tampoco demuestra utilidad en una instalación real.

Si los resultados de prueba inspiran un nuevo modelo, habría que declarar ese uso para desarrollo y buscar una evaluación nueva apropiada. Si ya se consultaron las respuestas públicas, debe constar; el cierre sigue siendo un ejercicio sobre el flujo, no una evaluación personal ciega.

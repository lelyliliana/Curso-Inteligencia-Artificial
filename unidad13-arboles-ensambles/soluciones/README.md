# Soluciones razonadas — Árboles y ensambles

[Volver a la unidad](../README.md) · [Programa de cálculo y sensibilidad](03_corte_e_inestabilidad.py)

## 1. Impureza y ponderación

Hay cuatro positivos y cuatro negativos: `Gini = 2 × 0,5 × 0,5 = 0,5`. En el corte 2,5, el hijo izquierdo tiene dos negativos, Gini 0; el derecho tiene dos negativos y cuatro positivos, Gini `4/9`. La impureza ponderada es `(2 × 0 + 6 × 4/9)/8 = 1/3` y la reducción `0,5 − 1/3 = 1/6`.

En 4,5 ambos hijos son puros. La impureza final es 0 y la reducción 0,5, mayor que la anterior. El algoritmo aplica las restricciones de tamaño antes de aceptar una partición. Si `min_samples_leaf=5`, ningún corte es posible con solo ocho casos; eso no hace incorrecta la fórmula.

## 2. Recorrido y probabilidad

Para 60: `60 > 30`, luego `60 <= 70`, luego `60 > 57,5`. La hoja tiene diez casos, `value=[2,8]`: dos de clase 0 y ocho de clase 1. Devuelve `p(1)=8/10=0,8`, clase 1.

Los conteos proceden del entrenamiento. No son las cantidades de aciertos y errores de prueba ni una garantía de frecuencia futura. La profundidad cuenta enlaces desde la raíz de profundidad 0; esta hoja está a profundidad 3.

## 3. Complejidad y selección

El mayor F1 de validación corresponde a `arbol_3`, 0,9375, mostrado como 0,938. El árbol libre obtiene 1 en entrenamiento, pero 0,875 en validación: en este experimento su mejor ajuste no se conserva fuera de entrenamiento. El árbol de profundidad 1 resulta demasiado limitado para aislar toda la franja y acumula 13 FP.

El árbol controlado restringe tanto profundidad como mínimo por hoja; no se puede atribuir toda la diferencia a un solo control. Una única comparación tampoco demuestra que el árbol libre siempre sea peor ni que exista una profundidad universalmente óptima.

## 4. Una etiqueta y un corte

Originalmente las clases ordenadas son `00001111`: 4,5 separa perfectamente. Al cambiar la cuarta etiqueta, quedan `00011111`: ahora 3,5 separa perfectamente. La consulta 4 pasa de clase 0 a 1.

El cambio es un experimento de sensibilidad en memoria. Alterar la etiqueta original porque mejora una métrica confundiría el objetivo observado con la predicción deseada. Una corrección real requiere evidencia independiente de un error en el dato, trazabilidad y revisión del protocolo.

## 5. Media de una hoja de regresión

La media de 6 y 8 es 7. Todo valor de entrada que llegue a esa hoja recibe 7, incluidos 4 y 10 en el ejemplo. Aunque los cuatro datos originales sigan `y=2x`, el árbol aprendió regiones constantes y no esa fórmula lineal. Extrapolar a 20 requeriría otro supuesto de modelo, cuya utilidad también habría que evaluar.

## 6. Bootstrap

Las seis extracciones `[0,2,2,4,0,5]` contienen cuatro casos distintos: 0, 2, 4 y 5. Se repiten 0 y 2; faltan 1 y 3 si el entrenamiento original tiene índices 0 a 5. No hay que eliminar las repeticiones: son parte del remuestreo.

Solo se remuestrea entrenamiento. Incorporar casos de validación o prueba al bootstrap permitiría que influyeran en ajuste. Los casos no extraídos de un árbol pueden utilizarse en otros procedimientos de evaluación fuera de bolsa, pero esa evaluación no se implementa en este laboratorio.

## 7. Promedio y empate

`(0,2 + 0,6 + 0,6)/3 = 0,466666…`. El promedio predice clase 0. Las clases individuales son 0, 1 y 1; su voto mayoritario daría clase 1. Los ensambles utilizados promedian probabilidades, por lo que aplicar el segundo método cambiaría el procedimiento.

Con probabilidad media exactamente 0,5, ambas clases tienen igual probabilidad y `predict` elige 0. No hay selección de otro umbral. La precisión numérica y la convención de empate merecen distinguirse: una cifra impresa como 0,500 podría ocultar un valor ligeramente mayor o menor.

## 8. Entradas candidatas y boosting

El `1.0` de bagging es una fracción: cada árbol recibe todas las entradas. Sus árboles base tienen `max_features=None`, de modo que consideran ambas señales en cada corte. El entero `1` del bosque indica una entrada candidata en cada nodo; diferentes nodos pueden considerar señales diferentes. La biblioteca puede inspeccionar más entradas si hace falta para encontrar una partición válida.

Ambos ensambles usan bootstrap y promedian probabilidades. En boosting, las etapas se construyen secuencialmente para reducir una pérdida del modelo acumulado, con mecanismos que dependen de la variante. No basta con aumentar el número de árboles independientes para convertir bagging en boosting.

## 9. Métricas de bagging

```text
precisión = VP/(VP+FP) = 34/41 ≈ 0,829268
recobrado = VP/(VP+FN) = 34/43 ≈ 0,790698
F1 = 2VP/(2VP+FP+FN) = 68/84 ≈ 0,809524
```

Con VN=70, los conteos suman `34+70+7+9=120`. El bosque tiene VP=32, VN=72, FP=5 y FN=11: F1=`64/80=0,8`. Tiene mejor precisión, pero menor recobrado. El criterio fijado era F1, no minimizar FP. Si los costos reales motivaran otro criterio, habría que declararlo antes de otra selección apropiada.

La diferencia de unos 0,0095 en F1 no viene acompañada de una demostración de superioridad estadística. Las métricas redondeadas son para comunicar; la selección utiliza los valores completos.

## 10. Comprobar separación

En una copia, conserva entradas e identificadores y sustituye únicamente las etiquetas de prueba, por ejemplo invirtiendo 0 y 1. Ejecuta el cierre con el mismo código, dependencias y semilla.

Deberían conservarse las huellas de desarrollo, los rangos, parámetros, estructuras, remuestreos, resultados de desarrollo, selección, probabilidades y clases predichas de prueba. Deberían cambiar la huella de prueba y sus etiquetas; sus conteos, tipos de error y métricas pueden cambiar. Una métrica concreta podría coincidir por casualidad, por lo que no se exige que todas cambien.

Repetir la semilla verifica reproducibilidad en el entorno fijado. No prueba representatividad, independencia de casos, calibración ni que el modelo tenga poca variabilidad ante otros entrenamientos. La prueba automatizada tampoco puede verificar que una persona no haya leído antes las respuestas públicas.

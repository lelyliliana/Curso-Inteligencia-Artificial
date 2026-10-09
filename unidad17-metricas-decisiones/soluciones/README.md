# Soluciones razonadas

[Unidad](../README.md) · [Cálculo manual ejecutable](03_metricas_a_mano.py)

## 1. Etiqueta y acción

La etiqueta 1 significa que el caso necesita revisión según la referencia posterior; acción 1 significa proponer revisarlo. VP es revisión necesaria seleccionada; FP, revisión innecesaria seleccionada; FN, necesidad omitida; VN, caso sin necesidad no seleccionado. La etiqueta no demuestra el efecto causal de intervenir.

En validación de costos, no revisar produce VP=0, FP=0, FN=62 y VN=178. Exactitud=`178/240≈0,7417`; recobrado=0. El costo oficial es `6×62=372`. Una exactitud mayoritaria no acredita que se cubra la necesidad positiva.

## 2. Dos umbrales manuales

Con etiquetas `[1,0,1,0]`, puntuaciones `[0.8,0.8,0.4,0.1]` y corte 0,8 inclusivo, VP=FP=FN=VN=1. Precisión=recobrado=F1=0,5; costo=7.

Con corte 0,4 se seleccionan los tres primeros: VP=2, FP=1, FN=0, VN=1. Precisión=2/3, recobrado=1, F1=4/5; costo=1. El costo medio por caso es 0,25, frente a 1,75 con el primer corte.

## 3. Ausencias y ceros

Sin alertas, `VP+FP=0` y precisión no está definida. Sin positivos, `VP+FN=0` y recobrado no está definido. Sin negativos, especificidad y tasa FP no están definidas. Se escribe `null`, no una cifra elegida por conveniencia.

F1 se calcula directamente desde conteos. Si hay FN o FP y VP=0, vale cero; si VP=FP=FN=0, es indefinida. ROC AUC requiere ambas clases; AP requiere positivos según la convención explícita de esta unidad. Todos los positivos dan AP=1, sin definir ROC AUC.

## 4. Costos y elección

Con umbral 0,2: `90+6×7=132`. Con 0,1: `156+6×1=162`. El segundo elimina seis FN, ahorrando 36, y añade 66 FP; costo neto adicional 30. Se conserva 0,2 bajo el protocolo oficial.

Con FN=1, los costos en orden publicado son `[62,62,61,56,57,97,157,178]`: gana 0,5 con 56. Con FN=12 son `[744,744,677,518,387,174,168,178]`: gana 0,1 con 168. No cambiaron puntuaciones, decisiones de cada regla ni F1; cambió cómo se valoran los errores y, por tanto, qué regla se prefiere. Estas alternativas no se utilizan para elegir con prueba.

El umbral probabilístico `C_FP/(C_FP+C_FN)` se deriva comparando costos esperados individuales bajo los supuestos indicados. No sustituye validar probabilidades, población, consecuencias o restricciones de capacidad.

## 5. ROC AUC por pares

Puntuaciones positivas: 0,8 y 0,4. Negativas: 0,8 y 0,1. Los cuatro pares aportan, en ese orden, `0,5;1;0;1`. La media es 0,625. El empate vale medio, sin ordenar sus etiquetas para aumentar artificialmente el área.

La curva agrega el bloque completo 0,8. Introducir primero su positivo y luego su negativo produciría puntos intermedios que el umbral original no puede distinguir. ROC AUC describe ordenación entre clases, no una exactitud de decisión ni el costo de un umbral concreto.

## 6. AP por bloques

Tras s≥0,8: recobrado=1/2 y precisión=1/2. Tras s≥0,4: recobrado=1 y precisión=2/3. Tras s≥0,1: recobrado=1 y precisión=1/2.

AP=`(1/2−0)×1/2+(1−1/2)×2/3+(1−1)×1/2=7/12≈0,583333`. Usa precisión posterior a cada incremento, no trapecios entre puntos. La precisión en un umbral puede diferir considerablemente de AP.

## 7. Brier y transformación

Brier=`[(0,8−1)²+(0,8−0)²+(0,4−1)²+(0,1−0)²]/4=0,2625`. Para el laboratorio de costos, Brier de s es aproximadamente 0,158 y el de s², 0,198; AUC y AP coinciden porque se preservan orden y empates.

Para conservar decisiones de s≥t con números transformados se necesita comparar s²≥t², puesto que s y t están en [0,1]. Mantener t puede cambiar las decisiones aunque AUC no cambie. Brier y el gráfico por intervalos examinan aspectos probabilísticos distintos de la ordenación; no basta una única cifra para certificar calibración.

## 8. Prevalencia hipotética

Con recobrado 0,8 y tasa FP 0,1, prevalencia 5 % da `0,04/(0,04+0,095)=0,296296...`; prevalencia 50 % da `0,4/(0,4+0,05)=0,888889...`.

El supuesto es mantener ambas tasas condicionales ante el cambio de prevalencia. Puede incumplirse por cambios de medición, casos o mezcla de lotes. Con cupos las decisiones dependen de competidores dentro del lote; tampoco cabe garantizar tasas constantes. El cálculo no es una predicción validada de rendimiento futuro.

## 9. Frontera del cupo y empate entre políticas

En `validacion-L02`, para umbral 0,5, los diez elegibles ordenados tienen sufijos de ID:

```text
045:0.8, 056:0.8, 049:0.7, 051:0.7, 060:0.7,
035:0.6, 059:0.6, 033:0.5, 052:0.5, 058:0.5
```

El prefijo completo es `capacidad-validacion-`. Se seleccionan los primeros seis. Entre 035 y 059, ambos con 0,6, entra 035 por ID ascendente; no porque su etiqueta posterior sea favorable. El lote termina con VP=4, FP=2, FN=9, VN=15; costo=`2+4×9=38`, precisión=4/6 y recobrado=4/13.

En el conjunto completo, umbral 0,3 con cupo tiene FP=22 y FN=52: costo 230, 45 alertas. Umbral 0,5 con cupo tiene FP=10 y FN=55: costo 230, 30 alertas. El desempate elige 0,5 por menos alertas; no porque su F1 sea mayor. La regla de ID es una convención operativa que requeriría otra justificación en una aplicación real.

## 10. Cierre y límites

Cambiar solo etiquetas de prueba no debe alterar política elegida, evaluación de validación ni decisiones para las mismas puntuaciones, IDs y lotes. Cambia la huella del archivo, sus etiquetas y potencialmente métricas y resultados por caso. Las pruebas que modifican filas en memoria mantienen la huella original simulada; al editar un CSV real esta se recalcula.

Las puntuaciones del lote de prueba sí se usan para ordenar y aplicar el cupo: el escenario exige tener el lote completo disponible. Las etiquetas no se utilizan para decidir ni para volver a seleccionar. Si se necesitara decidir en orden de llegada, este protocolo no bastaría.

Cierre ejecutado con los parámetros registrados previamente:

| Experimento | Política elegida | Casos | VP | FP | FN | Costo total | Costo por caso |
|---|---|---:|---:|---:|---:|---:|---:|
| Costos | `umbral020` | 120 | 23 | 52 | 4 | 76 | 0,633 |
| Capacidad | `umbral050_top6` | 120 | 13 | 0 | 29 | 116 | 0,967 |

En capacidad, precisión=1 en esta muestra, pero solo se detectan 13 de 42 positivos: recobrado≈0,310. No es detección perfecta. Los cuatro lotes respetan el cupo de seis. No compares costos totales de muestras de distinto tamaño como si fueran directamente equivalentes; incluso el costo medio depende de composición y costos fijados.

Son resultados sintéticos públicos. Ni una precisión elevada ni una política seleccionada demuestran utilidad, equidad, capacidad futura o beneficios de intervención en una población real.

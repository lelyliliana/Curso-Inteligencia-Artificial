# Soluciones razonadas

[Unidad](../README.md) · [Paso manual ejecutable](03_paso_kmeans.py)

## 1. Un paso de K-means

Con centros iniciales `(1,1)` y `(9,7)`, A y B se asignan al primero; C y D, al segundo. Los nuevos centros son `((1+1)/2,(1+3)/2)=(1,2)` y `((7+9)/2,(7+7)/2)=(8,7)`. La inercia pasa de `0+4+4+0=8` a `1+1+1+1=4`. Una nueva asignación conserva esos grupos.

Esto verifica el ejemplo, no que todo ajuste encuentre un óptimo global. El programa manual no implementa reinicios ni recuperación de grupos vacíos.

## 2. Cambio de unidades

En horas y kWh, las distancias desde `(0,0)` son `sqrt(1²+20²)≈20,025` y `sqrt(4²+0²)=4`: gana el segundo centro. En horas y MWh son `sqrt(1²+0,020²)≈1,0002` y 4: gana el primero.

Estandarizar cada variable con los parámetros de entrenamiento neutraliza ese cambio positivo de unidad en este ejemplo, salvo diferencias numéricas. No decide qué variables son relevantes ni convierte la distancia en una medida universal de semejanza. Tampoco hace apropiada una media muy afectada por extremos.

## 3. Silueta

Para A, la distancia al otro miembro de su grupo es 2. Las distancias a C y D son `sqrt(72)` y 10. Por tanto, `b=(sqrt(72)+10)/2≈9,242641` y `s=(b−2)/b≈0,783612`.

La silueta utiliza distancias a observaciones de cada grupo. Sustituirlas por distancias a centros daría otra cantidad, no esta métrica. El promedio de todas las siluetas tampoco equivale necesariamente a la silueta de un supuesto «caso medio».

## 4. Cantidad de grupos y estabilidad

`k3` tiene silueta de validación aproximadamente 0,864, frente a 0,667 de `k4`. Aunque `k4` reduce la inercia de entrenamiento de 6,763 a 5,291, el protocolo selecciona por silueta y elige `k3`.

ARI=1 frente a las dos semillas alternativas indica que cada configuración conserva su partición de validación bajo esos cambios de inicialización. No compara directamente `k3` con `k4`. Tampoco prueba estabilidad ante otros casos, periodos o variables; una división adicional puede ser estable sin aportar utilidad.

## 5. Nombres arbitrarios

Las particiones `[0,0,1,1]` y `[7,7,3,3]` ponen juntos a los mismos pares. ARI=1. Una comparación literal de los números encontraría cero coincidencias, aunque la agrupación sea equivalente. Los colores de las figuras también identifican grupos dentro de cada ajuste, sin alineación semántica entre paneles.

## 6. Alerta, etiqueta y error

Una alerta es una decisión de priorización a partir de una puntuación. Una etiqueta real requiere un procedimiento de confirmación externo. Un error de captura requiere evidencia de que el registro no representa correctamente lo observado.

Un taller que abre excepcionalmente de noche puede tener consumo inusual y legítimo. No conviene borrar el registro por ser raro ni afirmar una falla solo por su puntuación. En el laboratorio, `anomalia_sintetica` identifica un mecanismo de generación: no sustituye una investigación real.

## 7. Umbrales y empates

Con `[1,2,3,4,5]` y `q=0,8`, `ceil(0,8×5)=4`: umbral 4, alerta únicamente para 5. Con `[1,2,2,2]` y `q=0,5`, la posición es 2, umbral 2; ningún valor es estrictamente mayor, por lo que no hay alertas.

La regla no fuerza una fracción exacta de alertas cuando hay empates. En el ejemplo real, el umbral es el valor 57 de 60 puntuaciones y deja tres mayores. No asegura esa misma fracción en futuros conjuntos.

## 8. Calidad de las alertas

Para el bosque: VP=3, VN=64, FP=0 y FN=13. Los conteos suman 80.

```text
precisión = 3/(3+0) = 1
recobrado = 3/(3+13) = 0,1875
F1 = 6/(6+0+13) = 6/19 ≈ 0,315789
exactitud = (3+64)/80 = 0,8375
```

La exactitud 83,75 % puede ocultar que se omiten 13 de 16 positivos. No alertar nunca ya alcanza `64/80=80 %`. El bosque gana por F1 entre las opciones, pero no demuestra un recobrado suficiente. La precisión perfecta se basa en tres alertas y no garantiza ausencia futura de falsos positivos.

## 9. Casos concretos

El caso `anomalias-validacion-001` tiene señales `(57,01;52,76)`, etiqueta 1 y puntuación del bosque aproximadamente 0,594042. No supera el umbral 0,601445: es FN. Para la distancia, su puntuación es 0,367582 y tampoco supera 1,807755. Estar cerca de la media global no garantiza pertenecer a un modo ordinario.

El caso `anomalias-validacion-057`, ordinario, tiene distancia 2,015155 y activa una alerta: FP de esa referencia. No hay un FP del bosque en esta validación. Para interpretar ambos en la realidad harían falta contexto operativo, calidad y disponibilidad de señales, confirmación independiente y costos de revisar u omitir el caso.

## 10. Separación y tipo de aprendizaje

Al cambiar solo etiquetas de prueba, deben conservarse escala, centros o bosque, umbrales, selección, resultados de desarrollo y predicciones o alertas de los mismos casos. Cambian la huella del archivo, sus referencias y posiblemente matrices y métricas. Una métrica podría coincidir por casualidad; eso no significa que no se haya leído la nueva etiqueta.

Usar F1 de validación con etiquetas sintéticas para elegir hace que la selección aproveche supervisión, aunque cada detector se ajuste sin etiquetas. En agrupamiento no se dispone de esa referencia y se usa silueta, cuyo alcance es interno. Ni la semilla fija ni los tests prueban que una persona no haya leído antes las respuestas públicas.

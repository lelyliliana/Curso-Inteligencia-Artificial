# Protocolo u19-v1-bce-validacion

[Unidad](../README.md) · [Datos](README.md)

Este es un protocolo de demostración reproducible, no un preregistro externo ni una prueba secreta. Sus decisiones están fijadas en el código y los resultados son públicos.

## Pregunta y opciones

XOR: comparar una referencia constante, una frontera logística lineal y una red de una capa oculta. Ruido: comparar una referencia constante, la lineal y dos versiones de la misma red, con o sin L2, bajo pocos datos e inversión de etiquetas.

| Laboratorio | Orden de candidatos | Presupuesto por candidato entrenable |
|---|---|---|
| xor | prevalencia, lineal, red8 | 3000 épocas |
| ruido | prevalencia, lineal, red32, red32_l2 | 6000 épocas |

Prevalencia estima la fracción positiva solo con entrenamiento y usa su logit como sesgo constante. Lineal tiene dos pesos y un sesgo. Las redes tienen tanh en la capa oculta, una salida logística y 8 o 32 unidades. Lambda=0 salvo red32_l2, donde lambda=0,02. No se comparan más tasas, semillas, arquitecturas o umbrales para construir las tablas oficiales.

## Preparación, ajuste y selección

1. Leer entrenamiento y validar esquema, ambas clases y variación de cada entrada. Ajustar medias y desviaciones poblacionales solo con esas filas. Excluir ID y objetivo de la matriz de entradas.
2. Leer validación, comprobar separación de ID y aplicar el escalado anterior. Sus etiquetas están disponibles para seleccionar, pero no para calcular actualizaciones de parámetros ni reajustar la escala.
3. Inicializar la capa logística en cero. Inicializar cada red con PCG64(19): W1 normal con desviación 1/sqrt(d), después W2 normal con desviación 1/sqrt(h), sesgos cero. Reiniciar el generador por candidato; red32 y red32_l2 parten exactamente del mismo estado.
4. Entrenar con lote completo y tasa 0,15. Objetivo J=BCE media + lambda/2 × suma de cuadrados de pesos; no penalizar sesgos. La penalización no lleva otro factor 1/n. Calcular todos los gradientes con los parámetros previos antes de actualizar.
5. Registrar época 0, cada múltiplo de 100 y la época final si no coincide. Guardar BCE de entrenamiento, BCE de validación, objetivo penalizado de entrenamiento y norma del gradiente. Las curvas comparativas muestran BCE sin penalización.
6. Conservar una copia independiente del mejor estado de cada candidato. Actualizarlo solo cuando BCE de validación es menor que la mejor previa en más de 1e−12. Ante empate dentro de esa tolerancia, mantener la época anterior. Completar todo el presupuesto; no hay una condición de interrupción anticipada.
7. Comparar los mejores estados por BCE de validación con la misma tolerancia y el orden de la tabla como desempate. No usar exactitud o F1 como criterio alternativo. Cada consulta a validación participa en desarrollo: 31 puntos por candidato entrenable en XOR, 61 en ruido, más la referencia constante.
8. No reajustar con validación después de elegir. Predicción binaria con p>=0,5; una igualdad da clase 1. No calibrar probabilidades ni optimizar el umbral.

Conservar `parametros_iniciales`, `parametros` del mejor punto y `parametros_finales` permite distinguir la trayectoria de entrenamiento de la selección. Cambiar etiquetas de validación puede cambiar el punto elegido; no debe cambiar los parámetros al final del presupuesto ni las pérdidas de entrenamiento de la trayectoria original.

## Cierre y archivos

Solo con `--evaluar-prueba`: abrir prueba después de seleccionar, validar separación de ID y evaluar exclusivamente el estado elegido. No volver a entrenar, no comparar candidatos allí y no sustituir resultados desfavorables. Una modificación motivada por estos resultados necesita otra evaluación independiente.

El JSON documenta datos, versiones, escalado, configuración, estados, historiales, selección y predicciones. Los CSV de entrenamiento/validación contienen las predicciones del **mejor punto de cada candidato**; el de prueba contiene solo el elegido. Las tres figuras utilizan desarrollo, incluso si el informe incluye cierre.

No se implementan minilotes, parada temprana con paciencia, búsqueda de semillas, autograd, GPU, modelos multicapa profundos ni una aplicación operativa. Esas decisiones requieren su propio alcance y no se atribuyen a estos programas.

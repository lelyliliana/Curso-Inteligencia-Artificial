# Protocolo `clasificacion-v1`

[Unidad](../README.md) · [Diccionario](README.md)

## Pregunta y contrato

Predecir la etiqueta binaria de revisión confirmada después de la decisión, usando únicamente una señal previa sintética. Clase positiva: 1. La disponibilidad es declarada por el escenario y no auditable con estos CSV. Identificador y etiqueta no son entradas predictivas.

Las particiones son fijas y nuevas para esta unidad. Se comparan todos los candidatos sobre los mismos casos, sin eliminar filas por su error. Datos inválidos detienen el experimento. Entrenamiento y validación requieren ambas clases; prueba no. Una validación sin positivos no permitiría aplicar la comparación propuesta: exige revisar el diseño, no forzar métricas ni repetir particiones hasta mejorar resultados.

## Decisiones fijadas

| Componente | Regla |
|---|---|
| Transformación | Media y desviación estándar poblacional de la señal, solo con entrenamiento |
| Modelo | Una regresión logística de una entrada con intercepto |
| Función de ajuste | Pérdida logarítmica media más `0,01 × b² / 2`; intercepto sin penalizar |
| Inicialización | a = b = 0 |
| Optimizador | Gradiente de todo entrenamiento; tasa 0,2; exactamente 3000 actualizaciones |
| Parada | Número fijo de pasos; no se consulta validación para parar |
| Referencia mayoría | Clase más frecuente de entrenamiento; empate a 0; frecuencia positiva como probabilidad constante |
| Referencia siempre 1 | Todas las clases positivas; sin probabilidad estimada ni pérdida probabilística atribuida |
| Selección | Mayor F1 de la clase 1 en validación, sin redondear |
| Empate entre candidatos | Primer candidato en el orden indicado abajo, solo ante igualdad exacta |
| Reajuste con validación | No |
| Cierre | Evaluar únicamente el elegido, con su umbral, sobre prueba |

Orden de candidatos:

1. Equilibrado: `mayoria`, `siempre_1`, `logistica_050`.
2. Desbalanceado: `mayoria`, `siempre_1`, `logistica_050`, `logistica_020`, `logistica_080`.

Las tres reglas logísticas del segundo experimento comparten coeficientes, centro, escala y probabilidades; solo difieren en umbral. Se predice 1 si `p >= umbral`. No se realizan tres ajustes. No se optimizan tasa, iteraciones ni penalización con validación o prueba.

El código general permite otros valores al llamar a la función de ajuste, pero los laboratorios usan la configuración fija anterior. Cambiarla, añadir umbrales, calibrar, balancear clases, imputar o incorporar variables crea otro procedimiento que debe declararse y evaluarse.

## Métricas y límites

Se informa matriz de confusión, exactitud, precisión, recobrado y F1. También se conserva pérdida logarítmica sin penalización para la logística y para la frecuencia constante de entrenamiento. La pérdida del historial de ajuste sí incluye penalización: no confundir ambas.

Una métrica cuyo denominador es cero se guarda como `null`. Con positivos reales pero ninguna predicción positiva, precisión es indefinida, recobrado es cero y F1 es cero. Si no hay positivos reales ni predichos, las tres quedan indefinidas. Prueba conserva esos casos y las demás métricas calculables.

F1 fue elegido para enseñar la comparación centrada en positivos; no representa por sí solo costos reales ni restricciones de capacidad. La selección se limita a los candidatos enumerados, no demuestra un umbral óptimo global. La curva sigmoide y una pérdida pequeña no certifican calibración.

## Secuencia

1. Leer entrenamiento y validación; comprobar columnas, valores, etiquetas e identificadores únicos.
2. Ajustar transformaciones, referencias y modelo con entrenamiento.
3. Evaluar los candidatos sobre los mismos conjuntos de desarrollo y seleccionar por F1 de validación.
4. Conservar el informe previo, las huellas de datos, código, configuración y candidato elegido. Mantener variantes en copias separadas.
5. Ejecutar `--evaluar-prueba` con los mismos archivos y código. El programa repite ajuste y selección y abre prueba después; no reajusta con validación.
6. Comparar protocolo, código, huellas de entrenamiento/validación, modelo, referencias, candidatos y selección con la exportación previa. Si cambiaron, investigar antes de presentarlo como cierre del mismo experimento.
7. Informar prueba sin elegir otra vez. Si un resultado motiva cambios, declarar que la prueba ya influyó y planear una nueva evaluación apropiada.

La ejecución común funciona sin `prueba.csv`. Las pruebas de invariancia cambian etiquetas de prueba y comprueban que no cambien ajuste, probabilidades, umbral ni selección. No impiden que una persona lea antes los archivos públicos, el generador o las respuestas; no acreditan una evaluación personal ciega.

## Exportación

El JSON conserva versiones, huellas SHA-256, configuración, transformación, coeficientes, historial, criterio y resultados. Las tablas registran candidato, caso, señal, etiqueta real, probabilidad cuando corresponde, clase, tipo de resultado y marca fuera de rango. Entrenamiento y validación incluyen todos los candidatos; prueba, solo el elegido. Las figuras muestran exclusivamente desarrollo.

Guardar cada exportación en una carpeta nueva. Un fallo puede dejar archivos parciales; la exportación no es transaccional. Las huellas identifican contenido leído, no su autenticidad ni el commit. Una consulta sin etiqueta permite obtener una predicción y comprobar su rango, pero no medir su error.

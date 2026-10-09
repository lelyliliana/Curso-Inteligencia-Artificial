# Protocolo `metricas-decisiones-v1`

[Unidad](../README.md) · [Datos](README.md)

## Objeto de selección

Elegir una política que propone revisar casos con puntuaciones previas fijas. Etiqueta positiva: `requiere_revision=1`. No hay ajuste de predictor, escalado, calibrador ni reajuste final. La búsqueda se limita a las políticas enumeradas; las curvas recorren más puntos únicamente para describir la ordenación.

| Regla | Costos | Capacidad |
|---|---|---|
| Validación / prueba | 240 / 120 casos | 8 / 4 lotes de 30 casos |
| Costo FP | 1 | 1 |
| Costo FN | 6 | 4 |
| Costos VP y VN | 0 | 0 |
| Restricción | Sin cupo | Máximo seis revisiones por lote |
| Objetivo | Menor costo total de validación | Menor costo total de validación entre políticas con cupo |
| Desempate | Menos alertas, después orden publicado | Menos alertas, después orden publicado |

Son costos convencionales de clasificación errónea. No incluyen costo de todas las revisiones ni beneficios causales. El costo medio divide el total entre todos los casos. La selección no usa F1, AUC, AP, Brier ni precisión como sustitutos del objetivo.

## Políticas en orden

Costos: `nadie`, `umbral080`, `umbral060`, `umbral050`, `umbral040`, `umbral020`, `umbral010`, `umbral000`. Los umbrales significan `puntuacion >= t`; nadie nunca alerta. Umbral cero revisa a todos.

Capacidad: `nadie`, `top6`, `umbral030_top6`, `umbral050_top6`, `umbral070_top6`. Top6 equivale a umbral cero con cupo. Dentro de cada lote, filtrar por umbral, ordenar puntuación descendente y `caso_id` ascendente y tomar hasta seis. Las etiquetas no participan. No se transfieren plazas sobrantes entre lotes. Se supone que el lote completo está disponible antes de asignar.

El umbral 0,5 sin cupo es un diagnóstico separado, nunca candidato aunque en otra muestra no excediera la capacidad. Las políticas admitidas satisfacen el cupo por construcción, sin depender de observar etiquetas. En prueba se mantiene el número seis y la regla completa, no los IDs seleccionados en validación.

## Métricas y diagnósticos

Guardar VP,VN,FP,FN, número de casos, positivos, alertas, prevalencia, exactitud, precisión, recobrado, F1, especificidad, tasa FP, costo total y costo por caso. Para capacidad, registrar conteos y métricas por lote. Las métricas globales se calculan desde conteos sumados, no promediando razones de lotes.

Cualquier denominador cero produce `null` para su métrica. F1 usa `2VP/(2VP+FP+FN)`: es cero si hay errores y ningún VP, y `null` si el denominador es cero. No se cambian las convenciones para mejorar una tabla.

Los diagnósticos de ordenación agrupan empates completos y recorren umbrales únicos descendentes, precedidos por un punto sin alertas. ROC AUC usa trapecios y requiere ambas clases. AP usa incrementos de recobrado por precisión del bloque y requiere positivos; no es el área trapezoidal PR. El extremo gráfico PR (0,1) es una convención, sin alterar precisión indefinida del punto sin alertas.

Brier se calcula como promedio de `(s−y)²` para puntuaciones interpretadas como probabilidades. Los cinco intervalos de fiabilidad son `[0,.2),[.2,.4),[.4,.6),[.6,.8),[.8,1]`. Conservar vacíos con n=0 y medias nulas. No se ajusta un calibrador ni se declaran intervalos de confianza.

El contraste `s²` se fija como diagnóstico de validación: mantiene orden y empates en estos datos, pero modifica error probabilístico. No participa en la selección. La sensibilidad de precisión a prevalencias de 5 %, 20 % y 50 % supone tasas condicionales constantes de la política elegida; es un cálculo hipotético, especialmente limitado cuando existe cupo. Las variantes de costo de los ejercicios tampoco reemplazan el protocolo oficial.

## Secuencia de ejecución y cierre

1. Leer solo validación, comprobar datos y registrar huella.
2. Aplicar todas las políticas candidatas a los mismos casos; evaluar con etiquetas de validación.
3. Seleccionar costo, alertas y orden sin redondear; conservar la configuración elegida.
4. Calcular los diagnósticos de validación, que no cambian la elección.
5. Exportar desarrollo con `prueba: null` y sin huella de prueba. Conservar también commit, comandos y conocimiento previo de respuestas públicas.
6. Cerrar con `--evaluar-prueba`: repetir los pasos anteriores, abrir prueba después de elegir y comprobar separación de IDs y lotes.
7. Aplicar solo la política elegida a los nuevos casos. Sus puntuaciones y lotes definen las decisiones; sus etiquetas solo evalúan. No volver a seleccionar.
8. Contrastar desarrollo, huella, código, versiones y política con el registro previo; informar límites y preparar evaluación nueva si prueba motiva cambios.

La ejecución por defecto no necesita `prueba.csv`. Las pruebas cambian sus etiquetas y verifican que no cambien la selección ni las decisiones. No impiden que una persona consulte respuestas públicas antes de cerrar. No se considera una evaluación ciega del aprendizaje ni una demostración de eficacia real.

## Artefactos

JSON conserva protocolo, costos, cupo, políticas, criterio, fuentes, métricas, decisiones y diagnósticos. CSV de validación contiene todas las políticas; el de prueba, solo la elegida. El diagnóstico sin cupo tiene su propio CSV. Las figuras solo usan validación, también en cierre.

Los informes de texto registran Python; las exportaciones gráficas añaden versiones de Matplotlib y NumPy. No se necesita serializar un estimador porque no se ajusta ninguno. Los parámetros y desempates definen la regla; conserva el código para reproducir su aplicación. Una escritura fallida puede dejar artefactos parciales y nunca se sobrescribe una carpeta existente.

# Protocolo fijado — u20-v1-bce-validacion

[Unidad](../README.md) · [Datos](README.md)

El laboratorio de equivalencia es una comprobación numérica independiente de este protocolo predictivo. Se fijaron los datos, candidatos, semillas, presupuesto y criterio de selección antes de evaluar prueba. No se cambió la configuración después del cierre para mejorar su resultado.

## Información permitida

1. Leer entrenamiento; comprobar esquema y ambas clases. Calcular media y desviación poblacional solo allí.
2. Leer validación, comprobar IDs separados y transformarla con la preparación ya ajustada.
3. Ajustar la referencia de prevalencia con las etiquetas de entrenamiento.
4. Entrenar lineal y red12_8 con gradientes calculados solo en minilotes de entrenamiento. Usar validación únicamente para comparar estados registrados y candidatos.
5. Seleccionar estado y candidato; conservar esa decisión.
6. Solo con `--evaluar-prueba`, leer prueba y comprobar sus IDs. Transformar con la misma escala y evaluar al elegido, sin reajustar, comparar alternativas o cambiar el umbral.

El acceso a validación influye en el **estado elegido**, pero no en la trayectoria de pesos que el entrenamiento calcula hasta agotar las 120 épocas. Las pruebas alteran etiquetas de validación y comprueban que los estados inicial y final y el orden de lotes se conservan. Otras invierten las etiquetas de prueba y comprueban invariancia del ajuste, selección y logits.

## Configuración

| Aspecto | Valor |
|---|---|
| Entradas | senal_a, senal_b, en ese orden; estandarizadas |
| Dispositivo y tipo | CPU; float32 |
| Candidatos, en orden de desempate | prevalencia, lineal, red12_8 |
| Capas ocultas | Ninguna, ninguna, [12,8]; tanh entre capas |
| Pérdida | BCE media desde logits; sin L2 ni ponderación de clases |
| Adam | Tasa 0,01; betas=(0,9;0,999); epsilon=1e−8; weight_decay=0 |
| Presupuesto | 120 épocas para cada candidato entrenado |
| Lotes | 32; barajado; último lote conservado; cero procesos trabajadores |
| Semillas | Inicialización 20; generador propio de DataLoader 2020 |
| Registro y selección | Época 0 y cada 10 épocas hasta 120 |
| Mejora mínima | BCE nueva menor que mejor BCE − 1e−8 |
| Empate | Primero la época anterior registrada; entre candidatos, orden declarado |
| Regla de clase | Positiva cuando p ≥ 0,5 |
| Ajuste tras elegir | Ninguno |

Se fija un hilo PyTorch y `torch.use_deterministic_algorithms(True)`. Los generadores de orden se inicializan una vez por candidato, nunca una vez por época. La inicialización de Linear conserva sus valores predeterminados; no se copia la inicialización NumPy del primer laboratorio.

## Medición y selección

El historial evalúa cada estado fijo mediante suma de pérdidas por caso y división por n, conservando el último minilote parcial. La comparación de épocas usa esos valores float32. Las tablas de candidatos recalculan BCE con la fórmula estable NumPy float64 sobre logits del modelo float32; las últimas cifras pueden diferir por redondeo. El criterio, las tolerancias y la época elegida se conservan explícitamente.

Se elige entre estados **registrados**, no entre todas las actualizaciones. No se usa parada anticipada para reducir cómputo: lineal y red12_8 reciben 600 pasos cada uno. La referencia constante no usa Adam. Los pesos de cada mejor estado se clonan; el estado final queda separado para comparar.

El informe incluye fuentes y huellas, preparación, versiones, configuración, estados legibles, métricas, predicciones y curvas de desarrollo. Guarda índices de la primera permutación y huellas SHA-256 de la secuencia de índices de cada época, serializada como JSON compacto. Las huellas permiten comparar recorridos, no reconstruir por sí solas las permutaciones restantes.

## Artefacto y límites

La exportación guarda solo el modelo elegido en un archivo para inferencia. Lo recarga en CPU y comprueba igualdad exacta de los logits de validación en este entorno. Incluye escala y orden de entradas. No guarda el estado de Adam ni los generadores necesarios para reanudar entrenamiento.

La comparación predictiva es didáctica, con una semilla de datos y modelos y una validación pequeña. No estima dispersión entre semillas, calibración externa ni utilidad sobre señales reales. Los datos de prueba y sus resultados son públicos: nuevos ajustes informados por ellos necesitan datos de cierre nuevos. Consultar prueba repetidamente para rediseñar el modelo la convierte en material de desarrollo.

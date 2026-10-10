# Reto — Un entrenamiento que otra persona pueda comprobar

[Unidad](README.md) · [Plantilla](plantillas/informe_pytorch.md) · [Orientación de solución](soluciones/README.md)

**Situación:** una compañera recibe tu modelo y necesita saber qué aprendió, con qué datos se eligió y si puede recuperar sus predicciones. Prepara una entrega reproducible en CPU.

## Trabajo

1. Ejecuta y conserva la equivalencia NumPy/PyTorch. Explica una forma matricial, un gradiente y un paso SGD con números.
2. Reproduce el entrenamiento de referencia y exporta sus resultados a una carpeta nueva.
3. Antes de comparar, escribe una hipótesis y cambia **una** condición: tamaño de lote, arquitectura o frecuencia de evaluación. Registra configuración real, semillas, parámetros, épocas y número de pasos.
4. Compara con la referencia constante y el experimento original usando entrenamiento y validación. Explica un resultado desfavorable si lo hay; conserva todas las variantes que ensayaste.
5. Guarda el estado elegido y recárgalo en una instancia nueva. Compara logits sobre un conjunto fijo de casos y documenta la preparación incluida. Explica qué falta para reanudar Adam.
6. Entrega una curva legible, una tabla de comparación y una ficha de límites. Señala que las señales son sintéticas y que la aplicación real todavía no se ha validado.

Usa el [generador y diccionario](datos/README.md). Si ya conoces los resultados públicos de prueba, no los uses como confirmación independiente de tu cambio. Puedes entregar solo un estudio de desarrollo bien identificado. Para practicar un cierre nuevo, fija por escrito nuevas semillas, particiones y protocolo **antes de mirar sus resultados**, conserva una única evaluación final y recuerda que sigue siendo un experimento sintético.

## Entregables

- Código o cambios legibles y comandos desde la raíz.
- Informe siguiendo la plantilla, con versiones y huellas de datos.
- Tabla de candidatos y estados, figura y explicación de errores.
- Evidencia de recarga y archivo generado localmente; no hace falta subir binarios al repositorio.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Comprensión y comprobación matemática | 20 | Formas, derivada y actualización consistentes |
| Bucle y presupuesto | 20 | Limpieza de gradientes, lotes, épocas y pasos documentados |
| Selección sin filtración | 25 | Preparación solo con entrenamiento; criterio fijado; cierre con alcance honesto |
| Guardado y recarga | 20 | Estado elegido independiente; preparación incluida; discrepancia medida |
| Reproducción, comunicación y límites | 15 | Comandos, versiones, figura y conclusiones proporcionadas |

Una pérdida baja no compensa filtración de información. Una diferencia de logits tras recargar debe explicarse o corregirse antes de afirmar que el artefacto conserva el resultado. No se exige una mejora de la métrica para obtener una buena evaluación del reto.

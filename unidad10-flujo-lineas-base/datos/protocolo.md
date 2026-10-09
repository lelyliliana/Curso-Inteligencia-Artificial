# Protocolo fijado — `lineas-base-v1`

[Volver a la unidad](../README.md) · [Diccionario de datos](README.md)

Este documento describe las decisiones de los dos programas publicados. Se eligen para enseñar un procedimiento, no como resultado de una búsqueda de la mejor puntuación. Los parámetros se estiman con entrenamiento; la selección se calcula con validación. Las reglas ejecutables están en [flujo.py](../ejemplos/flujo.py) y quedan registradas en cada informe.

| Decisión | Regresión | Clasificación |
|---|---|---|
| Objetivo | Consumo en las próximas 24 horas, kWh | Fallo en las próximas 24 horas, clase positiva 1 |
| Entrada | Consumo del día anterior | Señal previa baja/alta |
| Generalización examinada | Días posteriores de una instalación | Equipos separados de los usados al ajustar |
| Partición | 20/6/6 casos, cortes temporales fijos | 4/2/2 equipos completos, 32/16/16 avisos |
| Candidatos y desempate exacto | Mediana, media, persistencia, en ese orden | Mayoría global, mayoría por señal, en ese orden |
| Ajuste | Media y mediana de objetivos; mediana de entradas observadas | Mayoría global y por categoría, solo con etiquetas de entrenamiento |
| Faltantes | En persistencia, mediana de entrada de entrenamiento; cero se conserva | No se admiten en estos CSV |
| Categoría sin soporte | No aplica | Usar mayoría global y registrar soporte cero |
| Empate de clase | No aplica | Elegir clase 0 |
| Métrica principal | MAE menor | F1 positivo mayor |
| Diagnósticos | RMSE, error medio firmado y errores por caso | Exactitud, precisión, recobrado, VP/VN/FP/FN y errores por equipo |
| Redondeo | Solo al imprimir; no al seleccionar | Solo al imprimir; no al seleccionar |
| Prueba | Archivo sin leer hasta `--evaluar-prueba` | Archivo sin leer hasta `--evaluar-prueba` |
| Cierre | Evaluar solo el seleccionado, sin reajustar con validación | Evaluar solo el seleccionado, sin reajustar con validación |
| Azar y semilla | No se usan | No se usan |

Las comparaciones de cada tarea usan los mismos casos en el mismo orden. No se excluyen filas por el error que producen. Si faltan todas las entradas de entrenamiento de regresión, no se puede ajustar el respaldo del protocolo completo: el programa se detiene. Si validación de clasificación no tiene positivos, se detiene la selección por F1 y se requiere revisar el diseño.

En regresión se verifica que las entradas estuvieran disponibles al predecir y que las etiquetas del bloque anterior llegaran antes o al comenzar el siguiente. En clasificación solo se verifica separación por equipos e identificadores; el archivo no permite auditar cronología. Estos controles no prueban autenticidad ni representatividad.

## Registro y cierre

Antes de ejecutar el cierre, guarda el commit del curso, protocolo, huellas de entrenamiento y validación, parámetros, selección y razón de la métrica. La [plantilla](../plantillas/informe_experimento.md) permite registrar esas decisiones.

El cierre vuelve a calcular ajuste y selección con los archivos actuales; no consume un modelo bloqueado de una ejecución anterior. Para comparar fases, deben coincidir el código y las huellas de entrenamiento/validación, así como ajuste y selección. Si cambian, documenta un nuevo experimento antes de consultar prueba. El programa no puede comprobar que una persona nunca haya leído el archivo público.

No se interpreta el ejemplo como una evaluación independiente del propio proceso de construcción del curso: autoría, pruebas y resultados educativos conocen estos datos sintéticos. La separación enseña el flujo que debe trasladarse a una evaluación real con datos nuevos y un protocolo apropiado.

Si el resultado final resulta insuficiente, se informa. Se puede rediseñar después, pero la prueba ya consultada pasa a formar parte del desarrollo y no debe reutilizarse como evidencia nueva de independencia.

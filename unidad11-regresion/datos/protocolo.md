# Protocolo `regresion-v1`

[Unidad](../README.md) · [Diccionario](README.md)

Este protocolo fija la comparación didáctica antes del cierre. Los datos son públicos y sintéticos; la separación que implementa el programa no acredita una evaluación externa ciega.

## Pregunta y datos permitidos

Predecir el consumo total de un ciclo, en kWh, antes de comenzar, con sus horas planificadas. Esa disponibilidad es una declaración del escenario; no se puede auditar con estos CSV. No usar identificador ni consumo real como entradas. Mantener las particiones publicadas y los mismos casos para todos los candidatos.

## Ajuste y comparación

| Decisión | Laboratorio lineal | Laboratorio curvo |
|---|---|---|
| Casos entrenamiento / validación / prueba | 24 / 12 / 12 | 10 / 9 / 8 |
| Candidatos, en orden de desempate | mediana, media, recta | mediana, media, recta, cuadratica, grado9 |
| Ajuste de referencias | Mediana o media de objetivos de entrenamiento | Igual |
| Ajuste de modelos | Recta con intercepto por mínimos cuadrados | Recta y polinomios de grados 2 y 9 por mínimos cuadrados |
| Transformación de entrada | Recta en horas originales | Recta en horas; polinomios con centro y escala de entrenamiento |
| Selección | Menor MAE de validación | Igual |
| Diagnóstico | MAE de entrenamiento, RMSE, error medio firmado, R² y residuos | Igual, más comparación de complejidad |
| Reajuste con validación | No | No |
| Cierre | Solo el elegido, sobre prueba | Igual |

Recta y polinomios minimizan SSE en entrenamiento. La mediana usa el criterio absoluto entre constantes; la media, el cuadrático. La selección entre todos usa MAE de validación. Los empates **exactos** conservan el primer candidato en el orden indicado, sin redondear números ni introducir una tolerancia para decidir. No se cambia métrica por observar resultados más favorables.

La recta usa la fórmula de desviaciones respecto de las medias. Los polinomios usan `z = (x − centro) / escala`, con centro igual a la media y escala igual a la máxima distancia al centro, ambos calculados solo con entrenamiento. Se construye la matriz de potencias desde grado cero y se llama a `numpy.linalg.lstsq(..., rcond=None)`. Se exige grado entero positivo menor que el número de casos y matriz de rango completo. No basta tener muchas filas si faltan entradas distintas. Una entrada constante no permite identificar la pendiente ni estos polinomios.

Validación, prueba y consultas conservan la transformación de entrenamiento. No se recortan entradas transformadas ni predicciones negativas. Se marca `fuera_rango` usando los extremos de entrada observados en entrenamiento; es una advertencia de extrapolación, no una estimación de incertidumbre.

R² se registra como `null` cuando hay menos de dos casos o el objetivo evaluado es constante. No se reemplaza por un valor finito por conveniencia. MAE, RMSE y error medio se conservan cuando son calculables.

## Secuencia de cierre

1. Leer entrenamiento y validación; validar estructura, valores e identificadores disjuntos. No cargar prueba.
2. Ajustar cada candidato con entrenamiento y comparar sobre toda la validación.
3. Guardar exportación, código utilizado, protocolo, versiones, huellas de desarrollo, parámetros y selección.
4. Documentar residuos, límites y cualquier variante exploratoria como experimento aparte. Una variante no reemplaza silenciosamente el protocolo original.
5. Ejecutar `--evaluar-prueba` con los mismos archivos y código. El programa vuelve a ajustar y seleccionar; después abre prueba, comprueba identificadores y evalúa solo al elegido. No reajusta con validación.
6. Comparar el cierre con la exportación previa: mismas huellas de entrenamiento y validación, mismos modelos, selección y protocolo. Si no coinciden, investigar antes de tratarlo como cierre del mismo experimento.
7. Informar prueba sin escoger un ganador nuevo. Si sus resultados motivan cambios de diseño, declarar que esa prueba ya intervino en desarrollo y planear una evaluación nueva apropiada.

El programa funciona sin `prueba.csv` en la ejecución común. Las pruebas automáticas comprueban que cambiar validación no altera los parámetros aprendidos y que alterar objetivos de prueba no cambia ajuste, selección ni predicciones. Los archivos públicos y el generador permiten conocer resultados por otras vías: estos controles verifican código, no el historial de conocimiento de una persona.

## Registro y fallos

`informe.json` guarda criterios, versiones, huellas SHA-256, modelos y evaluaciones. Las tablas guardan candidato, identificador, entrada, objetivo real, predicción, residuo, error absoluto y marca de extrapolación. En desarrollo se exportan todos los candidatos; en prueba, solo el elegido. Las figuras representan exclusivamente entrenamiento y validación, incluso al cerrar.

Las carpetas de salida deben ser nuevas. La exportación no es transaccional: un fallo puede dejar archivos parciales. La huella identifica el contenido leído; no prueba su autenticidad ni registra automáticamente el commit. Los informes originales se conservan en [recursos](../recursos/README.md).

Los datos incompletos o inválidos se rechazan. Incorporar imputación, exclusiones, otros grados, regularización o recorte de predicciones sería un protocolo nuevo que requiere decisiones explícitas y evaluación correspondiente.

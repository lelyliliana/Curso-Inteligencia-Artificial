# Soluciones razonadas

[Unidad](../README.md) · [Ejercicios](../ejercicios.md)

## 1. Longitud y dirección

q·a=3, q·b=1, pero cos(q,a)=3/5=0,6 y cos(q,b)=1. El producto favorece a por magnitud; el coseno favorece b por dirección. No ordenar embeddings por producto bruto salvo que la elección de representación/métrica lo justifique, por ejemplo vectores normalizados.

## 2. Normalización

Norma=5; resultado [0,6; 0,8]. Escalar positivamente conserva dirección y coseno; multiplicar por −1 los invierte. La norma nula impide dividir: la práctica rechaza embeddings nulos y adopta puntuaciones cero para ausencia de señal TF-IDF, con aviso. Ese convenio no vuelve matemáticamente definido el coseno de cero.

## 3. IDF

Orden alfabético: agua, sol. df(agua)=2, df(sol)=1, N=2. IDF(agua)=1 e IDF(sol)=1+ln(3/2)≈1,405465. El primer documento tiene pesos [1; 2,810930], que deben normalizarse. «luna» no pertenece al vocabulario: [0;0]. Transformar esa consulta no añade una nueva columna ni reajusta IDF.

## 4. Métricas

Hay un relevante entre tres, de dos conocidos: P@3=1/3, Recall@3=1/2, Hit@3=1, RR@3=1/2. La segunda consulta aporta RR=0, de modo que MRR=(0,5+0)/2=0,25. [Cálculo ejecutable independiente](03_metricas_recuperacion.py). No promediar solo las consultas que tuvieron aciertos.

## 5. Ausencia de respuesta

Recall tiene denominador cero. P@3 puede definirse como cero y algunas convenciones asignan RR=0 a estas consultas; esta unidad separa todo el caso, escribe `null` en las cuatro métricas y lo informa como consulta sin respuesta con candidatos. Así el resumen de ocho respondibles tiene un denominador explícito y se acompaña del diagnóstico 2/2. No existe política que haya aceptado esas fuentes como respuestas.

## 6. Tema frente a evidencia

D18 dice el nombre de la red y dónde solicitar la contraseña, pero no su valor. No puede responder la consulta exacta. F05a sin respuesta tiene coseno máximo 0,6809, superior a F02a respondible (0,5773). Para un criterio «aceptar si coseno ≥ t», ningún t acepta ese positivo y rechaza simultáneamente ese negativo. Esto refuta la separación perfecta en los ejemplos; no prueba que todos los umbrales carezcan de utilidad para un objetivo con costos definidos.

## 7. Importar frente a exportar

F07a pide sacar lecturas; D16 describe añadirlas. D08 sí explica la exportación, pero queda segundo. De las ocho consultas respondibles, siete tienen RR=1 y una RR=0,5: MRR=7,5/8=0,9375. Hay diez documentos relevantes recuperados en 24 posiciones, P media=10/24≈0,4167, y se recuperan todos los relevantes por consulta. Hit@3=1 ocultaría el error de primera posición y tampoco indicaría si faltara un segundo documento relevante.

## 8. Empates

El orden es A,B porque el desempate usa ID ascendente. Si las puntuaciones fueran 0,12341 para A y 0,12342 para B, B debe ir primero. Redondearlas a tres decimales antes de ordenar crearía un empate inexistente. Redondear únicamente para mostrar es aceptable.

## 9. Identidad del espacio

La recarga comprueba huellas, configuración, IDs, dimensiones, normas y el estado TF-IDF reconstruido. La comparación con la captura reconstruye además el índice y detecta cambios de metadatos o vectores densos, incluso si una fila alterada mantiene norma 1. El buscador de texto nuevo comprueba inventario local contra el índice. Compartir dimensión no asegura compartir ejes: hay que usar el mismo espacio. Reindexar cambia representaciones guardadas; entrenar cambia pesos aprendidos. Las huellas sin firma no prueban autenticidad frente a manipulación coordinada de todos los artefactos.

## 10. Diseño posible, aún no ejecutado

Ejemplo: comparar TF-IDF actual y n-gramas de caracteres 3–5 en nuevas consultas de desarrollo con variaciones ortográficas y códigos. Fijar k=3, desempate y criterio MRR antes de medir; congelar la configuración y abrir nuevas familias de cierre después. Mantener preguntas sin respuesta y medir su tratamiento aparte. Si se introduce abstención, definir qué se acepta, costos de aceptar evidencia insuficiente y de rechazar evidencia útil; seleccionar el umbral solo en desarrollo y conservarlo. No reutilizar este cierre conocido como evidencia independiente de ese ajuste.

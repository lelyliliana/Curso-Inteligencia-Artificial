# Soluciones razonadas — Unidad 22

[Unidad y enunciados](../README.md) · [Cálculo escalar ejecutable](03_tfidf_a_mano.py)

## 1. Tareas sobre un mensaje

Ante «La clase de robótica será el viernes a las 10», clasificar podría asignar `horario`; extraer podría devolver los fragmentos de día y hora; generar podría redactar una explicación o una respuesta. El laboratorio solo asigna una de tres clases. Ni conoce el calendario real ni comprueba que la afirmación sea cierta.

## 2. Tokenización

El resultado es `[no, sé, si, la, sesión, 2, cambió]`. Conservamos negación, números y acentos; `si` y `sí` no se confunden. Se pierden mayúsculas, exclamaciones y sus posiciones. NFC hace equivalentes las formas compuesta y descompuesta de un acento; no suprime ese acento. El tokenizador tampoco deduce que «cambió» y «cambiar» pertenecen a una misma familia morfológica.

## 3. TF-IDF manual

Orden: acceso/aula/material. Conteos de D1: `[1, 2, 0]`; df del corpus: `[2, 1, 2]`. Con tres documentos, `idf(acceso)=ln(4/3)+1=1,287682`, `idf(aula)=ln(4/2)+1=1,693147` e `idf(material)=1,287682`.

El vector bruto de D1 es `[1,287682; 3,386294; 0]`. Dividir por su norma produce `[0,355432; 0,934702; 0]`. La suma de sus cuadrados es uno, salvo redondeo. Si D1 pasa a contener diez apariciones de aula, su conteo será diez, df seguirá siendo uno e IDF no cambiará. La normalización aumentará la proporción correspondiente a aula y reducirá la de acceso. [El programa escalar](03_tfidf_a_mano.py) permite revisar cada operación.

## 4. Desconocidos

Con vocabulario fijo, «aula galaxia» da `[0, 1, 0]`; «galaxia» da `[0, 0, 0]`. No se ajusta de nuevo IDF ni se crea una columna. Un `<UNK>` requeriría una política explícita y un modelo entrenado para utilizarla. Descartar términos desconocidos puede hacer equivalentes entradas distintas.

## 5. Orden y negación

d01 y d02 contienen una vez cada token: necesito/acceso/no/material. Sus conteos, IDF y vectores normalizados coinciden. Cualquier función determinista de ese mismo vector devuelve la misma salida: al menos una referencia diferente quedará mal.

Con bigramas, «necesito acceso» y «no material» difieren de «necesito material» y «no acceso». El modelo con bigramas distingue aquí los dos casos, que son cercanos a frases de entrenamiento. Sigue sin representar una negación de alcance arbitrario, y forma pares incluso cruzando signos de puntuación eliminados. Este diagnóstico no estima exactitud sobre negaciones reales.

## 6. Familias y unidad de evidencia

Una misma plantilla produce tres textos cambiando solo el tema. Partir después de producirlos facilita que una variante de evaluación casi repita una de entrenamiento. Asignar primero familias impide ese cruce.

Hay 18/9/9 familias y 54/27/27 textos; no hay 108 personas ni estilos independientes. Incluso familias distintas fueron redactadas dentro del mismo diseño sintético. Harían falta mensajes de procedencia apropiada, diversidad y particiones coherentes con el despliegue para evaluar personas nuevas. Un intervalo calculado tratando las variantes como observaciones independientes exageraría la cantidad de información.

## 7. Tres filtraciones

El ID incluye metadatos de clase: se excluye de las entradas del estimador. El vocabulario global incorpora información de evaluación aunque no use etiquetas: se aprende vocabulario e IDF solo con entrenamiento y se transforma el resto con ese estado. Las variantes repartidas por filas comparten origen: se asigna la familia antes de expandirla y se comprueba que no cruce particiones.

Los controles de hash y duplicados no detectan automáticamente paráfrasis con el mismo significado. La auditoría del corpus también requiere revisar su origen y proceso de creación.

## 8. Métricas y elección

La diagonal suma 24 de 27: exactitud `8/9=0,888889`. Para acceso, se predicen 12 casos y 9 son correctos: precisión `3/4=0,75`; su recobrado es uno. Para material, 6 de 9 reales se reconocen: recobrado `2/3`; su precisión es uno. Horario tiene precisión y recobrado uno.

F1 de acceso es `18/21=6/7`; F1 de material, `12/15=4/5`; F1 de horario, uno. Macro F1 es `(6/7+4/5+1)/3=0,885714`. La referencia constante no predice material ni horario: su precisión en esas clases está indefinida, no es evidencia de «cero aciertos entre predicciones» cuando no hubo predicciones.

La regla predefinida usa CE: unigramas obtiene 0,7544 frente a 0,8159 de bigramas y 1,0986 de prevalencia. Los diagnósticos de negación no sustituyen ese criterio después de ver sus resultados. Mejorar una frase no justifica anunciar mejora del conjunto.

## 9. Vector cero y aclaración

Tanto d03 como d04 producen `x=0`, así que `z=W×0+b=b`. La clase acceso sale de los sesgos, no del significado de «credenciales caducadas». El acierto de d03 es compatible con una representación que ignora todo su contenido.

d06 pide acceso y material. En esta tarea de etiqueta única su referencia es `null`; no se debe escoger arbitrariamente una clase para computar exactitud. Una extensión puede permitir varias etiquetas o preguntar qué petición atender primero. Una regla de revisión podría detectar texto vacío y estudiar cobertura, desconocidos y probabilidades en desarrollo; habría que medir su costo y sus omisiones en datos nuevos. Un máximo softmax alto por sí solo no demuestra que una petición esté dentro del catálogo.

## 10. Persistencia y cierre

Se requieren formato, versión exacta del tokenizador, clases ordenadas, vocabulario ordenado, IDF, coeficientes y sesgos. El archivo conserva además configuración de ajuste; el informe registra versiones y huellas. Inferencia reutiliza ese estado y no aprende de la consulta. Reanudar entrenamiento necesitaría definir datos y estado del proceso de optimización; este JSON no implementa esa función.

El cierre acierta 27 textos de nueve familias, con CE 0,6682. Comprueba el comportamiento sobre esas plantillas reservadas y la ejecución del protocolo. No demuestra comprensión general, calibración, funcionamiento con mensajes reales ni manejo de las peticiones excluidas. Los fallos de validación y diagnósticos siguen siendo evidencia relevante aunque este pequeño cierre sea perfecto.

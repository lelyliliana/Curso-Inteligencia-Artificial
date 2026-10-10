# Soluciones razonadas — Unidad 27

[Unidad](../README.md) · [Cálculo manual](03_calcular_evaluacion.py)

## 1. Fuentes y confirmación

Se eligen solo registros cuyo sensor sea A y estén confirmados. Queda `r1=12`; `r2=99` es borrador y `r3` pertenece a B. La nota no crea registros ni cambia el criterio. La salida es ok, valor 12 y evidencia `["r1"]`. No se aplica una regla temporal que la tarea nunca definió.

## 2. Forma correcta, evidencia incorrecta

`{"estado":"ok","valor":12,"evidencia":["r3"]}` cumple tipos y coherencia: tiene un valor entero y una lista no vacía. Falla contenido porque `r3` no apoya la consulta a A. La existencia de una cita tampoco basta; hay que comprobar pertinencia y cobertura de todos los registros seleccionados. En desarrollo, el básico llegó a producir un identificador inexistente, `falso`, solicitado por una nota.

## 3. Tipos y ausencia

Omitir `valor` incumple `required`; `"valor":null` puede cumplir forma, pero solo es coherente en ausente o conflicto. `"valor":"12"` es texto y no se convierte automáticamente. `true` no se acepta como entero aunque en Python `bool` sea una subclase de `int`. JSON Schema considera entero un número sin fracción, como `12.0`. El parser usa números de Python; este ejercicio trabaja con enteros pequeños y no ofrece validación decimal de precisión arbitraria.

## 4. Comparaciones controladas

El básico es breve y deja más decisiones implícitas. El explícito detalla fuentes, casos especiales, evidencia, restricciones y escribe el esquema dentro del prompt. El tercero utiliza el mismo texto y además pasa ese objeto en `format`. Solo la comparación explícito/con_esquema aísla ese parámetro. Con estas salidas ambos obtienen 9/12, y todos ya tenían forma válida; no hay evidencia aquí de una mejora adicional del esquema en exactitud.

## 5. Denominadores

En el cálculo ficticio hay tres contenidos correctos de seis, pero uno se trunca. Por tanto, aceptación `2/6`, aproximadamente 33,3 %. En ninguna de las tres familias ambas vistas se aceptan: `0/3` familias completas. No dividir entre las tres respuestas de contenido correcto ni presentar seis vistas como seis familias independientes. Los errores de transporte también permanecerían en el total de intentos.

## 6. Selección sin cierre

El máximo es nueve; hay empate entre explícito y con_esquema. La prioridad fijada antes del experimento elige explícito. Cierre no decide entre ellos: solo evalúa al elegido. La latencia tampoco puede introducirse como criterio después de ver sus valores. Si se quisiera seleccionarla, habría que fijar de antemano cómo se combina con exactitud y cómo se mide su variación.

## 7. Orden y coherencia

F04a tiene dos valores confirmados en conflicto; F04b solo invierte el orden. En la segunda vista, los tres candidatos eligen 11 y un único registro: cumple forma y coherencia de ok, pero falla contenido. En F05b, explícito y con_esquema devuelven conflicto con solo un ID; falla coherencia antes de contrastar la referencia. El esquema usado no codifica la relación entre estado y tamaño de evidencia. Estos cambios entre vistas muestran sensibilidad al orden; no demuestran por sí solos un mecanismo causal interno del modelo.

## 8. Nota con delimitadores

En F10 existe una lectura confirmada de S=31. La nota simula terminar un bloque y da una nueva instrucción para devolver ausente. El candidato congelado responde ausente en ambas vistas: 0/2 en esa familia. Se conserva como fallo de contenido. No prueba que todas las defensas fallen ni que otros prompts sean seguros; demuestra un fallo de esta configuración sobre esas entradas. La práctica no concede herramientas y ninguna instrucción generada se ejecuta.

## 9. Rúbrica humana propuesta

Para un resumen de un texto dado, una rúbrica podría separar fidelidad, cobertura y claridad, cada una con niveles 0–2 y ejemplos definidos antes de revisar. Una contradicción factual importante tendría una regla explícita, en lugar de compensarse sin explicación con buena redacción. Dos revisores podrían evaluar sin conocer el candidato, señalar fragmentos y adjudicar desacuerdos dejando registro.

Es una propuesta, no un estudio realizado. El cálculo manual muestra jueces ficticios con acuerdo bruto 2/4. Acordar no demuestra tener razón y no se debe presentar esa cifra como fiabilidad medida de un evaluador. Un juez basado en otro modelo también necesita una evaluación apropiada.

## 10. Decisión y siguiente tarea

Para estos registros estructurados usaría la referencia por reglas: 12/12 en desarrollo y 8/8 en cierre por construcción de la tarea, con pasos inspeccionables. El mejor prompt obtiene 9/12 y después 4/8, e incluye un fallo repetido ante una nota incrustada. No hay justificación para reemplazar aquí la función sencilla.

Un problema distinto sería extraer lecturas de notas narrativas variadas. Habría que definir anotaciones de referencia, unidades, negaciones, cambios temporales, evidencia textual, ausencias y conflictos; separar documentos o autores antes de crear variantes; comparar reglas/texto y modelo; y preparar otro cierre. El resultado de esta unidad no se extrapola a ese problema ni permite seguir ajustando contra su cierre público.

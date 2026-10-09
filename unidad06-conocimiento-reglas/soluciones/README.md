# Soluciones comentadas — Unidad 6

[Volver a la unidad](../README.md)

Compara cada solución con tu intento. Una salida correcta sin explicar supuestos y límites deja parte del ejercicio sin resolver.

## 1. Representación

18 kWh es una medición de energía cuyo intervalo y procedencia faltan por precisar. `lectura_alta` es una proposición que depende de comparar una lectura con un umbral elegido. r1 es una regla que exige además verificar el sensor. `proponer_visita` es una consecuencia de varias reglas, no una medición ni una acción ejecutada.

El laboratorio acepta hechos simbólicos ya declarados: no comprueba archivos de sensores, unidades, umbrales, calibración ni autenticidad. Esas verificaciones pertenecen a la construcción de la base y a etapas de datos.

## 2. Conjunción

No se aplica ninguna regla con solo `lectura_alta` y `edificio_ocupado`: falta `sensor_verificado` para r1, `revisar_consumo` para r2, los apoyos de r3 y el mantenimiento de r4. El cierre contiene únicamente los dos hechos iniciales.

No se demuestra que el sensor esté sin verificar. Puede haberse omitido información. La respuesta debe conservar esa diferencia.

## 3. Dirección

Si solo está `proponer_visita`, ese símbolo se considera hecho inicial y ninguna regla deriva información adicional. La regla r3 tiene esa conclusión, pero no se ejecuta en sentido inverso.

Una implicación puede cumplirse con conclusión verdadera y antecedente falso. Además, otras reglas podrían proponer una visita por motivos diferentes. Por ello inferir lectura alta a partir de visita sería afirmar indebidamente el antecedente.

## 4. Ciclo y orden

Sin hechos iniciales no se activa ninguna regla. El cierre es vacío. Con `a`, el orden `a→b`, `b→c`, `c→a` añade b y c durante el primer recorrido; no vuelve a añadir a.

Con el orden inverso `c→a`, `b→c`, `a→b`, el primer recorrido añade b; el segundo añade c; el tercero confirma que no cambia nada. El cierre sigue siendo `{a,b,c}`.

La condición «añadir solo si no estaba» evita que el ciclo mantenga cambios ficticios. Guardar una primera justificación apoyada en hechos ya presentes permite explicar c sin entrar en una recursión circular.

## 5. Conflicto

La propuesta de visita se apoya en r3, r2 y r1, y finalmente en lectura alta, verificación, ocupación y disponibilidad. La propuesta de posponer se apoya en r4 y mantenimiento programado.

Las dos se conservan y el par declarado produce una señal de revisión. Antes de resolverla preguntaría si se refieren a la misma visita y momento, si la disponibilidad sigue vigente y si el mantenimiento afecta el propósito de la visita.

No basta con elegir la última regla: el orden del archivo no expresa una prioridad. Una política explícita de precedencia requeriría ampliar el diseño y sus pruebas.

## 6. Formulación

Variables: datos, reglas y revisión. Cada dominio contiene 1, 2 y 3. Restricciones: `datos < reglas`, `datos != revision`, `reglas != revision`.

Al añadir `reglas < revision`, solo queda:

```text
datos=1; reglas=2; revision=3
```

La precedencia no estaba implícita en el nombre «revisión». En la base original también eran válidas `(1,3,2)` y `(2,3,1)`.

## 7. Los 21 intentos

Con orden fijo y sin filtrado de dominios:

- Se intentan tres valores de datos.
- Por cada uno se intentan tres valores de reglas: nueve intentos.
- Solo tres parejas superan `datos < reglas`: `(1,2)`, `(1,3)` y `(2,3)`.
- Para cada pareja se intentan tres valores de revisión: nueve intentos.

Total: `3 + 9 + 9 = 21`. Solo nueve de esos intentos completan una asignación; tres son soluciones. La enumeración completa comprueba las 27 combinaciones, incluidas las que el retroceso descarta antes de asignar revisión.

Con poda quedan tres intentos de datos, tres de reglas y tres de revisión: nueve. Las evaluaciones de compatibilidad realizadas para filtrar no están incluidas en ese contador. No podemos deducir una razón de tiempos a partir de esos números.

## 8. Filtrado

Con `datos=2`, reglas conserva únicamente 3; revisión conserva 1 y 3. Al asignar `reglas=3`, revisión pierde 3 y conserva 1.

Antes de asignar reglas, el filtrado solo revisó las relaciones con datos; no eliminó todavía de revisión el valor que ocuparía reglas. En general, dominios restantes no vacíos pueden ser incompatibles entre sí. El filtrado no certifica por sí solo una solución.

## 9. Imposibilidad

Si todos deben separarse, necesitamos tres franjas diferentes. Con dos, al menos dos talleres coincidirían. La precedencia estrecha aún más las alternativas y no resuelve esa carencia.

Dos modificaciones posibles:

1. Añadir una tercera franja: aumenta el tiempo disponible, manteniendo la separación.
2. Permitir que revisión coincida con otro taller: modifica el supuesto de recurso compartido o participación. Requiere justificar que ese solapamiento es aceptable.

Si se permite coincidir solo con datos, `(datos=1, reglas=2, revision=1)` sería viable. No se debe presentar ese resultado como solución del problema original.

## 10. Preferencias

Si la preferencia es situar revisión lo más tarde posible, entre las tres soluciones del caso original elegiríamos `(1,2,3)`. Para implementarla podemos enumerar soluciones y maximizar el valor de revisión.

Si la preferencia es revisión lo antes posible, elegiríamos `(2,3,1)`. Ambas preferencias se refieren al mismo conjunto de soluciones duras, pero producen elecciones diferentes. Hay que indicar cómo se resuelven empates y qué hacer si no existe solución.

El programa actual no puntúa soluciones. Su orden depende del orden de variables, valores y la estrategia de búsqueda, no de una preferencia del usuario.

## Orientación para el reto

Puedes conservar los casos base y producir estas cuatro variantes documentadas:

| Variante | Cambio | Resultado esperado |
|---|---|---|
| Evidencia incompleta | Retirar `sensor_verificado` | No se deriva visita; no se afirma una negación |
| Conflicto | Añadir `mantenimiento_programado` | Dos propuestas y un par incompatible activo |
| Agenda viable | Tres franjas y restricciones originales | Tres soluciones |
| Agenda imposible | Dos franjas y las mismas restricciones | Ninguna solución |

Para una extensión propia, añade una condición motivada por tu escenario y explica su efecto antes de ejecutar. Por ejemplo, exigir revisión después de reglas elimina dos soluciones del horario base. No basta con renombrar archivos: el informe debe mostrar una decisión de modelado, una predicción y su verificación.

El motor de reglas y el CSP se ejecutan por separado. Una integración real necesita definir qué propuesta se convierte en actividad, qué hacer con conflictos y cómo conservar el identificador y la procedencia del caso.

# Datos y separación por familias

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_casos.py)

Los registros, sensores, notas y referencias son propios y ficticios. No proceden de personas ni de sistemas reales. Su función es probar un procedimiento, no representar la distribución de problemas de una organización.

| Partición | Familias | Vistas | Estados esperados |
|---|---|---:|---|
| [Desarrollo](desarrollo.json) | F01–F06 | 12 | 8 ok, 2 ausente, 2 conflicto |
| [Cierre](cierre.json) | F07–F10 | 8 | 4 ok, 2 ausente, 2 conflicto |

Cada familia tiene una consulta y un conjunto de registros; la vista `a` conserva su orden y la vista `b` lo invierte. Ambas quedan en la misma partición. Así no se selecciona un prompt viendo una versión reordenada de un caso de cierre. Los identificadores de registros tampoco se comparten entre particiones. Aun así, ambas usan la misma tarea y estructura: no acreditan generalización a otro idioma, dominio o formato.

Cada caso contiene `id`, `familia`, `fenomeno`, `entrada` y `esperado`. Solo `entrada` se envía al modelo. Esta tiene `consulta`, `registros` y `nota`. Cada registro aporta `id`, `sensor`, `valor` entero y `confirmado` booleano. No hay semántica temporal: un borrador posterior no sustituye a un registro confirmado.

La referencia filtra sensor y confirmación. Si no quedan registros, devuelve `ausente`, null y evidencia vacía. Si hay un valor único, devuelve `ok`, ese valor y todos los identificadores pertinentes. Si existen varios valores, devuelve `conflicto`, null y todos esos identificadores. La evidencia se evalúa como conjunto; no se admiten elementos repetidos.

Las notas incluyen intentos ficticios de cambiar la tarea: inventar un valor, elegir borradores, promediar conflictos o cerrar delimitadores. Son texto de entrada. El cliente no ejecuta instrucciones ni herramientas que aparezcan en ellas o en la salida. Un acierto en estas pocas notas no certifica resistencia a otros ataques.

Los archivos pueden reconstruirse en otra carpeta:

```bash
python unidad27-prompts-evaluacion/datos/generar_casos.py --salida resultados/u27/datos
```

El generador construye las referencias mediante las reglas; la función independiente del laboratorio las contrasta y las pruebas incluyen ejemplos manuales. No se empleó un modelo como juez. El [esquema](esquema.json) especifica tipos y campos, pero no sabe si un valor figura en los registros ni si una cita corresponde al sensor consultado.

El cierre se evalúa después de congelar la elección con desarrollo. Al publicar el material todos los casos se vuelven accesibles: para una nueva búsqueda de prompts deben prepararse otros casos de cierre, no seguir optimizando contra estas respuestas conocidas.

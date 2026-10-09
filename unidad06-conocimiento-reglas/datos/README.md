# Datos de la Unidad 6

[Volver a la unidad](../README.md)

Todos los casos son sintéticos y fueron diseñados para este curso. No representan edificios, personas, calendarios ni políticas reales. Los archivos son JSON UTF-8; los símbolos del motor de reglas usan minúsculas sin tildes para facilitar su escritura en código.

## Base de reglas

[reglas_revision.json](reglas_revision.json) representa una instantánea de un único caso. Contiene cuatro hechos iniciales, cuatro reglas y un par incompatible.

| Campo | Contenido | Condiciones |
|---|---|---|
| `hechos` | Lista de símbolos iniciales | Cada símbolo empieza por a-z y continúa con a-z, 0-9 o `_` |
| `reglas` | Lista de objetos con `id`, `si`, `entonces` | Identificadores únicos; sin otras claves |
| `si` | Lista de condiciones | Al menos una; todas deben estar presentes |
| `entonces` | Símbolo que se añade | Una única conclusión positiva |
| `incompatibles` | Lista de pares de símbolos | Dos símbolos distintos por par |

Los hechos repetidos se colapsan en un conjunto. Una lista vacía de hechos, reglas o incompatibilidades es válida. Una condición vacía se rechaza: el formato almacena los hechos incondicionales en `hechos`. Un símbolo mencionado solo como condición puede representar evidencia que todavía no está disponible.

| Símbolo | Significado en este caso ficticio |
|---|---|
| `lectura_alta` | Se declaró que una lectura supera el umbral elegido para el caso |
| `sensor_verificado` | Se declaró una verificación del sensor para esa lectura |
| `edificio_ocupado` | Se declaró ocupación del edificio en la instantánea |
| `tecnico_disponible` | Se declaró disponibilidad de un técnico |
| `mantenimiento_programado` | Se declaró mantenimiento que aconseja posponer esta visita |
| `revisar_consumo` | Se propone examinar el consumo |
| `priorizar_revision` | Se propone priorizar la revisión según la regla didáctica |
| `proponer_visita` | Se deriva una propuesta de visita, sin ejecutarla |
| `posponer_visita` | Se deriva una propuesta de aplazar esa misma visita |

No hay mediciones, umbral numérico, tiempo de validez, procedencia por hecho ni verificación física implementados. El motor no reconoce negación por nombres como `no_disponible`. La incompatibilidad entre las dos propuestas es una declaración del modelo, no una propiedad deducida del español.

## Horarios

[horarios.json](horarios.json) ofrece tres variables con dominios `[1,2,3]`; [horarios_imposibles.json](horarios_imposibles.json) utiliza `[1,2]`. Comparten tres restricciones.

| Campo | Contenido | Condiciones |
|---|---|---|
| `dominios` | Objeto variable → lista de enteros | Entre una y ocho variables; nombres no vacíos |
| Cada dominio | Franjas admitidas para ese taller | Hasta ocho enteros únicos, excluyendo booleanos |
| `restricciones` | Lista de objetos `a`, `op`, `b` | Variables existentes y diferentes; sin otras claves |
| `op` | Relación entre los valores de `a` y `b` | Solo `!=` o `<` |

Los enteros representan **orden de franjas**, no horas, fechas ni duración. El validador admite otros enteros para experimentos; sus unidades deben documentarse. Un dominio vacío es válido y hace imposible una asignación completa. Una lista vacía de restricciones permite todas las combinaciones de los dominios.

El orden de las variables y de los valores determina los desempates; no determina cuál solución es mejor. El programa de laboratorio limita la comparación a 100000 combinaciones completas. Los núcleos son educativos y conservan trazas en memoria.

Para modificar datos, crea una copia y usa `--datos ruta/a/la/copia.json`. No se guardan cambios en los originales durante las ejecuciones.

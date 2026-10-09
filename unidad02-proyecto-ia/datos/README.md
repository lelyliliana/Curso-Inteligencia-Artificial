# Datos del caso trabajado

[Volver a la unidad](../README.md)

Los dos archivos fueron creados para este curso. No provienen de una instalación, de estudiantes ni de equipos reales.

## Ficha de proyecto

[proyecto_ejemplo.json](proyecto_ejemplo.json) describe un proyecto ficticio de apoyo a revisiones de consumo. Las cifras, los horarios y los objetivos son decisiones didácticas.

## Lote de casos

[casos_revision.csv](casos_revision.csv) representa un único lote de doce casos.

| Campo | Significado | Restricción |
|---|---|---|
| `caso_id` | Identificador ficticio | Texto no vacío y único |
| `consumo_parcial_kwh` | Lectura que el escenario declara disponible a las 10:00 | Número finito y no negativo |
| `revision_referencia` | Etiqueta ficticia para comparar decisiones | `0` o `1` |

`1` significa que el caso merece revisión según la etiqueta del ejercicio. No demuestra una avería ni una conclusión profesional. Las etiquetas fueron asignadas para mostrar que distintos umbrales pueden tener la misma exactitud y consecuencias diferentes.

Los programas reciben las etiquetas porque se ejecutan en modo de evaluación. En una aplicación que recibe un caso nuevo, la predicción se produciría con la lectura disponible, sin conocer su etiqueta de referencia.

El archivo no contiene marcas temporales que prueben la recepción de la lectura. Su disponibilidad es un supuesto declarado del escenario; en un proyecto real habría que verificar tiempos de medición y recepción.

La capacidad de cuatro casos se aplica al lote completo. El CSV no permite evaluar capacidad por día ni hacer una partición temporal real. Tampoco justifica una distribución representativa de registros.

Cada caso omitido relevante cuesta cinco unidades didácticas y cada revisión innecesaria, una. No son pesos colombianos ni una valoración económica o social validada.

El lote es exploratorio: se utiliza para comparar y elegir una regla candidata. No es una prueba final independiente. Para validar posteriormente se necesitaría información adicional obtenida bajo un protocolo acordado.

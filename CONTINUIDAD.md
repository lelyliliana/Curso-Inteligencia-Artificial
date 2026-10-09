# Continuidad y revisión del curso

[Volver al índice](README.md)

Este documento conserva el punto de trabajo y los criterios para continuar la elaboración. Describe avances del material, no el progreso de aprendizaje de una persona.

## Punto de partida comprobado — 9 de octubre de 2026

El repositorio remoto tenía como último commit `14120bb4cefb0d3219537821fe950466c88afd25`: «Desarrollar Unidad 5: búsqueda, heurísticas y verificación de rutas». La rama consultada fue `main`, única rama encontrada al revisar.

La ruta original establece 36 unidades, numeradas del 0 al 35. Al retomar estaban desarrolladas y publicadas las unidades 0 a 5; las unidades 6 a 35 eran temas previstos en el índice. No se encontró un programa ejecutable común para comprobar todo el material.

La revisión inicial ejecutó correctamente 19 programas de ejemplos y soluciones y las siete pruebas existentes de búsqueda con Python 3.12.3 en Linux. Se inspeccionó la estructura del curso y el desarrollo de la última unidad para conservar sus convenciones. Esto no constituye una auditoría conceptual exhaustiva de cada párrafo de las unidades anteriores.

## Estado del material

| Material | Estado | Evidencia |
|---|---|---|
| Unidades 0–5 | Recuperadas del repositorio y comprobadas en ejecución | 19 programas y siete pruebas existentes |
| Unidad 6 | Desarrollada y comprobada | Dos laboratorios, tres archivos de datos, ejercicios con soluciones, reto, plantilla y 15 pruebas |
| Unidad 7 | Desarrollada y comprobada | Dos laboratorios, CSV y JSON documentados, diez ejercicios resueltos, reto, ficha y 19 pruebas |
| Unidad 8 | Desarrollada y comprobada | Dos laboratorios, corrección sintética explícita, trazabilidad, diez ejercicios resueltos, reto, informe y 20 pruebas |
| Verificación común | Disponible para las unidades 0–8 | [verificar_curso.py](herramientas/verificar_curso.py) |
| Unidades 9–35 | Pendientes de desarrollo | Alcance conservado en el índice |

La Unidad 6 se publicó en el commit `b7a2a9b` y la Unidad 7 en `1c047c2`. Esta entrega incorpora la Unidad 8 y amplía la verificación conjunta. El próximo contenido por desarrollar es la **Unidad 9: exploración y visualización**. Quedan 27 unidades de contenido tras esta entrega; no se considera terminado el curso por tener los títulos planificados.

## Enfoque que se conserva

- Español claro, conceptos explicados desde cero y Python básico como prerrequisito práctico.
- Intuición, formulación y ejemplo manual antes del programa.
- Ruta básica en CPU; paquetes, GPU, modelos descargables y costos externos explícitos cuando aparezcan.
- Aplicaciones en educación, energía, sensores, ambiente y documentos.
- Datos pequeños documentados; distinción entre demostración sintética y evidencia real.
- Ejemplos reproducibles, interpretación, experimentos, ejercicios, soluciones y reto evaluable.

## Ruta de elaboración por entregas

Cada entrega desarrolla una unidad y revisa su conexión con las anteriores. Los grupos siguientes sirven como hitos de integración, sin alterar la numeración original.

| Unidades | Trabajo pendiente | Evidencia al cerrar el hito |
|---|---|---|
| 7–9 | Unidades 7 y 8 terminadas; pendientes exploración y visualización | Dataset documentado, transformaciones reproducibles e informe exploratorio |
| 10–13 | Flujo de aprendizaje, líneas base, regresión, clasificación, árboles y ensambles | Comparaciones reproducibles con separación de datos y análisis de errores |
| 14–18 | Agrupamiento, anomalías, características, validación, métricas e interpretabilidad | Selección justificada sin filtración, umbrales y limitaciones documentadas |
| 19–24 | Redes, PyTorch, visión, lenguaje, tiempo, recomendación y refuerzo | Prácticas pequeñas y ejecutables; recursos y especialidades diferenciados |
| 25–31 | Generación, inferencia, prompts, embeddings, RAG, herramientas, adaptación y multimodalidad | Evaluaciones con casos verificables, citas y límites de permisos y recursos |
| 32–33 | Aplicación, operación, seguridad y observabilidad | Aplicación mínima con validación de entradas, registro útil y manejo de errores |
| 34–35 | Talleres y proyecto integrador | Proyecto con línea base, evaluación independiente, demostración y documentación |

Antes de desarrollar cada unidad, verificar documentación primaria de las bibliotecas y servicios que vaya a utilizar. Fijar y registrar las versiones que realmente se prueben; no asumir que una API o descarga futura conserva el mismo funcionamiento.

## Siguiente entrega concreta — Unidad 9

Pregunta guía: **¿qué preguntas podemos explorar con estos datos y cómo comunicar los patrones sin exagerar lo que muestran?**

Alcance propuesto, todavía no implementado:

1. Formular preguntas exploratorias y distinguir descripción de confirmación de hipótesis.
2. Relacionar tipos de variables con tablas de frecuencias, distribuciones y gráficos.
3. Conectar resúmenes numéricos de la Unidad 4 con forma, escala, dispersión y valores extremos.
4. Comparar grupos, relaciones y evolución temporal indicando tamaños y faltantes.
5. Explicar ejes, unidades, denominadores, agregaciones y decisiones visuales.
6. Retomar los datos preparados de la Unidad 8 sin ocultar cuarentena ni generalizar desde muestras mínimas.
7. Dos laboratorios reproducibles, figuras revisadas, ejercicios y reto de informe exploratorio.

Mantener los originales de la Unidad 7 y la política documentada de la Unidad 8. Para estudiar distribuciones, incorporar si hace falta otro conjunto sintético suficientemente amplio y explicar su generación; no fabricar una población real a partir de los pocos registros actuales. Declarar y comprobar cualquier dependencia gráfica antes de añadirla al flujo del curso.

## Criterios para considerar lista una unidad

| Dimensión | Comprobación |
|---|---|
| Coherencia | Objetivos observables; prerrequisitos suficientes; términos consistentes con unidades previas |
| Explicación | Ejemplo manual, código explicado, salida real e interpretación |
| Corrección | Fórmulas, supuestos y límites revisados; no atribuir al código capacidades ausentes |
| Datos | Procedencia, esquema, unidades, restricciones y alcance de los resultados |
| Reproducción | Comandos desde la raíz, versión probada y recursos necesarios |
| Práctica | Ejercicios con soluciones razonadas, experimentos y reto con rúbrica |
| Verificación | Ejemplos ejecutados; casos límite pertinentes; referencia independiente para algoritmos cuando sea útil |
| Fuentes | Referencias primarias comprobadas y enlaces locales válidos |
| Integración | Índice, navegación y seguimiento actualizados sin anunciar material inexistente |

## Comprobación del material disponible

Desde la raíz del curso:

```bash
python herramientas/verificar_curso.py
```

Comprueba sintaxis de Python, destinos de enlaces Markdown locales, 38 ejecuciones de programas y variantes y las 61 pruebas de las unidades 5, 6, 7 y 8. Usa la biblioteca estándar, un directorio temporal para el registro de la Unidad 0 y no instala paquetes. El verificador cubre explícitamente las unidades 0–8; al añadir otra unidad hay que incorporar su alcance y sus comprobaciones.

La comprobación de enlaces no valida URLs externas ni fragmentos `#ancla`. Ejecutar programas con éxito no demuestra que toda explicación sea correcta ni que se obtenga utilidad en una población real.

## Cierre del curso completo

Se considerará completo cuando las 36 unidades tengan material desarrollado y revisado, se hayan ejecutado sus prácticas bajo los entornos declarados y el proyecto final integre formulación, datos, línea base, evaluación, aplicación y análisis de limitaciones. Una última revisión transversal debe comprobar progresión, dependencias, navegación, criterios de evaluación y reproducibilidad desde un entorno limpio.

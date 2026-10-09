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
| Unidad 9 | Desarrollada y comprobada | Dos laboratorios, datos regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 21 pruebas |
| Verificación común | Disponible para las unidades 0–9 | [verificar_curso.py](herramientas/verificar_curso.py) |
| Unidades 10–35 | Pendientes de desarrollo | Alcance conservado en el índice |

La Unidad 6 se publicó en el commit `b7a2a9b`, la Unidad 7 en `1c047c2` y la Unidad 8 en `59ed8df`. Esta entrega incorpora la Unidad 9 y amplía la verificación conjunta. El próximo contenido por desarrollar es la **Unidad 10: flujo de aprendizaje y líneas base**. Quedan 26 unidades de contenido tras esta entrega; no se considera terminado el curso por tener los títulos planificados.

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
| 7–9 | Desarrollo terminado; reto integrador disponible | Datos documentados, preparación trazable y exploración con figuras e informe reproducible |
| 10–13 | Flujo de aprendizaje, líneas base, regresión, clasificación, árboles y ensambles | Comparaciones reproducibles con separación de datos y análisis de errores |
| 14–18 | Agrupamiento, anomalías, características, validación, métricas e interpretabilidad | Selección justificada sin filtración, umbrales y limitaciones documentadas |
| 19–24 | Redes, PyTorch, visión, lenguaje, tiempo, recomendación y refuerzo | Prácticas pequeñas y ejecutables; recursos y especialidades diferenciados |
| 25–31 | Generación, inferencia, prompts, embeddings, RAG, herramientas, adaptación y multimodalidad | Evaluaciones con casos verificables, citas y límites de permisos y recursos |
| 32–33 | Aplicación, operación, seguridad y observabilidad | Aplicación mínima con validación de entradas, registro útil y manejo de errores |
| 34–35 | Talleres y proyecto integrador | Proyecto con línea base, evaluación independiente, demostración y documentación |

Antes de desarrollar cada unidad, verificar documentación primaria de las bibliotecas y servicios que vaya a utilizar. Fijar y registrar las versiones que realmente se prueben; no asumir que una API o descarga futura conserva el mismo funcionamiento.

## Siguiente entrega concreta — Unidad 10

Pregunta guía: **¿cómo organizar un experimento predictivo y saber si un modelo mejora una referencia sencilla?**

Alcance propuesto, todavía no implementado:

1. Definir unidad de predicción, objetivo, horizonte e información disponible al decidir.
2. Distinguir entrenamiento, validación y prueba; justificar partición aleatoria, por tiempo o por grupo según el problema.
3. Separar ajuste de transformaciones y aplicación, retomando las unidades 7 y 8.
4. Construir líneas base sencillas para regresión y clasificación, aprendidas únicamente del conjunto permitido.
5. Introducir métricas mínimas apropiadas, comparación sobre los mismos casos y análisis de errores; reservar el desarrollo amplio para unidades posteriores.
6. Documentar protocolo, supuestos, semillas si hay azar y registro de experimentos sin usar prueba para seleccionar.
7. Dos laboratorios reproducibles, ejercicios resueltos y reto con informe de comparación y límites.

La Unidad 9 conserva las fuentes de 7–8 y añade 48 casos sintéticos separados para visualizar patrones. No reutilizarlos automáticamente como una población apta para modelado: definir datos y generación acordes con cada experimento. Mantener explícita la diferencia entre demostración del procedimiento y rendimiento útil en datos reales. Declarar y comprobar toda nueva dependencia antes de incorporarla.

La primera dependencia gráfica se incorporó en la Unidad 9: Matplotlib 3.10.8 y NumPy 2.2.6, probadas con Python 3.12.3 en un entorno virtual limpio. Los resúmenes de texto siguen usando biblioteca estándar; la exportación de gráficos y las 21 pruebas nuevas requieren esos paquetes. El [registro del entorno](unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt) conserva las versiones transitivas y los informes JSON anotan fuente, parámetros y versiones principales. Las tres figuras se revisaron visualmente.

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
python -m pip install -r unidad09-exploracion-visualizacion/requirements.txt
python herramientas/verificar_curso.py
```

Comprueba sintaxis de Python, destinos de enlaces Markdown locales, 45 ejecuciones de programas y variantes y las 82 pruebas de las unidades 5, 6, 7, 8 y 9. Las ejecuciones incluyen la exportación de ambas prácticas gráficas a carpetas temporales. El verificador no instala paquetes ni accede a servicios externos; requiere haber instalado las dependencias de la Unidad 9. Usa directorios temporales para resultados y caché gráfica. Cubre explícitamente las unidades 0–9; al añadir otra unidad hay que incorporar su alcance y sus comprobaciones.

La comprobación de enlaces no valida URLs externas ni fragmentos `#ancla`. Ejecutar programas con éxito no demuestra que toda explicación sea correcta ni que se obtenga utilidad en una población real.

## Cierre del curso completo

Se considerará completo cuando las 36 unidades tengan material desarrollado y revisado, se hayan ejecutado sus prácticas bajo los entornos declarados y el proyecto final integre formulación, datos, línea base, evaluación, aplicación y análisis de limitaciones. Una última revisión transversal debe comprobar progresión, dependencias, navegación, criterios de evaluación y reproducibilidad desde un entorno limpio.

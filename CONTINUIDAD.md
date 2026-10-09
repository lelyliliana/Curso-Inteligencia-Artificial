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
| Unidad 10 | Desarrollada y comprobada | Dos laboratorios, seis CSV regenerables, protocolo de selección y cierre, diez ejercicios resueltos, reto, informe y 24 pruebas |
| Unidad 11 | Desarrollada y comprobada | Dos laboratorios, sensibilidad a un extremo, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 26 pruebas |
| Verificación común | Disponible para las unidades 0–11 | [verificar_curso.py](herramientas/verificar_curso.py) |
| Unidades 12–35 | Pendientes de desarrollo | Alcance conservado en el índice |

La Unidad 6 se publicó en el commit `b7a2a9b`, la Unidad 7 en `1c047c2`, la Unidad 8 en `59ed8df`, la Unidad 9 en `56df425` y la Unidad 10 en `fe3b260`. Esta entrega incorpora la Unidad 11 y amplía la verificación conjunta. El próximo contenido por desarrollar es la **Unidad 12: clasificación**. Quedan 24 unidades de contenido tras esta entrega; no se considera terminado el curso por tener los títulos planificados.

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
| 10–13 | Unidades 10 y 11 terminadas; pendientes clasificación, árboles y ensambles | Comparaciones reproducibles con separación de datos y análisis de errores |
| 14–18 | Agrupamiento, anomalías, características, validación, métricas e interpretabilidad | Selección justificada sin filtración, umbrales y limitaciones documentadas |
| 19–24 | Redes, PyTorch, visión, lenguaje, tiempo, recomendación y refuerzo | Prácticas pequeñas y ejecutables; recursos y especialidades diferenciados |
| 25–31 | Generación, inferencia, prompts, embeddings, RAG, herramientas, adaptación y multimodalidad | Evaluaciones con casos verificables, citas y límites de permisos y recursos |
| 32–33 | Aplicación, operación, seguridad y observabilidad | Aplicación mínima con validación de entradas, registro útil y manejo de errores |
| 34–35 | Talleres y proyecto integrador | Proyecto con línea base, evaluación independiente, demostración y documentación |

Antes de desarrollar cada unidad, verificar documentación primaria de las bibliotecas y servicios que vaya a utilizar. Fijar y registrar las versiones que realmente se prueben; no asumir que una API o descarga futura conserva el mismo funcionamiento.

## Siguiente entrega concreta — Unidad 12

Pregunta guía: **¿cómo aprender a distinguir clases y evaluar las consecuencias de convertir una puntuación en una decisión?**

Alcance propuesto, todavía no implementado:

1. Formular clasificación binaria: unidad de predicción, entradas disponibles, etiqueta, clase positiva y consecuencias de error.
2. Introducir regresión logística, función sigmoide y predicción de clase con un ejemplo manual; distinguirla de regresión numérica pese a su nombre.
3. Explicar una función de pérdida de clasificación y un ajuste reproducible con transformaciones aprendidas solo en entrenamiento.
4. Comparar el modelo con mayoría y otras referencias pertinentes, usando validación para elegir y prueba solo al cierre.
5. Interpretar matriz de confusión, precisión, recobrado y F1; relacionar umbral y errores sin agotar las unidades 16 y 17.
6. Distinguir puntuación, probabilidad estimada, calibración y certeza; revisar desbalance y limitaciones de una evaluación pequeña.
7. Dos laboratorios reproducibles, figuras si ayudan, ejercicios resueltos y reto con comparación, errores y límites documentados.

La Unidad 11 incorpora datos sintéticos nuevos de ciclos de operación: un caso lineal y otro curvo. Ajusta referencias, recta y polinomios con entrenamiento; selecciona por MAE de validación y conserva un cierre separado. El ejemplo de grado 9 muestra sobreajuste frente a la cuadrática; una perturbación en memoria ilustra sensibilidad sin modificar los CSV. Se documentan unidades, coeficientes en la variable transformada, R² indefinido o negativo, redondeo, residuos y extrapolación. Las tres figuras PNG/SVG se revisaron visualmente. Las 26 pruebas incluyen referencias manuales y numéricas, invariancia del ajuste y selección frente a información no permitida, regeneración y correspondencia entre gráficos e informes.

La Unidad 10 añade dos conjuntos sintéticos independientes: 32 pronósticos diarios con cortes temporales y 64 avisos de ocho equipos separados por grupo. La ejecución común lee solo entrenamiento y validación; `--evaluar-prueba` abre prueba después de seleccionar y no reajusta. Se comprueban casos idénticos entre candidatos, disponibilidad de etiquetas en los cortes y separación de equipos. Las pruebas de invariancia alteran objetivos de prueba y verifican que no cambien ajuste, selección ni predicciones. No hay dependencias nuevas ni azar.

Las pruebas de las unidades 10 y 11 son públicas y sus resultados didácticos son conocidos. No reutilizarlas automáticamente para seleccionar modelos nuevos en la Unidad 12 y después presentarlas como evaluación independiente. Definir datos y particiones apropiados para cada nuevo experimento, o explicar claramente qué parte es desarrollo y qué evidencia nueva se aporta. Mantener la diferencia entre demostrar el procedimiento y demostrar rendimiento útil en datos reales.

La primera dependencia gráfica se incorporó en la Unidad 9: Matplotlib 3.10.8 y NumPy 2.2.6, probadas con Python 3.12.3 en un entorno virtual limpio. Sus resúmenes de texto usan biblioteca estándar; su exportación de gráficos y sus 21 pruebas requieren esos paquetes. La Unidad 11 reutiliza esas versiones: el ajuste de polinomios requiere NumPy y las figuras, Matplotlib. El [registro del entorno](unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt) conserva las versiones transitivas; los informes JSON anotan fuentes, parámetros y versiones principales.

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
python -m pip install -r unidad11-regresion/requirements.txt
python herramientas/verificar_curso.py
```

Comprueba sintaxis de Python, destinos de enlaces Markdown locales, 63 ejecuciones de programas y variantes y las 132 pruebas de las unidades 5 a 11. Las ejecuciones incluyen exportaciones gráficas y de experimentos predictivos, tanto en validación como en cierre, a carpetas temporales. El verificador no instala paquetes ni accede a servicios externos; requiere haber instalado las dependencias compartidas de las unidades 9 y 11. Usa directorios temporales para resultados y caché gráfica. Cubre explícitamente las unidades 0–11; al añadir otra unidad hay que incorporar su alcance y sus comprobaciones.

La comprobación de enlaces no valida URLs externas ni fragmentos `#ancla`. Ejecutar programas con éxito no demuestra que toda explicación sea correcta ni que se obtenga utilidad en una población real.

## Cierre del curso completo

Se considerará completo cuando las 36 unidades tengan material desarrollado y revisado, se hayan ejecutado sus prácticas bajo los entornos declarados y el proyecto final integre formulación, datos, línea base, evaluación, aplicación y análisis de limitaciones. Una última revisión transversal debe comprobar progresión, dependencias, navegación, criterios de evaluación y reproducibilidad desde un entorno limpio.

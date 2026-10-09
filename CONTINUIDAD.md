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
| Unidad 12 | Desarrollada y comprobada | Dos laboratorios, paso manual de gradiente, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 28 pruebas |
| Unidad 13 | Desarrollada y comprobada | Dos laboratorios, Gini manual y sensibilidad, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 30 pruebas |
| Unidad 14 | Desarrollada y comprobada | Dos laboratorios, paso manual de K-means, siete CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 30 pruebas |
| Unidad 15 | Desarrollada y comprobada | Dos laboratorios, proyección manual, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 30 pruebas |
| Unidad 16 | Desarrollada y comprobada | Dos laboratorios, CV manual, contraejemplo de escala, cortes temporales, cuatro CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 30 pruebas |
| Unidad 17 | Desarrollada y comprobada | Dos laboratorios, métricas manuales, costos y cupos, cuatro CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, informe y 30 pruebas |
| Unidad 18 | Desarrollada y comprobada | Dos laboratorios, reconstrucción manual, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, ficha de modelo y 30 pruebas |
| Unidad 19 | Desarrollada y comprobada | Dos laboratorios, retropropagación manual, seis CSV regenerables, tres figuras PNG/SVG, diez ejercicios resueltos, reto, ficha de límites y 32 pruebas |
| Verificación común | Disponible para las unidades 0–19 | [verificar_curso.py](herramientas/verificar_curso.py) |
| Unidades 20–35 | Pendientes de desarrollo | Alcance conservado en el índice |

La Unidad 6 se publicó en el commit `b7a2a9b`, la Unidad 7 en `1c047c2`, la Unidad 8 en `59ed8df`, la Unidad 9 en `56df425`, la Unidad 10 en `fe3b260`, la Unidad 11 en `e04adc8`, la Unidad 12 en `61a73f5`, la Unidad 13 en `81df395`, la Unidad 14 en `1f2b6f8`, la Unidad 15 en `b5ef367`, la Unidad 16 en `121e345`, la Unidad 17 en `5ea63cf` y la Unidad 18 en `ad665cc`. Esta entrega incorpora la Unidad 19 y amplía la verificación conjunta. El próximo contenido por desarrollar es la **Unidad 20: aprendizaje profundo con PyTorch**. Quedan 16 unidades de contenido tras esta entrega; no se considera terminado el curso por tener los títulos planificados.

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
| 10–13 | Desarrollo terminado: líneas base, regresión, clasificación y ensambles | Comparaciones reproducibles con separación de datos y análisis de errores |
| 14–18 | Desarrollo terminado: agrupamiento, representaciones, validación, decisiones e interpretabilidad | Selección justificada sin filtración, umbrales y limitaciones documentadas |
| 19–24 | Unidad 19 terminada; pendientes PyTorch, visión, lenguaje, tiempo, recomendación y refuerzo | Prácticas pequeñas y ejecutables; recursos y especialidades diferenciados |
| 25–31 | Generación, inferencia, prompts, embeddings, RAG, herramientas, adaptación y multimodalidad | Evaluaciones con casos verificables, citas y límites de permisos y recursos |
| 32–33 | Aplicación, operación, seguridad y observabilidad | Aplicación mínima con validación de entradas, registro útil y manejo de errores |
| 34–35 | Talleres y proyecto integrador | Proyecto con línea base, evaluación independiente, demostración y documentación |

Antes de desarrollar cada unidad, verificar documentación primaria de las bibliotecas y servicios que vaya a utilizar. Fijar y registrar las versiones que realmente se prueben; no asumir que una API o descarga futura conserva el mismo funcionamiento.

## Siguiente entrega concreta — Unidad 20

Pregunta guía: **¿cómo trasladar una red verificable a PyTorch y organizar un entrenamiento reproducible con tensores, autograd y evaluación separada?**

Alcance propuesto, todavía no implementado:

1. Introducir tensores, formas, tipos, dispositivos y conversión desde NumPy; ruta básica en CPU y costo de instalación explícito, sin imponer GPU.
2. Contrastar propagación y gradientes de una red pequeña con la referencia NumPy, evitando confundir esa equivalencia con evidencia predictiva independiente.
3. Explicar autograd, acumulación de gradientes, zero_grad, backward y step, así como nn.Module, pérdidas desde logits y modos train/eval/no_grad.
4. Organizar datos y minilotes, distinguir época de actualización y registrar semillas, orden de muestreo, configuración y límites de reproducibilidad.
5. Guardar y restaurar el estado elegido con un formato apropiado, validar la igualdad de predicciones y mantener la selección fuera de prueba; no cargar archivos de modelo de procedencia desconocida.
6. Entregar dos laboratorios pequeños, datos nuevos cuando se evalúe generalización, referencias matemáticas, figuras revisadas, ejercicios, soluciones, reto y documentación de recursos. Verificar una versión CPU de PyTorch compatible con el entorno antes de fijarla.

La Unidad 19 implementa una red tanh con NumPy y gradientes explícitos, BCE estable desde logits y L2 sin sesgos. Compara referencias y red8 en XOR, y una red32 con o sin penalización en un círculo con etiquetas ruidosas. Selecciona arquitectura y época por BCE de validación; conserva copias del estado inicial, elegido y final. Red32 sin L2 elige época 500 y luego sobreajusta; red32_l2 gana en ese laboratorio. Prueba evalúa solo el estado elegido sin reajuste. Las tres figuras se revisaron visualmente; las 32 pruebas incluyen forward escalar, paso manual, diferencias finitas de todos los parámetros, estabilidad, separación, regeneración y artefactos. Se reutilizó el entorno anterior; PyTorch todavía no es una dependencia.

La Unidad 18 fija dos modelos antes de leer validación: regresión lineal estandarizada con un duplicado exacto horas/minutos, y un árbol pequeño sobre una lectura. Reconstruye contribuciones y rutas, convierte unidades y contrasta permutación individual/conjunta. La auditoría conserva grupos sin positivos y sin filas; el árbol detecta 7 de 19 positivos desplazados en validación y 3 de 14 en cierre. No se reemplaza después de observar el fallo. Incluye ficha completada, plantilla y análisis de impacto con decisión de uso solo didáctico. Las tres figuras se revisaron visualmente; las 30 pruebas contrastan referencias matemáticas, fronteras float32 del árbol, separación, datos y artefactos. Se reutilizó el entorno anterior sin dependencias nuevas. Prueba se abre tras los diagnósticos y no orienta el ajuste.

La Unidad 17 compara políticas sobre puntuaciones sintéticas fijas, sin entrenar ni reajustar un predictor. El primer laboratorio selecciona umbral por costo FP=1/FN=6; el segundo añade un cupo de seis revisiones por lote, con desempate por puntuación e ID sin etiquetas. Un empate de costo se resuelve por menos alertas, conservando el criterio aunque cambie F1. Se explican denominadores, valores indefinidos, ROC AUC, AP por bloques, Brier, fiabilidad y sensibilidad condicional a prevalencia. El diagnóstico s² conserva orden y modifica error probabilístico; no se ajusta un calibrador. Prueba se abre tras elegir y solo evalúa esa política. Se documentan omisiones importantes incluso con precisión=1 en una muestra. Las tres figuras se revisaron visualmente y las 30 pruebas contrastan referencias matemáticas, biblioteca, cupos, separación y artefactos. Se reutilizó el entorno anterior sin dependencias nuevas.

La Unidad 16 introduce una rejilla de vecinos próximos y una referencia mediana, con cuatro pliegues y preparación ajustada dentro de cada uno. Compara casos independientes y generalización a equipos nuevos. Un diagnóstico fijo de KNN obtiene MAE 0,583 por filas y 27,990 por grupos: se mantiene GroupKFold según la pregunta y gana la mediana en ese escenario. Después de elegir, se reajusta una instancia nueva con todo desarrollo y solo entonces se abre prueba. Se diferencian OOF, estado reajustado, media por pliegue y dispersión sin interpretación de intervalo. La validación anidada se explica como extensión; los cortes temporales son un ejemplo de índices, no un tercer experimento predictivo. Las tres figuras se revisaron visualmente y las 30 pruebas incluyen distancias independientes, comparación con GridSearchCV, separación, regeneración y exportaciones. Se reutiliza el entorno anterior sin dependencias nuevas.

La Unidad 15 compara una referencia mediana, entradas originales y una interacción con significado físico, y contrasta regresión completa con PCA de uno o dos componentes. Los datos nuevos muestran que conservar el 99,9343 % de la varianza puede perder la señal predictiva; PCA de dos componentes conserva aquí la dimensión y produce predicciones equivalentes a la regresión completa. Se aprenden escala y ejes solo con entrenamiento; se selecciona por MAE de validación y se abre prueba después, sin reajuste. Se excluye expresamente una lectura posterior que revela el objetivo. Las tres figuras se revisaron visualmente; las 30 pruebas incluyen referencias independientes para mínimos cuadrados y proyección, separación de información, regeneración y exportaciones. Se reutilizó el entorno de la entrega anterior con las versiones registradas en la Unidad 13, sin dependencias nuevas.

La Unidad 14 incorpora agrupamiento de perfiles con K-means y detección de anomalías con distancia al centro e Isolation Forest. Ajusta escala y modelos con entrenamiento; en anomalías fija umbrales con una partición adicional de calibración. Selecciona k por silueta de validación y detector por F1 de referencias sintéticas, reconociendo que esta última selección aprovecha etiquetas. Compara inicializaciones con ARI sin confundir estabilidad con utilidad. El detector seleccionado omite 13 de 16 positivos de validación: se conserva y analiza esa limitación. Prueba se abre después de elegir, sin reajuste. Las tres figuras se revisaron visualmente; las 30 pruebas cubren referencias matemáticas independientes, separación de información, regeneración, exportaciones y correspondencia de gráficos. Se reutilizaron las versiones de la Unidad 13 en un entorno virtual limpio.

La Unidad 13 incorpora dos escenarios sintéticos nuevos: una franja con una señal y una región con dos. Introduce scikit-learn, Gini ponderado, recorridos, controles de crecimiento e inestabilidad; compara mayoría, árboles, bagging y bosque con selección por F1 de validación. Los ensambles promedian probabilidades y la convención de empate de la biblioteca se distingue de la Unidad 12. Prueba se abre solo después de elegir, sin reajuste con validación. Se documentan semillas, remuestreo, rangos, huellas y límites de los resúmenes exportados. Las tres figuras PNG/SVG se revisaron visualmente. Sus 30 pruebas incluyen una referencia exhaustiva de cortes, promedio independiente de probabilidades, invariancia ante información no permitida, reproducción de datos y correspondencia entre figuras y resultados.

La Unidad 12 incorpora dos escenarios sintéticos nuevos de clasificación binaria. Implementa una regresión logística de una entrada con gradiente completo, escalado de entrenamiento y penalización explícita. Compara mayoría y siempre positivo; en el escenario desbalanceado selecciona entre tres umbrales que conservan probabilidades y parámetros. La selección usa F1 de validación; prueba se abre después y evalúa solo al elegido. Se explican pérdida, clase positiva, métricas indefinidas, calibración y carácter determinista de los datos. Las tres figuras PNG/SVG se revisaron visualmente. Sus 28 pruebas incluyen cálculo manual, diferencias finitas, referencia independiente por Newton, invariancia frente a etiquetas de prueba y correspondencia de gráficos y resultados.

La Unidad 11 incorpora datos sintéticos nuevos de ciclos de operación: un caso lineal y otro curvo. Ajusta referencias, recta y polinomios con entrenamiento; selecciona por MAE de validación y conserva un cierre separado. El ejemplo de grado 9 muestra sobreajuste frente a la cuadrática; una perturbación en memoria ilustra sensibilidad sin modificar los CSV. Se documentan unidades, coeficientes en la variable transformada, R² indefinido o negativo, redondeo, residuos y extrapolación. Las tres figuras PNG/SVG se revisaron visualmente. Las 26 pruebas incluyen referencias manuales y numéricas, invariancia del ajuste y selección frente a información no permitida, regeneración y correspondencia entre gráficos e informes.

La Unidad 10 añade dos conjuntos sintéticos independientes: 32 pronósticos diarios con cortes temporales y 64 avisos de ocho equipos separados por grupo. La ejecución común lee solo entrenamiento y validación; `--evaluar-prueba` abre prueba después de seleccionar y no reajusta. Se comprueban casos idénticos entre candidatos, disponibilidad de etiquetas en los cortes y separación de equipos. Las pruebas de invariancia alteran objetivos de prueba y verifican que no cambien ajuste, selección ni predicciones. No hay dependencias nuevas ni azar.

Las pruebas de las unidades 10 a 19 son públicas y sus resultados didácticos son conocidos. No reutilizarlas automáticamente para seleccionar modelos nuevos en unidades posteriores y después presentarlas como evaluación independiente. Definir datos y particiones apropiados para cada nuevo experimento, o explicar claramente qué parte es desarrollo y qué evidencia nueva se aporta. Mantener la diferencia entre demostrar el procedimiento y demostrar rendimiento útil en datos reales.

La primera dependencia gráfica se incorporó en la Unidad 9: Matplotlib 3.10.8 y NumPy 2.2.6, probadas con Python 3.12.3 en un entorno virtual limpio. Sus resúmenes de texto usan biblioteca estándar; su exportación de gráficos y sus 21 pruebas requieren esos paquetes. Las unidades 11 y 12 reutilizan esas versiones: polinomios y logística requieren NumPy; las figuras, Matplotlib. La Unidad 13 incorpora scikit-learn 1.9.1, probado con Python 3.12.3 y las mismas versiones numéricas y gráficas en otro entorno virtual limpio. Su [registro completo del entorno](unidad13-arboles-ensambles/recursos/entorno-verificado.txt) añade las dependencias transitivas, incluida SciPy 1.18.1. Se conserva también el [registro del entorno anterior](unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt). Los informes JSON anotan fuentes, parámetros y versiones principales.

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
python -m pip install -r unidad19-redes-neuronales/requirements.txt
python herramientas/verificar_curso.py
```

Comprueba sintaxis de Python, destinos de enlaces Markdown locales, 139 ejecuciones de programas y variantes y las 372 pruebas de las unidades 5 a 19. Las ejecuciones incluyen exportaciones gráficas y de experimentos predictivos, tanto en validación como en cierre, a carpetas temporales. El verificador no instala paquetes ni accede a servicios externos; requiere haber instalado las dependencias compartidas y scikit-learn indicados en los requisitos de la Unidad 19. Usa directorios temporales para resultados y caché gráfica. Cubre explícitamente las unidades 0–19; al añadir otra unidad hay que incorporar su alcance y sus comprobaciones.

La comprobación de enlaces no valida URLs externas ni fragmentos `#ancla`. Ejecutar programas con éxito no demuestra que toda explicación sea correcta ni que se obtenga utilidad en una población real.

## Cierre del curso completo

Se considerará completo cuando las 36 unidades tengan material desarrollado y revisado, se hayan ejecutado sus prácticas bajo los entornos declarados y el proyecto final integre formulación, datos, línea base, evaluación, aplicación y análisis de limitaciones. Una última revisión transversal debe comprobar progresión, dependencias, navegación, criterios de evaluación y reproducibilidad desde un entorno limpio.

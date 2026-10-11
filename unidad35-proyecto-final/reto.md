# Reto final — Un proyecto que otra persona pueda revisar

[Unidad](README.md) · [Plantilla de proyecto](plantillas/proyecto.md) · [Traspaso](plantillas/traspaso.md)

Elige un problema acotado de energía, ambiente, educación/documentos u otro ámbito que puedas estudiar con datos y permisos suficientes. Puedes extender un taller o construir otro caso. No necesitas integrar todas las técnicas ni añadir un LLM si una regla o un modelo pequeño resuelve el contrato.

Reproducir el ejemplo sirve para practicar el proceso. Tu entrega propia debe formular una decisión, declarar qué datos/resultados ya conocías y justificar sus cambios. Si no tienes datos reales autorizados, usa datos ficticios identificados y limita las conclusiones a esa demostración.

## Hito 1 — Propuesta antes de ejecutar

Entrega usuario, decisión, entradas disponibles, salida, uso fuera de alcance, referencia, métrica/costo y criterio de aceptación. Documenta fuente y permisos, unidad de análisis, tamaño y particiones. Acuerda un alcance que permita llegar a una demostración y un informe, no solo a entrenar un modelo.

## Hito 2 — Desarrollo con evidencia

Prepara datos, ajusta la referencia y los candidatos fijados, selecciona con validación y guarda un estado. Conserva comandos y versiones. Comprueba recarga, entradas problemáticas y una referencia matemática o implementación independiente donde corresponda. Si cambias el protocolo durante desarrollo, registra qué viste y por qué cambió.

## Hito 3 — Cierre, demostración y decisión

Evalúa la versión congelada con los datos reservados y las comparaciones previstas. Conserva resultados desfavorables. Demuestra un caso útil, un rechazo y una limitación de calidad; explica cómo operar localmente y volver a una versión anterior. Una CLI es suficiente si corresponde al usuario y al alcance; una interfaz web no sustituye la evaluación.

## Carpeta de entrega

| Componente | Contenido mínimo |
|---|---|
| Guía de ejecución | Entorno, instalación, comandos y recursos necesarios |
| Propuesta/protocolo | Decisión, contrato, candidatos, partición y criterio previo |
| Datos | Procedencia, esquema, permisos, preparación y límites; sin secretos |
| Estado y evidencia | Modelo/reglas, preparación, versiones, métricas por caso y cierres |
| Demostración | Entrada/salida, errores y caso conocido de inicio |
| Informe y ficha | Resultados, errores, población, decisión y usos fuera del alcance |
| Operación/traspaso | Responsable, monitoreo propuesto, retención y reversión |
| Defensa | Guion breve con evidencia que pueda abrirse durante la exposición |

## Rúbrica — 100 puntos

| Dimensión | Puntos | Qué permite evaluar |
|---|---:|---|
| Problema y contrato | 15 | Usuario, acción y límites concretos |
| Datos y separación | 20 | Procedencia, disponibilidad, grupos/tiempos y ausencia de filtración |
| Referencia y desarrollo | 15 | Complejidad justificada, comparación y selección trazable |
| Cierre y errores | 20 | Estado congelado, denominadores, incertidumbre y fallos conservados |
| Demostración y operación | 15 | Uso reproducible, entradas inválidas y recuperación |
| Documentación y defensa | 15 | Evidencia localizable y argumentos proporcionados |

La entrega se considera suficiente con al menos 70 puntos y cuatro condiciones esenciales: procedencia/permisos declarados, separación honesta, ausencia de secretos/datos personales no autorizados y resultados conservados sin ocultar fallos. Si falla una, corrige esa parte antes de cerrar la evaluación. Superar a la referencia no es obligatorio: sí lo es tomar una decisión coherente con el resultado.

## Revisión de otra persona

Pide a una persona revisora que ejecute la guía, reproduzca una salida, localice el caso de un fallo y explique qué conclusión permiten los datos. Si debe adivinar dependencias, versiones o particiones, la entrega necesita ajustes. Registra su observación y tu respuesta sin sustituir el primer cierre por uno más favorable.

Al terminar, conserva una versión estable del proyecto y un registro de mejoras futuras. Completar esta unidad exige el trabajo del estudiante y la revisión de su evidencia; que el material del curso esté publicado no certifica automáticamente ese aprendizaje.

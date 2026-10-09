# Ficha de modelo — Árbol de alertas sintéticas

[Unidad](../README.md) · [Informe de desarrollo](alertas/informe.json) · [Protocolo](../datos/protocolo.md)

**Identificador:** u18-v1-modelos-fijos / alertas. **Fecha de revisión:** 9 de octubre de 2026. **Estado:** material didáctico. Esta ficha está completada con resultados del laboratorio; no atribuye una autorización operativa a ninguna persona u organización.

## Propósito y responsables

El propósito es aprender a reconstruir predicciones y auditar errores según condiciones sintéticas de medición. El usuario previsto es quien estudia el curso. La salida es una clase 0/1: 1 indica «requiere revisión» según una etiqueta ficticia del generador. El programa imprime y exporta resultados; no envía alertas ni controla dispositivos.

Quien entrega la práctica responde por reproducir y explicar sus resultados. No se ha designado una persona responsable de operación porque no existe un servicio real en esta práctica. Antes de cualquier adaptación operativa habría que identificar por nombre a quien valida datos, atiende errores, autoriza versiones y puede suspender decisiones automáticas, junto con su capacidad y plazos de atención.

Usos excluidos de esta evidencia: mantenimiento real automático, decisiones sobre personas y afirmaciones de seguridad, equidad o eficacia de sensores reales. No se ha evaluado disponibilidad, respuesta humana ni integración con un sistema físico.

## Datos y modelo

Seis CSV sintéticos nuevos entre dos laboratorios; este árbol usa tres: 236 filas de entrenamiento, 144 de validación y 114 de prueba. El [generador y sus semillas](../datos/README.md) documentan la procedencia. No hay datos personales ni grupos demográficos. Las huellas de los archivos de desarrollo están en el informe enlazado; ejecutar el cierre añade la de prueba.

Entrada: lectura adimensional en [0,1]. Grupo e ID están excluidos. Etiqueta: señal latente >=0,55; no se entrega la latente al modelo. Hay ruido y un desplazamiento de −0,30 para una condición de medición. Las etiquetas son perfectas respecto de la regla sintética, pero eso no reproduce errores de etiquetado de un proceso real.

Modelo: DecisionTreeClassifier de scikit-learn 1.9.1, max_depth=2, min_samples_leaf=8, random_state=18; los demás parámetros se conservan en el informe. Se ajusta solo con entrenamiento. No se ha elegido entre versiones ni reajustado con validación. Referencia: clase mayoritaria de entrenamiento.

## Evidencia de rendimiento y explicación

En validación, exactitud=127/144≈0,882, precisión=53/57≈0,930 y recobrado=53/66≈0,803. La referencia mayoritaria tiene exactitud=78/144≈0,542 y recobrado=0. La mejora global no decide automáticamente el uso.

| Condición | Evidencia de validación | Consecuencia para interpretar el resultado |
|---|---|---|
| estandar | 100 filas, 47 positivos, 1 FN, 4 FP | Hay errores en ambas direcciones |
| desplazado | 40 filas, 19 positivos, 12 FN, 0 FP | Omite la mayoría de positivos del grupo |
| escaso | 4 filas negativas | No se puede medir recobrado ni extrapolar a positivos |
| nuevo | 0 filas | Ausencia de evidencia de rendimiento |

La ruta local elegida por ID llega a hoja 2, con 1 positivo entre 92 casos de entrenamiento, y predice 0. La reconstrucción se contrasta con la biblioteca. Esa fidelidad no demuestra causalidad ni calibración por grupo; tampoco convierte la ruta de un caso en explicación representativa de todos los errores.

El cierre publicado conserva el árbol: VP=37, VN=65, FP=0, FN=12. En condición desplazada detecta 3 de 14 positivos; en estándar, 34 de 35. No se probaron otras versiones para mejorar esas cifras. El resultado confirma una limitación en este generador; no cuantifica el riesgo de un dispositivo real.

## Análisis de impacto proporcionado

Las siguientes consecuencias son **hipótesis de una futura adaptación**, no daños observados en el ejercicio:

| Situación | Proceso o persona potencialmente afectada | Respuesta propuesta | Límite de la respuesta |
|---|---|---|---|
| Falso negativo | Equipo sin revisión; persona responsable de mantenimiento | Verificar también una muestra de no alertados y obtener etiquetas posteriores | Revisar solo alertas no detecta omisiones; falta dimensionar personal y plazos |
| Falso positivo | Equipo de revisión y actividades que se interrumpen | Confirmar la señal antes de una intervención y registrar el motivo del descarte | La confirmación consume recursos y puede fallar |
| Medición desplazada | Equipos bajo otra condición de lectura | Investigar calibración y obtener datos por condición antes de otra versión | Corregir la lectura cambia la distribución y exige evaluación nueva |
| Condición sin ejemplos | Equipos o procesos no representados | Aplicar el procedimiento manual de referencia; declarar falta de cobertura | El laboratorio no ha implementado ese procedimiento operativo |
| Explicación tomada como garantía | Persona que decide confiar en la salida | Mostrar error conocido, soporte y alcance de la explicación | Un texto claro no garantiza comprensión ni corrige el predictor |

## Decisión y gestión de errores

**Decisión actual: apto para docencia; evidencia insuficiente para operación real.** No se autoriza una actuación sobre equipos. Una futura propuesta deberá definir utilidad frente a un procedimiento manual, tolerancias de error según consecuencias, cobertura de condiciones y capacidad efectiva de revisión antes de evaluar su aceptación.

En esta práctica, al detectar un error se conserva la fila sintética, versión, huella, ruta, predicción y etiqueta; se registra la limitación en el informe del estudiante y se comprueba la ejecución. Si se cambia código o datos, se documenta otra versión. No se borra la evidencia del error original.

Para una futura aplicación haría falta asignar recepción de incidentes, capacidad de detener automatización, revisión de casos no alertados, mecanismo de corrección y evidencia de resolución. Un cambio del sensor, una condición nueva o una caída del rendimiento con etiquetas verificadas serían motivos de revisión. No fijamos un número universal de alarma sin conocer consecuencias, volumen y variabilidad de las tasas.

Si se recopilaran datos reales, habría que definir permisos, acceso, minimización y conservación; esta ficha sintética no otorga esos permisos. Toda versión corregida necesitaría datos de desarrollo y un cierre independiente de los resultados ya examinados.

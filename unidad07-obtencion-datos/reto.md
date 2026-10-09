# Reto — Ficha y diagnóstico de una fuente

[Volver a la unidad](README.md) · [Ficha de datos](plantillas/ficha_datos.md)

## Escenario

Un equipo quiere utilizar lecturas y eventos para apoyar revisiones de consumo. Antes de construir una solución, te pide describir qué hay en sus archivos y qué preguntas siguen abiertas.

Usa las fuentes sintéticas de esta unidad como dos casos independientes. No necesitas descargar datos reales ni introducir información personal. Mantén los archivos originales y trabaja con copias para los experimentos.

## Trabajo

1. Formula una decisión que los datos podrían apoyar y relaciónala con la ficha de proyecto de la Unidad 2.
2. Documenta por separado procedencia, propósito, unidad de observación, clave, campos, unidades, versión y limitaciones del CSV y del JSON.
3. Calcula a mano faltantes e inválidos del consumo, duplicados y cobertura del CSV. Contrasta las cuentas con el programa.
4. Ejecuta una variante de datos y otra del plan esperado. Predice su efecto antes de ejecutar; no confundas cambiar el denominador con arreglar el archivo.
5. Audita el JSON para dos cortes temporales y uno equivalente en otra zona. Explica observación, disponibilidad y rol de los objetivos.
6. Provoca un error estructural en una copia y describe la respuesta del programa. Distingue ese error de una incidencia que puede incluirse en un perfil.
7. Exporta informes nuevos con huellas, conserva los comandos y registra la versión del código.
8. Propón un orden de revisión para las incidencias, indicando qué evidencia falta antes de corregirlas. La preparación efectiva corresponde a la siguiente unidad.

## Entregables

- Ficha de datos con los dos casos claramente separados.
- Copias de los archivos modificados y descripción de cada cambio.
- Informes JSON, comandos y parámetros de cada ejecución.
- Cuentas manuales y contraste con resultados reales.
- Conclusión que diferencie hallazgos, hipótesis y decisiones pendientes.
- Resultado de las pruebas y explicación de cualquier ampliación realizada.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Propósito y procedencia | 20 | Pregunta, fuente, granularidad y límites bien definidos |
| Esquema y diagnóstico | 20 | Tipos, unidades, faltantes, inválidos y duplicados correctamente interpretados |
| Cobertura y disponibilidad | 25 | Denominador explícito; cortes y zonas correctos; objetivos separados |
| Reproducción y experimentos | 20 | Copias, huellas, comandos, predicciones y resultados contrastados |
| Conclusión y decisión siguiente | 15 | Causas no inventadas; prioridades de revisión justificadas |

Objetivo de autoevaluación: al menos 80 puntos. Revisa la entrega aunque alcance esa cifra si confunde presencia de clave con calidad de medición, usa información futura como entrada o presenta los datos sintéticos como evidencia real.

Extensión opcional: documentar otra fuente pequeña con permiso de uso comprobado. Los programas incluidos aceptan esquemas concretos; un dataset diferente puede requerir adaptar lector, validación y pruebas.

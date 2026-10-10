# Reto — Un asistente con permisos demostrables

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe.md)

Amplía la práctica para responder sobre dos proyectos ficticios, cada uno con sus propios sensores y permisos. Conserva una ruta sin modelo. El objetivo es demostrar que el sistema responde con evidencia y respeta la identidad confiable del proyecto.

## Entregables

1. Datos propios nuevos, con al menos ocho familias y dos variantes por familia; separar desarrollo y cierre por sensor/proyecto antes de evaluar.
2. Política explícita de acceso, con casos permitidos, restringidos, ausentes y notas hostiles. Identidad fijada por la aplicación, fuera de argumentos generados por el modelo.
3. Herramientas, contratos de entrada/salida y pruebas de que los errores no entregan datos de otro proyecto. Mantener la demostración sin efectos externos.
4. Referencia por reglas y, si dispones de modelo, un bucle con pasos, tiempo y presupuesto de tokens documentados. Si usas respuestas artificiales, identificarlas como tales.
5. Registro de propuesta, validación, autorización, ejecución, respuesta y motivo de parada. Una afirmación de éxito sin evidencia debe rechazarse.
6. Informe de desarrollo y cierre congelado, con denominadores que conserven fallos, tareas/familias completas y costos. La recarga debe producir la misma evaluación sin red.

Usa [la plantilla](plantillas/informe.md). Si no puedes realizar inferencia local, entrega la política, el flujo fijo y pruebas artificiales: no inventes una captura ni una comparación medida del agente.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Datos y particiones | 15 | Familias nuevas, sin cruce de recursos entre desarrollo/cierre |
| Permisos y aislamiento lógico | 25 | Identidad confiable, casos cruzados rechazados, resultados sin fuga |
| Contratos y errores | 15 | Entradas hostiles, tipos, desconocidas y resultados inválidos comprobados |
| Bucle y presupuestos | 15 | Paradas reproducibles; origen real o artificial declarado |
| Evaluación y referencia | 20 | Evidencia de tarea, comparación honesta y cierre sin reajuste |
| Documentación y recarga | 10 | Instrucciones ejecutables, límites y trazas reconstruibles |

Una solución que entregue datos de un proyecto no autorizado debe corregirse antes de considerar completado el reto, aunque su media sea correcta.

**Extensión opcional:** conecta el agente al servidor MCP y comprueba correlación, permisos y equivalencia con el ejecutor directo. Otra extensión es implementar y probar una revisión MCP más reciente; documenta las diferencias reales, sin limitarte a renombrar la versión. Ninguna extensión requiere conectar correo, publicar en repositorios o modificar equipos físicos.

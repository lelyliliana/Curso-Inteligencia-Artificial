# Reto — Operar con evidencia

[Unidad](README.md) · [Plantilla](plantillas/informe.md)

Extiende una aplicación local del curso con un plan de operación comprobable. Conserva una versión anterior y el estado del modelo. Elige un problema concreto: saturación, falla de una dependencia, datos incompatibles o recuperación tras un error. No pruebes contra servicios ajenos.

Antes de ejecutar, define población de métricas, límites, estados, escenarios, resultado esperado y criterio de recuperación. Distingue fallos que inyectas de fallos que observas espontáneamente. Mantén separadas las métricas de operación y las de calidad predictiva.

## Entregables

1. Mapa de activos, entradas y riesgos con controles concretos y límites conocidos.
2. Admisión acotada y política de tiempos; si no puedes cancelar el trabajo, dilo y comprueba qué ocurre al abandonar el cliente.
3. Sondas con significados definidos, identificadores propios y registro sin entradas sensibles.
4. Contadores e indicador con numerador, denominador, ventana y tratamiento de cero solicitudes.
5. Escenarios reproducibles con al menos un fallo, un rechazo y una recuperación. Conservar respuestas y eventos correlacionados.
6. Procedimiento de cambio y reversión, informe de hallazgos y pruebas de una propiedad esencial de admisión o recuperación.

La ruta básica debe funcionar localmente sin cuentas ni claves. Un tablero vistoso no sustituye la definición de una métrica ni la evidencia de recuperación. No se exige desplegar en Internet.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Alcance y riesgos | 15 | Activos, controles y limitaciones concretas |
| Admisión y tiempos | 20 | Recursos acotados y comportamiento ante exceso/abandono |
| Observabilidad | 20 | Correlación, privacidad, denominadores y ventana |
| Fallos y recuperación | 25 | Escenarios ejecutados, resultados y pruebas |
| Cambio y reversión | 10 | Versiones conservadas y pasos verificables |
| Interpretación y reproducción | 10 | Comandos, artefactos y conclusiones proporcionadas |

No presentes tiempos inventados como una medición real ni tasas de un experimento de fallos como disponibilidad de producción. Una limitación que se identifica y reproduce es un resultado útil.

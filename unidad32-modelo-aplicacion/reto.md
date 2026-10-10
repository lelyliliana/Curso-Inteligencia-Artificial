# Reto — Una aplicación local revisable

[Unidad](README.md) · [Plantilla](plantillas/informe.md)

Construye una aplicación pequeña sobre un modelo del curso. Puedes extender Consulta de luces o reutilizar otro modelo verificado. Elige una necesidad concreta, entradas con límites y una salida que se pueda interpretar sin leer el código.

Antes de implementar, define el caso de uso, los campos, los errores, el estado del modelo y los criterios de aceptación. Conserva una referencia directa al servicio para contrastarla con la ruta HTTP. Reutiliza la preparación del modelo o documenta y evalúa cualquier cambio.

## Entregables

1. Arquitectura y responsabilidades: interfaz, contrato, preparación, inferencia y transporte.
2. Aplicación ejecutable localmente con instrucciones, carga una sola vez y error de inicio si falta el modelo.
3. Interfaz con estados de espera, éxito, rechazo y fallo de conexión; no conservar resultados obsoletos.
4. API con versiones, límites, identidad del modelo y errores sin predicciones inventadas.
5. Pruebas de contratos y HTTP real; al menos un recorrido documentado en navegador con entrada válida, rechazo y recuperación.
6. Informe que separe integración y calidad predictiva, detalle procedencia y declare capacidades no demostradas.

No hace falta desplegar en Internet ni comprar servicios. Si propones un cambio de preparación o pesos, crea una evaluación propia sin reutilizar como cierre los casos que guiaron el cambio. Una ampliación de interfaz puede conservar el modelo anterior.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Caso de uso y alcance | 15 | Necesidad concreta, criterios y limitaciones visibles |
| Contrato y preparación | 20 | Esquema, límites y equivalencia con la preparación probada |
| Carga e inferencia | 15 | Inicio comprobado, estado fijo y consultas sin entrenamiento |
| Interfaz | 15 | Flujo comprensible, espera, errores y recuperación |
| Pruebas | 25 | Contratos, HTTP y recorrido real con evidencia |
| Reproducción y documentación | 10 | Entorno, comandos, artefactos y separación de métricas |

Una respuesta incorrecta del modelo debe seguir siendo visible como tal en el informe. No reemplaces fallos por etiquetas esperadas para que la demostración aparente funcionar.

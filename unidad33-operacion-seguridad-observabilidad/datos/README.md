# Datos y protocolo de operación

[Unidad](../README.md)

Se reutiliza la escena `escena-024.png` de validación de la Unidad 31: izquierda apagada y derecha encendida. El catálogo original sigue disponible a través del servidor de la Unidad 32. No se modifica ningún PNG, peso, partición o código de preparación anterior.

El estado es el [modelo de fusión de U31](../../unidad31-adaptacion-multimodalidad/recursos/multimodal/modelo.json), SHA-256 `f439b8cabb3b24f2fc3208ac4de57439a5226888bba25e84180a9c4aeb8228bf`. No hay un conjunto nuevo de entrenamiento o cierre predictivo. La procedencia y los límites de las escenas están en [los datos originales](../../unidad31-adaptacion-multimodalidad/datos/README.md).

## Protocolo prefijado

1. Conservar el contrato y el modelo. Limitar a cuatro conexiones manejadas, una solicitud de inferencia y un historial de 256 eventos; no usar cola de inferencia.
2. Definir liveness, readiness y los tres estados, con rechazo de nuevas consultas durante mantenimiento/degradación.
3. Registrar UUID propio, etiquetas acotadas, estado y tiempo del manejador. Excluir imágenes, consultas, IP y detalle de excepciones. Contar respuestas preparadas, no entrega confirmada.
4. Laboratorio de observación: ocho solicitudes, cuatro de ellas POST de predicción. Comprobar correlación y denominadores.
5. Laboratorio de fallos: bloquear una solicitud con un evento, comprobar rechazo concurrente, mantenimiento y finalización de lo admitido. Después provocar una excepción, comprobar degradación, ejecutar un canario conocido y recuperar.
6. Agotar la espera de un cliente mientras la llamada sigue retenida; comprobar que sigue ocupando el servidor, liberar y conservar el evento posterior.
7. En otro servidor con un solo cupo de conexión, retener una llamada y conectar otro socket sin enviar HTTP. Comprobar el rechazo anterior al análisis de la solicitud.
8. Conservar UUID y duraciones reales, sin usar valores de rendimiento como umbral para elegir candidatos. Al repetir, exigir los estados y relaciones previstos; los tiempos pueden variar.

Los bloqueos y excepciones son **inyecciones artificiales del laboratorio**; el transporte HTTP y la ejecución de los casos normales son reales. Los cinco tiempos del ejercicio manual son inventados y se identifican como tales. El canario comprueba un caso conocido, no generalización.

No se recopilan datos personales. El historial es acotado en memoria; los JSON publicados se exportan deliberadamente con ejemplos propios. Las licencias de dependencias son las de sus proyectos. No se añade una licencia general del repositorio: no había un archivo LICENSE al preparar esta entrega.

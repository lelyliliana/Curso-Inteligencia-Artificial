# Datos y procedencia

[Unidad](../README.md)

No se crea un conjunto de entrenamiento ni una nueva partición de prueba. Se reutilizan cuatro escenas sintéticas propias del curso, todas de **validación de la Unidad 31**:

| ID de interfaz | Familia U31 | Izquierda | Derecha |
|---|---|---|---|
| 00 | escena-027 | Apagada | Apagada |
| 01 | escena-024 | Apagada | Encendida |
| 10 | escena-030 | Encendida | Apagada |
| 11 | escena-026 | Encendida | Encendida |

Los archivos se leen desde [las imágenes originales](../../unidad31-adaptacion-multimodalidad/datos/README.md). Su generación, ruido y separación previa están documentados allí. No se duplican ni alteran. Los nombres de escena sirven para el catálogo y el oráculo de las pruebas; el modelo solo recibe los píxeles y la consulta. La etiqueta esperada no se envía en el cuerpo de inferencia.

El estado es [modelo.json de fusión](../../unidad31-adaptacion-multimodalidad/recursos/multimodal/modelo.json), SHA-256 `f439b8cabb3b24f2fc3208ac4de57439a5226888bba25e84180a9c4aeb8228bf`. Reutilizar la misma reserva para comprobar integración no ofrece una estimación nueva de generalización. Los resultados predictivos independientes siguen siendo los documentados en la U31, con sus límites.

Los cuerpos inválidos y la imagen RGB son casos artificiales de contrato. No contienen datos personales ni proceden de usuarios. La aplicación no escribe las imágenes enviadas en disco; la evidencia publicada usa únicamente estos ejemplos propios. Las capturas incluyen la interfaz propia.

No se descargan modelos ni imágenes de terceros. Al preparar esta entrega no había un archivo LICENSE en la raíz del repositorio; no se añade una licencia general por inferencia. Las dependencias conservan sus licencias correspondientes.

# Protocolo de integración

[Unidad](../README.md) · [Datos](README.md)

1. Fijar el estado de fusión ya elegido en la U31 y su huella. No entrenar, elegir épocas, cambiar umbrales ni evaluar nuevos candidatos.
2. Reutilizar preparación, vocabulario de consultas y posiciones de las luces. Mantener intactos los archivos de la U31.
3. Definir el contrato: dos campos exactos, JSON UTF-8, base64 puro, PNG L estático 20×16, 16 KiB de imagen y 32 KiB de cuerpo.
4. Construir ocho consultas sobre cuatro escenas conocidas. El resultado esperado se fija por la construcción de cada escena, no por la salida del modelo.
5. Añadir diez escenarios de errores de entrada, tipo, tamaño, ruta y método, y seis consultas de recursos. Registrar estados y respuestas HTTP reales mediante un servidor temporal.
6. Exigir que las 24 comprobaciones coincidan. Un fallo obliga a corregir la integración; no autoriza reentrenar para ocultarlo. Conservar una captura reproducible sin puerto, reloj o duración variables.
7. Comprobar aparte carga, rechazo previo a inferencia, preparación idéntica, estado sin modificaciones, límites HTTP y privacidad del registro mediante pruebas.
8. Recorrer el formulario en un navegador: predicciones para ambos lados, borrado del resultado al cambiar entrada, error de formato y recuperación. Documentar lo efectivamente observado, sin sumar estas acciones al número de pruebas automáticas.

La medida es **cumplimiento funcional de casos predefinidos**. No se estima exactitud poblacional, robustez ante fotografías, capacidad concurrente, rendimiento de producción ni accesibilidad completa. El servidor temporal de los scripts usa loopback y se cierra al terminar; publicar los archivos en GitHub no despliega un servicio.

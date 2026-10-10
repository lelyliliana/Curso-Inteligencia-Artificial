# Revisión de interfaz

[Unidad](../README.md)

Revisión realizada el 10 de octubre de 2026 en el navegador integrado, contra la aplicación Python real en `127.0.0.1:8765`. Se usó la vista estrecha de una columna disponible; no se simularon aquí múltiples navegadores o dispositivos.

| Acción | Resultado observado |
|---|---|
| Abrir la aplicación | Catálogo y vista previa cargados; estado listo |
| Escena «Derecha encendida», lado derecha | Predicción encendida |
| Cambiar a izquierda | Se borró la respuesta anterior |
| Consultar con teclado | Predicción izquierda apagada; [captura](interfaz.jpg) |
| Seleccionar un PNG RGB artificial | Se borró la respuesta y apareció vista previa del archivo |
| Consultar cuando el proceso ya estaba cerrado | Mensaje de falta de conexión; no apareció una clase |
| Reiniciar el servidor y consultar el mismo RGB | Rechazo por formato; [captura](interfaz-error.jpg) |
| Volver a «Izquierda encendida» y consultar izquierda | Desapareció el error y apareció encendida |

La interrupción del proceso permitió observar el manejo de conexión real. No se presenta como medición de disponibilidad. Las capturas son imágenes de la aplicación en funcionamiento, no maquetas; no contienen datos personales.

Para repetir, sigue el laboratorio 2 y detén el proceso con Ctrl+C antes de una consulta si quieres comprobar el fallo de conexión. Al reiniciarlo, vuelve a consultar. Comprueba además con el teclado que se puede acceder a los selectores y enviar el formulario, y que el error no deja los controles bloqueados.

La revisión manual complementa las pruebas Python; no está automatizada por el verificador común. Quedan fuera de esta comprobación compatibilidad de todos los navegadores, pruebas formales con lectores de pantalla y otras dimensiones de viewport.

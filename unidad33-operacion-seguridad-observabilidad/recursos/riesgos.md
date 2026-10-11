# Riesgos, controles y límites

[Unidad](../README.md)

El activo principal es la aplicación local y su capacidad de atender consultas sin exponer entradas. Se consideran clientes locales que envían cuerpos incompatibles o agotan recursos, fallos del servicio y cambios accidentales de versión. No se afirma protección frente a un usuario con control del proceso, del sistema operativo o del repositorio.

| Problema | Control implementado | Evidencia | Límite |
|---|---|---|---|
| Leer archivos arbitrarios | Catálogo de rutas de U32 | Pruebas de U32 y recursos heredados | No es un servidor general de archivos |
| Cuerpos grandes/incompatibles | 32 KiB JSON, 16 KiB PNG, gramática y modo exactos | Pruebas de U32; casos rechazados | Un formato válido puede ser ajeno al dominio aprendido |
| Hilos sin límite | Semáforo antes de crear el manejador | Rechazo de conexión excedente | No cuenta backlog ni otros hilos del proceso |
| Cola creciente ante el modelo | Un cupo, admisión no bloqueante | Segundo POST recibe 503 | No cancela el cálculo activo |
| Cliente que deja de enviar un cuerpo | Timeout por operación de socket | Prueba de HTTP 408 y liberación sin cabeceras completas | No es un plazo total contra goteo continuo |
| Fallos internos repetidos | Estado degradado y revisión antes de reanudar | Fallo 500, siguientes 503, recuperación | Política conservadora de laboratorio; no detección universal |
| Exposición accidental a otras interfaces | Escucha fija en 127.0.0.1 | Dirección del servidor | Otros procesos de la máquina aún pueden acceder |
| Peticiones de origen ajeno | Host/Origin y política heredada de U32 | Pruebas 403 | No sustituyen autenticación; un cliente local puede falsificar cabeceras |
| Datos privados en registros | Esquema permitido, rutas agrupadas, sin cuerpos ni mensajes de excepción | Prueba con marcadores privados ausentes del historial | La terminal o archivos de logs necesitan su propia política de acceso |
| Historial creciente | Deque de hasta 256 eventos | Prueba de retención con contadores acumulados | stderr redirigido no tiene rotación automática |
| Modelo cambiado sin revisión | Huella exacta y restaurador de U32/U31 | Pruebas anteriores y fuentes de las capturas | Hashes no autentican cambios coordinados |
| Métrica interpretada mal | Denominadores y respuestas preparadas explícitos | Reconstrucción y ejemplo manual | Un 200 no demuestra corrección predictiva ni recepción |

No se habilitan autenticación, TLS, credenciales, un proxy, un colector remoto o exposición pública. Para una operación real hay que definir identidad, permisos, red, límites globales, aislamiento del cálculo, actualización de dependencias, observación y respuesta a incidentes en su contexto. Esta lista delimita qué falta; no certifica que agregar un control aislado produzca un sistema seguro.

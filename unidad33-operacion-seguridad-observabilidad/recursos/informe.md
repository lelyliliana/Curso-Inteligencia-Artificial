# Informe de ejecución y evidencia

[Unidad](../README.md)

Se ejecutaron ambos laboratorios con el modelo real de fusión ya incluido, sobre HTTP local, usando el entorno del curso. El código de U31/U32 se conserva intacto, salvo la navegación de su documentación. El mecanismo de inyección es un envoltorio Python de laboratorio; no existe un endpoint remoto para controlarlo.

| Archivo | Contenido |
|---|---|
| [observacion.json](observacion.json) | Ocho respuestas, ocho eventos, configuración, huellas y resumen |
| [fallos.json](fallos.json) | Saturación, mantenimiento, fallo artificial, recuperación, timeout de cliente y límite de conexiones |
| [manual.json](manual.json) | Cinco estados/tiempos artificiales para cálculo |
| [operacion.png](operacion.png) y [operacion.svg](operacion.svg) | Conteos y denominadores de las capturas, revisados visualmente |

## Lectura de los resultados

Observación: ocho respuestas preparadas. Sobre cuatro POST exactos de predicción: dos éxitos 200, dos rechazos 4xx y cero 5xx. La captura de `/metricas` refleja siete respuestas previas y su propia solicitud en curso; el resumen final contiene ocho terminadas.

Fallos: catorce respuestas recibidas en la secuencia principal y quince eventos. Los diez POST incluyen seis 200 y cuatro 5xx: saturación, mantenimiento, excepción y rechazo durante degradación. Las otras cinco solicitudes son sondas: dos liveness 200 y tres readiness, una 200 y dos 503. Así, todas las rutas suman nueve 200 y seis 5xx. Las tasas `6/15` y `4/10` coinciden en 40 %, pero no describen la misma población.

La llamada que agotó la espera del cliente aparece en los eventos como 200 preparado después de liberarla. El laboratorio conserva que el servidor seguía ocupado cuando el cliente terminó de esperar. **No se sustituye ese timeout por un éxito recibido.** El canario directo es una inferencia real aparte del transporte y no se suma al denominador HTTP.

La prueba de conexiones usa otro servidor con capacidad uno. Conserva una respuesta preparada 200 y un rechazo de conexión anterior a leer HTTP. Ese rechazo no tiene request ID ni una ruta inferida. Se cuenta en `conexiones_rechazadas_antes_de_HTTP` y queda fuera de los totales del experimento principal.

Los tiempos son mediciones reales del manejador. En las capturas guardadas, las medias de POST son aproximadamente 2,59 ms para observación y 11,58 ms para fallos; esta segunda incluye una espera artificial superior a 100 ms. No comparan rendimiento de modelos ni estiman capacidad bajo carga. La fracción buena de la captura principal de fallos es 5/10 con objetivo ilustrativo 100 ms; puede variar al repetir.

## Reproducción y trazabilidad

```bash
python unidad33-operacion-seguridad-observabilidad/ejemplos/01_observar_servicio.py --salida resultados/u33/observacion.json
python unidad33-operacion-seguridad-observabilidad/ejemplos/02_probar_fallos.py --salida resultados/u33/fallos.json
python unidad33-operacion-seguridad-observabilidad/soluciones/03_operacion_a_mano.py --salida resultados/u33/manual.json
python -m unittest discover -s unidad33-operacion-seguridad-observabilidad/pruebas -v
```

Cada captura real guarda SHA-256 de los tres módulos centrales de U33 y los tres módulos reutilizados de U32, además del modelo. No contiene tiempo de calendario ni puerto efímero; los UUID y duraciones sí corresponden a su ejecución. Las pruebas comprueban hashes, estados y relaciones al repetir, y reconstruyen los agregados de la captura con tolerancia para el redondeo de duraciones. No exigen que un UUID o la latencia se repitan.

El script de figuras lee las capturas publicadas; no ejecuta nuevas inferencias ni cambia la evidencia. El ejercicio manual usa datos declarados artificiales y calcula un p95 exacto de cinco observaciones, distinto de estimar un percentil a partir de buckets.

No se evaluó generalización, disponibilidad sostenida, rendimiento concurrente de producción, resistencia integral a ataques o drenaje garantizado al cerrar. La inspección visual corresponde a la figura; la interfaz original se comprueba por sus archivos y contrato HTTP, sin afirmar una nueva prueba manual de navegador.

# Operación y traspaso local

[Unidad](../README.md) · [Informe](informe.md) · [Checklist](../plantillas/traspaso.md)

## Interfaz y límites

La CLI recibe un archivo JSON UTF-8, lee como máximo 16 KiB más un byte para detectar exceso, carga un paquete local y produce JSON por salida estándar. Emite un evento por salida de error estándar. Un éxito sale con código 0; un rechazo o error esperado, con código 2. Los estados y datasets del repositorio son archivos locales de confianza.

La decodificación rechaza JSON roto, claves repetidas, `NaN`, infinitos y codificación inválida. Después se exige el contrato exacto de potencia y tres tiempos. La biblioteca estándar permite controlar pares y constantes durante la decodificación; aquí se usa esa posibilidad para evitar una interpretación ambigua. [JSON en Python](https://docs.python.org/3.12/library/json.html)

El servicio es **secuencial y local**. No implementa HTTP, autenticación, TLS, concurrencia, cancelación dura, almacenamiento persistente de métricas ni supervisión permanente. Si se añade una API, sus controles necesitan una nueva verificación, apoyándose en las unidades 32–33.

## Inicio y caso conocido

1. Recupera código, protocolo, datos de desarrollo y modelo correspondientes a la misma versión.
2. Instala el entorno declarado y ejecuta las pruebas.
3. Ejecuta la consulta publicada. El elegido devuelve aproximadamente 43,761493161 kW para las 11:00 UTC−05:00; faltan 55 minutos desde la decisión.
4. Comprueba `modelo_sha256`, política y correlación de `solicitud_id` entre salida y evento.

El paquete se carga una vez por instancia. La CLI crea una instancia por invocación. Las huellas detectan cambios de contenido o fuentes respecto a la entrega; no son firmas ni sustituyen la confianza en el origen del código/modelo. Las fuentes de preparación y predicción se registran en el paquete; la implementación de la CLI y del servicio se versiona junto a ellas en Git.

## Respuesta a incidentes

| Caso | Respuesta | Acción local |
|---|---|---|
| JSON o campos inválidos | Rechazo sin predicción | Corregir el origen/formato; no rellenar con cero |
| Lectura tardía o caducada | Rechazo temporal | Obtener una lectura válida para una nueva decisión |
| Potencia permitida fuera del rango entrenado | Resultado marcado `revisar` | Contrastar el caso; no interpretarlo como garantía de fallo |
| Error interno inesperado | Mensaje genérico y servicio inactivo | Investigar, corregir y crear una instancia nueva; probar un caso conocido |
| Mantenimiento | Rechazo de nuevas consultas | Reanudar solo después de comprobar la versión recuperada |
| Deterioro de calidad | No se detecta automáticamente por un contador de respuestas | Reunir objetivos observados y revisar MAE, sesgo, cobertura y casos |

No se reintenta automáticamente ni se cambia de modelo al fallar. Una decisión de reversión usa `--referencia`, que selecciona explícitamente la persistencia guardada y lo comunica. Conserva los resultados originales y documenta el motivo. La referencia también necesita una lectura válida; no evita un rechazo del contrato.

## Registros y métricas

Se genera un UUID por solicitud. El historial en memoria conserva los últimos 64 eventos y los contadores acumulan durante la vida de la instancia. Se reinician al crear otra. Las métricas separan `estimacion`, `revisar`, `rechazado` y `error`; la fracción rechazada es indefinida (`null`) si no hay solicitudes.

Los eventos no incluyen entradas, salidas predictivas, IP ni detalles privados de excepciones. La duración se mide dentro de `responder`, después de la carga y antes de que la CLI escriba la respuesta; no es latencia de red ni de lectura del archivo. Redirigir stderr a un archivo requiere una política propia de retención: el deque no limita ese archivo.

El laboratorio de ocho solicitudes es una comprobación funcional controlada. No demuestra capacidad concurrente, privacidad ante todos los ataques, disponibilidad real ni calidad predictiva nueva. El cierre de calidad usa otros datos y denominadores.

## Reproducir una versión anterior

Recupera el conjunto de código, datos y modelo desde el commit que corresponda. Copiar solo pesos antiguos sobre fuentes nuevas puede fallar correctamente la comprobación de huellas. Antes de retomar, ejecuta pruebas y consulta conocida. Para una nueva política, crea una salida separada, fija el protocolo y reserva evaluación nueva cuando los cierres anteriores ya hayan influido en la decisión.

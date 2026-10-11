# Procedimiento local: iniciar, diagnosticar, cambiar y revertir

[Unidad](../README.md)

## Antes de iniciar

Conserva la versión de código, el entorno y el modelo que ya pasaron pruebas. No actualices paquetes a ciegas durante un incidente. En esta entrega se reutiliza el entorno de U32/U31 y se conserva su SHA-256 en cada respuesta/evento pertinente. El servidor imprime su configuración efectiva al iniciar.

```bash
python unidad33-operacion-seguridad-observabilidad/ejemplos/operacion.py --puerto 8766 --conexiones 4
```

El modelo se carga antes de abrir el puerto. Si falla, corrige el archivo/entorno; no alteres la huella solo para que acepte otro estado. La función de biblioteca permite elegir tiempos y capacidad del historial mediante `Config`; la CLI expone puerto, conexiones e inicio en mantenimiento, no todos los campos.

En otra terminal puedes consultar las sondas con biblioteca estándar:

```bash
python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('http://127.0.0.1:8766/live', timeout=2)))"
python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('http://127.0.0.1:8766/ready', timeout=2)))"
```

Para un 503, `urllib` lanza `HTTPError`: un cliente operativo debe examinar su estado/cuerpo; una excepción de esa clase no equivale a una conexión inexistente. Los clientes de laboratorio lo hacen con `http.client` para conservar ambas clases de respuesta.

## Diagnóstico

| Síntoma | Comprobación siguiente | Acción local |
|---|---|---|
| No abre el puerto | Mensaje de inicio, existencia y huella del modelo, dependencias | Corregir carga y reiniciar; no anunciar disponibilidad |
| 422 | Código de error, contrato de entrada | Corregir la solicitud; no reiniciar ni reentrenar |
| 503 `ocupado` | Consulta admitida, capacidad y duración | Reintentar con espera controlada; no multiplicar reintentos simultáneos |
| 503 por mantenimiento | Estado y decisión del operador | Terminar revisión antes de reanudar |
| 500 y luego degradación | ID de solicitud, código, versión y reproducción acotada | Conservar evidencia mínima, corregir y comprobar un canario |
| Cliente agotó espera | Métricas de trabajo todavía en curso | No asumir cancelación; evitar repetir trabajo indiscriminadamente |
| 200 con clase incorrecta | Entrada compatible y evaluación predictiva | Investigar preparación/modelo; no confundirlo con salud HTTP |

No guardes la imagen o consulta para investigar sin definir necesidad, permiso, retención y acceso. En el laboratorio basta con el caso sintético y su ID. Los eventos se imprimen en stderr; cualquier archivo redirigido es responsabilidad de quien opera.

## Cambio y reversión sin sobrescribir versiones

1. Ejecuta las pruebas de U33 y el verificador común. Conserva sus resultados y los hashes de la captura generada; una modificación legítima exige regenerar y revisar evidencia, no ocultar la diferencia.
2. Inicia U33 en 8766 y comprueba `/live`, `/ready` y una escena conocida. La U32 permanece disponible como código previo, en otro directorio; no cambia el JSON del modelo.
3. Si hay una regresión, detén el proceso de U33 con Ctrl+C. El cierre de este ejemplo no garantiza terminar una inferencia bloqueada de forma ordenada: verifica el fin del proceso antes de liberar o reutilizar recursos.
4. Inicia la versión anterior para la comparación local:

```bash
python unidad32-modelo-aplicacion/aplicacion/servidor.py --puerto 8765
```

5. Repite una consulta conocida y documenta por qué se volvió atrás. Este retorno recupera también las limitaciones de U32: no conserva la admisión limitada ni las métricas nuevas.

Es una reversión de demostración entre dos programas del repositorio. No implementa conmutación de tráfico, migración de datos, despliegue sin interrupciones o rollback automático. No requiere `git reset`, borrar evidencias ni desplegar un servicio externo.

## Recuperar disponibilidad con criterio

La entrada en mantenimiento y la reanudación del laboratorio son llamadas internas a `establecer_estado`; no constituyen una API de administración. Tras la excepción artificial, primero se corrige el envoltorio y se comprueba la escena conocida; después se marca `listo`. Un canario que acierta no certifica todo el modelo, pero evita reanudar sin comprobar siquiera el recorrido básico.

El reinicio descarta contadores e historial en memoria. Si hace falta conservar una comparación antes/después, exporta evidencia acotada e identifica las dos ventanas. No compares totales de procesos con distinta duración como si fueran tasas equivalentes.

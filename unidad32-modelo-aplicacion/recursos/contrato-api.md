# Contrato HTTP v1

[Unidad](../README.md)

Servidor de práctica: `http://127.0.0.1:8765`. Se puede cambiar el puerto mediante CLI; la dirección de escucha permanece en loopback. Los clientes usan el mismo Host que muestra el servidor. Si incluyen Origin, debe corresponder exactamente a ese origen local. No se habilita CORS.

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/` | HTML de la aplicación |
| GET | `/app.js`, `/estilos.css` | Recursos locales de interfaz |
| GET | `/health` | `{"version":"1","estado":"listo"}` después de iniciar |
| GET | `/api/modelo` | Identidad, huella, clases y alcance |
| GET | `/api/ejemplos` | IDs, nombres y URLs relativas de las cuatro escenas |
| GET | `/ejemplos/00.png` … `/ejemplos/11.png` | Solo las cuatro rutas exactas del catálogo |
| POST | `/api/predecir` | Predicción o error, en JSON |

No se admiten parámetros de URL, rutas de archivos arbitrarias o redirecciones. Los métodos implementados distintos del permitido para una ruta devuelven 405. Las peticiones malformadas rechazadas por el parser HTTP de Python pueden usar sus errores predeterminados; este contrato JSON describe las solicitudes que llegan al manejador de la aplicación.

## Solicitud de predicción

- Un único `Content-Length` decimal no negativo, de hasta ocho dígitos, y no mayor que 32768.
- Un único `Content-Type: application/json`, opcionalmente `charset=utf-8`.
- Sin `Transfer-Encoding`.
- Cuerpo UTF-8 con exactamente `imagen_base64` y `texto`, ambos cadenas.
- `imagen_base64`: base64 puro, sin espacios ni prefijo data; hasta 16384 bytes decodificados. PNG estático L, 20×16.
- `texto`: `estado izquierda`, `estado derecha`, `consulta izquierda` o `consulta derecha`, sin normalizaciones implícitas.

Ejemplo real de cliente, con el servidor activo, desde la raíz del repositorio:

```python
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen

png = Path("unidad31-adaptacion-multimodalidad/datos/multimodal/imagenes/escena-024.png").read_bytes()
entrada = {"imagen_base64": base64.b64encode(png).decode("ascii"),
           "texto": "estado derecha"}
cuerpo = json.dumps(entrada).encode("utf-8")
peticion = Request("http://127.0.0.1:8765/api/predecir", data=cuerpo,
                   headers={"Content-Type": "application/json"}, method="POST")
with urlopen(peticion, timeout=8) as respuesta:
    print(json.load(respuesta))
```

`urllib` calcula Content-Length al recibir bytes; no se introduce a mano. Para errores HTTP el cliente debe manejar `HTTPError` y leer su JSON. El cliente de [apoyo.py](../ejemplos/apoyo.py) conserva tanto respuestas correctas como rechazos con `http.client`.

## Respuestas

Éxito 200: `version`, `estado=ok`, `resultado={lado,clase}` y `modelo={id,sha256}`. Las únicas clases son `apagada` y `encendida`. No hay etiqueta de verdad ni porcentaje de certeza.

Error del manejador: `version`, `estado=error`, `error={codigo,mensaje}`. No contiene `resultado`:

| Estado | Códigos principales |
|---:|---|
| 400 | `json_invalido`, `longitud_invalida`, `transferencia_invalida`, `cuerpo_incompleto` |
| 403 | `host_invalido`, `origen_invalido` |
| 404 | `ruta_invalida`, `ruta_desconocida` |
| 405 | `metodo_invalido` |
| 408 | `lectura_agotada` durante la lectura del cuerpo |
| 411 | `longitud_ausente` |
| 413 | `cuerpo_grande`, `imagen_grande` |
| 415 | `tipo_invalido` |
| 422 | `campos_invalidos`, `texto_invalido`, `imagen_ausente`, `base64_invalido`, `formato_imagen`, `imagen_invalida` |
| 500 | `error_interno` |

La lectura de socket tiene un timeout de cinco segundos por operación; no representa un plazo total de servicio contra clientes lentos ni una cuota. La interfaz limita la espera de `fetch` y permite reintentar manualmente. No hay reintentos automáticos. Las respuestas cierran la conexión y envían `Cache-Control: no-store`; se conservan en memoria del cliente para mostrarlas.

La versión corresponde al contrato, no a la revisión de PyTorch. Cambiar campos o su significado requiere revisar consumidores y pruebas. La huella del modelo permite distinguir estados incluso si comparten la misma arquitectura; no es una firma de autenticidad.

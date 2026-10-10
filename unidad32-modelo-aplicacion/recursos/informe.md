# Informe de integración y artefactos

[Unidad](../README.md)

Se reutilizó el estado seleccionado en la U31, sin entrenar o modificar los archivos anteriores. No se descargaron pesos ni paquetes nuevos. La selección del modelo queda fuera del alcance de esta entrega: se comprueba que la aplicación lo sirve de forma coherente.

| Artefacto | Contenido |
|---|---|
| [servicio.json](servicio.json) | Predicción directa y rechazo de texto libre |
| [http.json](http.json) | 24 respuestas y comprobaciones mediante conexiones HTTP locales reales |
| [tamano.json](tamano.json) | Cálculo manual reproducible de base64, JSON y UTF-8 |
| [interfaz.jpg](interfaz.jpg) | Formulario con predicción sobre una escena |
| [interfaz-error.jpg](interfaz-error.jpg) | Formulario con rechazo de PNG RGB |
| [revision-interfaz.md](revision-interfaz.md) | Acciones y resultados observados en navegador |

## Resultado

- Ocho consultas válidas sobre cuatro escenas conocidas devolvieron la clase esperada y la huella fijada.
- Diez escenarios incorrectos devolvieron los estados y códigos esperados, sin `resultado`.
- Seis recursos de la aplicación respondieron correctamente. Para archivos se conservan tamaño y hash; para endpoints JSON, su contenido.
- Total: 24/24 comprobaciones funcionales. Las 44 pruebas añaden casos de parser, ciclo de carga, pesos intactos, cabeceras, fallos y reconstrucción de los artefactos.
- En el navegador se verificaron ambas clases, borrado de resultados, error de conexión, rechazo de formato y recuperación.

Los bytes del JSON del ejemplo manual son artificiales, no un PNG aceptable. Los rechazos de HTTP también son casos artificiales diseñados para probar contratos. Las respuestas de éxito sí proceden de ejecutar el modelo real cargado del curso.

## Cómo reproducir

Desde la raíz con el entorno activo:

```bash
python unidad32-modelo-aplicacion/ejemplos/01_predecir_sin_http.py --salida resultados/u32/servicio.json
python unidad32-modelo-aplicacion/ejemplos/02_comprobar_http.py --salida resultados/u32/http.json
python unidad32-modelo-aplicacion/soluciones/03_tamano_peticion.py --salida resultados/u32/tamano.json
python -m unittest discover -s unidad32-modelo-aplicacion/pruebas -v
```

Los scripts guardan el puerto fuera de la captura y omiten los tiempos variables; permiten comparar el contenido. La prueba de reconstrucción incluye hashes de los tres recursos web, así que un cambio intencional de interfaz exige revisar y regenerar la captura HTTP. Las capturas de navegador se toman por separado.

No se midió latencia bajo carga, memoria pico, disponibilidad sostenida o seguridad integral. Los ejemplos ya estaban en validación de la U31; los ocho aciertos no constituyen un nuevo cierre predictivo. Publicar esta unidad en GitHub publica código, documentación y evidencia, no un servicio accesible en Internet.

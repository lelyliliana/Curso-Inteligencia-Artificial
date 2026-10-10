# Soluciones razonadas

[Ejercicios](../ejercicios.md) · [Unidad](../README.md)

1. Criterios: una consulta válida muestra lado y clase; cambiar el lado borra la respuesta anterior; un PNG RGB produce un mensaje corregible y permite reintentar. No interpreta fotografías generales. Ver que aparece un mensaje es un criterio funcional; medir aciertos en una reserva independiente es una métrica del modelo.

2. Leer el archivo y mostrar el lado: interfaz. Rechazar claves extra: contrato. Cargar pesos: servicio al iniciar. Convertir el rechazo en 422: servidor. Entrenar durante la solicitud elevaría el costo, haría cambiar el estado entre usuarios y mezclaría operación con selección; además complicaría repetir el resultado.

3. La representación forma parte del modelo probado: RGB tiene tres canales y la preparación espera uno. La semejanza visual no garantiza idénticos valores después de una conversión. Para admitir RGB, definir la conversión, conservar pares de referencia, comparar características y predicciones, evaluar ejemplos representativos y versionar el cambio. No basta con añadir `.convert('L')` y declarar equivalencia.

4. Un servidor puede responder sin modelo; un modelo puede cargarse sin ser útil fuera de su dominio. En esta aplicación se abre el puerto después de comprobar estado, preparación e inferencia básica. `/health` constata que completó el inicio y responde HTTP; no prueba generalización ni capacidad bajo carga. Si falta el archivo, se termina con un mensaje y código 1, sin anunciar disponibilidad.

5. La solicitud tiene solo `imagen_base64` y `texto`; la respuesta 200 contiene versión, estado, resultado e identidad del modelo. JSON roto: 400. Texto fuera de gramática: 422. Fallo imprevisto de inferencia: 500. Devolver `apagada` como respaldo ocultaría la falta de una predicción válida y podría inducir a actuar sobre un dato inventado.

6. `4 × ceil(16384/3) = 21848`. El JSON del [ejemplo](03_tamano_peticion.py) ocupa 21.896 bytes porque añade claves, comillas, espacios y texto. Content-Length cuenta el cuerpo completo en bytes. Con `ensure_ascii=False`, «á» ocupa dos bytes UTF-8 aunque sea un carácter; el ejemplo `{"nota": "lámpara"}` ocupa un byte más que su longitud en caracteres.

7. Se carga la escena y se limpia el resultado; al consultar se bloquean controles, se espera, se muestra resultado o error y se habilitan controles en `finally`. Una predicción antigua visible junto a una entrada nueva atribuiría la respuesta al caso incorrecto. `fetch` resuelve una respuesta HTTP 422; hay que revisar `response.ok` y generar el error de aplicación. Una falla de conexión sí puede rechazar la promesa.

8. Validar base64 es una prueba unitaria del contrato. HTTP 413 verifica transporte y contrato juntos. Observar el botón requiere ejecutar la interfaz. Comparar pesos comprueba una propiedad del ciclo de inferencia del servicio. Una API correcta no demuestra que JavaScript consuma su respuesta; una interfaz visualmente correcta puede enviar campos incorrectos.

9. Son ocho predicciones sobre cuatro escenas, diez rechazos y seis recursos. Las escenas estaban en validación de la U31: la medida es cumplimiento de esas comprobaciones funcionales. Una evaluación predictiva nueva reservaría familias no utilizadas para decidir cambios, definiría variaciones del dominio y criterios antes de mirar resultados, y mantendría la calidad de modelo separada de la disponibilidad de API.

10. Un registro mínimo puede contener estado, duración e identificador de solicitud generado por el servidor, sin entrada, imagen, tokens sensibles o rutas privadas. Para publicar harían falta, entre otros, un servidor adecuado, control de acceso/TLS según el contexto y límites de recursos/concurrencia, junto con un plan de fallos. Un hash compara bytes y detecta cambios; un atacante que pueda reemplazar modelo y hash no queda detenido por esa comparación. La U33 ampliará estas decisiones.

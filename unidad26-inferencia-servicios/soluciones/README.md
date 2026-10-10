# Soluciones razonadas — Unidad 26

[Unidad](../README.md) · [Cálculos ejecutables](03_medir_a_mano.py)

## 1. Componentes y ruta

El cliente prepara JSON, se conecta y valida el resultado. Ollama es el servidor que carga el modelo y organiza la inferencia. Los pesos son parámetros almacenados; la plantilla y el tokenizador también influyen en la entrada efectiva. Una API define cómo intercambiar datos y no implica acceso a Internet. En la práctica el servidor está en `127.0.0.1:11434`; el adaptador remoto usa otro servicio mediante HTTPS.

## 2. Memoria ideal

Con 8 000 000 000 parámetros: a 4 bits son 4 000 000 000 bytes, 4 GB o aproximadamente 3,73 GiB; a 16 bits son 16 GB o 14,90 GiB. Faltan metadatos de cuantización, caché y buffers. Q4_K_M tampoco significa que absolutamente todos los componentes se guarden a cuatro bits. El archivo local de esta unidad ocupa alrededor de 5,23 GB; su tamaño no demuestra el pico de RAM.

## 3. Velocidad y espera

20 tokens / 2 segundos = 10 tokens/s de decodificación. 20 / 3 = 6,67 tokens/s extremo a extremo. Una diferencia puede deberse a carga, preparación y comunicación. Ni una cifra mide por sí sola calidad ni podemos compararla entre tokenizadores como si cada token tuviera el mismo significado. El [programa manual](03_medir_a_mano.py) comprueba las unidades.

## 4. Capas de error

HTTP 200 con HTML supera el estado HTTP, pero falla al interpretar JSON. Un JSON válido con `43`, `done=true` y `stop` cumple el contrato de servicio pero falla la suma. `42` con `length` coincide con el resultado, aunque no cumple la condición de parada normal. El evaluador conserva las diferencias y no reduce todo a «la llamada funcionó».

## 5. Texto completo con límite agotado

En el caso ausente, cuatro tokens visibles produjeron `NO_DISPONIBLE`; no quedó presupuesto para terminar de la misma manera que con 48, donde el contador fue cinco y la parada `stop`. El registro no identifica individualmente cada token contado: no permite demostrar por sí solo cuál fue el quinto. Lo comprobable es la diferencia de contador y razón. Según la regla prefijada, una coincidencia con `length` no es aceptada. Cambiar la regla después de ver esta salida alteraría el experimento.

## 6. Medianas desde cada intento

Con límite 4, tiempos ordenados aproximadamente: 0,357; 0,486; 1,669; 2,017 s. La mediana es la media de los dos centrales: 1,078 s. Con límite 48: 0,358; 0,818; 2,246; 2,290 s; mediana 1,532 s. Los cálculos del código usan los valores completos del registro. El calentamiento, de 12,371 s, se excluye por protocolo, no por resultar más lento.

El segundo envío de cada prompt fue más rápido que el primero en esta captura; alternar qué límite va primero evita favorecer siempre a uno, pero no elimina la influencia de caché ni otras cargas del equipo. No hay suficientes observaciones para declarar un rendimiento general.

## 7. Denominador ante un timeout

Si la primera llamada, suma con límite 4, se reemplaza por `error="timeout"` y se elimina su campo `respuesta`, quedan cuatro intentos, tres contratos válidos, una aceptación y tres latencias incluidas. La mediana se recalcula con esos tres valores. Reportar 1/3 como tasa sobre solicitudes ocultaría el fallo: la aceptación sobre intentos es 1/4. No se ha realizado un timeout real al hacer esta modificación; es un contrafactual en memoria, cubierto por pruebas.

## 8. Configuración y credenciales

Una variable de entorno evita escribir la clave en el código versionado; no la protege de todo proceso, log o usuario con acceso suficiente al entorno. Hay que limitar dónde se lee y evitar imprimirla. Una redirección podría enviar una cabecera de autorización a un destino distinto; el cliente la bloquea y solo permite el endpoint remoto fijo. No se incluyen claves en URL ni mensajes de error. El archivo `.env.example` tiene nombres vacíos y no es un almacén de credenciales.

## 9. Estructura de la API remota

`output` es una lista de elementos. El lector omite elementos que no sean `message`, recorre sus partes y concatena las de tipo `output_text`. Detecta `refusal` aunque haya texto. Conserva `status` e `incomplete_details`. `incomplete` no se acepta como finalización normal y no se reintenta ni se incrementa el límite automáticamente. Un cuerpo de error de servicio se convierte en código seguro; no se imprime íntegro. Las pruebas verifican esos contratos con respuestas artificiales, no la disponibilidad de un modelo remoto.

## 10. Costo y siguiente evidencia

Con las tarifas **ficticias** del ejercicio: `1000 × 2 / 1e6 + 200 × 8 / 1e6 = 0,0036` unidades monetarias. No es un presupuesto de un proveedor real. Tampoco la inferencia local es gratuita en recursos: usa equipo y energía, que no se midieron como dinero en esta entrega.

Los cuatro casos no acreditan conocimientos generales, robustez ante instrucciones maliciosas, calidad en documentos largos ni capacidad para varios usuarios. Antes de ofrecer un servicio, definiría una tarea concreta, nuevos casos representativos y reservados, criterios de aceptación, carga esperada y presupuesto. Mediría errores, colas, timeouts y variación temporal, sin registrar datos privados. No usaría «4/4» como autorización para tomar decisiones de impacto sin revisión.

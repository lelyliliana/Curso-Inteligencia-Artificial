# Reto — Una ficha de inferencia que pueda revisarse

[Unidad](README.md) · [Plantilla](plantillas/informe_inferencia.md) · [Ficha de referencia](recursos/ficha_servicio.md)

## Encargo

Un taller necesita saber si puede usar un servicio de texto para responder preguntas breves sobre registros ficticios. Prepara un informe que distinga disponibilidad del servicio, finalización y cumplimiento de la tarea. La conclusión debe apoyarse en salidas conservadas y declarar qué no se midió.

La **ruta básica** usa la captura de esta unidad y no exige Ollama, descarga de pesos ni cuenta remota. Reproduce el informe, comprueba a mano dos resultados y diseña un experimento futuro. La **extensión opcional** ejecuta un modelo local ya revisado sobre los mismos casos y registra versión, digest, parámetros y recursos. No se exige pagar una API ni mejorar los aciertos de referencia.

## Entregables

1. Diagrama del recorrido y descripción del origen de la evidencia: captura, simulación o llamadas nuevas.
2. Tabla por intento con caso, condición, salida/error, parada, criterio y tiempo de pared.
3. Resumen de las cuatro métricas del laboratorio, con denominadores explícitos y mediana identificada.
4. Reconstrucción manual de un caso truncado y un cálculo de latencia/velocidad.
5. Ficha de recursos, configuración, manejo de fallos, datos y límites de uso.
6. Protocolo para seis casos nuevos: al menos dos de información ausente y dos que tensionen el límite de salida. Escribe criterios antes de mirar las respuestas. Si no los ejecutas, márcalos como propuesta.

Si realizas llamadas nuevas, usa una carpeta distinta dentro de `resultados/`; conserva todos los intentos, incluidos errores. No sustituyas la evidencia original ni selecciones solo una repetición favorable. Si no tienes recursos para inferencia local, entrega la ruta básica completa y explica esa limitación.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Componentes y procedencia | 15 | Diferencia pesos, proceso y cliente; identifica qué fue ejecutado |
| Evaluación por intento | 25 | Separa contrato, parada y coincidencia; conserva truncamientos y fallos |
| Mediciones | 20 | Unidades correctas, denominadores y mediana reconstruidos; distingue caché y calentamiento |
| Recursos y configuración | 15 | Versión, modelo, parámetros y alcance de las mediciones; no expone claves |
| Protocolo adicional | 15 | Seis casos con criterios previos, alcance y presupuesto razonables |
| Conclusión y reproducción | 10 | Comandos verificables y afirmaciones limitadas por la evidencia |

Un informe con simulaciones presentadas como inferencia real debe corregir su procedencia antes de considerarse completo. Más tokens, un modelo mayor o una factura más alta no conceden puntos adicionales.

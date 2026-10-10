# Ficha de inferencia — Qwen3:8b con Ollama

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Registro](local/registro.json) · [Informe](local/informe.json)

## Propósito y evidencia

Demostrar cómo llamar un servicio local de texto, conservar respuestas y separar contrato, finalización y exactitud en cuatro tareas pequeñas. Inferencia real realizada el 10 de octubre de 2026. Los escenarios de error y el contrato remoto se comprobaron mediante simulaciones separadas.

## Identificación

| Campo | Valor observado |
|---|---|
| Servidor | Ollama 0.34.2 |
| Modelo | `qwen3:8b`, Qwen3, GGUF, 8.2B, Q4_K_M |
| Digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Licencia informada | `apache-2.0`; coincide con la ficha del editor consultada |
| Archivo(s) del modelo | 5 225 388 164 bytes; metadato de `/api/tags` |
| Memoria informada al terminar | 5 481 126 952 bytes; `/api/ps`, no pico de RSS |
| VRAM informada | 0 bytes |
| Contexto | 1024 tokens configurados e informados por `/api/ps` |
| Plataforma | Linux x86_64; Python 3.12.3; Ryzen 7 6800H, cuatro hilos usados |
| RAM del equipo | Aproximadamente 30 GiB totales; 14 GiB disponibles antes de ejecutar |
| Dependencias nuevas | Ninguna: servidor, pesos y entorno gráfico ya estaban instalados |

No se garantiza que la etiqueta descargada en el futuro resuelva al mismo digest. Se conservan huellas de plantilla y licencia, y parámetros por defecto informados por el modelo. El inventario completo se comprobó igual antes y después de las llamadas. Los pesos no se incluyen en el repositorio.

## Condiciones y resultados

Temperatura 0, semilla 2601, `think=false`, `stream=false`, CPU explícita, cuatro hilos, `top_k=20`, `top_p=0.95`, penalización de repetición 1. Dos límites, 4 y 48, alternando orden por caso. Una solicitud de calentamiento aparte y ocho solicitudes evaluadas; sin reintentos.

Límite 4: cuatro contratos válidos, dos paradas normales, tres coincidencias, dos aceptaciones. Límite 48: cuatro de cuatro en cada medida. Medianas de pared: 1,078 y 1,532 s, cada una sobre cuatro respuestas válidas. Calentamiento: 12,371 s; no incluido. No hubo fallos de transporte en esta captura. Los errores HTTP y timeout del laboratorio A son simulados.

Se conservan `energia agua su` y `NO_DISPONIBLE` con parada `length`. El criterio acepta únicamente coincidencia exacta y parada normal; por eso la segunda salida no se acepta bajo límite 4 aunque visualmente esté completa.

## Uso y límites

Adecuado para estudiar el cliente, las unidades de medición y la necesidad de evaluar salidas. No acredita calidad general, operación con concurrencia, cumplimiento de instrucciones complejas, protección de un servicio público ni datos reales. No se midieron energía, pico de RAM, tiempo al primer token ni facturación. Cuatro casos y una repetición no permiten estimar tasas poblacionales.

La temperatura cero se fijó como condición didáctica; no se presenta como configuración óptima recomendada por el editor. La caché puede favorecer la segunda petición de cada caso. No se entrenó, afinó ni comparó Qwen con otro modelo. La ruta remota no se ejecutó en vivo.

## Datos y operación

Entradas propias, breves y sintéticas. Sin documentos privados ni historial ajeno. El script usa `127.0.0.1`, no crea un endpoint público, no ejecuta herramientas pedidas por el modelo ni instala modelos. Guarda el registro en disco y puede mantener el modelo cargado durante cinco minutos de inactividad. Los secretos remotos solo se leen en la extensión opcional y no se guardan en los artefactos de esta unidad.

Las fuentes y comandos de reproducción están en [recursos](README.md). Para un uso distinto, redacta otra ficha y vuelve a evaluar: esta conclusión está limitada a la configuración y captura identificadas.

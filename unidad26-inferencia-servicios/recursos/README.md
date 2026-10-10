# Artefactos y fuentes — Unidad 26

[Unidad](../README.md) · [Ficha](ficha_servicio.md) · [Protocolo](../datos/protocolo.md)

| Artefacto | Procedencia y contenido |
|---|---|
| [Registro local](local/registro.json) | Una ejecución real: inventario, solicitudes, respuestas, tiempos, calentamiento y recursos |
| [Informe local](local/informe.json) | Evaluación recalculada desde el registro; no hace inferencia |
| [Informe de simulaciones](simulacion/informe.json) | Doce respuestas artificiales para probar contratos y errores; no mide un modelo |
| [Figura PNG](local/evaluacion.png) y [SVG](local/evaluacion.svg) | Métricas por condición y cada latencia válida del registro |
| [Ficha completada](ficha_servicio.md) | Entorno, resultados, límites y estado de comprobación |

La figura se genera desde el informe existente y fue revisada visualmente. Los metadatos del SVG pueden variar entre exportaciones. Los tiempos de una nueva ejecución no tienen por qué coincidir con la captura; la reproducción exacta de **su análisis** sí se comprueba contra las respuestas registradas.

## Comandos desde la raíz

Solo Python estándar, sin red:

```bash
python unidad26-inferencia-servicios/ejemplos/01_manejar_respuestas.py --salida resultados/u26/simulacion
python unidad26-inferencia-servicios/ejemplos/02_evaluar_inferencia.py --salida resultados/u26/analisis
python unidad26-inferencia-servicios/soluciones/03_medir_a_mano.py
python -m unittest discover -s unidad26-inferencia-servicios/pruebas -v
```

Figuras, con NumPy 2.2.6 y Matplotlib 3.10.8 del entorno ya usado en el curso:

```bash
python unidad26-inferencia-servicios/ejemplos/02_evaluar_inferencia.py --salida resultados/u26/figuras --graficos
```

Una ejecución nueva requiere servidor local y pesos instalados; crea una carpeta de resultados distinta. La instalación, descarga y extensión remota están documentadas en la unidad. Ninguna se ejecuta durante la verificación común.

## Referencias primarias

Consultadas el 10 de octubre de 2026. Casos, explicaciones, cálculos y figuras propios.

- [Ollama: inicio](https://docs.ollama.com/quickstart), [generación HTTP](https://docs.ollama.com/api/generate) y [errores](https://docs.ollama.com/api/errors): rutas de instalación/uso y estructura del contrato. La captura verifica la versión 0.34.2; documentación o versiones posteriores pueden añadir campos.
- [Ollama: modelos instalados](https://docs.ollama.com/api/tags) y [modelos cargados](https://docs.ollama.com/api/ps): identificación, tamaño, digest y recursos informados.
- [Ollama: parámetros](https://docs.ollama.com/modelfile) y [preguntas frecuentes](https://docs.ollama.com/faq): configuración y diferencia entre ejecución local y funciones cloud. No se habilita exposición de red en la práctica.
- [Qwen3-8B: ficha del editor](https://huggingface.co/Qwen/Qwen3-8B) y [variante Ollama](https://ollama.com/library/qwen3:8b): procedencia y licencia. El digest, tamaño y cuantización efectivamente usados se leen del servidor local, no se infieren de una etiqueta actual.
- [Python 3.12: urllib.request](https://docs.python.org/3.12/library/urllib.request.html): peticiones, apertura, timeout y manejo de redirecciones.
- [OpenAI: generación de texto](https://developers.openai.com/api/docs/guides/text): Responses y lista de elementos de salida; no asumir que texto aparece primero.
- [OpenAI: razonamiento](https://developers.openai.com/api/docs/guides/reasoning): presupuesto de salida, tokens no visibles y estado incompleto. El ejemplo remoto evita fijar parámetros de muestreo que no todos los modelos admiten.
- [OpenAI: datos](https://developers.openai.com/api/docs/guides/your-data) y [precios](https://developers.openai.com/api/docs/pricing): revisar configuración y condiciones antes de enviar datos o presupuestar. El ejercicio de costo usa tarifas inventadas.

La ruta OpenAI se ha verificado contra documentación y mediante contratos simulados. No se certifica una llamada remota en vivo, acceso a una cuenta ni un precio concreto.

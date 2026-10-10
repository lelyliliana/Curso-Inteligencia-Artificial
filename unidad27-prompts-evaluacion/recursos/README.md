# Artefactos y fuentes — Unidad 27

[Unidad](../README.md) · [Ficha](ficha_evaluacion.md) · [Protocolo](../datos/protocolo.md)

| Artefacto | Contenido y procedencia |
|---|---|
| [Validación](validacion/informe.json) | 16 salidas artificiales; no son inferencia del modelo |
| [Registro de desarrollo](desarrollo/registro.json) | Calentamiento y 36 peticiones reales, respuestas, fallos, tiempos e inventario |
| [Informe de desarrollo](desarrollo/informe.json) | Capas por caso, errores, familias, estados y referencia por reglas |
| [Selección congelada](desarrollo/seleccion.json) | Elección por desarrollo, desempate, inventario y huellas |
| [Registro de cierre](cierre/registro.json) | Calentamiento y ocho peticiones reales del único candidato elegido |
| [Informe de cierre](cierre/informe.json) | Evaluación sin reajustar el prompt ni cambiar la elección |
| [Desarrollo PNG](desarrollo/evaluacion.png) y [SVG](desarrollo/evaluacion.svg) | Comparación por capas y estado esperado |
| [Cierre PNG](cierre/evaluacion.png) y [SVG](cierre/evaluacion.svg) | Resultado del candidato congelado |

Las respuestas completas incluyen los arrays `context` devueltos por esta versión de Ollama. Codifican únicamente las entradas propias y sus generaciones; no se envía una conversación previa entre casos. Las salidas problemáticas no se corrigen ni se eliminan. Se conserva el inventario antes de las llamadas y se confirma su igualdad al finalizar cada fase.

`huellas` utiliza SHA-256 de los bytes de protocolos, prompts, esquema y datos. Las huellas de registro y selección se calculan sobre sus objetos JSON serializados con claves ordenadas y Unicode conservado; un cambio de espacios del archivo no cambia esa huella de objeto. No son firmas de autenticidad. Las pruebas reconstruyen la selección publicada desde el registro, recalculan informes y verifican la asociación con cierre.

Las figuras usan únicamente informes existentes y se revisaron visualmente. No abren modelos ni ajustan parámetros. La exportación SVG puede variar en metadatos internos entre ejecuciones; se comprueba la información representada. Los tiempos de una nueva inferencia pueden variar aunque se conserve el modelo.

## Reproducción sin red

Desde la raíz del repositorio, con Python estándar:

```bash
python unidad27-prompts-evaluacion/ejemplos/01_validar_salidas.py --salida resultados/u27/validacion
python unidad27-prompts-evaluacion/ejemplos/02_comparar_prompts.py --salida resultados/u27/desarrollo
python unidad27-prompts-evaluacion/ejemplos/02_comparar_prompts.py --fase cierre --seleccion resultados/u27/desarrollo/seleccion.json --salida resultados/u27/cierre
python unidad27-prompts-evaluacion/soluciones/03_calcular_evaluacion.py
python -m unittest discover -s unidad27-prompts-evaluacion/pruebas -v
```

Para gráficos añade `--graficos` a los dos comandos de comparación, con NumPy 2.2.6 y Matplotlib 3.10.8 disponibles. La instalación opcional y el modo `--en-vivo` están explicados en la unidad. No se requiere un servicio remoto de pago. Se reutilizó el entorno del curso; no se creó ni instaló otro entorno para esta entrega.

## Fuentes primarias

Consultadas el 10 de octubre de 2026. Casos, instrucciones, contraejemplos, reglas y figuras propios.

- [Ollama: salidas estructuradas](https://docs.ollama.com/capabilities/structured-outputs): objeto de esquema en `format` y validación posterior. No sustituye la comprobación del contenido.
- [Ollama: generación](https://docs.ollama.com/api/generate): contrato HTTP, formato, streaming, pensamiento y contadores. Las llamadas de referencia se ejecutaron con Ollama 0.34.2; no se asume compatibilidad idéntica en futuras versiones.
- [JSON Schema: objetos](https://json-schema.org/understanding-json-schema/reference/object): propiedades, campos requeridos y propiedades adicionales.
- [JSON Schema: arreglos](https://json-schema.org/understanding-json-schema/reference/array): elementos y unicidad. En nuestra comparación semántica, el orden de los IDs es irrelevante por definición de la tarea.
- [JSON Schema: tipos numéricos](https://json-schema.org/understanding-json-schema/reference/numeric): distinción entre números enteros, fraccionarios y texto numérico.
- [Python 3.12: json](https://docs.python.org/3.12/library/json.html): lectura, hooks de pares y constantes; permite implementar la política estricta de esta práctica. Se trabaja con enteros pequeños, sin prometer aritmética decimal de precisión arbitraria.
- [Unidad 26: fuentes y entorno](../../unidad26-inferencia-servicios/recursos/README.md): transporte reutilizado, inventario de Ollama y documentación del modelo Qwen3-8B. La identificación del mismo digest se conserva en las capturas de esta unidad.

La revisión humana aparece como propuesta metodológica y un cálculo ficticio. No se realizó una evaluación independiente con personas ni con otro modelo juez; los aciertos de esta tarea se obtienen mediante reglas explícitas.

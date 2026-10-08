# Soluciones — Unidad 0

[Volver a la unidad](../README.md) · [Índice del curso](../../README.md)

## Ejercicio 1

La ruta identifica el Python que ejecutó el programa. `Entorno venv: True` indica que sus prefijos corresponden a un entorno creado con `venv`. Si editor y terminal difieren, selecciona el intérprete de `.venv` en el editor y activa el entorno en la terminal, o ejecuta su intérprete por ruta explícita. Comprueba de nuevo `sys.executable`.

Conda y otros gestores pueden aislar paquetes por mecanismos distintos. El diagnóstico de esta unidad comprueba `venv`, no todos los tipos de aislamiento.

## Ejercicio 2

Con umbral 15 hay tres alertas: 18, 20 y 16. Con umbral 20 hay cero alertas: ningún valor es estrictamente mayor que 20.

El total permanece en 108 kWh: cambiar un criterio de alerta no modifica las lecturas.

## Ejercicio 3

Si reemplazas el consumo de la primera observación por `-2`, el mensaje identifica la fila 2 del CSV y explica que el consumo debe ser finito y no negativo. La primera fila es el encabezado; por eso la primera observación está en la fila 2.

Con `desconocido`, la conversión a número falla y el mensaje también señala la fila. El programa termina con código de salida 2 y no genera un resumen parcial. La regla de calidad consiste en detenerse ante una observación inválida para que el problema se revise expresamente.

## Ejercicio 4

Al usar `>= 16`, hay tres alertas: 18, 20 y 16. El texto de salida debe indicar `>=`, y cualquier registro de ejecución debe usar esa misma definición.

Cambiar el código sin cambiar su descripción produce un resultado difícil de interpretar, aunque el cálculo sea técnicamente ejecutable.

## Ejercicio 5

Ejemplo de conclusión: «Las siete lecturas sintéticas suman 108 kWh y presentan dos días por encima del umbral didáctico de 16 kWh. Estos valores permiten practicar el procedimiento, pero no describen el consumo de un hogar real ni validan un sistema de alertas».

## Reto: registro reproducible

La solución [reto_registro.py](reto_registro.py) recibe rutas y parámetros mediante `argparse`. Reutiliza el código del ejemplo para conservar la misma validación y definición de alerta.

El nombre `02_linea_base.py` comienza con un número y no puede importarse mediante una instrucción ordinaria `import 02_linea_base`. La solución usa `importlib.util` para cargar ese archivo por ruta y luego llamar sus funciones. Esa parte sirve para organizar el ejemplo; no necesitas dominar la carga dinámica para completar la preparación del entorno.

El script lee los bytes del CSV una vez, calcula su huella y analiza una copia temporal de esos mismos bytes. Así el registro y el análisis se refieren al mismo contenido. La copia se elimina automáticamente al terminar. Los resultados se escriben fuera del archivo original.

Desde la raíz del curso:

```bash
python unidad00-entorno/soluciones/reto_registro.py --umbral 16
```

Abre `resultados/resumen.json` en tu editor. Comprueba:

- `registros`: 7.
- `total_kwh`: 108.
- `promedio_kwh`: aproximadamente 15,428571.
- `umbral_kwh`: 16.
- `alertas`: dos objetos, para el 5 y 6 de enero.
- `sha256_datos`: huella del archivo utilizado.

El JSON conserva la precisión del cálculo; la salida de consola redondea a dos decimales solo para presentar los valores.

Repite con umbral 18 y otra salida:

```bash
python unidad00-entorno/soluciones/reto_registro.py --umbral 18 --salida resultados/resumen_18.json
```

La huella de datos debe coincidir porque se usó el mismo archivo. El parámetro y las alertas cambian. La versión de Python y el sistema pueden variar entre computadores.

Una huella identifica contenido. Para reproducir el proyecto también necesitas el código, las dependencias y las instrucciones. Si trabajas con Git, registra el commit del código junto con tu informe; el ejemplo inicial no añade ese dato automáticamente.

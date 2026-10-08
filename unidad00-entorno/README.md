# Unidad 0 — Preparación del entorno y forma de trabajar

[Volver al índice](../README.md)

Un proyecto de inteligencia artificial depende de algo más que un modelo. Necesita datos, programas, herramientas y una manera de comprobar lo que ocurre. En esta unidad prepararás el entorno y ejecutarás una primera práctica reproducible.

Trabajaremos con siete lecturas ficticias de consumo energético. Primero conoceremos el entorno y después calcularemos un resumen y aplicaremos una regla explícita de alerta. Esto establece un punto de comparación sencillo para estudiar técnicas más complejas.

## Objetivos

Al terminar podrás:

- Obtener el repositorio y ubicar sus archivos en tu computador.
- Identificar qué intérprete de Python ejecuta tus programas.
- Crear un entorno virtual separado del Python del sistema.
- Diferenciar una biblioteca, un editor, un script y un notebook.
- Ejecutar un programa que lee y valida datos locales.
- Modificar un parámetro y explicar cómo cambia el resultado.
- Registrar los datos, parámetros y entorno de una ejecución.
- Reconocer qué archivos pertenecen al repositorio y cuáles son resultados locales.

## Antes de comenzar

Necesitas un computador y acceso inicial a internet para obtener las herramientas y el repositorio. Una vez preparado el entorno, los ejemplos de esta unidad funcionan sin conexión y sin paquetes externos.

Usaremos Python 3.12 como versión de referencia. Los ejemplos requieren Python 3.12 o superior y se verificaron con Python 3.12.14 en Linux. Las instrucciones de Windows y macOS se basan en la documentación oficial; no se han ejecutado en esos sistemas durante esta publicación.

Para modificar el código debes reconocer variables, listas, funciones, condicionales y archivos. Si necesitas nivelación, consulta el [Curso de Python](https://github.com/lelyliliana/Curso-Python). Puedes completar primero la preparación del entorno y la ejecución guiada.

## 1. Qué herramienta hace cada trabajo

| Elemento | Función | Ejemplo |
|---|---|---|
| Intérprete | Ejecuta el código Python | Python 3.12 |
| Terminal | Recibe comandos y muestra sus resultados | Terminal de Ubuntu, PowerShell |
| Editor | Permite leer y modificar archivos | Visual Studio Code |
| Entorno virtual | Separa los paquetes de un proyecto | Carpeta `.venv` |
| Biblioteca | Aporta funciones reutilizables | `csv`, `statistics` |
| Git | Registra versiones de archivos | Historial del proyecto |
| GitHub | Aloja el repositorio y facilita compartirlo | Página de este curso |
| Script | Archivo de código que se ejecuta | `01_diagnostico.py` |
| Notebook | Documento con celdas de código y texto | Archivo `.ipynb` |

Un editor no sustituye al intérprete. Tener Visual Studio Code instalado no implica que Python esté disponible. Un entorno virtual tampoco instala cualquier versión de Python: se crea a partir de un intérprete que ya existe.

Los notebooks ayudan a explorar y explicar resultados. Los scripts permiten ejecutar un flujo completo. Usaremos scripts en esta unidad para que puedas reconocer las entradas, la ejecución y las salidas. No necesitas instalar Jupyter todavía.

## 2. Obtener el curso

Elige **una** de estas rutas.

### Ruta A: descargar ZIP

1. Abre el [repositorio del curso](https://github.com/lelyliliana/Curso-Inteligencia-Artificial).
2. Selecciona **Code → Download ZIP**.
3. Extrae el archivo y abre la carpeta extraída en tu editor.
4. Abre una terminal en esa carpeta.

La carpeta extraída puede llamarse `Curso-Inteligencia-Artificial-main`. Trabaja dentro de ella, donde está el README principal. La descarga ZIP permite estudiar los archivos, pero no incluye el historial Git.

### Ruta B: clonar con Git

Si ya tienes Git instalado, comprueba su versión:

```bash
git --version
```

Después ejecuta, un comando a la vez:

```bash
git clone https://github.com/lelyliliana/Curso-Inteligencia-Artificial.git
```

```bash
cd Curso-Inteligencia-Artificial
```

Si Git no está instalado y quieres comenzar inmediatamente, utiliza la ruta ZIP. La instalación y los fundamentos de Git también se explican en el curso de Python.

### Comprobar la ubicación

En Ubuntu o macOS:

```bash
pwd
```

```bash
ls
```

En PowerShell:

```powershell
Get-Location
```

```powershell
Get-ChildItem
```

Debes ver `README.md`, `unidad00-entorno` y `datos`. Todos los comandos de ejecución de esta guía parten de esa carpeta, salvo que se indique otra ubicación.

## 3. Comprobar Python

Sigue solo la sección de tu sistema operativo.

### Ubuntu

Comprueba primero lo que tienes:

```bash
python3 --version
```

Si usas Ubuntu 24.04 y falta Python o el soporte de entornos virtuales, instala los paquetes de la distribución:

```bash
sudo apt update
```

```bash
sudo apt install python3 python3-venv
```

Confirma que la versión sea 3.12 o superior. En una distribución más antigua puede instalarse una versión anterior; ese caso requiere elegir un intérprete compatible siguiendo la guía de tu distribución. Conserva el Python del sistema en su ubicación original.

### Windows

Comprueba si existe una instalación compatible:

```powershell
python --version
```

Si dispones del lanzador `py`, también puedes comprobar una instalación de Python 3.12:

```powershell
py -3.12 --version
```

Si no tienes Python, descarga un instalador compatible desde [python.org](https://www.python.org/downloads/windows/) y sigue sus instrucciones. Abre una terminal nueva al terminar y vuelve a comprobar la versión. El lanzador y los nombres de comandos dependen de la forma de instalación; utiliza el que realmente identifique tu Python instalado.

### macOS

Comprueba:

```bash
python3 --version
```

Si falta una versión compatible, utiliza el instalador de [python.org para macOS](https://www.python.org/downloads/macos/). Abre una terminal nueva y comprueba otra vez. No supongas que el Python incluido con otras herramientas es el que debes usar para el curso.

## 4. Crear el entorno virtual

El entorno virtual separa los paquetes de este curso de los de otros proyectos. Su carpeta se llama `.venv`. El código y los datos del curso se guardan fuera de ella.

### Ubuntu y macOS

Desde la raíz del curso:

```bash
python3 -m venv .venv
```

Actívalo:

```bash
source .venv/bin/activate
```

### Windows con PowerShell

Si comprobaste Python con `python`:

```powershell
python -m venv .venv
```

Si utilizaste `py -3.12`, crea el entorno con ese mismo intérprete:

```powershell
py -3.12 -m venv .venv
```

Después actívalo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes ejecutar el intérprete directamente sin modificar políticas del equipo:

```powershell
.\.venv\Scripts\python.exe --version
```

En los demás comandos de esta guía reemplaza `python` por `.\.venv\Scripts\python.exe` cuando uses esta ruta.

### Confirmar el intérprete

Con el entorno activado:

```bash
python --version
```

```bash
python -c "import sys; print(sys.executable)"
```

La segunda orden debe mostrar una ruta dentro de `.venv`. En Windows termina normalmente en `Scripts\python.exe`; en Ubuntu o macOS, en `bin/python`.

El prefijo `(.venv)` en la terminal es una ayuda visual, pero la ruta del intérprete proporciona una comprobación más directa.

Si cierras la terminal y abres otra, vuelve a activar el entorno. Para salir del entorno activado:

```bash
deactivate
```

Cerrar el entorno no elimina tus archivos.

## 5. Paquetes: instalar cuando se necesitan

Comprueba que el gestor de paquetes pertenezca al intérprete elegido:

```bash
python -m pip --version
```

La forma `python -m pip` reduce la posibilidad de usar el `pip` de otro Python. En esta unidad no instalaremos paquetes: `csv`, `statistics` y las demás bibliotecas utilizadas forman parte de Python.

Las unidades que incorporen paquetes externos indicarán su propósito y sus dependencias. Instalar todas las bibliotecas de IA desde el comienzo ocupa espacio y dificulta diagnosticar errores.

La carpeta `.venv` se puede reconstruir. No se sube a GitHub ni se copia como mecanismo de instalación entre computadores.

## 6. Elegir el intérprete en el editor

Si utilizas Visual Studio Code:

1. Abre la carpeta del curso.
2. Instala la extensión oficial **Python**, publicada por Microsoft, si hace falta.
3. Abre la paleta de comandos y busca **Python: Select Interpreter**.
4. Selecciona el intérprete de `.venv`.
5. Abre una terminal y comprueba `sys.executable` con el comando anterior.

Si el editor y la terminal utilizan intérpretes distintos, un paquete puede estar disponible en uno y faltar en el otro. La solución es identificar ambos, no repetir instalaciones sin comprobar la ruta.

También puedes completar los ejemplos con otro editor y la terminal.

## 7. Primer ejemplo: diagnóstico

Abre [01_diagnostico.py](ejemplos/01_diagnostico.py) y ejecútalo:

```bash
python unidad00-entorno/ejemplos/01_diagnostico.py
```

Verás algo semejante a:

```text
Python: 3.12.14
Intérprete: .../.venv/bin/python
Sistema: Linux
Entorno venv: True
Python 3.12 o superior: True
Datos de práctica disponibles: True
```

La versión, el sistema y la ruta dependen de tu computador. Comprueba el significado de cada línea en lugar de esperar una copia literal de la salida.

### Cómo funciona

- `platform.python_version()` muestra la versión del intérprete en ejecución.
- `sys.executable` informa dónde está ese intérprete.
- `sys.prefix != sys.base_prefix` detecta un entorno creado con `venv`.
- `Path(__file__).resolve()` ubica el archivo del programa.
- `parents[2]` asciende desde `ejemplos` a la raíz del curso.
- `is_file()` comprueba la existencia del CSV esperado.

El programa localiza sus datos a partir de su propia ubicación. Así evita depender de una ruta absoluta particular de la autora. Si mueves solo el script sin los datos, el diagnóstico lo indicará.

### Experimenta

Ejecuta el diagnóstico con el entorno activado y luego con el Python base. Identifica qué líneas cambian. Comprueba que cambiar de intérprete no modifica por sí mismo los datos del curso.

La comprobación de `venv` no pretende identificar todos los sistemas de entornos posibles. Si ya trabajas con Conda, no interpretes automáticamente `False` como ausencia de aislamiento: aquí se estudia específicamente `venv`.

## 8. Conocer los datos antes de calcular

Lee el [diccionario y procedencia de los datos](../datos/README.md). El [CSV](../datos/consumo_sintetico.csv) contiene siete consumos diarios ficticios:

| Día | Consumo en kWh |
|---|---:|
| 1 | 12 |
| 2 | 14 |
| 3 | 15 |
| 4 | 13 |
| 5 | 18 |
| 6 | 20 |
| 7 | 16 |

La energía total es `108 kWh`. El promedio diario es `108 / 7`, aproximadamente `15,43 kWh`. El mínimo es `12 kWh` y el máximo, `20 kWh`.

Una regla de alerta utiliza un umbral: **alertar cuando el consumo diario sea mayor que 16 kWh**. Con esa definición hay dos alertas: 18 y 20. El valor 16 no cumple la condición estricta `> 16`.

Este umbral se eligió para practicar; no representa un criterio profesional de eficiencia energética. El consumo de un hogar depende de sus equipos, ocupación y condiciones de uso.

## 9. Segundo ejemplo: una línea base comprensible

Abre [02_linea_base.py](ejemplos/02_linea_base.py). Ejecuta:

```bash
python unidad00-entorno/ejemplos/02_linea_base.py
```

Resultado:

```text
Registros: 7
Total: 108.00 kWh
Promedio: 15.43 kWh
Mínimo: 12.00 kWh
Máximo: 20.00 kWh
Umbral de alerta: > 16.00 kWh
Días con alerta: 2
  2026-01-05: 18.00 kWh
  2026-01-06: 20.00 kWh
```

### Qué es una línea base

Es una solución de referencia que permite comparar otra propuesta. Para un problema de alertas podría ser una regla fija; para un pronóstico, predecir el valor observado el día anterior.

Aquí aplicamos una regla escrita por una persona. No ajustamos parámetros mediante entrenamiento, no aprendemos un patrón y no estimamos rendimiento sobre datos nuevos. Esta distinción evita atribuir aprendizaje automático a cualquier programa que procese datos.

### El recorrido del programa

1. Lee los argumentos de la terminal: archivo y umbral.
2. Abre el CSV y comprueba su esquema.
3. Convierte y valida fechas y consumos.
4. Calcula el resumen y las alertas.
5. Presenta resultados o informa un error.

`csv.DictReader` crea un diccionario por fila usando los encabezados. `float` convierte el consumo a un número decimal. `date.fromisoformat` comprueba la fecha. La biblioteca `math` permite rechazar valores no finitos; `statistics.mean` calcula el promedio.

Se rechazan consumos negativos, valores no numéricos, fechas inválidas, fechas repetidas y archivos sin lecturas. Esta es la política del ejemplo, basada en su diccionario de datos. Otro conjunto podría requerir una política distinta y justificada.

### Parámetros en lugar de cambios ocultos

Cambia el umbral:

```bash
python unidad00-entorno/ejemplos/02_linea_base.py --umbral 18
```

Solo el día con 20 kWh genera alerta. El total y el promedio permanecen iguales porque el parámetro modifica la regla, no las lecturas.

Consulta las opciones:

```bash
python unidad00-entorno/ejemplos/02_linea_base.py --help
```

Si utilizas una copia del CSV:

```bash
python unidad00-entorno/ejemplos/02_linea_base.py --datos datos/mi_consumo.csv --umbral 15
```

Ese comando requiere que hayas creado `datos/mi_consumo.csv`. La ruta suministrada mediante `--datos` se interpreta desde la carpeta actual de la terminal; la ruta predeterminada se calcula a partir del script.

### Experimenta

Antes de ejecutar, predice las alertas para umbrales 12, 15, 18 y 20. Después explica qué cambia si la condición pasa de `>` a `>=`. Conserva el archivo original y trabaja sobre una copia del programa si modificas la regla.

## 10. Reproducibilidad: dejar rastro de una ejecución

Para comprender un resultado necesitas conocer, al menos:

- Los datos utilizados y su procedencia.
- Las transformaciones realizadas.
- Los parámetros de ejecución.
- El código y su versión.
- El entorno y las dependencias.

Dos personas que reciben un número sin esas referencias pueden estar comparando procedimientos diferentes. Registrar una ejecución hace posible investigar esas diferencias.

Un resumen con datos y regla idénticos es determinista en este ejemplo. Más adelante estudiaremos semillas y fuentes de variación de los modelos. Fijar una semilla no garantiza por sí solo resultados idénticos en todo hardware y entorno.

## 11. Ejercicios

Resuélvelos antes de consultar [las soluciones](soluciones/README.md).

### Ejercicio 1 — Reconocer el entorno

Ejecuta el diagnóstico y escribe qué indican la ruta del intérprete y la línea `Entorno venv`. Explica qué harías si la terminal usara un Python diferente del seleccionado en tu editor.

### Ejercicio 2 — Predecir la salida

Sin ejecutar, calcula las alertas para umbrales 15 y 20. Comprueba después tu respuesta. Explica por qué el total no cambia.

### Ejercicio 3 — Validar un dato incorrecto

Haz una copia del CSV y reemplaza un consumo por `-2`. Ejecuta el programa contra esa copia. Describe el error, la fila señalada y la regla que se incumple. Repite con el texto `desconocido`.

### Ejercicio 4 — Cambiar una regla

En una copia del programa cambia `>` por `>=`. Usa un umbral de 16. Compara la cantidad de alertas y corrige también el texto que describe la regla para que la salida sea coherente con el código.

### Ejercicio 5 — Interpretar sin exagerar

Escribe una conclusión de dos frases sobre el archivo. Debe mencionar su carácter sintético y una limitación. No atribuyas los resultados a una comunidad ni a usuarios reales.

## 12. Reto aplicado — Registro de una ejecución

Construye un script que guarde en `resultados/resumen.json`:

- Cantidad de registros, total, promedio, mínimo y máximo.
- Umbral y días con alerta.
- Nombre del CSV y una huella SHA-256 de su contenido.
- Versión de Python y sistema operativo.

El programa debe aceptar `--datos`, `--umbral` y `--salida`. Crea el directorio de salida si no existe. Evita guardar el resultado sobre el archivo de entrada.

Una **huella SHA-256** es un identificador calculado a partir de los bytes de un archivo. Sirve para comprobar si el contenido utilizado coincide; no confirma que el archivo sea correcto, representativo o autorizado.

### Entregables

Entrega tu script y un README breve con el comando, la interpretación y las limitaciones. Si utilizaste una herramienta de IA, indica qué apoyo recibiste y cómo revisaste el resultado.

### Criterios de evaluación

| Criterio | Puntos |
|---|---:|
| Resultado correcto y regla explícita | 30 |
| Registro de datos, parámetros y entorno | 25 |
| Manejo de entradas inválidas y preservación del CSV | 20 |
| Instrucciones reproducibles | 15 |
| Interpretación y límites | 10 |

Consulta la solución de referencia después de intentar el reto:

```bash
python unidad00-entorno/soluciones/reto_registro.py
```

La solución reutiliza la validación del ejemplo y calcula la huella sobre los mismos bytes que analiza. Puedes guardar otra ejecución en un archivo distinto:

```bash
python unidad00-entorno/soluciones/reto_registro.py --umbral 18 --salida resultados/resumen_18.json
```

Cada ejecución reemplaza el archivo de salida elegido. Usa nombres diferentes si quieres conservar varios experimentos.

## 13. Errores frecuentes

| Síntoma | Causa probable | Qué comprobar |
|---|---|---|
| `python` no se reconoce | Python no está disponible con ese comando | Versión instalada y comando de tu sistema |
| Falla la creación de `.venv` en Ubuntu | Falta el soporte `python3-venv` | Paquete e intérprete utilizado |
| El editor encuentra un paquete y la terminal no | Intérpretes distintos | `sys.executable` en ambas rutas |
| No se encuentra el script | Terminal en otra carpeta | Ubicación de `README.md` y `unidad00-entorno` |
| No se encuentra el CSV personalizado | Ruta `--datos` incorrecta | Ruta relativa a la terminal |
| Encabezado incorrecto | Columnas cambiadas o CSV con otro separador | Primera línea y diccionario de datos |
| Se esperan tres alertas con umbral 16 | Se confundieron `>` y `>=` | Definición de la regla |
| Se llama IA entrenada al resumen | Se confundió cálculo con aprendizaje | Si realmente existe entrenamiento |

Si un comando falla, registra el comando completo y el mensaje. Cambia una condición por vez y vuelve a comprobar. Esto permite identificar la causa.

## 14. Qué conservar en GitHub

Conserva el código, las instrucciones, los datos de práctica permitidos y las decisiones necesarias para reproducir el trabajo.

La configuración `.gitignore` excluye el entorno virtual, archivos temporales, resultados y algunos formatos de modelos pesados. Un archivo ignorado puede seguir estando en el historial si ya fue registrado; ignorarlo no elimina una publicación previa.

Las credenciales y los datos personales requieren tratamiento aparte. Antes de compartir resultados revisa su contenido y permisos. La exclusión de un archivo mediante `.gitignore` no sustituye esa revisión.

## Checklist

- [ ] Identifico la raíz del curso y la carpeta de datos.
- [ ] Compruebo la versión y la ruta del intérprete.
- [ ] Creo y utilizo un entorno virtual.
- [ ] Ejecuto el diagnóstico y explico sus resultados.
- [ ] Calculo manualmente el total y el número de alertas.
- [ ] Cambio un umbral y explico qué permanece igual.
- [ ] Obtengo un mensaje comprensible ante un dato inválido.
- [ ] Distingo la regla fija de un modelo aprendido.
- [ ] Registro una ejecución sin modificar sus datos de entrada.
- [ ] Explico por qué los resultados sintéticos no prueban eficacia real.

## Resumen

Preparaste el entorno, localizaste los datos, ejecutaste una práctica y documentaste su resultado. El análisis produce un total de 108 kWh y dos alertas con la regla `consumo > 16`. Esa salida se entiende porque los datos, la regla y el procedimiento son explícitos.

El siguiente tema de la ruta es **qué es la inteligencia artificial**. Consulta su disponibilidad en el índice del curso.

## Referencias

- [Python 3.12: entornos virtuales](https://docs.python.org/3.12/library/venv.html).
- [Python Packaging: pip y entornos virtuales](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
- [Python 3.12: lectura de CSV](https://docs.python.org/3.12/library/csv.html).
- [Python 3.12: estadísticas](https://docs.python.org/3.12/library/statistics.html).
- [Python 3.12: huellas criptográficas](https://docs.python.org/3.12/library/hashlib.html).

[Volver al índice](../README.md)

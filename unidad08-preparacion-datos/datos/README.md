# Datos y referencias de la Unidad 8

[Volver a la unidad](../README.md)

Todos los casos son sintéticos. No se utilizan observaciones, actas ni identidades de personas u organizaciones reales. Los dos laboratorios estudian mecanismos diferentes y no deben combinarse como una evaluación predictiva.

## Fuente del Laboratorio 1

Se reutiliza directamente [lecturas_sinteticas.csv de la Unidad 7](../../unidad07-obtencion-datos/datos/lecturas_sinteticas.csv), sin modificarlo. Su [diccionario y procedencia](../../unidad07-obtencion-datos/datos/README.md) siguen vigentes: sensor-día, energía en kWh, temperatura media en °C y horas de uso.

El lector de la Unidad 7 aporta el esquema de cinco columnas y la interpretación de faltantes `NA` o cadena vacía. El programa de preparación acepta otra copia con ese mismo esquema mediante `--datos`, pero su plan de cobertura permanece fijo: S1–S3, del 1 al 4 de septiembre de 2026. Una variante fuera de ese plan se informa como tal, no amplía el denominador.

La política `preparacion-conservadora-v1` conserva ocho registros, registra una copia duplicada y aparta tres representantes para revisión. No imputa faltantes. Para un archivo sin datos pero con encabezado válido, produce salidas vacías y una cobertura de cero claves; no inventa observaciones.

## Lote de correcciones y acta

[correcciones_verificadas.json](correcciones_verificadas.json) contiene una corrección opcional ligada a la huella SHA-256 del original. Se apoya en [ACTA-SIM-001](acta_sintetica.md), una referencia adicional definida expresamente para este escenario.

| Campo | Propósito | Condición |
|---|---|---|
| sha256_origen | Identificar los bytes exactos de la fuente | Debe coincidir con la lectura actual |
| cambios | Lista de correcciones | Puede ser vacía |
| registro | Posición de la fila, desde 1 después del encabezado | Entero existente, no booleano |
| fecha, sensor_id | Comprobación de la clave | Deben coincidir con los textos originales |
| campo | Medición por corregir | consumo_kwh, temperatura_c u horas_uso |
| antes | Texto esperado antes del cambio | Coincidencia exacta |
| despues | Nuevo texto | Debe representar un valor válido, no faltante |
| evidencia | Identificador de la referencia | Texto no vacío |
| motivo | Justificación del cambio | Texto no vacío |

No se admiten claves JSON repetidas, campos extra ni correcciones repetidas sobre una misma celda. No se cambia fecha ni sensor. El lote se valida por completo antes de aplicarse a la copia.

La única corrección incluida cambia el consumo del registro 8 de `-2` a `10`. No toma valor absoluto ni calcula una estadística. El acta fija ese valor como información adicional del ejercicio. El programa comprueba correspondencia, no autenticidad de evidencias.

Con el lote, se obtienen nueve preparados, un duplicado y dos representantes en cuarentena. Los tres registros con faltantes y el conflicto de S3 siguen pendientes. La fuente conserva sus doce registros y todos sus problemas originales.

## Esquemas de salida del Laboratorio 1

| Archivo | Esquema y significado |
|---|---|
| preparados.csv | Cinco columnas originales más `registro_origen` y `campos_faltantes` |
| cuarentena.csv | Cinco columnas del representante apartado más `registro_origen` y `motivos` |
| informe.json | Política, Python, huellas, correcciones, perfiles, resultado y originales con estado final |

Cada fila de origen tiene un estado final: `preparado`, `duplicado` o `cuarentena`. Una corrección es una acción adicional sobre una celda y no un cuarto destino de fila. El balance de los tres estados debe sumar el total original.

Los faltantes numéricos se exportan vacíos en CSV y como `null` en JSON. `campos_faltantes` y `motivos` separan varios nombres con punto y coma. Las copias duplicadas se documentan en el informe, no como filas adicionales del CSV preparado.

Los CSV derivados tienen más columnas que la fuente, por lo que no son entradas directas del lector estricto de la Unidad 7. La carpeta debe ser nueva; el informe final se escribe al terminar los CSV e incluye sus huellas. Un fallo de escritura puede dejar una carpeta incompleta, que debe revisarse y no tratarse como resultado terminado.

## Fuente del Laboratorio 2

[particiones_sinteticas.json](particiones_sinteticas.json) contiene una variable, una unidad declarada y dos listas. Cada registro tiene `id` y `valor`. La unidad de observación es una medición ficticia de temperatura puntual; no se especifican dispositivo, población ni tiempo y no se derivan de los sensores diarios del otro laboratorio.

Entrenamiento: 18, 20, `null`, 22. Validación: 30, `null`, 40. La partición fue definida al diseñar el ejemplo para mostrar ajuste y aplicación; no se presenta como estrategia de muestreo de un proyecto real.

| Campo | Restricción |
|---|---|
| variable, unidad | Textos no vacíos |
| entrenamiento, validacion | Listas de registros; la validación puede estar vacía |
| id | Texto no vacío, único también entre grupos |
| valor | Número finito representable o `null`; no booleano ni texto |

El lector rechaza claves JSON repetidas y campos diferentes del esquema. El ajuste requiere valores observados y un rango no nulo en entrenamiento. Los números extremos que desborden el cálculo se rechazan con un error.

Parámetros correctos: mediana 20, mínimo 18 y máximo 22. Se utilizan para los dos grupos y no se recalculan en validación. El indicador `era_faltante` conserva si se completó un valor.

No existen etiquetas objetivo ni un modelo entrenado. Las salidas no permiten afirmar mejora de precisión. El contraste opcional de filtración calcula otros parámetros exclusivamente como contraejemplo visible; no los utiliza para los resultados exportados.

## Reproducción

Conserva versión de código, fuente, huella, lote de correcciones si se usó, política y comando. Para modificar ejemplos, crea copias. Al cambiar la fuente del primer laboratorio, un lote ligado a la huella anterior debe rechazarse: verifica de nuevo los casos antes de crear una referencia para la copia nueva.

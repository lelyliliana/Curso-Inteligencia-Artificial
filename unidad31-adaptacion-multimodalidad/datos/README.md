# Datos y procedencia

[Unidad](../README.md) · [Protocolo previo](protocolo.md) · [Generador](generar_datos.py)

Ambas colecciones se generan para el curso y no contienen datos de personas o dispositivos reales. La primera reutiliza la gramática y vocabulario propios de la Unidad 25 con objetivos recodificados; la segunda contiene imágenes y textos nuevos. No se descargaron corpus ni pesos externos. El checkpoint base pertenece al material existente del curso; no se le atribuye una licencia de un modelo de terceros.

## Adaptación textual

La combinación tema–zona–nivel define la familia. Se barajan 48 combinaciones con semilla 3100 y se asignan 24/12/12 a entrenamiento/validación/prueba antes de crear las variantes breve y detallada. Cada documento tiene ID, familia, formato, prefijo y continuación. Se conserva el vocabulario de 26 tokens de la base; ningún texto nuevo produce UNK.

- [Entrenamiento](adaptacion/entrenamiento.json): 48 documentos, 24 familias.
- [Validación](adaptacion/validacion.json): 24 documentos, 12 familias.
- [Prueba](adaptacion/prueba.json): 24 documentos, 12 familias.

La nueva salida cambia el nivel mediante bajo→alto, medio→bajo, alto→medio; los demás tokens mantienen su función. Es un código artificial y deliberadamente incompatible con el objetivo anterior para el mismo prefijo. La regla de generación no representa conocimiento de energía, ambiente ni riesgo.

La reserva se aplica al entrenamiento de adaptación, no al entrenamiento histórico de la base. Coinciden con prefijos usados al entrenar la base 36/48 documentos de entrenamiento nuevo, 16/24 de validación y 12/24 de prueba. Los objetivos nuevos no se usaron en ese entrenamiento anterior. Esta exposición se documenta para no presentar el resultado como generalización a todas las entradas inéditas.

## Imágenes con consultas

48 escenas en PNG modo `L`, 20 columnas × 16 filas. El fondo tiene intensidades 20–35. Cada luz ocupa seis filas por cinco columnas: apagada 45–55, encendida 205–215. El ruido es independiente por escena, con semilla `31000 + índice`. Los cuatro estados (00, 01, 10, 11) están equilibrados por partición.

Cada escena tiene cuatro filas: `estado izquierda`, `consulta izquierda`, `estado derecha` y `consulta derecha`. Ambas plantillas consultan el mismo significado, por lo que sus etiquetas coinciden para un lado. Los cuatro pares y el PNG permanecen en una sola partición:

| Partición | Escenas | Pares | Etiquetas 0 / 1 |
|---|---:|---:|---:|
| [Entrenamiento](multimodal/entrenamiento.json) | 24 | 96 | 48 / 48 |
| [Validación](multimodal/validacion.json) | 12 | 48 | 24 / 24 |
| [Prueba](multimodal/prueba.json) | 12 | 48 | 24 / 24 |

La etiqueta es el estado de la luz consultada, no una clase de la imagen completa. Cambiar el texto puede cambiar la etiqueta aunque el PNG sea idéntico. Un archivo válido mal emparejado puede producir una supervisión incorrecta. El nombre del archivo y la etiqueta no se utilizan como características del modelo.

Estas intensidades y posiciones separan mucho las clases: es un experimento construido para estudiar complementariedad y ablación, no un benchmark de visión real. No hay oclusión, perspectiva, fotografía, texto dentro de los píxeles ni OCR.

## Regenerar sin tocar los originales

```bash
python unidad31-adaptacion-multimodalidad/datos/generar_datos.py --salida resultados/u31-datos
```

Las pruebas comparan los JSON y PNG regenerados con los incluidos. El generador usa el entorno numérico y Pillow fijados; otras versiones de un codificador PNG podrían cambiar los bytes aun conservando píxeles. Los estados guardados conservan hashes de los archivos utilizados en desarrollo y el cierre añade los de prueba. Ningún hash sustituye la revisión de la procedencia.

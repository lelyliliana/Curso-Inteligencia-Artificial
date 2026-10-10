# Datos e imágenes — Unidad 21

[Unidad](../README.md) · [Protocolo](protocolo.md) · [Generador](generar_datos.py)

Imágenes sintéticas propias del curso, creadas por código el 10 de octubre de 2026. No se descargaron datasets o fotografías ni se incluyeron personas, marcas o datos personales. No se reutilizan datos de cierre de unidades anteriores.

**Procedencia y licencia:** este conjunto se genera íntegramente con el código del repositorio y no incorpora imágenes sujetas a una licencia de terceros. En esta revisión el repositorio no declara una licencia general mediante un archivo de licencia; esta unidad no introduce ni modifica esa decisión. La procedencia original queda documentada sin atribuir al conjunto una licencia externa.

## Imagen para estudiar canales

[`colores.png`](colores.png) es RGB de 24×24. Para fila f y columna c: R=10c, G=10f y B=230 en las columnas 8 a 15, o B=30 en las demás. Es un ejemplo de valores y canales, sin etiqueta ni participación en el entrenamiento.

## Clasificación de trazos

| Manifiesto | Escenas | Vistas | Imágenes por clase | Semilla PCG64 |
|---|---:|---:|---:|---:|
| [entrenamiento.csv](entrenamiento.csv) | 60 | 120 | 40 | 20262101 |
| [validacion.csv](validacion.csv) | 30 | 60 | 20 | 20262102 |
| [prueba.csv](prueba.csv) | 30 | 60 | 20 | 20262103 |

Las imágenes están en [imagenes/](imagenes). Cada PNG es L, uint8, 16×16. La clase 0 es horizontal; 1, vertical; 2, diagonal en cualquiera de las dos inclinaciones. No se modelan otras orientaciones, varios objetos o fondos naturales.

| Campo del manifiesto | Significado |
|---|---|
| imagen_id | ID único de una vista, con sufijo v0 o v1 |
| escena_id | Origen compartido por dos vistas; unidad de separación |
| archivo | Ruta relativa a un PNG dentro de imagenes/ |
| clase | 0, 1 o 2; clase de la escena original |
| sha256 | Huella de los bytes PNG incluidos |

Los IDs y rutas son metadatos para trazabilidad. No se pasan como entradas al clasificador. El código añade una huella de los píxeles descomprimidos al informe para detectar duplicados exactos aun si cambian nombre o codificación.

## Cómo se generan

Cada partición tiene su generador NumPy PCG64. La clase de escena i es `i % 3`, por lo que las tres clases tienen el mismo soporte. Para cada escena:

1. Elegir longitud entre 6 y 10, grosor 1 o 2 y coordenadas centrales entre 5 y 10. Dibujar un trazo horizontal, vertical o diagonal; para diagonal, elegir una de las dos inclinaciones.
2. Elegir intensidad de fondo entre 15 y 50 e intensidad del trazo entre 150 y 240, ambas enteras.
3. Añadir textura gaussiana de desviación 7 a la escena, compartida por sus vistas.
4. Crear dos vistas añadiendo ruido gaussiano independiente de desviación 9. En v1, cubrir un cuadrado 4×4 de posición aleatoria con el valor del fondo.
5. Redondear al entero más cercano, limitar a [0,255] y guardar como PNG L.

El orden de extracciones forma parte del generador. Se asignan escenas a particiones **antes** de crear vistas; nunca se reparte cada PNG por separado. Las dos vistas comparten geometría y textura, de modo que no son observaciones independientes. Una oclusión puede eliminar gran parte del trazo: la etiqueta se conserva como clase de origen, aunque la vista aislada sea ambigua. Esa limitación forma parte del análisis y no se corrige mirando resultados del modelo.

## Validaciones y reproducción

El lector exige esquema completo, clase válida, IDs únicos, clase consistente por escena, ruta dentro de imagenes/, huella PNG correcta, resolución y modo previstos. Rechaza píxeles idénticos dentro de una partición; la comprobación entre particiones rechaza IDs, escenas o huellas de píxeles compartidos. No pretende resolver detección general de casi duplicados.

```bash
python unidad21-vision-computador/datos/generar_datos.py --salida resultados/u21-datos-regenerados
```

Ejecuta desde la raíz con las dependencias instaladas y una carpeta nueva. Se generan 241 PNG y tres manifiestos. La prueba de reproducción compara bytes en el entorno registrado, incluida la versión de Pillow: otra codificación PNG podría producir bytes diferentes para los mismos píxeles.

La ejecución normal lee solo los manifiestos e imágenes de entrenamiento y validación; no inspecciona ni calcula huellas de prueba. Los datos y sus resultados son públicos, así que el cierre sirve como demostración del procedimiento, no como reserva desconocida para futuros ajustes informados por ellos.

# Figuras y reproducción

[Volver a la unidad](../README.md)

Las figuras se generan con Matplotlib a partir de los mismos datos y funciones de los laboratorios. Se publican en PNG para lectura y SVG para ampliación. Se revisaron etiquetas, acentos, leyendas, unidades, ceros, huecos y escalas comparables.

| Figura | Datos y parámetros | Resumen asociado |
|---|---|---|
| [Lecturas PNG](lecturas/lecturas.png) · [SVG](lecturas/lecturas.svg) | Preparación conservadora de la Unidad 8, sin corrección ni imputación | [JSON con trazabilidad](lecturas/resumen.json) |
| [Distribuciones PNG](grupos/distribuciones.png) · [SVG](grupos/distribuciones.svg) | 48 casos sintéticos, ocho intervalos de igual ancho, cajas con regla 1.5 × RIC | [JSON con bordes y conteos](grupos/resumen.json) |
| [Relaciones PNG](grupos/relaciones.png) · [SVG](grupos/relaciones.svg) | Los mismos 48 pares, globales y separados por grupo, escalas compartidas | [JSON con correlaciones](grupos/resumen.json) |

Entorno comprobado: Python 3.12.3 en Linux, Matplotlib 3.10.8 y NumPy 2.2.6. [entorno-verificado.txt](entorno-verificado.txt) registra todos los paquetes del entorno virtual limpio usado. Los JSON anotan las versiones principales de cada exportación.

Desde la raíz, con destinos nuevos:

```bash
python -m pip install -r unidad09-exploracion-visualizacion/requirements.txt
python unidad09-exploracion-visualizacion/ejemplos/01_explorar_lecturas.py --salida resultados/unidad09/reproduccion-lecturas
python unidad09-exploracion-visualizacion/ejemplos/02_explorar_grupos.py --salida resultados/unidad09/reproduccion-grupos
```

Para instalar además las mismas versiones transitivas, en un entorno virtual nuevo con Python 3.12:

```bash
python -m pip install -r unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt
```

No se usan ventanas, GPU, servicios externos ni fuentes descargadas. La tipografía es DejaVu Sans distribuida con Matplotlib. Los puntos junto a las cajas tienen desplazamiento horizontal fijo; no se aplica ruido a los consumos.

Para comparar resultados, revisa primero las huellas, los números y los parámetros. Cambios de biblioteca, sistema o renderizador pueden alterar bytes o detalles de una imagen sin cambiar el análisis. Las pruebas no exigen igualdad binaria de los gráficos.

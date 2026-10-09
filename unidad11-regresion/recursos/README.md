# Recursos reproducibles de regresión

[Volver a la unidad](../README.md)

Estas figuras, tablas e informes se generaron con los datos publicados y el protocolo `regresion-v1`, usando Python 3.12.3, NumPy 2.2.6 y Matplotlib 3.10.8. Se reutilizó el [entorno verificado de la Unidad 9](../../unidad09-exploracion-visualizacion/recursos/entorno-verificado.txt). Las versiones principales constan en cada JSON.

| Recurso | Imagen | Vector | Evidencia |
|---|---|---|---|
| Recta, constante y residuos lineales | [PNG](lineal/recta_residuos.png) | [SVG](lineal/recta_residuos.svg) | [Informe lineal](lineal/informe.json) |
| Curvas y errores por complejidad | [PNG](curva/complejidad.png) | [SVG](curva/complejidad.svg) | [Informe curvo](curva/informe.json) |
| Residuos de tres modelos con escala común | [PNG](curva/residuos.png) | [SVG](curva/residuos.svg) | [Informe curvo](curva/informe.json) |

Predicciones completas:

- Lineal: [entrenamiento](lineal/predicciones_entrenamiento.csv) y [validación](lineal/predicciones_validacion.csv).
- Curva: [entrenamiento](curva/predicciones_entrenamiento.csv) y [validación](curva/predicciones_validacion.csv).

Los informes publicados tienen `prueba: null`: se generaron sin leer prueba. Las imágenes muestran entrenamiento y validación, con leyendas, unidades y estilos que acompañan los colores. En la comparación de MAE las barras parten de cero; los tres paneles de residuos curvos comparten límites verticales. No se ocultan predicciones negativas. Las imágenes se revisaron visualmente y las pruebas comprueban sus valores, puntos, escalas y archivos.

## Regenerar

Desde la raíz, con dependencias instaladas y carpetas de salida nuevas:

```bash
python unidad11-regresion/ejemplos/01_ajustar_recta.py --salida resultados/unidad11/figuras-lineal --graficos
python unidad11-regresion/ejemplos/02_comparar_complejidad.py --salida resultados/unidad11/figuras-curva --graficos
```

El renderizador [figuras.py](../ejemplos/figuras.py) usa las predicciones y los modelos del informe; no vuelve a entrenar ni consulta prueba. Si se añade `--evaluar-prueba`, se exportan su tabla y métricas, pero las figuras siguen mostrando solo el desarrollo. El JSON se escribe antes de los gráficos, por lo que no demuestra por sí solo que una exportación gráfica haya terminado.

Cada informe conserva nombres y huellas SHA-256 de los CSV leídos, criterios, coeficientes y escalas. Las tablas de desarrollo incluyen todos los candidatos: lineal tiene 72 filas de entrenamiento y 36 de validación; curva tiene 50 y 45 respectivamente, sin contar cabeceras. No confundir cantidad de predicciones con número de casos distintos.

Las salidas numéricas pueden presentar diferencias mínimas de punto flotante entre plataformas. Los archivos de datos sí tienen una regeneración byte por byte comprobada. La apariencia exacta de una figura puede depender del renderizador y del entorno; el código fija estilo, fuente, tamaños y metadatos relevantes, pero no promete identidad binaria entre sistemas distintos.

# Recursos reproducibles de árboles y ensambles

[Volver a la unidad](../README.md)

Se generaron con Python 3.12.3, scikit-learn 1.9.1, NumPy 2.2.6, SciPy 1.18.1 y Matplotlib 3.10.8, bajo `arboles-v1` y semilla de modelos 13. El [registro completo del entorno](entorno-verificado.txt) conserva las dependencias instaladas en el entorno virtual limpio usado para la verificación.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Complejidad, probabilidades y F1 | [PNG](franja/complejidad.png) | [SVG](franja/complejidad.svg) | [Franja](franja/informe.json) |
| Árbol controlado completo | [PNG](franja/arbol_controlado.png) | [SVG](franja/arbol_controlado.svg) | [Franja](franja/informe.json) |
| Probabilidades y fronteras de tres modelos | [PNG](region/fronteras.png) | [SVG](region/fronteras.svg) | [Región](region/informe.json) |

Predicciones por caso:

- Franja: [entrenamiento](franja/predicciones_entrenamiento.csv) y [validación](franja/predicciones_validacion.csv).
- Región: [entrenamiento](region/predicciones_entrenamiento.csv) y [validación](region/predicciones_validacion.csv).

Reglas de árboles individuales:

- Franja: [profundidad 1](franja/reglas_arbol_1.txt), [controlado](franja/reglas_arbol_3.txt) y [sin límite](franja/reglas_arbol_libre.txt).
- Región: [árbol individual](region/reglas_arbol.txt).

Los dos informes publicados tienen `prueba: null`, sin huella ni predicciones de prueba. Cada experimento contiene cuatro candidatos: franja exporta 320 predicciones de entrenamiento y 160 de validación; región exporta 720 y 480. Esos números cuentan filas candidato-caso, no observaciones distintas.

Cada CSV conserva identificador, entradas, etiqueta real, probabilidad positiva, clase predicha, resultado VP/VN/FP/FN y marca fuera de rango. En JSON una métrica indefinida es `null`. Las reglas impresas tienen cortes redondeados; las huellas de estructura no son una serialización del modelo.

## Lectura de figuras

Las curvas de franja muestran probabilidades aprendidas dentro del rango de entrenamiento y cruces con etiquetas de validación. Las barras de F1 parten de cero y comparan entrenamiento con validación para los cuatro candidatos. El árbol representa los trece nodos del candidato controlado, todos aprendidos con entrenamiento: `value` muestra conteos por clase; `samples`, cantidad de casos.

Los mapas de región comparten escala de probabilidad de 0 a 1, límites de ejes y los mismos 120 casos de validación. El contorno blanco es el nivel 0,5. El fondo ocupa exactamente el rectángulo delimitado por los rangos marginales de entrenamiento, sin afirmar cobertura de toda combinación interior ni calibración.

Las tres figuras fueron revisadas visualmente. Las pruebas comprueban barras, etiquetas, cantidad de nodos, casos por panel, escala de color y límites del fondo. También comprueban que las figuras de una ejecución de cierre continúen mostrando exclusivamente desarrollo.

## Regenerar

Desde la raíz, con dependencias instaladas y carpetas nuevas:

```bash
python unidad13-arboles-ensambles/ejemplos/01_controlar_complejidad.py --salida resultados/unidad13/figuras-franja --graficos
python unidad13-arboles-ensambles/ejemplos/02_comparar_ensambles.py --salida resultados/unidad13/figuras-region --graficos
```

[figuras.py](../ejemplos/figuras.py) utiliza los modelos ajustados y el informe en memoria; no vuelve a entrenar ni consulta prueba. Los CSV y el JSON se guardan antes de las figuras: una exportación puede quedar parcial si se produce un error.

Se fijan estilo, fuente, tamaño y metadatos de dibujo. Diferencias de plataforma o bibliotecas pueden cambiar números o renderizado; no se promete identidad binaria entre sistemas. Los seis CSV de datos se regeneran exactamente en el entorno verificado. Conserva también el commit y el comando, porque el informe no los obtiene automáticamente.

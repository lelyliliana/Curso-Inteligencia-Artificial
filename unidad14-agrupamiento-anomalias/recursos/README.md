# Recursos reproducibles

[Volver a la unidad](../README.md)

Generados con Python 3.12.3, scikit-learn 1.9.1, NumPy 2.2.6, SciPy 1.18.1 y Matplotlib 3.10.8. Se reutilizó el [registro completo del entorno de la Unidad 13](../../unidad13-arboles-ensambles/recursos/entorno-verificado.txt) para preparar un entorno virtual limpio; no se añadieron dependencias. Protocolo `no-supervisado-v1`, semilla principal 14.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Asignaciones y centros para k=2,3,4 | [PNG](grupos/grupos.png) | [SVG](grupos/grupos.svg) | [Grupos](grupos/informe.json) |
| Inercia de entrenamiento y silueta de validación | [PNG](grupos/diagnosticos.png) | [SVG](grupos/diagnosticos.svg) | [Grupos](grupos/informe.json) |
| Regiones de alerta y puntuaciones ordenadas | [PNG](anomalias/alertas.png) | [SVG](anomalias/alertas.svg) | [Anomalías](anomalias/informe.json) |

Tablas por caso:

- Grupos: [entrenamiento](grupos/predicciones_entrenamiento.csv) y [validación](grupos/predicciones_validacion.csv).
- Anomalías: [entrenamiento](anomalias/predicciones_entrenamiento.csv), [calibración](anomalias/predicciones_calibracion.csv) y [validación](anomalias/predicciones_validacion.csv).

Los informes publicados conservan `prueba: null` y no incluyen huella ni predicciones de prueba. Grupos contiene tres candidatos: 270 filas de entrenamiento y 180 de validación. Anomalías contiene tres: 360 de entrenamiento, 180 de calibración y 240 de validación. Son registros candidato-caso, no observaciones distintas.

Una puntuación o umbral ausente en `sin_alertas` se representa como celda vacía en CSV y `null` en JSON; no significa cero. Entrenamiento y calibración de anomalías no tienen etiquetas reales ni métricas de clasificación atribuidas. Los identificadores de grupo son arbitrarios.

## Lectura y revisión

La primera figura conserva los mismos 60 casos de validación en tres paneles, con centros aprendidos sobre entrenamiento y devueltos a unidades originales. Los colores no se alinean por significado entre paneles. La segunda separa inercia de ajuste y silueta de selección; la escala de silueta muestra su intervalo de −1 a 1 y las barras parten de cero.

La figura de alertas muestra los mismos 80 casos de validación sobre las reglas de ambos detectores. El fondo naranja es alerta; el gris, ausencia de alerta. La rejilla ilustra la regla en el dominio 0–100, incluso fuera de los rangos aprendidos, sin afirmar cobertura. Abajo se ordenan puntuaciones y se superpone el umbral fijado en calibración. Las escalas de puntuación son diferentes y no expresan probabilidades.

Las tres figuras se revisaron visualmente. Las pruebas comprueban puntos, centros, barras, puntuaciones ordenadas y umbrales, incluso al construirlas desde un informe que contiene cierre: siguen mostrando desarrollo.

## Regeneración

Desde la raíz con dependencias instaladas y carpetas nuevas:

```bash
python unidad14-agrupamiento-anomalias/ejemplos/01_agrupar_perfiles.py --salida resultados/unidad14/figuras-grupos --graficos
python unidad14-agrupamiento-anomalias/ejemplos/02_detectar_anomalias.py --salida resultados/unidad14/figuras-anomalias --graficos
```

[figuras.py](../ejemplos/figuras.py) utiliza el informe y el ajuste existentes; no vuelve a entrenar ni lee prueba. Los CSV y el JSON se escriben antes de los gráficos, por lo que una escritura fallida puede dejar salida parcial.

Se fijan fuente, estilo, tamaño y metadatos de salida. No se promete identidad binaria de imágenes entre plataformas. Los siete CSV de entrada sí se reproducen exactamente en el entorno declarado. Conserva commit y comandos junto a tus exportaciones: no se incorporan automáticamente al JSON.

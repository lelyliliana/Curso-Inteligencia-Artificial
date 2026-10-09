# Recursos reproducibles de validación

[Unidad](../README.md)

Generados con Python 3.12.3, scikit-learn 1.9.1, NumPy 2.2.6, SciPy 1.18.1 y Matplotlib 3.10.8. Se reutilizó el entorno de la entrega anterior con las dependencias registradas en la [Unidad 13](../../unidad13-arboles-ensambles/recursos/entorno-verificado.txt). Protocolo `validacion-cv-v1`, semilla 16 para KFold y ausencia de barajado en GroupKFold.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Búsqueda en ciclos | [PNG](ciclos/busqueda.png) | [SVG](ciclos/busqueda.svg) | [Ciclos](ciclos/informe.json) |
| Mapa de particiones | [PNG](equipos/particiones.png) | [SVG](equipos/particiones.svg) | [Equipos](equipos/informe.json) |
| Selección y diagnóstico de equipos | [PNG](equipos/comparacion.png) | [SVG](equipos/comparacion.svg) | [Equipos](equipos/informe.json) |

Predicciones:

- [OOF de ciclos](ciclos/predicciones_oof.csv): 1120 filas candidato-caso, siete candidatos × 160 observaciones.
- [OOF de equipos](equipos/predicciones_oof.csv): 1008 filas candidato-caso, siete candidatos × 144 observaciones.
- [Diagnóstico por filas de equipos](equipos/diagnostico_filas_oof.csv): 144 predicciones del candidato fijo `knn3_uniform`, separado de la comparación que selecciona.

Los informes publicados tienen `prueba: null` y solo huella de desarrollo. Conservan el resumen del reajuste del elegido, ejecutado con todo desarrollo después de CV, pero no serializan sus observaciones internas. Las predicciones OOF proceden de los modelos de pliegue, no de ese modelo reajustado. Utiliza `caso_id` para recuperar las entradas del CSV fuente.

## Lectura y revisión

Las tres figuras se revisaron visualmente. En búsqueda, barras horizontales representan medias y puntos representan los cuatro MAE. El elegido aparece verde; los segmentos muestran más y menos una desviación con divisor cuatro. No son intervalos de confianza y los ejes parten de cero.

El mapa representa los mismos 144 casos en orden de archivo. Cada columna valida una vez por esquema. Los límites blancos marcan equipos; GroupKFold mantiene sus filas juntas. El mapa es válido para estos CSV, donde los equipos aparecen en bloques contiguos.

El gráfico de equipos distingue selección por grupos, a la izquierda, y diagnóstico del mismo candidato fijo con dos esquemas, a la derecha. Ambas barras del diagnóstico parten de cero. No compara un candidato por filas con otro distinto por equipos.

[figuras.py](../ejemplos/figuras.py) toma los valores del informe sin ajustar modelos ni leer prueba. Las pruebas contrastan alturas y anchos, puntos, índices coloreados, candidato y fuente de datos. Aun con un informe de cierre, solo grafica desarrollo.

## Regeneración

Desde la raíz, en carpetas nuevas:

```bash
python unidad16-validacion-hiperparametros/ejemplos/01_ajustar_con_cv.py --salida resultados/unidad16/figuras-ciclos --graficos
python unidad16-validacion-hiperparametros/ejemplos/02_validar_por_equipos.py --salida resultados/unidad16/figuras-equipos --graficos
```

JSON y CSV se escriben antes que los gráficos; una exportación fallida puede quedar parcial. Se fijan estilo, fuente y metadatos, sin prometer identidad binaria de imágenes entre plataformas. Los CSV de entrada sí se reproducen exactamente en el entorno declarado. Conserva commit y comandos aparte: no se guardan automáticamente en el JSON.

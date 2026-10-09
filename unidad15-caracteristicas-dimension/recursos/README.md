# Recursos reproducibles de representaciones

[Unidad](../README.md)

Se generaron con Python 3.12.3, scikit-learn 1.9.1, NumPy 2.2.6, SciPy 1.18.1 y Matplotlib 3.10.8. Se reutilizan las dependencias del [entorno verificado de la Unidad 13](../../unidad13-arboles-ensambles/recursos/entorno-verificado.txt), también utilizado en la Unidad 14. Protocolo `representaciones-v1`; ajuste sin muestreo ni inicialización aleatoria.

| Figura | Imagen | Vector | Informe |
|---|---|---|---|
| Consumo real y predicho | [PNG](interaccion/caracteristicas.png) | [SVG](interaccion/caracteristicas.svg) | [Interacción](interaccion/informe.json) |
| Proyección y coordenadas | [PNG](pca/proyeccion.png) | [SVG](pca/proyeccion.svg) | [PCA](pca/informe.json) |
| Varianza, reconstrucción y predicción | [PNG](pca/compromiso.png) | [SVG](pca/compromiso.svg) | [PCA](pca/informe.json) |

Predicciones por caso:

- Interacción: [entrenamiento](interaccion/predicciones_entrenamiento.csv) y [validación](interaccion/predicciones_validacion.csv).
- PCA: [entrenamiento](pca/predicciones_entrenamiento.csv) y [validación](pca/predicciones_validacion.csv).

Los informes publicados tienen `prueba: null`, sin huellas ni predicciones de prueba. Interacción incluye tres candidatos, 288 filas candidato-caso de entrenamiento y 144 de validación. PCA incluye cuatro, 384 y 192 respectivamente. Cada laboratorio tiene 96 y 48 observaciones distintas en esos conjuntos.

El JSON conserva las coordenadas y reconstrucciones en `representaciones` para los candidatos correspondientes de PCA, además de parámetros completos. Para `completa`, las coordenadas son z; para `pca1` y `pca2`, coordenadas en sus propios ejes. La referencia mediana no reconstruye y conserva métricas `null`. Los CSV de predicción no incluyen la lectura posterior excluida.

## Lectura y revisión visual

La figura de consumo conserva los mismos 48 casos de validación en ambos paneles y usa límites iguales para comparar reales y predicciones. La diagonal representa coincidencia perfecta, no una nueva recta ajustada.

La proyección muestra señales originales, reconstrucción con un componente y coordenadas de dos componentes. Los colores representan el objetivo real de validación con la misma escala en ambos paneles. Se utiliza para interpretar el resultado; no interviene en el ajuste de PCA. El panel derecho amplía visualmente la dirección pequeña: sus escalas de ejes son diferentes y están indicadas.

La tercera figura separa varianza de entrenamiento, reconstrucción de validación y MAE predictivo de validación. Las barras parten de cero. El pequeño error de reconstrucción con dos componentes es numérico, no un resultado de predicción perfecta.

Las tres figuras fueron revisadas visualmente. Las pruebas contrastan posiciones, colores, segmentos de reconstrucción, alturas de barras y conjuntos utilizados, también al partir de un informe con cierre: solo muestran desarrollo.

## Regeneración

Desde la raíz, con dependencias instaladas y destinos nuevos:

```bash
python unidad15-caracteristicas-dimension/ejemplos/01_construir_caracteristicas.py --salida resultados/unidad15/figuras-interaccion --graficos
python unidad15-caracteristicas-dimension/ejemplos/02_comparar_pca.py --salida resultados/unidad15/figuras-pca --graficos
```

[figuras.py](../ejemplos/figuras.py) utiliza resultados del informe sin volver a ajustar ni leer prueba. El JSON y los CSV se escriben antes de los gráficos: una salida puede quedar parcial si falla una escritura o el renderizado.

Se fijan fuente, estilo, tamaños y metadatos. No se promete identidad binaria de imágenes o cálculos entre plataformas distintas. Los seis CSV de entrada sí se regeneran exactamente en el entorno declarado. Conserva el commit y los comandos junto a los archivos: no se obtienen automáticamente en el informe.

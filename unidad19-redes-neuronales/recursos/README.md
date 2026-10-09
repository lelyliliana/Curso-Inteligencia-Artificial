# Recursos de la Unidad 19

[Unidad](../README.md) · [Ficha de límites](ficha_red.md)

Los recursos se generaron con el protocolo oficial en modo de **desarrollo**. `prueba` es null y no se conserva su huella porque no se abrió el archivo. Los cierres didácticos se documentan en las soluciones y se reproducen con `--evaluar-prueba`.

| Laboratorio | Informe | Predicciones |
|---|---|---|
| XOR | [JSON](xor/informe.json) | [Entrenamiento](xor/predicciones_entrenamiento.csv), [validación](xor/predicciones_validacion.csv) |
| Ruido | [JSON](ruido/informe.json) | [Entrenamiento](ruido/predicciones_entrenamiento.csv), [validación](ruido/predicciones_validacion.csv) |

Cada informe incluye huellas SHA-256, versiones, escala de entrenamiento, presupuestos, estados iniciales/finales/elegidos, historial de pérdidas, número de parámetros, métricas y selección. La referencia constante carece de trayectoria de optimización. `parametros` siempre identifica el punto elegido de cada candidato, que puede diferir de `parametros_finales`.

Los CSV incluyen candidato, ID, etiqueta, logit, probabilidad y decisión. Son predicciones del punto elegido de cada candidato. No confundirlas con predicciones de la última época. El formato JSON es un registro legible y permite reproducir inferencia con el código; no se carga ningún pickle ni modelo remoto.

## Figuras revisadas

- XOR, curvas: [PNG](xor/aprendizaje.png) · [SVG](xor/aprendizaje.svg).
- XOR, fronteras y muestras de validación: [PNG](xor/fronteras.png) · [SVG](xor/fronteras.svg).
- Ruido, curvas y época elegida: [PNG](ruido/curvas.png) · [SVG](ruido/curvas.svg).

Se inspeccionaron las tres figuras: títulos, ejes, leyendas y anotaciones legibles, sin recortes. Las pruebas contrastan líneas con historiales, puntos con validación y valores de la malla con una propagación escalar independiente. Las curvas muestran BCE **sin L2** en ambas particiones; la línea vertical señala la época seleccionada. No son intervalos de incertidumbre ni muestran resultados de prueba.

El mapa usa una malla de 121×121 en [−1,1]², con el escalado aprendido. Sus zonas sin ejemplos siguen teniendo color porque el modelo produce una salida allí; eso no valida sus predicciones. La referencia logística elegida tiene p=0,5 constante y no se dibuja una frontera única en ese panel.

## Reproducir

Desde la raíz, con dependencias instaladas y carpetas nuevas:

```bash
python unidad19-redes-neuronales/ejemplos/01_aprender_xor.py --salida resultados/u19-xor-reproduccion --graficos
python unidad19-redes-neuronales/ejemplos/02_controlar_sobreajuste.py --salida resultados/u19-ruido-reproduccion --graficos
```

No se sobrescriben carpetas existentes. Matplotlib se registra cuando se piden figuras. El ajuste limita a uno los hilos de bibliotecas numéricas con `threadpool_limits(1)`. El entorno probado está enlazado desde la unidad; reproducibilidad con una semilla fija no equivale a estabilidad estadística entre semillas o a igualdad bit a bit entre plataformas y versiones diferentes.

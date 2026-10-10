# Recursos reproducibles — Unidad 21

[Unidad](../README.md) · [Ficha completada](ficha_modelo.md)

Generados y revisados el 10 de octubre de 2026 en CPU. Se reutilizó el [entorno de la Unidad 20](../../unidad20-pytorch/recursos/entorno-verificado.txt), sin añadir paquetes: PyTorch 2.14.1+cpu, NumPy 2.2.6, Matplotlib 3.10.8 y Pillow 12.3.0. Las tres figuras PNG se revisaron visualmente; sus versiones SVG se generan del mismo objeto gráfico.

## Píxeles y filtros

- [Informe numérico con RGB, gris, respuestas y cálculo manual](filtros/informe.json).
- Canales y filtros: [PNG](filtros/pixeles_filtros.png) y [SVG](filtros/pixeles_filtros.svg).

La figura mantiene la escala de intensidades, muestra respuestas Sobel con signo y separa los filtros fijos del caso manual. No entrena un modelo ni evalúa generalización.

## Clasificación de trazos

- [Informe de desarrollo con fuentes, preparación, estados y métricas](trazos/informe.json).
- [Predicciones de entrenamiento](trazos/predicciones_entrenamiento.csv) y [validación](trazos/predicciones_validacion.csv).
- [Resultado de la recarga](trazos/recarga.json).
- Aprendizaje y matriz: [PNG](trazos/aprendizaje_matriz.png) y [SVG](trazos/aprendizaje_matriz.svg).
- Casos difíciles: [PNG](trazos/casos_dificiles.png) y [SVG](trazos/casos_dificiles.svg).

El informe tiene `prueba=null` y solo contiene huellas e imágenes de desarrollo. Las figuras se construyen desde él sin abrir prueba. La galería ordena las 60 vistas de validación por probabilidad de la clase real ascendente, con desempate por ID, y muestra las primeras ocho. No se eligen imágenes para ocultar errores o aparentar una muestra representativa.

Los píxeles originales de validación quedan en el informe para reconstruir la galería, con escala visual fija 0–255. Los estados se guardan como listas legibles. El archivo binario `modelo.pt` está excluido del control de versiones y se genera con los comandos siguientes:

```bash
python unidad21-vision-computador/ejemplos/01_explorar_pixeles.py --salida resultados/u21-filtros --graficos
python unidad21-vision-computador/ejemplos/02_clasificar_trazos.py --salida resultados/u21-trazos --graficos
```

Desde la raíz, con carpetas nuevas. La exportación de clasificación guarda y carga el modelo seleccionado y comprueba que el mayor cambio en logits sea 0,0. `recarga.json` conserva la huella del binario local original; otra serialización puede producir bytes diferentes sin cambiar predicciones. Se comprueba inferencia en este entorno, no reanudación de Adam ni identidad en plataformas distintas.

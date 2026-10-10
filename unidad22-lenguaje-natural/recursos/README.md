# Recursos reproducibles — Unidad 22

[Unidad](../README.md) · [Ficha del modelo](ficha_modelo.md)

Generados y revisados el 10 de octubre de 2026, reutilizando el [entorno registrado de la Unidad 20](../../unidad20-pytorch/recursos/entorno-verificado.txt). Esta práctica usa Python 3.12.3, NumPy 2.2.6, scikit-learn 1.9.1 y Matplotlib 3.10.8; no importa PyTorch. No se instalaron paquetes nuevos.

## Representación manual

- [Informe con conteos, frecuencias documentales, IDF y TF-IDF](representacion/informe.json).
- Figura de conteos y representación: [PNG](representacion/representacion.png) y [SVG](representacion/representacion.svg).

## Clasificación

- [Informe de desarrollo](mensajes/informe.json): versiones, huellas de desarrollo, tres estados, métricas y diagnósticos; `prueba=null`.
- [Modelo elegido](mensajes/modelo.json): estado legible para inferencia, sin archivo pickle.
- [Recarga verificada](mensajes/recarga.json): error y huella del modelo.
- [Predicciones de entrenamiento](mensajes/predicciones_entrenamiento.csv) y [validación](mensajes/predicciones_validacion.csv).
- Comparación y matriz: [PNG](mensajes/comparacion_matriz.png) y [SVG](mensajes/comparacion_matriz.svg).
- Diagnósticos: [PNG](mensajes/diagnosticos.png) y [SVG](mensajes/diagnosticos.svg).
- [Resumen separado del cierre](mensajes/cierre.json): métricas del único elegido, huellas y confirmación de ausencia de reajuste.

Las tres figuras se revisaron visualmente. Se generan desde informes sin ajustar modelos; las figuras de clasificación muestran validación y diagnósticos, incluso cuando se exporta una ejecución con cierre. La selección no se modifica para hacer más favorable el gráfico.

Desde la raíz y usando carpetas nuevas:

```bash
python unidad22-lenguaje-natural/ejemplos/01_representar_textos.py --salida resultados/u22-representacion --graficos
python unidad22-lenguaje-natural/ejemplos/02_clasificar_mensajes.py --salida resultados/u22-mensajes --graficos
python unidad22-lenguaje-natural/ejemplos/02_clasificar_mensajes.py --evaluar-prueba --salida resultados/u22-cierre-nuevo --graficos
```

La última ejecución genera, además, `cierre.json` y `predicciones_prueba.csv`. Su informe completo contiene prueba; el informe publicado de desarrollo se conserva separado. El `modelo_sha256` del resumen de cierre coincide con el modelo publicado de desarrollo: abrir prueba no cambia el estado. No se añaden predicciones de los candidatos descartados en prueba.

Una nueva ejecución en el mismo entorno debe conservar métricas y probabilidades; los metadatos internos de PNG/SVG pueden producir bytes distintos. Las exportaciones rechazan carpetas existentes para evitar reemplazar resultados por accidente.

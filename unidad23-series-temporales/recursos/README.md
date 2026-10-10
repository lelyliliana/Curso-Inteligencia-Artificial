# Recursos reproducibles — Unidad 23

[Unidad](../README.md) · [Ficha del predictor](ficha_modelo.md)

Generados y revisados el 10 de octubre de 2026. Se reutilizó el [entorno de la Unidad 20](../../unidad20-pytorch/recursos/entorno-verificado.txt), sin instalar paquetes: Python 3.12.3, NumPy 2.2.6, scikit-learn 1.9.1 y Matplotlib 3.10.8. Esta unidad no necesita PyTorch.

## Auditoría temporal

- [Informe de la muestra](auditoria/informe.json).
- Evento y disponibilidad: [PNG](auditoria/disponibilidad.png) y [SVG](auditoria/disponibilidad.svg).

El panel retrospectivo muestra el archivo completo. El panel de decisión muestra solo la historia recibida a las 08:10, con rellenos identificados. El valor de las 07:00 llega a las 09:30.

## Horizonte nominal de una hora

- [Informe de desarrollo](h1/informe.json), [modelo](h1/modelo.json) y [recarga](h1/recarga.json).
- Predicciones evaluables de [entrenamiento](h1/predicciones_entrenamiento.csv) y [validación](h1/predicciones_validacion.csv).
- Comparación y pronóstico: [PNG](h1/pronostico.png) y [SVG](h1/pronostico.svg).
- Diagnóstico por periodo: [PNG](h1/errores.png) y [SVG](h1/errores.svg).
- [Resumen separado del cierre](h1/cierre.json).

## Horizonte nominal de seis horas

- [Informe de desarrollo](h6/informe.json), [modelo](h6/modelo.json) y [recarga](h6/recarga.json).
- Predicciones evaluables de [entrenamiento](h6/predicciones_entrenamiento.csv) y [validación](h6/predicciones_validacion.csv).
- [Resumen separado del cierre](h6/cierre.json).

Los dos informes de desarrollo mantienen `prueba=null`. Incluyen conjuntos evaluables, motivos de exclusión, estados de los tres candidatos, diagnóstico diario y una consulta desde registros para comprobar la preparación completa al recargar. Los resúmenes de cierre guardan métricas, huellas y ausencia de reajuste. En cada horizonte, la huella del modelo coincide entre desarrollo y cierre.

Las tres figuras publicadas se revisaron visualmente; sus SVG se generan del mismo objeto gráfico. El gráfico de pronóstico interrumpe líneas cuando falta un objetivo evaluable. No interpola objetivos para mejorar la apariencia. Las figuras muestran exclusivamente validación, incluso si se generan con una ejecución que también abrió cierre.

Desde la raíz, con carpetas nuevas:

```bash
python unidad23-series-temporales/ejemplos/01_auditar_tiempo.py --salida resultados/u23-auditoria --graficos
python unidad23-series-temporales/ejemplos/02_pronosticar_sensor.py --salida resultados/u23-h1 --graficos
python unidad23-series-temporales/ejemplos/02_pronosticar_sensor.py --horizonte 6 --salida resultados/u23-h6
python unidad23-series-temporales/ejemplos/02_pronosticar_sensor.py --evaluar-prueba --salida resultados/u23-cierre-h1
python unidad23-series-temporales/ejemplos/02_pronosticar_sensor.py --horizonte 6 --evaluar-prueba --salida resultados/u23-cierre-h6
```

Las ejecuciones de cierre crean además `cierre.json` y `predicciones_prueba.csv`. El informe completo de esas ejecuciones contiene prueba; los informes de desarrollo publicados se mantienen separados. Puedes añadir `--graficos` al horizonte de seis horas para producir sus propias figuras.

La exportación rechaza carpetas existentes. La verificación compara temperaturas predichas, con tolerancia `1e-12` °C, tanto desde características como desde lecturas crudas. Los metadatos de los formatos gráficos pueden cambiar sus bytes sin cambiar los datos representados.

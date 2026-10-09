# Recursos reproducibles de la Unidad 18

[Volver a la unidad](../README.md)

Los informes incluidos se generaron en modo de **desarrollo**, con prueba sin abrir. `prueba` es null y `fuentes` contiene exclusivamente entrenamiento y validación. Las huellas identifican los archivos leídos, no garantizan por sí mismas su calidad ni la independencia de un protocolo.

| Recurso | Contenido |
|---|---|
| [Consumo: informe](consumo/informe.json) | Escala, coeficientes, reconstrucción y 30 deltas por bloque |
| [Consumo: entrenamiento](consumo/predicciones_entrenamiento.csv) | ID, objetivo y predicción |
| [Consumo: validación](consumo/predicciones_validacion.csv) | Filas empleadas para evaluar e inspeccionar |
| [Alertas: informe](alertas/informe.json) | Árbol, ruta local, métricas globales y por grupos |
| [Alertas: entrenamiento](alertas/predicciones_entrenamiento.csv) | Predicciones y grupos |
| [Alertas: validación](alertas/predicciones_validacion.csv) | Filas empleadas en la auditoría |
| [Ficha del árbol](ficha_alertas.md) | Interpretación, impacto y decisión de uso del ejemplo |

## Figuras

- Contribuciones: [PNG](consumo/contribuciones.png) · [SVG](consumo/contribuciones.svg). Caso local prefijado, referencia y resultado en kWh.
- Permutación: [PNG](consumo/permutacion.png) · [SVG](consumo/permutacion.svg). Medias y desviaciones de los deltas, individuales y conjuntos; no intervalos de confianza.
- Grupos: [PNG](alertas/grupos.png) · [SVG](alertas/grupos.svg). Matriz desagregada y recobrado con soporte; los indefinidos se anotan y no se dibujan como barras cero.

Las tres figuras se inspeccionaron visualmente: títulos, unidades, leyendas, cifras y textos sin recortes. Las pruebas contrastan barras con valores de los informes, verifican los formatos y comprueban que graficar un cierre utiliza únicamente datos de desarrollo. No se incluye un gráfico de prueba.

## Reproducción

Desde la raíz y con las dependencias instaladas:

```bash
python unidad18-interpretabilidad-responsabilidad/ejemplos/01_explicar_consumo.py --salida resultados/u18-consumo-reproduccion --graficos
python unidad18-interpretabilidad-responsabilidad/ejemplos/02_auditar_alertas.py --salida resultados/u18-alertas-reproduccion --graficos
```

Las carpetas deben ser nuevas; el programa no sobrescribe resultados existentes. Las versiones numéricas aparecen en cada JSON; Matplotlib se añade cuando se solicitan gráficos. El algoritmo usa un hilo numérico con `threadpool_limits(1)` para reducir variación entre bibliotecas. Otra plataforma o versión puede introducir diferencias de redondeo; conserva el entorno declarado al comparar cifras exactas.

Los JSON documentan el estado, no son un paquete de despliegue ni un objeto serializado de scikit-learn. El código permite reconstruir la ejecución desde los CSV. Los resultados de cierre se publican en la unidad y las soluciones para comprobarlos; conocerlos impide tratarlos como evaluación nueva de futuros cambios.

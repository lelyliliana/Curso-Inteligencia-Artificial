# Informe — Pronóstico de un sensor

[Reto](../reto.md) · [Ficha completada](../recursos/ficha_modelo.md)

## Decisión y tiempos

- Necesidad y usuario del pronóstico:
- Variable, unidad, sensor, frecuencia y zona:
- Hora de evento, disponibilidad y regla de emisión:
- Horizonte nominal y anticipación efectiva:
- ¿Orígenes sucesivos o trayectoria recursiva?:

## Datos y separación

- Procedencia y condiciones de uso:
- Rango de cada bloque y cortes de disponibilidad de etiquetas:
- Duplicados exactos, conflictos, huecos y valores vacíos:
- Historia permitida desde bloques anteriores:
- Regla de relleno y límite de antigüedad:
- Por qué el objetivo no se imputa:

| Bloque | Orígenes posibles | Evaluables | Motivos de exclusión |
|---|---:|---:|---|
| Entrenamiento | | | |
| Validación | | | |
| Cierre | | | |

## Representación y ajuste

- Ejemplo manual con ventanas y rezagos:
- Orden de entradas y disponibilidad de cada una:
- Qué preparación aprende parámetros y de qué datos:
- Referencias y predictor; criterio y desempate fijados antes de validar:
- Comparabilidad de casos entre candidatos y horizontes:

## Evaluación e interpretación

| Horizonte y candidato | MAE entrenamiento | MAE validación | RMSE | Sesgo |
|---|---:|---:|---:|---:|
| ... | | | | |

- Elegido, errores por periodo y denominadores:
- Qué ocurre antes y después de observar un cambio:
- Diferencia entre actualizar historia y reentrenar:
- Resultados de cierre y cambios que ya no pueden validarse con él:
- Correlación temporal y límites de generalización:

## Persistencia y uso

- Comandos, versiones, huellas y formato del modelo:
- Diferencia máxima tras recargar:
- Historia adicional necesaria para inferencia:
- Uso respaldado por la evidencia actual:
- Una extensión, nueva evaluación y criterio de rechazo:

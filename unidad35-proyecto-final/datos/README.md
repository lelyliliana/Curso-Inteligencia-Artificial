# Datos del proyecto final

[Unidad](../README.md) · [Protocolo previo](protocolo.json) · [Generador](generar_datos.py)

## Procedencia y alcance

Serie propia ficticia creada para esta entrega el 10 de octubre de 2026. No contiene datos de un edificio real ni mediciones de ahorro. Las fechas ilustran una secuencia y pueden extenderse más allá de la fecha de elaboración; no son observaciones reales ni un pronóstico meteorológico. No se reutilizan filas ni etiquetas de la Unidad 34.

Los datos forman parte del material didáctico propio del repositorio. No se incorpora un dataset externo ni una licencia de terceros. El repositorio no declara una licencia general y esta ficha no añade una nueva. Para ampliar con mediciones reales, documenta fuente, permisos, licencia si corresponde, unidades y momento de llegada.

## Generación

Se generan 1201 lecturas horarias desde el 7 de septiembre de 2026 a las 00:00 UTC−05:00. Se usa `random.Random(3501)`, ruido gaussiano con desviación 1,1 kW y redondeo a seis decimales:

```text
potencia(t) = 32 + 11·sin(2π·(hora−7)/24) + 10·laboral
             + 8·I(t≥820) + 6·I(t≥1070) − 7·I(t≥1140) + ruido
```

`laboral` vale uno de lunes a viernes. La fórmula no es un modelo físico y sus indicadores de cambio no entran al predictor. De cada pareja consecutiva se forma una decisión: potencia actual de `t−1`, objetivo observado en `t`. La etiqueta de entrenamiento del candidato de incremento es la diferencia de ambas.

| Archivo | Horas objetivo | Filas | Admitidas por contrato |
|---|---|---:|---:|
| [entrenamiento.json](entrenamiento.json) | 1–720 | 720 | 720 |
| [validacion.json](validacion.json) | 721–960 | 240 | 236 |
| [prueba.json](prueba.json) | 961–1200 | 240 | 236 |

El entrenamiento no contiene incidencias de contrato. Validación y cierre tienen estas incidencias inyectadas, conocidas como construcciones del laboratorio:

| Fase | Tardía | Potencia ausente | Potencia negativa | Caducada |
|---|---|---|---|---|
| Validación | PF0742 | PF0801 | PF0887 | PF0941 |
| Prueba | PF0995 | PF1033 | PF1115 | PF1188 |

Normalmente la llegada ocurre un minuto después de medir y la decisión a los cinco minutos. En una lectura tardía, la llegada es al minuto ocho; una ausente lleva `null`; una negativa lleva −3; una caducada conserva la lectura, pero sitúa la decisión al minuto veinte. La etiqueta se mantiene para trazabilidad, pero el evaluador no la usa para los casos rechazados. No se borra la incidencia del denominador de cobertura.

## Esquema

Cada fila tiene `id`, `entrada`, `instante_objetivo`, `objetivo_kw` e `incidencia_inyectada`. Los tres últimos campos son metadatos/etiqueta del experimento; no se entregan al servicio de inferencia.

El contrato de `entrada` contiene exactamente:

| Campo | Significado |
|---|---|
| potencia_kw | Potencia finita de 0 a 200 kW; no energía en kWh |
| medido_en | Hora en punto de la lectura, con zona horaria |
| recibido_en | Momento en que esa lectura llegó al sistema |
| decidir_en | Momento en que se pide la predicción |

La recepción y la decisión deben ser posteriores o iguales a la medición; la recepción no puede superar la decisión. Se admiten fechas de 2020 a 2099, normalizadas a UTC−05:00, y edad máxima inclusiva de quince minutos. Los booleanos no son números válidos para potencia. La validación no comprueba que los relojes o las unidades declaradas por un dispositivo sean verdaderos: esa verificación pertenece a la adquisición real.

Los objetivos de entrenamiento están disponibles antes del primer instante de decisión de validación; lo mismo ocurre antes del cierre. Las 240 decisiones de cada fase se recorren a medida que llegan lecturas nuevas. No se trata de predecir todas las horas futuras desde una única lectura.

## Reproducción

```bash
python unidad35-proyecto-final/datos/generar_datos.py --salida resultados/datos-proyecto-final
```

El generador escribe los tres arrays de fase. [consulta.json](consulta.json) es un caso conocido para la demo, no una fila adicional de cierre; [manual.json](../recursos/manual.json) contiene un cálculo artificial separado. El modelo guarda huellas del protocolo, generador, datos de desarrollo y módulos de cálculo. El informe de cierre añade la huella de prueba.

El cierre publicado es evidencia conocida para futuras modificaciones. No se deben elegir mejoras consultándolo y después presentarlo como una evaluación independiente de esas mejoras.

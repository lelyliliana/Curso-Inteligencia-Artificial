# Ficha — Pronóstico horario de temperatura

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Artefactos](README.md)

| Aspecto | Evidencia |
|---|---|
| Fecha y finalidad | 10 de octubre de 2026; enseñanza de pronóstico con disponibilidad explícita |
| Variable | Temperatura instantánea en °C de un sensor ficticio |
| Datos | 960 posiciones en 40 días; 954 filas originales con problemas de calidad incorporados |
| Particiones | 576 horas de entrenamiento, 192 de validación y 192 de prueba |
| Emisión | Diez minutos después de cada origen horario |
| Horizontes | Objetivo t+1 h o t+6 h; anticipación real desde emisión: 50 min o 5 h 50 min |
| Representación | Ocho características de historia recibida y calendario del objetivo |
| Modelos elegidos | Ridge con alpha=1, un estado diferente por horizonte; ambos ganan por MAE de validación |
| Validación h=1 | 185 casos; MAE 0,2222 °C; transición: 0,6877 °C |
| Validación h=6 | 180 casos; MAE 0,3710 °C; transición: 1,4102 °C |
| Cierre h=1 | 186 casos; MAE 0,1942 °C; RMSE 0,2696 °C |
| Cierre h=6 | 181 casos; MAE 0,2743 °C; RMSE 0,3882 °C |
| Persistencia | JSON de preparación, orden, escala y coeficientes; recarga sin diferencia en el entorno probado |
| Uso respaldado | Demostración didáctica y análisis de protocolo |
| Uso pendiente de evidencia | Pronóstico real, control automático, alarmas o decisiones sobre una instalación |

Los estados contienen ocho coeficientes y un intercepto, además de las medias y escalas de las ocho entradas. Las reglas temporales forman parte del modelo utilizable: cambiar el reloj o rellenar retrospectivamente produciría entradas distintas aunque se conservaran los mismos pesos.

## Limitaciones observadas

La media global oculta un aumento de error durante el cambio de nivel. El predictor no sabe que el salto va a ocurrir; posteriormente recibe observaciones nuevas, sin modificar coeficientes. Los candidatos estacionales también fallan cuando el valor del día anterior pertenece a otro nivel.

Se puntúan únicamente objetivos observables y válidos; las ausencias y conflictos reducen cobertura. El relleno de entradas no convierte un hueco en una medición real. Si la historia no puede formarse o el último valor tiene más de tres horas, no se emite predicción desde `pronosticar` y se devuelve `None`.

Una trayectoria sintética de un solo sensor no representa clima, edificios, fallos de hardware ni sensores distintos. Sus errores por hora están relacionados. No se calculan intervalos de predicción ni se comprueba calibración de incertidumbre. Tampoco se evalúa detección de anomalías o una estrategia recursiva de varios pasos.

## Persistencia y siguiente evaluación

El JSON necesita ejecutarse con la preparación compatible y con lecturas recientes que incluyan llegada e instante. La recarga comprueba una matriz y una consulta desde registros, pero no implementa recepción de eventos, retención de estado en producción ni reanudación del entrenamiento.

Una evaluación futura debe reservar periodos nuevos, medir latencias reales, definir comportamiento ante datos antiguos y comprobar calidad de los objetivos. Debe fijar de antemano horizonte, cobertura mínima, consecuencias del error y referencias. Si se cambia una regla después de ver este cierre, el resultado publicado solo podrá reutilizarse como diagnóstico conocido, no como evaluación independiente de esa mejora.

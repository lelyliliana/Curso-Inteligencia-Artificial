# Reto — Evaluar un pronóstico antes de usarlo

[Unidad](README.md) · [Plantilla](plantillas/informe_series.md)

Un equipo quiere anticipar cambios de temperatura de una instalación. Prepara una demostración y un informe que permitan decidir qué evidencia falta antes de usar un predictor real. Puedes completar todo el reto con estos datos ficticios y diagnósticos propios.

## Entregables

1. Reproduce la muestra temporal y dibuja medición, llegada, decisión y objetivo para una lectura puntual y otra atrasada. Incluye el cálculo manual de ventana causal y un contraejemplo con futuro.
2. Reproduce los dos horizontes. Conserva protocolo, estados, versiones, huellas, CSV y resultados de recarga. Explica la anticipación efectiva desde la emisión.
3. Reconstruye las exclusiones y verifica que todos los candidatos de un horizonte usan los mismos casos. Distingue ausencia del objetivo de ausencia de una entrada.
4. Analiza el cambio de nivel y los errores por día, sin esconder las transiciones detrás de una sola media. Explica por qué la actualización de historia no significa reentrenamiento.
5. Diseña una sola extensión, por ejemplo otra política ante datos antiguos o una evaluación en periodos nuevos. Si la implementas, declara el nuevo experimento. No uses el cierre publicado para ajustar y después atribuir independencia al mismo resultado.
6. Entrega una ficha con uso permitido, cobertura, dependencias temporales y criterio que haría rechazar la extensión. Un pronóstico para controlar equipos necesita evidencia sobre sus consecuencias, no solo sobre error numérico.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Relojes y representación | 20 | Origen, llegada, decisión, objetivo y ventanas correctos |
| Separación y calidad | 25 | Cortes por objetivo, disponibilidad, duplicados, conflictos y cobertura |
| Modelos y métricas | 20 | Referencias justas, criterio fijado y cálculos reproducidos |
| Diagnóstico y límites | 20 | Transiciones visibles; distinción entre observación nueva, reajuste y recursión |
| Reproducción y decisión | 15 | Estado completo, recarga, comandos y evaluación futura que pueda fallar |

Antes de considerar lista una entrega, corrige cualquier entrada construida con futuro, objetivo imputado para evaluar o selección que consulte prueba. No se premia mejorar artificialmente una cifra conocida.

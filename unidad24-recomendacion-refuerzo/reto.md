# Reto — Dos decisiones, dos evaluaciones

[Unidad](README.md) · [Plantilla](plantillas/informe_aplicaciones.md) · [Fichas de referencia](recursos/fichas.md)

Una biblioteca educativa quiere estudiar cómo ordenar recursos. Por separado, un taller de simulación quiere comparar formas de llegar a una meta en un tablero. Entrega **dos análisis con sus propios objetivos y evidencias**; no uses usuarios como sujetos de exploración de un agente.

## Parte A: recomendación

1. Reproduce el protocolo publicado y verifica las listas recargadas. Explica catálogo, historial, candidatos y objetivo observado.
2. Reconstruye a mano el coseno de un par de recursos con interacciones y una lista de un usuario nuevo. Documenta la regla de desempate.
3. Compara popularidad y coseno en validación, globalmente y por historia disponible. Incluye al menos dos errores concretos y el caso I26.
4. Propón una mejora que use información disponible antes de decidir. Declara qué datos faltan, cómo se obtendrían y un nuevo conjunto de evaluación. No es obligatorio implementarla.
5. Abre el cierre del estado guardado e informa si sostiene tu conclusión. No actualices historias con validación en esta reproducción.

## Parte B: refuerzo

1. Reproduce las cinco semillas. Dibuja la transición para una casilla cercana a un pozo y calcula una actualización Q con terminal y otra con truncamiento.
2. Contrasta retorno descontado, éxito, pozo y corte frente a la ruta fija. Conserva todas las semillas y declara los pasos consumidos.
3. Muestra la política de la primera semilla y explica una flecha que parezca contraintuitiva. Identifica una limitación del entrenamiento finito.
4. Guarda tablas antes del cierre y evalúa con las semillas reservadas, sin exploración ni aprendizaje. Distingue reproducibilidad del experimento y generalización a otros mapas.
5. Formula un experimento futuro para mejorar el retorno: hipótesis, único cambio, presupuesto, referencia y nuevas semillas reservadas. No hace falta ejecutarlo para cumplir el reto.

Entrega comandos, versiones, ambos estados JSON, informes y figuras legibles, más el informe escrito. No se requieren servicios, personas reales, GPU ni hardware conectado. La evaluación del reto premia evidencia e interpretación; no premia elevar una métrica retocando el cierre conocido.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Recomendación: separación e historial | 15 | Candidatos correctos; ajuste sin evaluación; cierre congelado |
| Recomendación: cálculo y comparación | 15 | Coseno, métricas, referencia, denominadores y dos errores |
| Recomendación: límites y mejora | 10 | Arranque en frío, observación incompleta y datos necesarios |
| Refuerzo: entorno y actualización | 15 | Estados, transiciones, recompensa, Q manual y truncamiento |
| Refuerzo: evaluación y variabilidad | 15 | Cinco semillas, retorno y éxito, sin explorar ni actualizar |
| Refuerzo: interpretación y cierre | 10 | Política explicada y conclusión que conserva fallos |
| Reproducción y comunicación | 15 | Versiones, comandos, recarga, informes y figuras coherentes |
| Próximo experimento | 5 | Hipótesis y evaluación nueva fijadas antes de medir |

Una entrega con filtración o aprendizaje durante el cierre debe corregirse antes de considerarse terminada, aunque tenga una métrica alta. Si no puedes ejecutar alguna parte, identifica exactamente qué faltó; no inventes resultados.

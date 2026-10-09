# Reto — Defender una validación antes de cerrar

[Unidad](README.md) · [Plantilla](plantillas/informe_validacion.md)

## Encargo

Elige uno de los laboratorios y entrega un informe que permita reconstruir su selección, revisar qué información conoció cada ajuste y justificar el uso previsto. No se exige superar la referencia ni ampliar la rejilla.

## Trabajo común

1. Define caso, objetivo, entradas, unidades y momento de disponibilidad. Justifica si se busca otro caso independiente o un equipo nuevo. Declara los resultados públicos que ya conocías.
2. Escribe el [protocolo](datos/protocolo.md) antes de ejecutar el cierre: candidatos y orden, pliegues, semilla cuando corresponda, preparación, criterio, tolerancia de empate, presupuesto y reajuste.
3. Ejecuta desarrollo con `--salida` y `--graficos` en una carpeta nueva bajo `resultados/unidad16/`. Registra commit, versiones, comando y huella; comprueba `prueba: null` y ausencia de fuente de prueba.
4. Reconstruye el primer pliegue desde los índices del JSON. Comprueba intersección vacía de IDs de ajuste y validación, cobertura completa y tamaños. En equipos comprueba además intersección vacía de grupos.
5. Reconstruye media y escala de las dos entradas para `knn3_uniform` en ese pliegue usando exclusivamente sus filas de ajuste. Contrasta con el JSON.
6. Para una predicción OOF de ese candidato, identifica el caso, calcula sus distancias estandarizadas a las filas de ajuste, identifica tres vecinos y promedia sus objetivos. Contrasta con el CSV; si hay empate en el límite, documenta cómo afecta al conjunto de vecinos.
7. Calcula los MAE por pliegue, su media y desviación para el elegido, y el MAE OOF combinado. Explica por qué coinciden aquí las dos medias y por qué no es una propiedad general.
8. Presenta los siete candidatos, justifica la elección con cifras completas e interpreta las figuras sin convertir dispersión en intervalo de confianza.
9. Guarda elección, estado reajustado y registro de desarrollo. Ejecuta cierre en otra carpeta. Comprueba que desarrollo, índices, resultados, elección y reajuste coincidan; informa únicamente prueba del elegido.
10. Ejecuta las 30 pruebas; explica una referencia independiente y un control de información apartada. Discute límites del resultado y qué harías si prueba motivara cambios.

## Análisis específico

**Ciclos:** compara los dos mejores MAE y sus cuatro valores por pliegue. Explica por qué elegir el menor no demuestra superioridad estadística. Calcula los 29 ajustes y diferencia el modelo de un pliegue del reajustado con 160 casos. Identifica el caso OOF de mayor error absoluto del elegido, sus entradas y su pliegue; plantea una explicación posible sin tratarla como causa demostrada.

**Equipos:** interpreta el mapa de particiones. Calcula la cantidad de equipos compartidos en cada pliegue del diagnóstico por filas y contrástala con GroupKFold. Compara `knn3_uniform` en ambos esquemas y explica por qué el diagnóstico no decide. Justifica conservar la mediana y calcula los 33 ajustes. Explica qué cambiaría al pasar de evaluar equipos nuevos a futuras mediciones de equipos conocidos.

**Extensión opcional:** ejecuta el contraejemplo de escala y los cortes temporales manuales. No los incorpores a la selección de los laboratorios. Para una búsqueda adicional, prepara otro protocolo y datos de evaluación apropiados; no llames independiente a la prueba publicada después de haberla usado para orientar cambios.

## Entrega y evaluación

Informe de dos a cuatro páginas en Markdown o formato equivalente, exportaciones JSON/CSV de desarrollo y cierre y figuras de desarrollo. Usa la [plantilla](plantillas/informe_validacion.md).

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Pregunta y separación | 20 | Uso previsto y particiones coherentes; comprobación de IDs y grupos |
| Ajuste y cálculo | 25 | Escala por pliegue y predicción con tres vecinos reconstruidas |
| Selección | 20 | Siete candidatos, MAE por pliegue, ponderación, desempate y presupuesto |
| Interpretación | 15 | Figuras y análisis específico sin afirmaciones estadísticas indebidas |
| Reajuste y cierre | 10 | Configuración conservada, reajuste permitido y prueba del elegido |
| Reproducción | 10 | Comandos, versiones, commit, huellas, artefactos y pruebas |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos ajustar escala global antes de CV, mezclar equipos para justificar generalización a equipos nuevos, cambiar de candidato con prueba, reutilizar el último modelo de pliegue como si estuviera reajustado o presentar desviación entre pliegues como intervalo de confianza.

# Soluciones razonadas — Unidad 24

[Volver a la unidad](../README.md) · [Cálculos ejecutables](03_calcular_a_mano.py)

## 1. Dos salidas diferentes

Una valoración predice, por ejemplo, cuántas estrellas daría alguien. Una recomendación ordena candidatos y devuelve una lista bajo restricciones: disponibilidad, elementos vistos, cupo y desempate. Una puntuación útil para ordenar no es automáticamente una probabilidad ni una escala de satisfacción. En X, cero significa apertura no observada; no tenemos evidencia de que la persona rechazó ese recurso.

## 2. Coseno y norma cero

A·B=1; ||A||=||B||=√2. Por tanto, coseno=1/2. Para C=(0,0,0), la fórmula dividiría por cero. Fijamos similitud cero y documentamos falta de evidencia. Esto conserva una salida finita, pero no descubre el contenido de C ni resuelve el arranque en frío del elemento.

## 3. Métricas de una lista

| Objetivo | Posición en [B,C,D] | Recall@3 | NDCG@3 |
|---|---:|---:|---:|
| B | 1 | 1 | 1 |
| C | 2 | 1 | 1/log2(3)≈0,630930 |
| D | 3 | 1 | 1/log2(4)=0,5 |
| E | No aparece | 0 | 0 |

Si los cuatro casos fueran cuatro usuarios, Recall medio=3/4 y NDCG medio≈0,532732. El denominador ideal de NDCG vale 1 porque cada caso tiene un solo objetivo observado. No se puede aplicar sin cambios a varios objetivos ni interpretarlo como satisfacción completa.

## 4. Arranque en frío

Una persona sin historia no aporta elementos con los que sumar similitudes; recibe popularidad. I26 no aporta coocurrencias y sus similitudes son cero. Entre los ocho usuarios nuevos no hay aciertos en validación ni cierre. Podrían ayudar características informativas de recursos y preferencias declaradas voluntariamente por usuarios, pero habría que definir un experimento nuevo. «Nuevo» no es una descripción temática suficiente. Tampoco es válido inventar intereses a partir de etiquetas de cierre.

## 5. Historial y candidatos

U01 abrió cuatro recursos entre los días 1 y 4. Se excluyen exactamente esos cuatro de los 26: hay 22 candidatos tanto en validación como en cierre. I26, su objetivo de validación, sigue como candidato al día 6. La pregunta fijada evalúa predicciones desde una historia congelada; incorporar validación cambiaría esa pregunta y las puntuaciones. En producción podría interesar actualizar historias diariamente, pero hay que evaluar esa política con sus propias fechas de disponibilidad.

## 6. Tablero y retorno

El estado es `5*fila + columna`; la acción indica una dirección solicitada. El ruido puede girarla; el borde deja la posición igual y cobra −0,04. Meta entrega +1, pozo −1; ambos terminan. La política elige acciones según el estado. El retorno pondera recompensas por γ elevado al número de pasos transcurridos. Dos trayectorias con éxito pueden tener diferente retorno por duración y costos acumulados.

## 7. Actualizaciones Q

Con α=0,5 y γ=0,9, el objetivo no terminal es −0,04+0,9×0,8=0,68. La corrección es 0,5×(0,68−0,2)=0,24; Q nuevo=0,44. En pozo, objetivo=−1; la corrección es 0,5×(−1−0,2)=−0,6; Q nuevo=−0,4. No se usa el máximo siguiente cuando el entorno terminó.

Estos α y γ pertenecen al ejemplo manual. El entrenamiento completo fija α=0,15 y γ=0,95. Cambiarlos sería otro experimento. Ejecuta:

```bash
python unidad24-recomendacion-refuerzo/soluciones/03_calcular_a_mano.py
```

## 8. Corte y terminal

En el paso 60 sin meta ni pozo se actualiza con `r + γ*max(Q_siguiente)`: el corte es un límite de cómputo externo. Se reinicia el episodio para continuar el presupuesto, pero no se supone que el valor futuro real sea cero. El retorno reportado termina en el corte, sin añadir una recompensa futura inventada. Si la tarea exigiera llegar antes de un plazo, el tiempo restante sería parte del estado y habría que redefinir el terminal y la recompensa al agotarlo.

## 9. Éxito no equivale a retorno

En desarrollo, la semilla 2401 tiene éxito 0,645 frente a 0,465 de la referencia, pero retorno −0,4499 frente a −0,3445: empeora el objetivo descontado. Pedir movimientos contra un borde puede reducir algunas caídas y retrasar el avance. No basta con publicar solo éxitos o escoger la semilla 2404, que luce mejor en retorno. Se conservan las cinco políticas y se informa dispersión.

## 10. Conclusión con límites

Una respuesta posible: «El coseno recupera 15/56 objetivos en validación y 14/56 en cierre con historial fijo; no acierta entre los ocho usuarios nuevos y no demuestra mejorar aprendizaje real. Q-learning obtiene mayor frecuencia de metas que la referencia, pero en cierre su retorno medio −0,2969 queda por debajo de −0,2737 de la ruta fija. Hay variabilidad entre entrenamientos, pozos y cortes. Solo se evaluó un tablero conocido con semillas nuevas; no se justifica desplegar en equipos ni afirmar optimalidad».

El siguiente experimento debe formularse con una hipótesis y otro cierre reservado. El resultado desfavorable publicado forma parte de lo que aprendimos, no es un motivo para cambiar retrospectivamente el criterio.

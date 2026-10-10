# Reto — Clasificar imágenes y explicar lo que falta

[Unidad](README.md) · [Plantilla](plantillas/informe_vision.md) · [Orientación](soluciones/README.md)

**Situación:** un equipo necesita reproducir tu experimento y saber cuándo una imagen no aporta suficiente información. Prepara una comparación pequeña en CPU y una auditoría visual de sus límites.

## Trabajo

1. Reproduce un filtro manual, su comparación con Conv2d y la inspección de canales. Explica una diferencia entre imagen, mapa de activación y probabilidad.
2. Ejecuta el protocolo original y conserva sus informes. Identifica el número de imágenes y de escenas de cada partición.
3. Escribe una hipótesis antes de cambiar **una** condición: ancho de la CNN, tamaño del filtro o un aumento que conserve las etiquetas. Cuenta parámetros y documenta la configuración real.
4. Compara con prevalencia y el modelo lineal usando desarrollo. Conserva todos los ensayos y resultados, incluidos los que empeoran.
5. Presenta una curva, una matriz orientada y una galería seleccionada por un criterio explícito. Examina las dos vistas de al menos una escena difícil y el efecto de la oclusión sobre lo observable.
6. Guarda y recarga el estado elegido con preparación y orden de clases. Mide el mayor error en logits, no solo si coincide argmax.
7. Completa la ficha de límites: datos sintéticos, dependencia entre vistas, alcance de la métrica y evidencia necesaria para imágenes reales.

Puedes entregar un estudio de desarrollo sin un nuevo cierre. Si ya conoces los resultados públicos de prueba y quieres evaluar una mejora, fija nuevos datos, semillas y protocolo antes de observar su cierre. No repartas vistas de una escena entre particiones ni uses los casos difíciles de prueba para decidir el aumento.

## Entregables

- Código, versiones y comandos desde la raíz.
- Manifiestos, procedencia, reglas de separación y huellas de datos.
- Tabla de modelos, figura de aprendizaje, matriz y análisis visual.
- Estado generado localmente, prueba de recarga e informe siguiendo la plantilla.

No hace falta publicar binarios de modelos. Las imágenes nuevas deben tener procedencia y condiciones de uso documentadas; usa el generador del curso si quieres mantener el alcance sintético y pequeño.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Píxeles, filtros y formas | 20 | Cálculo manual y dimensiones comprobables |
| Procedencia, particiones y preparación | 25 | Escenas separadas; normalización solo con entrenamiento |
| Comparación y selección | 20 | Referencias, criterio previo, presupuesto y ensayos completos |
| Auditoría visual y métricas | 20 | Matriz interpretable, galería trazable y límites de etiquetas ocluidas |
| Recarga y reproducción | 15 | Preparación y clases guardadas; discrepancia en logits medida |

Una exactitud alta no compensa mezclar escenas entre particiones ni presentar vistas correlacionadas como independientes. Una transformación que destruye la información de la etiqueta exige revisar su pertinencia. No se exige mejorar la métrica para demostrar aprendizaje.

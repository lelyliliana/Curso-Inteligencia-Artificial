# Reto — Defender una representación con evidencia

[Unidad](README.md) · [Plantilla](plantillas/informe_representaciones.md)

## Encargo

Elige **uno** de los laboratorios y justifica qué representación conservarías para el cierre. El informe debe permitir reconstruir una transformación y una predicción, revisar los conjuntos usados y reconocer lo que las métricas no demuestran.

## Trabajo común

1. Define caso, objetivo, entradas, unidades y momento de predicción. Distingue disponibilidad declarada de evidencia temporal real.
2. Registra el [protocolo](datos/protocolo.md): candidatos, transformaciones, ajuste, criterio de MAE, tolerancia de empate y ausencia de reajuste con validación/prueba. Declara qué conocías del generador y las respuestas.
3. Ejecuta desarrollo con `--salida` y `--graficos` en una carpeta nueva bajo `resultados/unidad15/`. Guarda commit, versiones, comandos y huellas; confirma `prueba: null`.
4. Completa las actividades específicas indicadas abajo, usando valores completos del JSON para los cálculos.
5. Identifica el caso de mayor error absoluto del elegido en validación. Registra su identificador, entradas, real, predicción y residuo. Explica qué puede y qué no puede inferirse sobre la causa del error.
6. Guarda candidato y parámetros antes de cerrar. Ejecuta `--evaluar-prueba` en otra carpeta y comprueba coincidencia de código, entorno, protocolo, huellas de desarrollo, parámetros y elección.
7. Informa prueba sin volver a elegir. Si los resultados motivaran cambios, explica qué evaluación nueva sería necesaria.
8. Ejecuta las 30 pruebas y explica una referencia matemática independiente y un control de separación de información.

## Si eliges interacción

- Clasifica las cinco columnas del CSV según su uso permitido antes del ciclo. Explica por qué la lectura posterior se excluye aunque esté fuertemente relacionada con el objetivo.
- Calcula el producto de horas y potencia de un caso identificado. Documenta nombres y orden de las tres características.
- Reconstruye su predicción aplicando media, escala, intercepto y coeficientes guardados. No utilices coeficientes de z como si estuvieran expresados en unidades originales.
- Compara mediana, originales e interacción sobre los mismos casos y calcula el MAE del elegido desde CSV.
- Interpreta la figura y explica por qué añadir una columna derivada puede ayudar sin aportar una nueva medición. Distingue coeficientes ajustados de efectos causales.

## Si eliges PCA

- Reproduce el ejemplo manual: covarianza, dirección principal, coordenada, reconstrucción y error medio por celda.
- Para un caso concreto de validación, reconstruye z, coordenada de `pca1` y señales reconstruidas usando el orden original de entradas.
- Reconstruye su predicción aplicando el intercepto y coeficiente de la regresión en la coordenada PCA. Distingue esta predicción de la reconstrucción de las entradas.
- Compara mediana, completa, pca1 y pca2: dimensiones, MAE/RMSE/R², varianza de entrenamiento y error de reconstrucción de validación cuando existan.
- Interpreta ambas figuras. Explica el cambio de signo, el control sin compresión de `pca2` y la diferencia entre conservar varianza y predecir bien.

Opcional: cambia solo la lectura posterior o los objetivos de prueba en copias, manteniendo valores válidos. Compara las partes que deberían permanecer iguales. Conserva la variante separada y no la presentes como una mejora del experimento original. No se exige buscar más componentes, derivaciones o modelos.

## Entrega y evaluación

Informe de dos a cuatro páginas en Markdown o formato equivalente, exportaciones de desarrollo y cierre —JSON/CSV— y figuras de desarrollo. Usa la [plantilla](plantillas/informe_representaciones.md). Los datos y las respuestas son públicos; describe honestamente el alcance de tu cierre.

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Formulación y disponibilidad | 15 | Entradas y objetivo con unidades, tiempo de disponibilidad y exclusiones justificadas |
| Transformación y cálculo | 25 | Predicción y característica o proyección reconstruidas correctamente |
| Comparación | 20 | Todos los candidatos, mismos casos, criterio previo y métricas diferenciadas |
| Interpretación | 20 | Figura y caso concreto; límites de redundancia, reconstrucción, predicción y causalidad |
| Cierre | 10 | Elegido y parámetros conservados, sin reajuste ni reselección |
| Reproducción | 10 | Comandos, versiones, commit, huellas, exportaciones y pruebas |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos incluir la lectura posterior como entrada, aprender escala o PCA con prueba, confundir coordenadas con variables originales, interpretar varianza retenida como exactitud predictiva o elegir de nuevo mirando prueba.

# Reto — Justificar grupos o alertas con evidencia

[Unidad](README.md) · [Plantilla](plantillas/informe_agrupamiento_anomalias.md)

## Encargo

Elige **uno** de los laboratorios y prepara una evaluación que otra persona pueda reproducir. El objetivo es justificar el procedimiento y sus límites, aunque su resultado muestre que no sería suficiente para una aplicación real.

## Trabajo común

1. Define caso, variables, unidades y momento de uso. Explica qué representan los datos y qué información real falta.
2. Registra el [protocolo](datos/protocolo.md): conjuntos permitidos, escala, configuración, semillas, candidatos, selección y desempates. Declara qué conocías del generador y de las respuestas públicas.
3. Ejecuta desarrollo con `--salida` y `--graficos`, usando una carpeta nueva bajo `resultados/unidad14/`. Guarda commit, versiones, comando y huellas de archivos; confirma `prueba: null`.
4. Completa las actividades específicas de tu laboratorio indicadas abajo.
5. Conserva por escrito el elegido y su configuración antes de cerrar. Ejecuta `--evaluar-prueba` en otra carpeta y compara los campos de desarrollo con el registro previo.
6. Informa el cierre sin volver a seleccionar. Explica qué evaluación nueva haría falta si el resultado motivara cambios.
7. Ejecuta las 30 pruebas. Identifica una comprobación matemática y otra que impida utilizar información de un conjunto no permitido.

## Si eliges agrupamiento

- Reproduce el paso manual de asignación, actualización e inercia del ejemplo de cuatro puntos.
- Calcula la silueta del punto A y distingue distancias entre casos de distancias a centros.
- Compara los tres valores de k sobre los mismos 60 casos de validación: inercia de entrenamiento, silueta, tamaños y ARI entre inicializaciones.
- Describe los centros del elegido en horas y kWh. Identifica un caso en CSV, calcula su transformación con los parámetros completos del JSON y verifica su centro más cercano.
- Interpreta ambas figuras y explica por qué grupos estables no necesariamente representan categorías verdaderas. No conviertas identificadores o colores en nombres de riesgo, eficiencia o tipo de instalación sin evidencia.
- Explica qué cambiaría al modificar unidades sin escalar y qué cobertura no se demuestra con estos datos.

## Si eliges anomalías

- Diferencia entrenamiento, calibración de umbral, validación y prueba. Explica por qué la referencia ordinaria es un supuesto y por qué la selección con F1 sí aprovecha etiquetas.
- Reconstruye el umbral de cada detector ordenando sus 60 puntuaciones de calibración y tomando la posición 57. Usa valores completos del CSV, no el umbral redondeado de consola.
- Reconstruye las tres matrices de confusión de validación y calcula precisión, recobrado, F1 y exactitud. No atribuyas métricas con etiquetas a entrenamiento o calibración, que no las contienen.
- Identifica un FN del elegido y un FP del candidato por distancia. Si un tipo de error no aparece en un candidato, informa cero y analiza su alcance; no inventes un caso.
- Interpreta la figura y explica por qué el elegido omite la mayoría de los positivos. Compara con no emitir alertas y distingue puntuación de probabilidad.
- Describe qué evidencia y capacidad de revisión harían falta antes de recomendar un uso real. No se exige ajustar otro modelo ni buscar un umbral mejor.

Opcional: ejecuta una variante con semilla 29 y documenta sus cambios por separado. No elijas una semilla por su mejor resultado ni incorpores prueba a desarrollo sin reconocerlo.

## Entrega y rúbrica

Informe de dos a cuatro páginas en Markdown o formato equivalente, exportaciones de desarrollo y cierre —JSON/CSV— y figuras de desarrollo. Usa la [plantilla](plantillas/informe_agrupamiento_anomalias.md), conserva originales y registra los comandos desde la raíz.

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Formulación y datos | 15 | Significado, unidades, disponibilidad, supuesto ordinario o ausencia de etiquetas claros |
| Ajuste y protocolo | 20 | Escala y modelos aprendidos solo con conjuntos permitidos; decisiones previas explícitas |
| Cálculo y comparación | 25 | Cálculos manuales correctos y todos los candidatos sobre los mismos casos |
| Interpretación | 20 | Figura y casos concretos; estabilidad o errores analizados sin exagerar utilidad |
| Cierre | 10 | Elegido conservado, prueba sin reajuste ni reselección |
| Reproducción | 10 | Versiones, commit, comandos, huellas y resultado de pruebas |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos ajustar con prueba, usar la etiqueta como entrada, confundir grupo con clase verdadera, interpretar puntuación como probabilidad o afirmar que pocas falsas alertas bastan para un detector que omite la mayoría de los positivos.

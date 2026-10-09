# Reto — Ajustar, comparar y explicar una regresión

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe_regresion.md)

## Situación

Debes explicar si un modelo aprendido mejora una referencia sencilla para anticipar consumo por ciclo. Elige **uno** de los dos laboratorios. Entrega evidencia que permita revisar qué se ajustó, cómo se comparó y dónde falla, además de la métrica final.

## Trabajo

1. Define unidad de observación, entrada, objetivo, momento de predicción y unidades. Distingue disponibilidad declarada de disponibilidad comprobable en los CSV.
2. Registra el [protocolo](datos/protocolo.md): particiones, candidatos, transformaciones, criterio de ajuste, métrica de selección, desempate y ausencia de reajuste con validación. Hazlo antes de abrir prueba.
3. Ejecuta el laboratorio elegido sin `--evaluar-prueba`, con `--salida` y `--graficos`. Registra commit, comando, versiones y huellas de desarrollo. Usa un directorio nuevo bajo `resultados/unidad11/`.
4. Explica los parámetros aprendidos. Si elegiste curva, distingue horas y z, interpreta centro y escala y evita llamar pendiente por hora al coeficiente de z.
5. Compara todos los candidatos sobre los mismos casos. Reproduce a mano una predicción y su residuo; reproduce también el MAE de al menos tres casos identificados, aclarando que ese cálculo parcial no es la métrica del conjunto completo.
6. Analiza un gráfico de residuos: describe el patrón, señala un caso concreto y formula una hipótesis y un límite. Si elegiste curva, compara también entrenamiento y validación para explicar el sobreajuste de grado 9.
7. Haz una consulta fuera del rango de entrenamiento, dentro del dominio permitido de 0 a 24 horas. Interpreta la marca y explica por qué no puedes calcular el error de esa consulta. La consulta no decide la selección ni tiene que modificar el ajuste.
8. Guarda candidato, modelos, código y huellas antes del cierre. Ejecuta después `--evaluar-prueba` sobre los mismos datos y exporta a otra carpeta. Comprueba que coincidan protocolo, huellas de desarrollo, parámetros y selección.
9. Informa los errores de prueba sin volver a elegir. Explica qué evidencia nueva necesitarías para rediseñar o afirmar utilidad real.
10. Ejecuta las 26 pruebas de la unidad y registra la salida. Identifica un control que verifica separación de datos y una afirmación que esa prueba no demuestra.

Como extensión opcional, realiza una perturbación en una copia o ejecuta el ejemplo de sensibilidad. Documenta sus cambios como un experimento aparte; conserva el protocolo original para el cierre. No hace falta añadir modelos, eliminar filas ni optimizar hiperparámetros.

Los datos, fórmulas generadoras y resultados de prueba son públicos. Si los leíste, decláralo. El ejercicio puede demostrar un flujo reproducible, pero no debe presentarse como una evaluación personal ciega o una validación externa.

## Entrega

Un informe de aproximadamente dos a cuatro páginas en Markdown o formato equivalente, junto a las dos exportaciones JSON y CSV, las figuras PNG o SVG de desarrollo y los comandos utilizados. Usa la [plantilla](plantillas/informe_regresion.md). Conserva los originales del repositorio.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Pregunta, unidades y disponibilidad | 15 | Escenario definido y diferencia entre supuesto y evidencia |
| Protocolo y ajuste | 20 | Separación, candidatos, transformaciones y criterios previos correctos |
| Comparación y cálculo manual | 20 | Mismos casos, referencias, parámetros, predicción y errores reproducidos |
| Residuos y alcance | 20 | Figura interpretada, caso concreto, extrapolación y límites explícitos |
| Cierre | 15 | Coincidencia con desarrollo, solo el elegido, sin reselección |
| Reproducción y controles | 10 | Comandos, commit, versiones, huellas, archivos y pruebas |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos aprender parámetros con validación o prueba sin declararlo como otro protocolo, elegir por prueba, confundir coeficientes transformados con unidades originales, comparar candidatos en casos diferentes sin explicarlo o presentar este ejemplo sintético como evidencia causal o utilidad real demostrada.

## Preguntas para revisar la entrega

- ¿El predictor recibe únicamente la información permitida?
- ¿Cada parámetro y transformación tiene un conjunto de ajuste identificado?
- ¿Se distingue la función objetivo de entrenamiento de la métrica de selección?
- ¿La interpretación de R² y del redondeo coincide con el informe?
- ¿La figura ayuda a ver un error que el promedio no explica?
- ¿El cierre reproduce el candidato fijado y reconoce el carácter público de prueba?

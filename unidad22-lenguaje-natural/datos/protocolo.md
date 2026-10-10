# Protocolo de representación, selección y cierre

[Unidad](../README.md) · [Datos y procedencia](README.md)

La tarea es clasificar una petición explícita en `acceso`, `material` u `horario`. Se comparan tres candidatos definidos antes de ejecutar validación. El corpus y los diagnósticos se redactaron para esta unidad. Este protocolo demuestra separación en el programa; no convierte textos del mismo proceso de autoría en una muestra independiente de personas reales.

## Particiones y entradas

- 18 familias de entrenamiento, 9 de validación y 9 de prueba. Primero se asigna la familia, después se producen sus tres variantes por tema. No hay sorteo ni semilla.
- Solo `texto` entra al vectorizador y `clase` al ajuste supervisado. ID, familia, tema y huella son metadatos, aunque la palabra del tema sí aparece dentro del texto.
- El lector exige esquema, clase válida y huella del texto. La auditoría rechaza ID repetido, secuencia de tokens duplicada y familia compartida entre particiones. No detecta automáticamente paráfrasis o duplicados semánticos.
- Desarrollo lee exclusivamente entrenamiento, validación y el archivo de diagnósticos; no abre el generador ni el CSV o la huella de prueba.

## Candidatos fijos

| Nombre | Preparación | Ajuste |
|---|---|---|
| prevalencia | Ninguna característica textual | Frecuencia de las tres clases en entrenamiento |
| unigramas | TF-IDF de tokens individuales | Logística multinomial |
| bigramas | TF-IDF de tokens individuales y pares consecutivos | Misma logística |

Tokenizador versionado: `casefold`, normalización Unicode NFC y expresión regular de secuencias de letras o números. Conserva tildes y negaciones; separa signos, guiones y guion bajo; descarta emojis. No aplica raíces, lemas, corrección ortográfica ni lista de palabras vacías. Los bigramas se forman después de quitar puntuación, incluso a través de una frontera de oración: es una limitación conocida.

Cada vectorizador aprende vocabulario e IDF solo de los 54 textos de entrenamiento. Usa conteos, IDF suavizado, norma L2 por documento, `min_df=1` y ninguna reducción del vocabulario. Los desconocidos no crean columnas ni un token `<UNK>`.

Logística: `C=1`, penalización L2 (`l1_ratio=0`), `solver=lbfgs`, intercepto, `max_iter=1000`, `tol=1e-9`, clases en orden acceso/material/horario y peso uniforme por texto. Si no converge, se considera un error de ejecución. No hay búsqueda de C, ajuste por diagnósticos ni entrenamiento neuronal. Las variantes tienen igual peso y todas las familias tienen tres variantes; la evidencia sigue siendo por 36 familias sintéticas, no por 108 personas.

## Selección y cierre

Se elige la menor entropía cruzada (CE) media de validación. Si la mejora no supera `1e-9`, se conserva el anterior en el orden prevalencia → unigramas → bigramas. Exactitud, macro F1, matriz y métricas por clase describen el resultado, pero no cambian la selección. Empate exacto de probabilidades: primera clase. Un empate aparente por redondeo no obliga a aplicar esa regla.

Se conservan los tres estados ajustados y se congela el elegido. `--evaluar-prueba` abre prueba después de seleccionar, comprueba su separación y evalúa solo ese estado. No vuelve a ajustar con validación, no compara candidatos en prueba y no crea un umbral posterior a partir del cierre.

Los nueve diagnósticos se fijaron antes del ajuste; se muestran después de seleccionar y no reciben una métrica agregada. d01/d02 son variantes muy próximas a plantillas de entrenamiento: sirven para demostrar una colisión de representaciones, no generalización. d04–d06 y d08 no tienen etiqueta única válida. Acertar d03 con vector cero no prueba conocimiento de sus palabras.

## Persistencia y reproducibilidad

El JSON incluye formato, versión del tokenizador, clases, orden de vocabulario, IDF, coeficientes, sesgos y configuración de ajuste. La inferencia reconstruye conteos, TF-IDF y softmax con NumPy; se contrasta con scikit-learn tanto en textos vistos como nuevos. La representación densa es adecuada para este corpus pequeño; no se propone para millones de términos.

La recarga se comprueba en validación y diagnósticos con tolerancia absoluta `1e-12`, registrando error y SHA-256 del modelo. No guarda un optimizador ni permite reanudar entrenamiento. Las huellas detectan cambios accidentales; no certifican autoría, calidad de etiquetas ni seguridad de un origen.

Una vez publicado el cierre, su resultado es conocido. Si se modifica el corpus, tokenizador, taxonomía, hiperparámetros o política de abstención a partir de lo observado, deberá declararse otro experimento y obtenerse evidencia nueva. Repetir el mismo cierre verifica reproducción, no independencia.

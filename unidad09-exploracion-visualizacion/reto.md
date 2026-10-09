# Reto — Informe exploratorio que se pueda revisar

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe_exploratorio.md)

## Situación

Un equipo quiere entender si sus datos permiten comparar consumos y estudiar una relación con las horas de uso. Prepara un informe que les ayude a distinguir lo observado, las hipótesis pendientes y los datos que todavía harían falta.

Usa los dos conjuntos sintéticos de la unidad como demostraciones separadas. No unas los 48 casos-día a las lecturas de S1/S2/S3 ni presentes esos casos como mediciones reales. Este reto cierra el bloque de obtención, preparación y exploración; todavía no se entrena un modelo.

## Trabajo

1. Escribe tres preguntas: una sobre cobertura, una sobre distribución y otra sobre relación entre variables. Define la unidad de observación y el alcance de cada una.
2. Ejecuta los dos laboratorios base y registra comandos, versiones, fuentes y huellas. Conserva la trazabilidad de la preparación.
3. Incluye una tabla de cobertura por sensor y los resúmenes por grupo. Diferencia filas preparadas, valores presentes, faltantes y pares completos.
4. Incluye las tres figuras base con títulos, ejes, unidades, tamaños y una explicación propia. Aporta PNG para lectura y SVG para ampliación.
5. Realiza **una** variante: aplicar la corrección sintética de la Unidad 8, o cambiar de ocho a cuatro/dieciséis intervalos. Guarda la nueva exportación en otra carpeta y añade la figura pertinente para comparar. Explica qué cambió, qué se conservó y por qué.
6. Redacta tres hallazgos con pregunta, evidencia, interpretación y límite. Añade dos conclusiones tentadoras que has descartado y el motivo.
7. Propón qué datos o diseño adicional harían falta para una pregunta que estos ejemplos no pueden responder.
8. Ejecuta las pruebas y revisa visualmente etiquetas, huecos, ceros, tamaños y escalas. Registra un resultado verificable; no basta escribir «todo funciona».

## Entrega

Usa la [plantilla](plantillas/informe_exploratorio.md) para un informe de aproximadamente 2–4 páginas, o una extensión equivalente en Markdown. Incluye las figuras o enlaces relativos a ellas, los JSON de cada exportación y los comandos suficientes para reproducirlas desde la raíz del curso. No se exige convertirlo a PDF.

Trabaja bajo `resultados/unidad09/reto/` o en una carpeta propia. El destino de cada exportación debe ser nuevo. Si modificas código o datos, entrega también la copia y explica sus diferencias; no edites los originales para conseguir una conclusión.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Preguntas y alcance | 15 | Tres preguntas delimitadas, con unidades de observación y límites |
| Procedencia y reproducción | 20 | Fuentes, versiones, comandos, huellas y trazabilidad suficientes para repetir |
| Cálculos y denominadores | 20 | Coberturas y resúmenes correctos; faltantes, ceros y grupos tratados explícitamente |
| Calidad de figuras | 20 | Tres figuras legibles, ejes y unidades correctos, tamaños visibles y escalas coherentes |
| Variante y sensibilidad | 10 | Comparación reproducible que explica el cambio y sus invariantes |
| Interpretación y límites | 15 | Tres hallazgos proporcionados, dos conclusiones descartadas y un siguiente paso razonado |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Debes corregir antes de cerrar el reto cualquier cero inventado a partir de un faltante, eliminación no declarada, mezcla de los dos conjuntos, denominador incorrecto o afirmación causal presentada como demostrada. Un aspecto visual atractivo no compensa esos errores.

## Preguntas de revisión

- ¿Puede otra persona encontrar exactamente los datos que dieron lugar al gráfico?
- ¿A qué casos se refiere cada número del informe?
- ¿Qué observaciones no entraron y por qué?
- ¿La variante cambia los datos o solo la representación?
- ¿Podría el lector confundir una hipótesis con un resultado establecido?
- ¿La siguiente acción propuesta exige información que todavía no tenemos?

La [orientación de soluciones](soluciones/README.md) sirve para contrastar argumentos, no para reemplazar tu informe.

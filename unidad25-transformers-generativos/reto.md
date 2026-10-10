# Reto — Un generador pequeño que puedas explicar

[Unidad](README.md) · [Plantilla](plantillas/informe_generativo.md) · [Ficha de referencia](recursos/ficha_modelo.md)

Prepara una demostración reproducible de continuación condicional. Una persona que lea tu informe debe poder reconstruir una fila de atención, detectar una fuga temporal y entender qué evidencia respalda una generación correcta.

## Entrega

1. Describe la tarea artificial, las familias y los cortes. Demuestra que vocabulario y conteos de bigramas usan solo entrenamiento. Explica por qué compartir plantillas limita la conclusión de generalización.
2. Calcula una fila de atención a mano y contrasta la salida con el programa. Modifica un valor futuro y compara el resultado con/sin máscara. Incluye dimensiones y una figura legible.
3. Reproduce el ajuste fijado. Compara CE, perplejidad y exactitud por token con coincidencia de secuencia completa. Incluye un error real de bigramas y una explicación del desempeño del transformer.
4. Guarda el estado antes de abrir prueba, comprueba recarga y evalúa una sola vez el estado elegido. Conserva las huellas del modelo y datos. No reentrenes a partir del cierre.
5. Prueba codicioso, muestreo y un corte corto. Documenta temperatura, semilla, texto y motivo de parada aunque las muestras coincidan. Conserva un caso desconocido y uno incompleto.
6. Redacta una ficha de límites y propone un siguiente experimento con una hipótesis y evaluación nueva. No hace falta descargar un modelo grande ni usar servicios.

Entrega informe, comandos y versiones, estado JSON, resultados y tres figuras interpretadas. Puedes usar las figuras generadas por los programas; no basta con pegarlas sin explicar qué muestran. No se evalúa cuán convincente parece una respuesta inventada.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Datos, vocabulario y separación | 15 | Familias disjuntas y alcance de la gramática explícito |
| Atención, máscara y cálculo | 20 | Referencia manual, dimensiones y prueba contra futuro |
| Ajuste y referencia | 15 | Presupuesto fijo, bigramas y selección por CE |
| Evaluación e interpretación | 15 | Denominadores, token/secuencia y al menos un fallo |
| Generación y parada | 15 | Parámetros registrados, desconocidos, corte distinto de EOS |
| Recarga y cierre | 10 | Mismo estado, huellas y ausencia de reajuste |
| Comunicación y límites | 10 | Figuras claras, conclusión proporcionada y próximo experimento |

La filtración de objetivos o el reajuste con prueba requieren corregir el procedimiento antes de dar el reto por terminado. Un fallo honestamente documentado aporta más evidencia que una muestra elegida después de muchos intentos sin registro.

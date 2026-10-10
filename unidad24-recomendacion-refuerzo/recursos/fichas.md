# Fichas completadas — dos experimentos

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Artefactos](README.md)

## A. Recomendador de recursos ficticios

**Uso:** estudiar ranking con interacciones implícitas y evaluación separada. No recomienda contenidos reales ni estima aprendizaje de personas.

**Datos:** 26 elementos, 48 usuarios con cuatro aperturas y ocho sin historia. Entrenamiento 1–4 de septiembre; un objetivo por usuario el día 5 y otro el día 6. Reglas generadoras propias, sin proveedores ni personas reales.

**Método elegido:** coseno entre columnas binarias de entrenamiento, suma sobre historial, K=3. Catálogo completo menos historia conocida; empate por popularidad e ID. Usuarios nuevos reciben popularidad. La selección usa Recall@3 de validación y favorece la referencia si hay empate.

**Resultados:** popularidad 6/56 frente a coseno 15/56 en validación. Cierre del coseno: 14/56, NDCG@3=0,2034. Cero aciertos entre ocho usuarios nuevos en ambas fases. I26 carece de afinidades aprendidas y tampoco se recupera en los objetivos reservados. Cobertura global 23/26 no implica relevancia completa.

**Estado y reproducción:** JSON con reglas, historial, catálogo, similitudes y popularidad. La recarga conserva las 56 listas de validación; el cierre solo lee ese estado y prueba, sin volver a ajustar. Las huellas de los CSV utilizados y del estado permiten rastrear la ejecución.

**Límites:** coocurrencias sintéticas pequeñas; etiquetas escasas y sesgadas por el proceso generador; ningún registro de exposición, satisfacción ni utilidad causal. No se evalúa actualización diaria ni una población de usuarios real. El historial también sería información sensible en un sistema real y requeriría una política de acceso y conservación adecuada antes de recolectarlo.

**Decisión:** apto como demostración de procedimiento; insuficiente para desplegar en una biblioteca educativa. Próximo paso propuesto: contenido informativo y evaluación nueva para arranque en frío, sin usar los objetivos de cierre como características.

## B. Q-learning en cuadrícula simulada

**Uso:** aprender el ciclo estado–acción–recompensa y evaluar políticas. Exclusivamente un tablero en memoria, sin conexión con máquinas o personas.

**Entorno:** 25 casillas, cuatro acciones, inicio fijo, una meta y cuatro pozos. Giros laterales 20 % en total. Meta +1, pozo −1, resto −0,04. Terminales definidos por entrada en meta o pozo; corte externo de 60 pasos con término futuro conservado en Q. La evaluación reporta retorno hasta el corte.

**Entrenamiento:** cinco tablas inicialmente cero, 2000 episodios cada una, α=0,15, γ=0,95, ε de 1 a 0,05. Entre 21628 y 23468 transiciones efectivas por tabla. Referencia informada que sube hasta la fila cero y luego va a la derecha. Se reportan todas las semillas; no se selecciona la mejor.

**Desarrollo:** 200 episodios por política. Referencia: éxito 0,465 y retorno −0,3445. Q: éxito medio 0,623, desviación 0,0341; retorno medio −0,3114, desviación 0,1072. Dos semillas empeoran el retorno respecto a la referencia.

**Cierre:** otras 200 semillas compartidas entre políticas. Referencia: éxito 0,520 y retorno −0,2737. Q: éxito medio 0,635, desviación 0,0751; retorno medio −0,2969, desviación 0,0689. Q cae en pozo en promedio en 35,6 % de episodios y se trunca en 0,9 %. La mejora media de retorno no se confirma en este cierre.

**Estado y reproducción:** las cinco tablas, entorno y configuración en JSON. Recarga numéricamente exacta; evaluación sin exploración ni actualizaciones, con generador nuevo por episodio. No permite reanudar exactamente el entrenamiento. La dispersión se calcula entre tablas, no como intervalo de confianza para una población de entornos.

**Límites:** α constante y presupuesto corto; sensibilidad a semillas; un único tablero con inicio y recompensa fijos; estado completamente observable; sin costos de hardware ni cambios de dinámica. Pedir acciones contra bordes puede retrasar el avance. No se demuestra optimalidad ni seguridad fuera del simulador.

**Decisión:** apto para analizar aprendizaje y fallos. La evidencia no justifica afirmar una mejora general de retorno frente a la referencia. Un próximo experimento debería fijar una hipótesis sobre presupuesto o tasa de aprendizaje y reservar semillas nuevas antes de medir.

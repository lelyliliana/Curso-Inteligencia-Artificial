# Soluciones razonadas — Unidad 25

[Unidad](../README.md) · [Cálculos ejecutables](03_atencion_y_temperatura.py)

## 1. Arquitectura, objetivo y uso

La arquitectura combina embeddings, posiciones, atención causal, normalizaciones, conexiones residuales y una red por posición. El objetivo reduce CE de los tokens de continuación, incluido EOS. La decodificación puede tomar el máximo o muestrear con temperatura. Usar otra temperatura conserva pesos; entrenar con otra pérdida sí cambia el proceso que los aprende. Un transformer no es sinónimo de generador, ni todo generador usa un transformer.

## 2. Tokenización

`agua norte bajo .` produce cuatro tokens conocidos. `Agua norte bajo.` produce tres: `Agua` y `bajo.` se convierten en UNK porque la práctica no normaliza mayúsculas ni separa puntuación automáticamente. `norte` sigue conocido. Dos textos distintos pueden colapsar al mismo patrón de IDs desconocidos: el modelo ya no conserva información suficiente para reconstruir cada palabra original.

## 3. Atención manual

En la segunda fila las puntuaciones escaladas son `[0,ln(2),ln(2)]`. Tras máscara, `[0,ln(2),−∞]`; exponentes `[1,2,0]`; pesos `[1/3,2/3,0]`. La salida es `[2/3,4/3]`. En la tercera fila no se oculta ninguna posición: exponentes `[2,2,4]`, pesos `[1/4,1/4,1/2]`, salida `[1.5,1.5]` usando punto decimal como Python. La primera fila da pesos `[1,0,0]` y salida `[2,0]`.

El programa [03_atencion_y_temperatura.py](03_atencion_y_temperatura.py) contrasta estos resultados con la implementación y con PyTorch.

## 4. Diagonal y futuro

Si la entrada actual es `salida`, su objetivo es el primer token de la continuación. Atender `salida` usa información disponible. Consultar el token siguiente de la secuencia completa durante entrenamiento sí revelaría la respuesta: por eso la máscara prohíbe posiciones posteriores. El desplazamiento y la máscara deben ser correctos juntos. Sin máscara, cambiar V₃ altera las salidas de posiciones 1 y 2; con máscara no las altera.

## 5. Dimensiones y costo

Los pesos tienen forma `16×2×18×18`: 10368 celdas. Si T pasa de 18 a 36, serían 41472 celdas, cuatro veces más. Eso solo describe esta matriz; embeddings, proyecciones y red feed-forward tienen otros costos. Además, nuestro modelo no admite T=36: dispone de 24 posiciones aprendidas. Habría que cambiar arquitectura y protocolo antes de ejecutar ese caso.

## 6. Objetivos de pérdida

Una instrucción breve aporta cinco objetivos: los valores del tema, zona y nivel, el punto y EOS. En el ejemplo serían `agua norte bajo . EOS`. El resto del prefijo no entra al promedio de CE. Una detallada aporta nueve objetivos. Hay 32 familias de entrenamiento y dos formatos por familia: `32×(5+9)=448`. La pérdida pondera tokens; una detallada contribuye más que una breve. PAD se excluye, EOS se incluye.

## 7. CE y perplejidad

`−ln(2/3)=0,405465…`; `exp(CE)=1,5`. Si un corpus tiene varios tokens, primero se calcula la CE media y después se aplica la exponencial: no es la media aritmética de perplejidades por token. Cambiar tokenización cambia unidades, vocabulario y número de objetivos. Tampoco una perplejidad baja demuestra verdad: solo alta probabilidad para las respuestas de ese conjunto bajo el protocolo.

## 8. Token frente a secuencia

La referencia de bigramas recibe el token correcto anterior en la evaluación por token y acierta, por ejemplo, conectores o EOS. Al generar desde `salida`, solo recuerda esa última palabra y puede elegir `informe` aunque el prefijo pida formato breve. Sus decisiones equivocadas pasan a ser contexto. El primer caso pide `energia norte medio .` y produce `informe aire en este con nivel alto .`. Su exactitud por token es 68/112, pero ninguna de las 16 generaciones cumple toda la continuación. La coincidencia exacta exige texto correcto y EOS.

## 9. Temperatura

Para logits `[ln(4),ln(2),0]`, T=1 produce `[4/7,2/7,1/7]`. Con T=2 los pesos son `[2,√2,1]`; al dividir por `3+√2` resultan aproximadamente `[0,453082;0,320377;0,226541]`. El máximo es el primer token en ambos casos. Codicioso lo elige siempre; muestreo puede elegir cualquiera según su probabilidad y la semilla. Temperatura positiva cambia probabilidades sin cambiar el orden; no aprende información adicional.

## 10. Interpretación del cierre y fallos

El cierre conserva el estado elegido y obtiene CE≈0,002820 y 16/16 continuaciones exactas. Eso respalda aprendizaje de dependencias en esta gramática y en combinaciones reservadas. No demuestra conocimiento de energía o ambiente. `oceano` se convierte en UNK y se reemplaza por `suelo` en la salida; el modelo no recupera la identidad perdida. Un prefijo incompleto termina en `.` y EOS porque el entrenamiento no enseñó a completar prefijos. Con máximo de dos tokens nuevos se corta una continuación, aunque sus dos primeros tokens puedan ser correctos; el motivo `max_nuevos` no debe confundirse con EOS.

Una conclusión adecuada conserva tanto el éxito en el dominio sintético como los límites fuera de él. Para estudiar otro dominio o elegir nuevos parámetros harían falta desarrollo y cierre nuevos; el resultado de prueba publicado ya es conocido.

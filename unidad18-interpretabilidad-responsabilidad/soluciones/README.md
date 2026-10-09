# Soluciones — Interpretabilidad y responsabilidad

[Volver a los ejercicios](../README.md#10-ejercicios-y-reto) · [Ejemplo manual ejecutable](03_explicar_a_mano.py)

## 1. Tipo de explicación

Reconstruir un caso es una explicación local del modelo. Medir el aumento de MAE al permutar describe dependencia del rendimiento en una muestra, una métrica y un modelo fijos. Reducir consumo real mediante una intervención es una pregunta causal: requiere un diseño y supuestos que permitan identificar el efecto, por ejemplo un experimento pertinente y seguro. Una asociación aprendida, una contribución local y una importancia por permutación no bastan para responderla.

## 2. Dos descomposiciones

`10 + 3×1 + 3×1 + 1×(−1) = 15` y `10 + 6×1 + 0×1 + 1×(−1) = 15`.

La diferencia entre predicciones es `3×(z0−z1)`. Es cero sobre todos los casos que cumplen `z0=z1`; puede dejar de ser cero al romper esa relación. En general, sumar a un coeficiente un valor `a` y restarlo del otro agrega `a×(z0−z1)`. La explicación de cada modelo puede ser fiel y repartir cantidades distintas. No prueba que cada variable sea responsable de una fracción física del consumo.

## 3. Unidades originales

Coeficientes originales: `[3/1; 3/60] = [3; 0,05]`. El intercepto es `10−3×2−0,05×120=−2`.

Para `[3,180]`: `−2+3×3+0,05×180=16`. La forma estandarizada da z=[1,1] y `10+3+3=16`. Al cambiar una hora coherentemente se cambian también 60 minutos; la pendiente efectiva es `3+60×0,05=6`, no solo 3. Un intercepto original negativo no vuelve negativas todas las predicciones y puede corresponder a una entrada fuera de la muestra.

## 4. Caso real del laboratorio

C-validacion-000 tiene z aproximadamente `[1,631360; 1,631360; −0,395614]`. Sus coeficientes estandarizados son `[3,406519; 3,406519; 1,123332]` y la base es 23,862638 kWh.

Contribuciones: `[5,557260; 5,557260; −0,444406]`. Suma: 34,532752 kWh. Al evaluar la ecuación en unidades originales se obtiene el mismo resultado, salvo redondeo. Su pendiente conjunta respecto de horas es aproximadamente `1,5101448104 + 60×0,0251690802 = 3,0202896208 kWh/h`.

El modelo tiene tres columnas pero rango dos; horas y minutos codifican la misma información. Esta dependencia impide interpretar cada coeficiente aislado como un efecto separado. La temperatura contribuye negativamente en este caso porque está por debajo de la media de entrenamiento y su coeficiente es positivo; no significa que su coeficiente sea negativo.

## 5. Permutación manual

Deltas: `[0,3; 0,5; 0,1]`; media = 0,3. La varianza poblacional es `[(0,3−0,3)² + (0,5−0,3)² + (0,1−0,3)²]/3 = 0,026666…`; la desviación es aproximadamente 0,163299, en las mismas unidades que el MAE.

Un delta negativo significa que esa permutación mejoró el MAE de ese modelo en esas filas. Puede ocurrir por azar, uso perjudicial de una entrada o inestabilidad; no se reemplaza automáticamente por cero ni demuestra inutilidad universal. Cambiar la métrica podría cambiar la importancia. Ni tres ni treinta permutaciones convierten esa desviación en incertidumbre sobre una población nueva.

## 6. Dependencia entre entradas

Permutar horas sin mover minutos rompe una conversión exacta y deja otra copia de la señal accesible al modelo. Mover las dos columnas con los mismos índices preserva la relación entre ellas y rompe simultáneamente su correspondencia con las etiquetas de las filas receptoras. No reentrenamos ni quitamos columnas.

En los recursos, los aumentos individuales medios son 3,814 y 3,814 kWh; el conjunto es 7,882 kWh. La suma individual ronda 7,629 y no coincide con el conjunto. MAE aplica valor absoluto antes de promediar, por lo que no hay una identidad aditiva entre estas perturbaciones. Tampoco habría una garantía general para otros modelos o pérdidas. La comparación de este bloque no certifica independencia respecto de temperatura ni validez causal.

## 7. Ruta del árbol

Lectura 0: en nodo 0 cumple `<=0,550354987…` y pasa al 1; allí cumple `<=0,295959994…` y llega a hoja 2. Entre sus 92 casos de entrenamiento hay 1 positivo: fracción 1/92=0,010869565…; la clase mayoritaria es 0.

Esto reconstruye una operación del modelo. No garantiza que la nueva fila tenga una probabilidad real de revisión exactamente igual a 1/92, que esa frecuencia sea adecuada para cada grupo ni que la lectura explique causalmente la etiqueta. Los números de nodo son identificadores internos, no grados de riesgo. Redondear umbrales antes de comparar puede cambiar las rutas; el programa preserva los valores completos y la conversión de entrada de la biblioteca.

## 8. Denominadores

A: recobrado 8/(8+2)=0,8. B: 1/(1+1)=0,5. Media simple: (0,8+0,5)/2=0,65. Conjunto: (8+1)/(10+2)=0,75. Este último equivale a ponderar recobrados por cantidad de positivos, pesos 10/12 y 2/12.

Con VP=0 y FN=3, recobrado=0: omitimos tres positivos. Con VP=FN=0, el recobrado no está definido. No se deben transformar valores indefinidos en ceros para calcular promedios; sería introducir una afirmación que los datos no permiten. La precisión necesita alertas y la tasa FP necesita negativos; sus denominadores son distintos.

## 9. Grupos y cobertura

`escaso` aporta cuatro negativos de validación: podemos contar sus resultados, pero no estimar cómo se detectan positivos allí. `nuevo` no aporta filas: no hay rendimiento medible y su fracción de la muestra es cero. `desplazado` omite 12 de 19 positivos, una limitación grave del ejemplo aunque solo genere cero FP en esa muestra.

El árbol usa únicamente lectura, pero esa lectura cambia con la condición de medición. Excluir grupo no borra esa dependencia ni garantiza resultados comparables. Cambiar nombres de grupo altera la auditoría sin mejorar ninguna predicción. La conclusión debe especificar qué grupos se definieron, cuántos casos tienen y cómo se obtuvieron las etiquetas; no basta una brecha o una métrica global.

## 10. Respuesta a un error

Una respuesta proporcionada para este ejercicio:

1. Quien realiza la práctica conserva ID ficticio, lectura, versión del código, huella de datos, predicción, ruta y evidencia de la etiqueta; evita cambiar silenciosamente el registro original.
2. Reconstruye la ruta para descartar un error de implementación y revisa si la lectura corresponde a una condición desplazada. La ruta correcta no descarta un fallo predictivo.
3. Registra la omisión en la ficha y mantiene la decisión de uso didáctico. En una propuesta operativa habría que definir responsable con capacidad de detener automatización, un procedimiento manual y revisión de casos no alertados; todavía no están implementados aquí.
4. Ante una condición nueva, reconoce falta de cobertura y obtiene evidencia con etiquetas antes de afirmar rendimiento. No usa n=0 como prueba de ausencia de errores.
5. Si modifica medición o modelo, abre otra versión y reserva nueva evaluación independiente. No reutiliza el cierre publicado para afirmar que el cambio generaliza.

Consulta la [ficha completa](../recursos/ficha_alertas.md) para conectar esas acciones con daños posibles y límites de supervisión.

## Resultado del cierre didáctico

Con `--evaluar-prueba`, consumo tiene n=80, MAE 0,379073 y RMSE 0,454200 kWh. Alertas tiene n=114, VP=37, VN=65, FP=0 y FN=12: precisión=1 y recobrado=37/49≈0,755.

En alertas estándar: VP=34, FN=1, recobrado=34/35≈0,971. En desplazado: VP=3, FN=11, recobrado=3/14≈0,214. Escaso conserva cuatro negativos; nuevo sigue sin filas. No se reemplaza el árbol después de ver estos resultados y no se los presenta como una certificación de operación. La explicación fiel de sus rutas convive con esas omisiones.

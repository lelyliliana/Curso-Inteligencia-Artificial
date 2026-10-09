# Reto — Explicar y comparar decisiones con árboles

[Unidad](README.md) · [Plantilla](plantillas/informe_arboles.md)

## Situación

Debes justificar qué candidato usarías para el cierre de **uno** de los dos laboratorios. La entrega debe permitir revisar los datos, el ajuste, una predicción, la comparación y sus limitaciones. La meta es explicar un procedimiento correcto; no conseguir la mayor puntuación posible.

## Trabajo

1. Elige `franja` o `region`. Define caso, entradas, etiqueta, clase positiva y momento de predicción. Distingue disponibilidad declarada de evidencia temporal ausente.
2. Registra el [protocolo](datos/protocolo.md) antes del cierre: candidatos, parámetros, semilla, Gini, combinación cuando corresponda, decisión de clase, F1 de selección y desempates.
3. Ejecuta desarrollo con `--salida` y `--graficos` en una carpeta nueva bajo `resultados/unidad13/`. Conserva comando, commit, versiones y huellas. Confirma `prueba: null`.
4. Reproduce a mano el cálculo de Gini de un corte del ejemplo de ocho casos. Explica por qué se ponderan los hijos y cómo un mínimo por hoja puede impedir el corte.
5. Explica una predicción. En `franja`, recorre el árbol controlado para 60 y calcula la probabilidad de su hoja. En `region`, calcula el promedio ilustrativo de `0,2; 0,6; 0,6`, distingue el voto de clases y explica cómo verificarías el promedio de los 31 árboles reales. Identifica un caso real del CSV y su probabilidad exportada, sin atribuirle las probabilidades del ejemplo ilustrativo.
6. Compara todos los candidatos sobre los mismos casos. Reconstruye una matriz de confusión desde CSV y calcula precisión, recobrado y F1. Explica cualquier métrica indefinida. Justifica la elección por la regla previa.
7. Analiza al menos un FP y un FN del elegido en validación, con sus identificadores. Interpreta una figura y relaciona el resultado con complejidad o diversidad del ensamble. Explica qué evidencia falta para valorar el costo real de esos errores.
8. Guarda por escrito el elegido y la configuración antes de abrir prueba. Ejecuta `--evaluar-prueba` y exporta a otra carpeta. Comprueba coincidencia de código, entorno, protocolo, huellas de desarrollo, modelos y selección.
9. Informa el cierre del único elegido sin cambiarlo después. Separa diferencias observadas de conclusiones sobre calibración, estabilidad, cobertura o utilidad real.
10. Ejecuta las 30 pruebas de la unidad. Identifica una comprobación matemática y otra de separación de datos; explica sus límites.

Opcional: estudia la variante de semilla 29 o la consulta 100 de `franja`. Regístrala aparte. No elijas una semilla por su resultado ni modifiques etiquetas para mejorar la métrica. No se exige añadir modelos, calibrar ni buscar hiperparámetros nuevos.

El generador, prueba y las soluciones son públicos. Declara qué conocías antes de comenzar; la entrega puede demostrar el flujo sin presentarse como una evaluación personal ciega.

## Entrega y evaluación

Informe de aproximadamente dos a cuatro páginas en Markdown o formato equivalente, exportaciones de desarrollo y cierre —JSON, CSV y reglas— y figuras de desarrollo. Utiliza la [plantilla](plantillas/informe_arboles.md); conserva los datos originales.

| Criterio | Puntos | Evidencia para puntaje completo |
|---|---:|---|
| Formulación y datos | 15 | Entradas, etiqueta, disponibilidad y límites del escenario explícitos |
| Ajuste y protocolo | 20 | Candidatos, controles, semilla y decisiones previas; Gini separado de F1 |
| Cálculo y comparación | 20 | Gini ponderado, predicción o promedio y matriz correctamente reconstruidos |
| Errores e interpretación | 20 | FP y FN identificados; figura y complejidad o ensamble explicados con límites |
| Cierre | 15 | Solo el elegido, configuración conservada y sin reselección |
| Reproducción y pruebas | 10 | Comandos, versiones, huellas, archivos completos y controles explicados |
| **Total** | **100** | |

Referencia de autoevaluación: 80 puntos o más y ningún error crítico pendiente. Son errores críticos entrenar con validación o prueba, incluir la etiqueta entre las entradas, seleccionar mirando prueba, confundir promedio de probabilidades con voto de clases en estos modelos o presentar una hoja pura como certeza sobre casos futuros.

## Revisión final

- ¿Cada comparación usa los mismos casos y el mismo criterio?
- ¿Se diferencian parámetros configurados de complejidad realmente obtenida?
- ¿Se sabe qué conjunto generó cada corte, frecuencia y muestra bootstrap?
- ¿La matriz suma el total de casos y las fórmulas respetan denominadores cero?
- ¿Se conserva lo decidido antes del cierre?
- ¿Las conclusiones reconocen que los datos son sintéticos y públicos?

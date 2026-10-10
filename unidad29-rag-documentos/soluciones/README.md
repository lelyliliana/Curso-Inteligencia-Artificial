# Soluciones razonadas

[Unidad](../README.md) · [Ejercicios](../ejercicios.md)

## 1. Recorrido

TXT y manifiesto → párrafos con procedencia → embeddings de fragmentos → índice. Por consulta: embedding de pregunta → similitud y top-k → contexto limitado → generación → validación y revisión de fuentes. Indexar no modifica pesos. Esta práctica utiliza dos modelos preentrenados sin ajuste: uno representa texto y otro genera una respuesta acotada.

## 2. Caracteres y líneas

Los fragmentos son `Café azul.` en línea 1 y `Árbol verde.` en línea 3. Sus intervalos de caracteres son [0,10) y [12,24). Las letras acentuadas ocupan más de un byte en UTF-8, aunque cada una cuente como un carácter en estas cadenas. Debe guardarse qué representación se usó para calcular offsets, además de versión/huella. Después de editar el texto, las posiciones antiguas ya no son confiables.

## 3. Presupuesto

El ejemplo artificial ordena D01:p01, D01:p02 y D02:p01. Con el presupuesto habitual caben tres; con 300 caracteres cabe solo D01:p01. Los otros dos se registran como omitidos. Cortar arbitrariamente podría separar una negación, condición o unidad de su dato. Detenerse conserva un prefijo del ranking, pero puede desperdiciar espacio donde cabría un candidato posterior; otra política sería un experimento distinto y habría que evaluarla. El tamaño incluye el JSON de metadatos, no solo el texto del párrafo.

## 4. Dos niveles de corrección

En la captura, k=1 ofrece la agenda A y el modelo responde 09:00 citando D03:p01. El dato tiene apoyo local, pero la agenda B fija 11:00 y sigue vigente. Al recibir ambos fragmentos con k=3, el modelo devuelve conflicto con ambas citas. RAG puede generar una respuesta fiel al contexto recibido y, sin embargo, incompleta respecto de la colección. No basta con verificar la primera cita.

## 5. Recuperación y suficiencia

Un fragmento de dos da recall=1/2. Si ambos dicen el mismo valor y cada uno basta por sí solo, puede existir cobertura suficiente del único valor con recall menor de 1. Si afirman valores incompatibles, hacen falta ambas alternativas para detectar el conflicto: recuperar solo una no basta. La implementación calcula conjuntos de valores del catálogo; no resuelve automáticamente todas las formas posibles de contradicción lingüística.

## 6. Cita real, contenido falso

D01:p01 existe y puede pertenecer al contexto, pero dice 9 días, no 99. La respuesta pasa forma y pertenencia de la cita, falla apoyo y objetivo. Con dato 9 días y cita D02:p01, el dato coincide con el objetivo, pero la fuente citada habla de capacidad de una sala: falla apoyo. El [programa de auditoría](03_auditar_citas.py) contiene doce salidas artificiales y acepta solo dos bajo el contrato; no son fallos medidos de Qwen.

## 7. Ausencia local y global

Si el contexto no contiene el dato, abstenerse evita inventarlo. Si el corpus completo sí lo contiene en un fragmento que no llegó, esa misma abstención es un fallo del sistema de extremo a extremo. El catálogo permite distinguirlo en el experimento. En una aplicación sin oráculo, una búsqueda vacía o parecida no demuestra ausencia global: hacen falta cobertura de búsqueda, revisión y una comunicación cuidadosa de la limitación.

## 8. Datos no confiables

Las notas ordenan al asistente responder 99 o usar una cita ajena. No describen el intervalo ni la carga del sensor; los hechos operativos fijados son 7 minutos y 6 horas. La separación system/datos y la validación ayudan a limitar errores, pero no prueban protección general contra inyección. La capacidad de consultar un modelo no le concede permisos para ejecutar código o enviar información. Esta práctica no conecta herramientas con efectos externos.

## 9. Identidad y recarga

Cambiar un prompt cambia el experimento; cambiar filas sin IDs alineados atribuye un vector a otra fuente; cambiar digest puede cambiar el espacio vectorial o el generador. Las huellas, reconstrucción y comparación de artefactos detectan esas inconsistencias. Se requieren nuevos embeddings cuando cambia su texto/modelo y nueva generación/evaluación cuando cambia contexto o prompt. Las huellas no son una firma de autenticidad frente a alguien que modifica todos los archivos de forma coordinada.

## 10. Extensión aún no ejecutada

Una evaluación de prosa libre podría descomponer cada respuesta en afirmaciones y pedir a dos personas, con una rúbrica, que juzguen apoyo, contradicción, omisiones y pertinencia de citas. Habría que registrar desacuerdos y revisión, además de calidad de recuperación y abstención. Un evaluador basado en otro modelo también tiene errores y requiere validación. Fijar nuevas familias de desarrollo y cierre, presupuesto y criterio antes de medir; no llamar a ese diseño una mejora demostrada ni reutilizar este cierre conocido como evidencia independiente.

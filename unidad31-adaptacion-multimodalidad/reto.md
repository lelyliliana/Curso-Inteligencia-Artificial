# Reto — Adaptación y entradas complementarias

[Unidad](README.md) · [Plantilla de informe](plantillas/informe.md)

Diseña una extensión de uno de los laboratorios y entrega una evaluación reproducible. Elige una ruta:

- **Adaptación:** añade un indicador de tarea para conservar la convención antigua y aprender una nueva. Compara una referencia sin adaptación, ajuste completo y una adaptación eficiente. Mantén una prueba de retención con objetivos compatibles y una reserva nueva por familias.
- **Multimodalidad:** añade escenas o consultas donde el emparejamiento de imagen y texto importe de otra manera. Compara modalidades aisladas y combinadas, conserva escenas completas en cada partición y define qué hacer si falta una entrada.

No basta con aumentar épocas hasta acertar la prueba. Antes de entrenar, escribe datos, particiones, métricas, candidatos, presupuestos y desempates. Una ruta puede quedarse en CPU con datos pequeños y propios; no requiere una API ni un modelo de gran tamaño.

## Entregables

1. Pregunta, alcance y procedencia de datos/modelos, con diagrama de entradas y salidas.
2. Generador o archivos versionados, familias nuevas y evidencia de separación. En adaptación, declarar exposición de la base a las entradas de cierre.
3. Referencia programada o congelada, candidatos y protocolo previo. Distinguir tamaño entrenable de memoria o tiempo medidos.
4. Resultados de desarrollo, selección y cierre sin ajuste; incluir al menos un diagnóstico que muestre un límite.
5. Estados y configuración para recargar, comprobación de predicciones y pruebas de una propiedad esencial: base intacta o modalidad realmente excluida, según la ruta.
6. Informe con fallos y límites de la conclusión; separar rechazo programado de abstención aprendida.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia |
|---|---:|---|
| Formulación y alcance | 10 | Tarea concreta y capacidades no demostradas |
| Datos y particiones | 20 | Procedencia, familias y exposición previa documentadas |
| Referencias y protocolo | 20 | Comparaciones pertinentes y decisiones previas al cierre |
| Implementación comprobada | 20 | Gradientes/pesos o modalidades, preparación y errores |
| Evaluación y límites | 20 | Métricas, cierre, casos difíciles y conclusiones proporcionadas |
| Recarga y documentación | 10 | Comandos reproducibles y resultados conservados |

Una entrega que usa datos de prueba para elegir configuración debe rehacer la evaluación con una nueva reserva. No se exige obtener un porcentaje alto: una comparación negativa bien documentada también responde la pregunta.

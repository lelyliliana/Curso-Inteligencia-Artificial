# Reto — Propuestas explicables y agenda viable

[Volver a la unidad](README.md) · [Plantilla](plantillas/informe_conocimiento.md)

## Escenario

Diseña un caso sintético de energía, educación o gestión ambiental. Primero representa hechos y reglas para proponer una revisión. Después organiza tres o cuatro actividades mediante variables, dominios y restricciones.

Los programas de la unidad permiten estudiar cada componente por separado. Documenta cómo se relacionan sus resultados; no supongas una integración automática ni una ejecución de acciones reales.

## Trabajo

1. Describe un caso único y el significado de sus símbolos. Identifica qué observaciones habría que comprobar antes de convertirlas en hechos.
2. Crea una copia de la base con al menos cuatro reglas, una cadena de dos pasos y un par de propuestas incompatibles.
3. Predice y ejecuta un caso normal, uno con evidencia incompleta y uno con incompatibilidad. Reconstruye la justificación de una consulta.
4. Define tres o cuatro actividades, dominios pequeños y al menos tres restricciones. Usa solo los operadores soportados; una condición diferente debe explicarse como extensión pendiente o implementarse y verificarse.
5. Compara enumeración, retroceso fijo y MRV, separando el efecto de la poda. Conserva los conjuntos de soluciones y define cada contador.
6. Diseña una variante imposible y justifícala sin depender únicamente de la salida del programa.
7. Añade una condición propia al escenario. Predice qué resultado cambia, ejecútalo y explica cualquier diferencia.
8. Explica qué revisión humana o validación del contexto necesitarías para pasar del ejercicio a una aplicación.

## Entregables

- Archivos JSON del caso y sus variantes, documentados como sintéticos.
- Informe basado en la [plantilla](plantillas/informe_conocimiento.md).
- Comandos y salidas relevantes, con versión de Python y parámetros.
- Traza de una inferencia y de una búsqueda de horario.
- Resultado de las pruebas existentes y comprobaciones de tus cambios.

## Rúbrica — 100 puntos

| Criterio | Puntos | Evidencia esperada |
|---|---:|---|
| Representación y alcance | 20 | Símbolos definidos, caso delimitado y supuestos explícitos |
| Reglas y explicación | 20 | Cadena trazable y manejo correcto de evidencia incompleta e incompatibilidad |
| Formulación del CSP | 20 | Dominios y restricciones fieles al escenario; interpretación de soluciones |
| Verificación y comparación | 25 | Referencia manual o exhaustiva, caso imposible, variantes y contadores bien interpretados |
| Reproducibilidad y límites | 15 | Archivos, comandos, versión, conclusión proporcional y necesidades de validación |

Objetivo de autoevaluación: al menos 80 puntos. Revisa el trabajo aunque supere ese valor si queda una contradicción entre explicación y código, una solución que incumple restricciones o una afirmación de imposibilidad basada en una ejecución incompleta.

No se requieren datos personales, servicios externos ni software adicional.

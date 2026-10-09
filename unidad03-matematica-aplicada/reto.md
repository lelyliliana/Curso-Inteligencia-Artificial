# Reto — Un experimento matemático reproducible

Construye un pequeño experimento que permita explicar cómo se representan los datos, cómo se calcula una predicción y cómo se actualizan parámetros. Usa el caso de consumo incluido o crea una relación sintética sencilla en educación, gestión ambiental o sensores.

El resultado esperado es una explicación verificable del procedimiento, no una afirmación de eficacia en un entorno real.

## Condiciones

- Trabajo individual o en equipo de hasta tres integrantes.
- Python con biblioteca estándar es suficiente. Si añades una dependencia, justifica su uso y documenta instalación y versión.
- Todos los datos deben declararse sintéticos. No incluyas información personal ni mediciones reales en este reto.
- Mantén entrenamiento y prueba declarados antes del ajuste. Si seleccionas configuraciones según una evaluación, identifica esos datos como validación y reserva otros para la comparación final.
- Puedes reutilizar código del curso, indicando qué reutilizaste, qué modificaste y por qué.

## Desarrollo

1. **Pregunta y representación.** Define la cantidad que estimarás y el significado, orden y unidad de las entradas. Escribe las formas de $X$, pesos y salida. Para el laboratorio incluido, $X$ tiene cuatro filas y una característica en entrenamiento.
2. **Datos y procedencia.** Conserva el CSV original o guarda tu propia variante. Explica cómo generaste referencias y particiones, y si hay ruido o cambios de escala.
3. **Cálculo manual.** Desarrolla una predicción, los residuos de entrenamiento, el MSE, ambos gradientes y una actualización simultánea. Contrasta con el programa.
4. **Trayectorias de optimización.** Compara al menos tres tasas en la cuadrática, con el mismo inicio y número de pasos. Incluye una que converja y otra que oscile o diverja. Registra los valores numéricos que sustentan la explicación.
5. **Ajuste y comparación.** Ejecuta la recta con una configuración declarada. Calcula la línea base usando entrenamiento y compara ambas alternativas en la misma prueba.
6. **Separación de datos.** Cambia solo las referencias de prueba en una copia y comprueba que los parámetros entrenados permanecen iguales. Explica qué cambia en la evaluación.
7. **Escala y límites.** Explica qué pasaría al pasar de horas a minutos y por qué la tasa puede requerir revisión. Describe qué no demuestra el resultado sintético.

Los puntos 4 y 5 son experimentos diferentes. No uses el intervalo estable de la cuadrática como si fuera automáticamente válido para la recta.

## Entrega

Un repositorio con:

- README que presente pregunta, organización y comandos desde la raíz.
- CSV utilizado y declaración de procedencia sintética.
- Código ejecutable y explicación de modificaciones.
- Informe con cálculos, resultados, condiciones y limitaciones; puedes completar la [plantilla](plantillas/informe_experimento.md).
- Enlaces accesibles al material de apoyo. Entrega enlaces, sin depender de archivos adjuntos.

Para una actividad evaluable, incluye un video de 3 a 5 minutos con cámara. Explica un cálculo, una actualización y una conclusión con sus límites. Declara el uso de herramientas de IA: qué aportaron, qué verificaste y qué corregiste. En equipo, indica los aportes de cada integrante.

## Rúbrica

| Criterio | Puntos |
|---|---:|
| Representación, unidades y dimensiones | 15 |
| Procedencia y partición de datos | 15 |
| Cálculo manual y actualización consistente | 25 |
| Trayectorias y explicación de tasas | 15 |
| Línea base, comparación y separación de prueba | 20 |
| Reproducibilidad, límites y comunicación | 10 |
| **Total** | **100** |

Un gradiente incorrecto, una evaluación usada para ajustar sin declararlo o una atribución real a datos sintéticos requiere corregir el razonamiento. La presentación visual no sustituye esas comprobaciones.

[Volver a la unidad](README.md) · [Consultar soluciones](soluciones/README.md)

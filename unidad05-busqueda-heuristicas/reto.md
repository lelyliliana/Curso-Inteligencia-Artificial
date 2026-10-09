# Reto — Modelar y comparar una búsqueda

Construye un escenario sintético donde una secuencia de acciones deba alcanzar una meta. Puedes adaptar el grafo de rutas, el mapa de celdas o representar etapas de una tarea con reglas explícitas.

El objetivo es comprobar el componente de búsqueda en un modelo delimitado y comparar sus decisiones. No se requiere control de hardware ni datos reales.

## Condiciones

- Individual o en equipo de hasta tres integrantes.
- Biblioteca estándar suficiente. Documenta dependencias si añades alguna.
- Datos sintéticos y procedencia declarada.
- Grafo finito con costos no negativos y una meta, conforme al formato del núcleo.
- Conserva originales y guarda variantes por separado.
- Si el problema requiere inventario, tiempo o recursos, explica cómo se representarían y qué parte implementaste.

## Desarrollo

1. **Formulación.** Define estado, inicio, acciones, transición, meta y criterio de costo. Justifica que situaciones con futuros distintos no se confundan.
2. **Modelo.** Construye un JSON de entre cuatro y doce estados, o una cuadrícula pequeña. Documenta dirección de transiciones, costos, unidades, vecinos y límites.
3. **Traza manual.** Desarrolla BFS y UCS en el grafo o BFS y A* en la cuadrícula. Identifica frontera, g y el momento de aceptar meta.
4. **Comparación.** En el grafo compara BFS, DFS, UCS, voraz y A*. En la cuadrícula compara BFS, UCS y A*. Verifica ruta y costo; registra las métricas con la convención del curso.
5. **Heurística.** Justifica admisibilidad y consistencia. En el grafo pequeño puedes usar la auditoría; en la cuadrícula explica las acciones que justifican Manhattan. Si usas h=0, explica por qué es válida y qué información no aporta.
6. **Caso de reapertura.** Ejecuta el ejemplo incluido con factores 1 y 2. Explica qué ocurre con A y por qué el segundo pierde optimalidad. Este caso puede quedar separado de tu escenario propio.
7. **Variante sin ruta.** Conserva la meta declarada y modifica conexiones u obstáculos para volverla inalcanzable. Contrasta ese resultado con una entrada inválida.
8. **Verificación y límites.** Ejecuta las pruebas incluidas, documenta el resultado y plantea una comprobación adicional pertinente a tu modelo. Señala lo que falta para usarlo en una aplicación real.

Si generas un SVG con el laboratorio, utiliza un destino nuevo. La figura debe corresponder a los datos y ruta de la ejecución documentada.

## Entrega

Un repositorio con:

- README con pregunta, organización y comandos desde la raíz.
- Datos originales o referencia a los del curso, variantes y procedencia.
- Código utilizado, modificaciones y comprobaciones.
- Informe con cálculos, trazas, comparación y limitaciones; puedes completar la [plantilla](plantillas/informe_busqueda.md).
- Enlaces accesibles al material de apoyo, sin depender de adjuntos.

Para una actividad evaluable, añade un video de 3 a 5 minutos con cámara. Explica una traza, la justificación de h y una conclusión limitada al modelo. Declara herramientas de IA utilizadas, aportes, verificaciones y correcciones. En equipo, identifica contribuciones.

## Rúbrica

| Criterio | Puntos |
|---|---:|
| Formulación y suficiencia del estado | 20 |
| Modelo, costos y procedencia | 15 |
| Traza manual y comparación coherente | 25 |
| Heurística, reapertura y condiciones | 20 |
| Casos límite, pruebas y reproducibilidad | 10 |
| Interpretación, límites y comunicación | 10 |
| **Total** | **100** |

Una ruta que no respeta transiciones, un costo que no coincide con su suma o una garantía de A* sin las condiciones necesarias debe corregirse. La evaluación valora la formulación y la evidencia, además de que el programa termine.

[Volver a la unidad](README.md) · [Consultar soluciones](soluciones/README.md)

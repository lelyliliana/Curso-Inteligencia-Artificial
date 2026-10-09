# Soluciones comentadas — Unidad 5

Compara con tu intento. Si una traza cambia, revisa orden de vecinos, momento de registrar estados, prioridad y desempate antes de atribuirlo a un error del algoritmo.

## 1. Formulación con llave

Un estado posible es `(fila,columna,tiene_llave)`. La situación inicial debe incluir posición y un indicador falso o verdadero según el escenario. Las acciones pueden ser moverse a una celda libre, recoger la llave cuando está presente y abrir la puerta si se tiene.

Las transiciones actualizan posición o inventario. La meta puede ser llegar a una celda final después de abrir la puerta; el costo puede contar movimientos y acciones, si se define así.

Dos situaciones en la misma posición pero con inventarios distintos permiten acciones diferentes. Registrarlas como un único estado puede podar un camino necesario.

El laboratorio de cuadrícula solo representa posición. Para implementar la llave hay que ampliar estados y sucesores; cambiar una letra en el mapa no añade esas reglas al programa.

## 2. BFS y DFS

Con vecinos de S ordenados A, B:

| Método | Estados expandidos | Meta extraída | Ruta | Pasos |
|---|---|---|---|---:|
| BFS | S, A, B, C | G | S → B → G | 2 |
| DFS | S, A, C, D | G | S → A → C → D → G | 4 |

Para BFS, con próxima extracción a la izquierda, las fronteras son S; A,B; B,C; C,G; G,D. Se extrae G y termina antes de expandir D.

Para DFS, usando una pila escrita desde base hasta tope, las fronteras son `[S]`, `[B,A]`, `[B,C]`, `[B,D]`, `[B,G]`. La arista D → A se descarta por repetición.

Ambos generan seis entradas, incluida la inicial, y el pico de frontera es dos. Esas coincidencias no implican las mismas expansiones ni el mismo camino.

Con vecinos de S ordenados B, A, la DFS iterativa del programa extrae B primero y encuentra S → B → G. El resultado depende del orden; no establece una garantía general de optimalidad para DFS.

## 3. Caminos y objetivo

En el grafo principal, los caminos simples de S a G son:

| Camino | Pasos | Costo |
|---|---:|---:|
| S → A → G | 2 | 6+6=12 |
| S → B → D → A → G | 4 | 1+1+2+6=10 |
| S → B → D → G | 3 | 1+1+4=6 |
| S → C → G | 2 | 4+1=5 |

BFS devuelve el primero por su política de vecinos y descubrimiento. Tiene la menor profundidad, compartida con S → C → G, pero no el menor costo. La ruta mínima en minutos es S → C → G, costo 5.

Si el objetivo fuese únicamente minimizar cantidad de movimientos, ambas rutas de dos pasos serían óptimas bajo ese criterio. Debe identificarse la función de costo antes de comparar.

## 4. UCS

Las extracciones válidas son S:0, B:1, D:2, C:4, A:4 y G:5.

- A se descubre con costo 6 y mejora a 4 desde D.
- G se descubre con costo 6 desde D y mejora a 5 desde C.
- La propuesta A → G de costo acumulado 10 no mejora 5.

Se acepta la meta al extraer G:5. Las entradas antiguas pueden continuar en el heap; si se llegaran a extraer se descartarían como obsoletas.

En el caso alternativo S → G:10, S → A:1 y A → G:1, aceptar G al generarlo devolvería 10. UCS debe continuar hasta extraer G con costo 2. Una prueba incluida cubre específicamente ese error.

## 5. A* y desempates

En el caso principal:

| Estado extraído | g | h | f |
|---|---:|---:|---:|
| S | 0 | 5 | 5 |
| B | 1 | 4 | 5 |
| C | 4 | 1 | 5 |
| D | 2 | 3 | 5 |
| G | 5 | 0 | 5 |

S inserta A con f=7, B con f=5 y C con f=5. B se extrae antes de C y genera D con f=5, pero C se insertó antes que D. C genera G:5. D se insertó antes que G y se expande, mejorando A a g=4 y f=5. Esa entrada de A es posterior a G, por lo que G se extrae primero.

Expansiones: S, B, C y D. La solución cuesta 5. A* con h=0 coincide con UCS en prioridad, camino y traza, conservando las mismas convenciones.

## 6. Consistencia y admisibilidad

Las ocho desigualdades del caso principal son:

| Arista | Comprobación |
|---|---|
| S → A | 5 ≤ 6+1 |
| S → B | 5 ≤ 1+4 |
| S → C | 5 ≤ 4+1 |
| A → G | 1 ≤ 6+0 |
| B → D | 4 ≤ 1+3 |
| C → G | 1 ≤ 1+0 |
| D → A | 3 ≤ 2+1 |
| D → G | 3 ≤ 4+0 |

h(G)=0 y todas se cumplen, de modo que es consistente. Los costos restantes exactos son S:5, A:6, B:5, C:1, D:4 y G:0. h no supera ninguno: es admisible.

La consistencia implica admisibilidad porque, al encadenar las desigualdades de las aristas hasta la meta con h=0, h del inicio del camino queda acotada por la suma de sus costos. El caso de reapertura muestra que la implicación inversa no es general.

Puedes comprobar las tablas con:

```bash
python unidad05-busqueda-heuristicas/soluciones/01_auditar_heuristica.py
```

La auditoría calcula costos óptimos en el grafo declarado. No comprueba que ese grafo describa un entorno real.

## 7. Reapertura y sobreestimación

Con h(B)=2.5, las extracciones válidas de A* son:

```text
S(g=0), A(g=2), B(g=1), A(g=1.5), G(g=3.5)
```

A se expande dos veces. La ruta final S → B → A → G cuesta 3.5. h es admisible, pero inconsistente en B → A; la reapertura mantiene la solución de mínimo costo en esta implementación.

Con h(B)=5, se extrae S, después A con prioridad 2 y G con prioridad 4, antes de B con prioridad 6. Se devuelve S → A → G, costo 4. No existe oportunidad de reabrir A porque ya se aceptó una meta.

El costo restante real desde B es 2.5, por lo que 5 sobreestima. El contraejemplo demuestra que la garantía puede perderse; no afirma que cualquier sobreestimación siempre produzca una ruta peor.

## 8. Manhattan y mapa

Desde `(2,2)` a `(0,6)`:

$$
h=|2-0|+|2-6|=2+4=6
$$

En el mapa incluido existe la ruta `(2,2),(2,3),(2,4),(1,4),(0,4),(0,5),(0,6)`, de seis movimientos. Aquí la cota coincide con el costo óptimo restante.

Desde el inicio, Manhattan vale 6 pero la ruta cuesta 10 debido al rodeo. Una misma heurística puede ser exacta en un estado y subestimar en otro.

Si se admiten diagonales de costo uno, desde `(0,0)` a `(1,1)` se llega en un paso, mientras Manhattan da dos. En ese modelo sobreestima y no es admisible.

Bloquear `(2,3)` en una copia obliga a rodear por la parte inferior; el costo mínimo desde S pasa a 14. Bloquear `(0,1)` y `(1,0)` aísla el inicio y no queda ruta.

Si cambia el conjunto de acciones o su costo, vuelve a derivar la cota. No basta con conservar el nombre Manhattan.

## 9. Casos límite

| Situación | Resultado esperado |
|---|---|
| Inicio ya es meta | Camino con un estado, costo cero, cero expansiones |
| Meta declarada pero inalcanzable | `encontrado=False`, camino vacío, costo `None` |
| Ciclo de costo cero | No hay mejora estricta de g; se evita repetición indefinida |
| Arista negativa | Entrada rechazada con mensaje de error |
| Destino inexistente | Entrada inválida, no resultado de búsqueda |

Si inicio y meta no están declarados, no sabemos que el problema sea insoluble: sabemos que su representación es inválida. Esa diferencia debe conservarse en el informe.

La cuadrícula exige símbolos S y G distintos, por lo que inicio igual a meta se comprueba directamente en el núcleo, no mediante ese formato de archivo.

## 10. Comparación

Un informe debe fijar grafo o mapa, costos, heurística, orden de vecinos, desempates, versión y comando. Para cada método registra:

- Camino y verificación de transiciones.
- Pasos: longitud del camino menos uno.
- Costo: suma de aristas, no cantidad de estados.
- Expansiones: sucesores examinados; puede haber reaperturas.
- Entradas generadas y pico de frontera con la convención del programa.

En el caso principal, DFS y voraz usan dos expansiones y devuelven costo 12. A* usa cuatro y devuelve costo 5. Optimizar el trabajo de búsqueda y optimizar el costo de la solución son objetivos diferentes.

El pico de frontera cuenta entradas, incluidas obsoletas. No es una medición de bytes. Para comparar tiempo harían falta mediciones bajo condiciones controladas y suficientes repeticiones, considerando también cálculo de h y validación. Esta unidad no presenta un benchmark temporal.

## Pruebas y orientación para el reto

Ejecuta:

```bash
python -m unittest discover -s unidad05-busqueda-heuristicas/pruebas -v
```

La referencia por enumeración de caminos simples permite contrastar resultados sin reutilizar la misma cola de prioridad. Se usa en grafos diminutos; no sustituye la búsqueda eficiente en casos grandes.

Un reto sólido puede mostrar una variante sin solución o una heurística que falla como cota, si lo interpreta y documenta. Evita presentar ese resultado como garantía de navegación o planificación real.

[Volver a la unidad](../README.md) · [Ver el reto](../reto.md)

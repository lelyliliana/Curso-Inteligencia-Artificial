# Procedencia y formato — Unidad 5

Los grafos y la cuadrícula son sintéticos, elaborados para enseñar búsqueda. No contienen mapas reales, coordenadas geográficas, tiempos medidos ni datos de personas.

## Grafo principal

`grafo_rutas.json` tiene seis estados y ocho transiciones dirigidas. Los costos se llaman minutos para practicar unidades, pero son inventados.

- Inicio: S; meta: G.
- Camino de costo mínimo: S → C → G, costo 5.
- Camino con menos pasos elegido primero por BFS: S → A → G, costo 12.
- Heurística incluida: admisible y consistente en el grafo declarado.

El orden de vecinos forma parte de la reproducción de desempates. S declara A, B y C en ese orden.

## Grafo de reapertura

`grafo_reapertura.json` tiene cuatro estados y cuatro transiciones. Se fabricó para mostrar una heurística admisible e inconsistente.

- S → A cuesta 2; S → B, 1; B → A, 0.5; A → G, 2.
- h(S)=0, h(A)=0, h(B)=2.5 y h(G)=0.
- Camino mínimo: S → B → A → G, costo 3.5.
- La arista B → A viola consistencia.
- Multiplicar h por dos sobreestima desde B y hace que el A* del laboratorio devuelva costo 4.

Es un contraejemplo didáctico concreto, no una comparación estadística del desempeño general de los algoritmos.

## Esquema JSON

| Campo | Contenido |
|---|---|
| `descripcion` | Texto no vacío que documenta el caso |
| `inicio` | Nombre de un estado declarado |
| `meta` | Nombre de un estado declarado |
| `grafo` | Objeto: estado → lista de pares `[destino,costo]` |
| `heuristica` | Objeto: estado → estimación no negativa |

Se requieren exactamente esos campos. Cada nombre de estado es un texto no vacío; cada destino debe existir. No se admiten destinos repetidos desde el mismo estado, claves JSON duplicadas, costos negativos, booleanos como números ni valores no finitos.

La heurística debe incluir exactamente los estados del grafo y valer cero en la meta. Estos requisitos no garantizan admisibilidad. La auditoría incluida calcula costos restantes en el grafo para comprobarla.

Límites del núcleo: de 1 a 500 estados y hasta 10 000 transiciones. Costos y heurística se procesan como `float`; enteros pequeños y 0.5 de los casos incluidos tienen representación binaria exacta.

## Cuadrícula

`cuadricula.txt` es rectangular, de 5 filas por 7 columnas. Contiene 25 celdas transitables y 10 bloqueadas. Los índices empiezan en cero.

- S: inicio en `(0,0)`.
- G: meta en `(0,6)`.
- Punto: celda libre.
- Numeral: celda bloqueada.
- Acciones: arriba, derecha, abajo, izquierda; costo uno.
- No hay diagonales, envoltura de bordes, llaves, batería ni incertidumbre.

Manhattan desde el inicio vale 6; la ruta real óptima del mapa cuesta 10. La figura `recursos/ruta_cuadricula.svg` se generó con el Laboratorio 3 y ese mismo mapa.

El lector admite hasta 30 celdas por dimensión y 500 transitables. La presencia de S y G no demuestra que estén conectadas.

## Otros casos

El Laboratorio 1 contiene en el código un grafo unitario de seis estados, con ciclo D → A. Sus valores también son fabricados. Las pruebas generan veinte grafos diminutos usando semilla 7 para comparar con enumeración independiente de caminos simples.

## Variantes y límites

Conserva originales, guarda copias y registra cambios de costos, aristas, obstáculos, heurística y orden. Si cambias la unidad de costo, adapta h y la documentación para mantener compatibilidad.

Una solución óptima en estos modelos no demuestra que exista una ruta físicamente transitable ni que sea adecuada para una aplicación real. Es necesario validar mapa, geometría, reglas y objetivo del proyecto.

[Volver a la unidad](../README.md)

"""Núcleo didáctico para grafos finitos con costos no negativos y una meta."""

from collections import deque
import heapq
from itertools import count
import json
import math
from pathlib import Path


ALGORITMOS = ("bfs", "dfs", "ucs", "voraz", "astar")


def numero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser numérico.")
    try:
        valor = float(valor)
    except OverflowError as exc:
        raise ValueError(f"{nombre} fuera del rango numérico.") from exc
    if not math.isfinite(valor) or valor < 0:
        raise ValueError(f"{nombre} debe ser finito y no negativo.")
    return valor


def validar_grafo(grafo, inicio, meta):
    if not isinstance(grafo, dict) or not 1 <= len(grafo) <= 500:
        raise ValueError("El grafo debe contener entre 1 y 500 estados.")
    if any(not isinstance(s, str) or not s.strip() for s in grafo):
        raise ValueError("Cada estado debe tener un nombre de texto no vacío.")
    if not isinstance(inicio, str) or not isinstance(meta, str) or inicio not in grafo or meta not in grafo:
        raise ValueError("Inicio y meta deben pertenecer al grafo.")
    resultado, aristas = {}, 0
    for estado, vecinos in grafo.items():
        if not isinstance(vecinos, (list, tuple)):
            raise ValueError(f"Los vecinos de {estado} deben ser una lista.")
        destinos, nuevos = set(), []
        for par in vecinos:
            if not isinstance(par, (list, tuple)) or len(par) != 2:
                raise ValueError("Cada transición debe ser [destino, costo].")
            destino, costo = par
            if not isinstance(destino, str) or destino not in grafo or destino in destinos:
                raise ValueError(f"Destino desconocido o repetido desde {estado}.")
            destinos.add(destino)
            nuevos.append((destino, numero(costo, "Costo")))
            aristas += 1
        resultado[estado] = nuevos
    if aristas > 10000:
        raise ValueError("El laboratorio admite hasta 10000 transiciones.")
    return resultado


def validar_heuristica(grafo, meta, valores):
    if not isinstance(valores, dict) or set(valores) != set(grafo):
        raise ValueError("Se requiere una heurística para cada estado y ningún nombre adicional.")
    h = {s: numero(v, f"h({s})") for s, v in valores.items()}
    if h[meta] != 0:
        raise ValueError("La heurística de la meta debe ser cero.")
    return h


def violaciones_consistencia(grafo, h):
    # Comparación directa: la consistencia es una condición matemática exacta.
    return [(s, t) for s, vecinos in grafo.items() for t, costo in vecinos
            if h[s] > costo + h[t]]


def sin_claves_repetidas(pares):
    resultado = {}
    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(f"Clave JSON repetida: {clave}")
        resultado[clave] = valor
    return resultado


def leer_problema(ruta):
    contenido = json.loads(Path(ruta).read_text(encoding="utf-8"), object_pairs_hook=sin_claves_repetidas)
    campos = {"descripcion", "inicio", "meta", "grafo", "heuristica"}
    if not isinstance(contenido, dict) or set(contenido) != campos:
        raise ValueError("Campos requeridos: descripcion, inicio, meta, grafo y heuristica.")
    if not isinstance(contenido["descripcion"], str) or not contenido["descripcion"].strip():
        raise ValueError("La descripción debe ser texto no vacío.")
    g = validar_grafo(contenido["grafo"], contenido["inicio"], contenido["meta"])
    h = validar_heuristica(g, contenido["meta"], contenido["heuristica"])
    return g, contenido["inicio"], contenido["meta"], h


def reconstruir(padres, meta, g):
    # Un registro conserva su propio predecesor, aunque el estado mejore después.
    camino, registro = [], (meta, g)
    while registro is not None:
        camino.append(registro[0])
        registro = padres[registro]
    return list(reversed(camino))


def buscar(grafo, inicio, meta, algoritmo, heuristica=None):
    grafo = validar_grafo(grafo, inicio, meta)
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo permitido: {', '.join(ALGORITMOS)}")
    h = (validar_heuristica(grafo, meta, heuristica) if algoritmo in ("astar", "voraz")
         else {s: 0.0 for s in grafo})
    padres, mejor_g = {(inicio, 0.0): None}, {inicio: 0.0}
    extraidos, expandidos, generados, pico = [], [], 1, 1

    def resultado(encontrado):
        return {"encontrado": encontrado,
                "camino": reconstruir(padres, meta, mejor_g[meta]) if encontrado else [],
                "costo": mejor_g[meta] if encontrado else None,
                "extraidos": extraidos, "expandidos": expandidos,
                "generados": generados, "frontera_maxima": pico}

    if algoritmo in ("bfs", "dfs"):
        frontera = deque([inicio])
        while frontera:
            estado = frontera.popleft() if algoritmo == "bfs" else frontera.pop()
            extraidos.append((estado, mejor_g[estado], 0.0, None))
            if estado == meta:
                return resultado(True)
            expandidos.append(estado)
            vecinos = grafo[estado] if algoritmo == "bfs" else reversed(grafo[estado])
            for destino, costo in vecinos:
                if destino not in mejor_g:
                    nuevo_g = numero(mejor_g[estado] + costo, "Costo acumulado")
                    padres[(destino, nuevo_g)] = (estado, mejor_g[estado])
                    mejor_g[destino] = nuevo_g
                    frontera.append(destino)
                    generados += 1
            pico = max(pico, len(frontera))
        return resultado(False)

    secuencia = count()

    def prioridad(estado, g):
        if algoritmo == "ucs":
            return g
        if algoritmo == "voraz":
            return h[estado]
        return numero(g + h[estado], "Prioridad g+h")

    frontera = [(prioridad(inicio, 0.0), next(secuencia), inicio, 0.0)]
    while frontera:
        f, _, estado, g = heapq.heappop(frontera)
        # Una mejora inserta otra entrada; descartamos la antigua al extraerla.
        if g != mejor_g[estado]:
            continue
        extraidos.append((estado, g, h[estado], f))
        if estado == meta:
            return resultado(True)
        expandidos.append(estado)
        for destino, costo in grafo[estado]:
            nuevo_g = numero(g + costo, "Costo acumulado")
            if nuevo_g < mejor_g.get(destino, math.inf):
                padres[(destino, nuevo_g)] = (estado, g)
                mejor_g[destino] = nuevo_g
                heapq.heappush(frontera, (prioridad(destino, nuevo_g), next(secuencia), destino, nuevo_g))
                generados += 1
        pico = max(pico, len(frontera))
    return resultado(False)


def imprimir_resultado(nombre, resultado, traza=False):
    if resultado["encontrado"]:
        camino = " → ".join(resultado["camino"])
        print(f"{nombre}: ruta={camino}; pasos={len(resultado['camino'])-1}; costo={resultado['costo']:g}")
    else:
        print(f"{nombre}: sin ruta hacia la meta.")
    print(f"  Expansiones={len(resultado['expandidos'])}; entradas generadas={resultado['generados']}; pico frontera={resultado['frontera_maxima']}")
    if traza:
        print("  Extraídos válidos (estado, g, h, prioridad):", resultado["extraidos"])
        print("  Estados expandidos:", resultado["expandidos"])

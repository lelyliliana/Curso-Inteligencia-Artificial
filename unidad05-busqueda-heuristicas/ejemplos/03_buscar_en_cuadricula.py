"""Convierte una cuadrícula en un grafo y usa Manhattan con pasos unitarios."""

import argparse
from html import escape
from pathlib import Path
import sys
from busqueda import buscar, imprimir_resultado, violaciones_consistencia


DATOS = Path(__file__).resolve().parents[1] / "datos" / "cuadricula.txt"


def leer_cuadricula(ruta):
    filas = Path(ruta).read_text(encoding="utf-8").splitlines()
    if not filas or not filas[0] or any(len(f) != len(filas[0]) for f in filas):
        raise ValueError("Se requiere una cuadrícula rectangular no vacía.")
    if len(filas) > 30 or len(filas[0]) > 30:
        raise ValueError("Cada dimensión admite hasta 30 celdas.")
    if any(c not in ".#SG" for fila in filas for c in fila):
        raise ValueError("Símbolos permitidos: ., #, S y G.")
    inicio = [(i,j) for i,fila in enumerate(filas) for j,c in enumerate(fila) if c == "S"]
    meta = [(i,j) for i,fila in enumerate(filas) for j,c in enumerate(fila) if c == "G"]
    if len(inicio) != 1 or len(meta) != 1:
        raise ValueError("Debe existir exactamente una S y una G.")
    libres = [(i,j) for i,fila in enumerate(filas) for j,c in enumerate(fila) if c != "#"]
    if len(libres) > 500:
        raise ValueError("El núcleo admite hasta 500 celdas transitables.")
    return filas, inicio[0], meta[0], libres


def construir_grafo(filas, libres):
    transitables = set(libres)
    nombre = lambda p: f"{p[0]},{p[1]}"
    grafo = {}
    for i,j in libres:
        # Arriba, derecha, abajo, izquierda. Sin diagonales ni envoltura.
        destinos = [(i-1,j), (i,j+1), (i+1,j), (i,j-1)]
        grafo[nombre((i,j))] = [(nombre(p), 1) for p in destinos if p in transitables]
    return grafo


def guardar_svg(filas, camino, destino):
    tam, izquierda, arriba = 54, 68, 78
    ancho = max(486, izquierda + len(filas[0])*tam + 40)
    alto = arriba + len(filas)*tam + 84
    elementos = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" role="img" aria-labelledby="titulo descripcion">',
                 '<title id="titulo">Ruta en una cuadrícula sintética</title>',
                 '<desc id="descripcion">Movimientos ortogonales de costo uno. Las celdas oscuras son obstáculos. La línea une los estados de la ruta de A estrella.</desc>',
                 f'<rect width="{ancho}" height="{alto}" fill="white"/>',
                 '<g font-family="Arial, sans-serif" fill="#172b4d">',
                 '<text x="24" y="28" font-size="19" font-weight="bold">Búsqueda en cuadrícula</text>',
                 f'<text x="24" y="51" font-size="13">Ruta A*: {len(camino)-1} movimientos · Datos sintéticos</text>']
    for j in range(len(filas[0])):
        elementos.append(f'<text x="{izquierda+j*tam+tam/2}" y="{arriba-10}" text-anchor="middle" font-size="12">{j}</text>')
    for i,fila in enumerate(filas):
        elementos.append(f'<text x="{izquierda-18}" y="{arriba+i*tam+tam/2+4}" text-anchor="middle" font-size="12">{i}</text>')
        for j,c in enumerate(fila):
            color = "#334155" if c == "#" else "#eff5fa"
            elementos.append(f'<rect x="{izquierda+j*tam}" y="{arriba+i*tam}" width="{tam}" height="{tam}" fill="{color}" stroke="white" stroke-width="2"/>')
    puntos = []
    for estado in camino:
        i,j = map(int, estado.split(","))
        puntos.append(f"{izquierda+j*tam+tam/2},{arriba+i*tam+tam/2}")
    elementos.append(f'<polyline points="{escape(" ".join(puntos))}" fill="none" stroke="#007c83" stroke-width="5" stroke-linejoin="round"/>')
    for i,fila in enumerate(filas):
        for j,c in enumerate(fila):
            if c in "SG":
                cx,cy = izquierda+j*tam+tam/2, arriba+i*tam+tam/2
                elementos.extend([f'<circle cx="{cx}" cy="{cy}" r="17" fill="#007c83"/>',
                                  f'<text x="{cx}" y="{cy+5}" text-anchor="middle" fill="white" font-size="16" font-weight="bold">{c}</text>'])
    elementos.extend([f'<text x="24" y="{alto-42}" font-size="13">S: inicio · G: meta · Oscuro: bloqueado · Índices desde cero</text>',
                      f'<text x="24" y="{alto-19}" font-size="12">Sin diagonales, batería, incertidumbre ni control de un robot real.</text>', '</g></svg>'])
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(elementos)+"\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, default=DATOS)
    parser.add_argument("--svg", type=Path, help="Guarda una figura si existe ruta; requiere destino nuevo.")
    parser.add_argument("--traza", action="store_true")
    args = parser.parse_args()
    try:
        filas, inicio, meta, libres = leer_cuadricula(args.datos)
        if args.svg is not None and args.svg.exists():
            raise ValueError("El destino SVG ya existe; elige un nombre nuevo.")
        g = construir_grafo(filas, libres)
        s, t = f"{inicio[0]},{inicio[1]}", f"{meta[0]},{meta[1]}"
        h = {f"{i},{j}": abs(i-meta[0])+abs(j-meta[1]) for i,j in libres}
        resultados = [(a, buscar(g,s,t,a,h)) for a in ("bfs","ucs","astar")]
        a_star = resultados[-1][1]
        if args.svg is not None and a_star["encontrado"]:
            guardar_svg(filas, a_star["camino"], args.svg)
    except (OSError, UnicodeError, ValueError, OverflowError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Cuadrícula={len(filas)} × {len(filas[0])}; transitables={len(libres)}; h(inicio)={h[s]}")
    print("Violaciones de consistencia Manhattan:", violaciones_consistencia(g,h))
    for nombre, resultado in resultados:
        imprimir_resultado(nombre.upper(), resultado, args.traza)
    if args.svg is not None:
        print(f"Figura guardada: {args.svg}" if a_star["encontrado"] else "No se guarda figura porque no existe ruta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

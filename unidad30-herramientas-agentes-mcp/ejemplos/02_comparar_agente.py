"""Predeterminado: reconstruir las capturas, sin servicio ni modelos instalados."""

import argparse
from pathlib import Path

from experimento import analizar, capturar, graficar
from herramientas import UNIDAD, cargar, guardar, huella


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fase", choices=("desarrollo", "cierre"), default="desarrollo")
    p.add_argument("--en-vivo", action="store_true")
    p.add_argument("--registro", type=Path)
    p.add_argument("--desarrollo", type=Path, default=UNIDAD / "recursos/desarrollo/registro.json")
    p.add_argument("--salida", type=Path)
    p.add_argument("--graficos", action="store_true")
    a = p.parse_args()
    if (a.en_vivo or a.graficos) and a.salida is None:
        p.error("--en-vivo y --graficos requieren --salida")
    if a.en_vivo and a.registro:
        p.error("No combinar --en-vivo y --registro")
    r = capturar(a.fase, a.salida, a.desarrollo) if a.en_vivo else cargar(a.registro or UNIDAD / f"recursos/{a.fase}/registro.json")
    if r["fase"] != a.fase:
        raise ValueError("Fase de captura incorrecta")
    if a.fase == "cierre":
        desarrollo = cargar(a.desarrollo)
        analizar(desarrollo)
        if (desarrollo["fase"] != "desarrollo" or r["desarrollo_sha256"] != huella(a.desarrollo)
                or desarrollo["inventario"] != r["inventario"]):
            raise ValueError("El cierre no corresponde al desarrollo indicado")
    informe = analizar(r)
    print("Recarga sin red: solicitudes, resultados y decisiones del host comprobados.")
    for fila in informe["resumen"]:
        print(f"{fila['metodo']}: aceptadas={fila['aceptada']}/{fila['tareas']}; "
              f"familias completas={fila['familias_completas']}/{fila['familias']}; llamadas modelo={fila['llamadas_modelo']}")
    if a.salida:
        guardar(a.salida / "informe.json", informe)
    if a.graficos:
        graficar(informe, a.salida)


if __name__ == "__main__":
    main()

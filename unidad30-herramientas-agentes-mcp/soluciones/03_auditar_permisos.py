"""Escenarios artificiales del host, separados de la medición del modelo."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from herramientas import Sesion, guardar


def auditar():
    filas = []
    simples = [
        ("nombre inexistente", "ejecutar_shell", {}, "desconocida"),
        ("ruta como ID", "consultar_sensor", {"sensor": "../../secreto"}, "argumentos_invalidos"),
        ("argumento extra", "consultar_sensor", {"sensor": "S-11", "permiso": True}, "argumentos_invalidos"),
        ("ID restringido", "consultar_sensor", {"sensor": "S-14"}, "denegado"),
        ("escritura", "cambiar_umbral", {"sensor": "S-11", "umbral_c": 99}, "denegado"),
        ("sin evidencia previa", "calcular_media", {"sensor": "S-11"}, "sin_consulta"),
        ("dato ausente", "consultar_sensor", {"sensor": "S-90"}, "no_disponible"),
    ]
    for nombre, herramienta, argumentos, esperado in simples:
        s = Sesion()
        r = s.llamar(herramienta, argumentos)
        assert r["codigo"] == esperado
        filas.append({"escenario": nombre, "esperado": esperado, "eventos": s.eventos})
    s = Sesion()
    s.llamar("consultar_sensor", {"sensor": "S-11"})
    assert s.llamar("consultar_sensor", {"sensor": "S-11"})["codigo"] == "repetida"
    filas.append({"escenario": "repetición", "eventos": s.eventos})
    s = Sesion(max_llamadas=1)
    s.llamar("consultar_sensor", {"sensor": "S-11"})
    assert s.llamar("calcular_media", {"sensor": "S-11"})["codigo"] == "limite_llamadas"
    filas.append({"escenario": "presupuesto de llamadas", "eventos": s.eventos})
    tiempo = [0]
    s = Sesion(segundos=1, reloj=lambda: tiempo[0])
    tiempo[0] = 2
    assert s.llamar("consultar_sensor", {"sensor": "S-11"})["codigo"] == "limite_tiempo"
    filas.append({"escenario": "reloj artificial", "eventos": s.eventos})
    s = Sesion()
    s.llamar("consultar_sensor", {"sensor": "S-23"})
    assert s.llamar("cambiar_umbral", {"sensor": "S-23", "umbral_c": 99})["codigo"] == "denegado"
    assert s.llamar("calcular_media", {"sensor": "S-23"})["datos"]["media_c"] == 1
    filas.append({"escenario": "seguir artificialmente una inyección", "eventos": s.eventos})
    return {"origen": "propuestas_artificiales_no_generadas_por_modelo", "escenarios": filas}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    r = auditar()
    print(f"Auditoría artificial: {len(r['escenarios'])} escenarios; ninguna escritura ejecutada.")
    if a.salida:
        guardar(a.salida / "auditoria.json", r)


if __name__ == "__main__":
    main()

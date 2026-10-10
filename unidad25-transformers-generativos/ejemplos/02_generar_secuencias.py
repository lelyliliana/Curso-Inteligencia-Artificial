"""Compara bigramas y transformer; cierre solo desde un estado guardado."""
import argparse
from pathlib import Path
import transformer_curso as curso


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--datos", type=Path, default=curso.UNIDAD / "datos")
    p.add_argument("--salida", type=Path)
    p.add_argument("--graficos", action="store_true")
    p.add_argument("--evaluar-prueba", action="store_true")
    p.add_argument("--modelo", type=Path)
    a = p.parse_args()
    if a.evaluar_prueba != (a.modelo is not None):
        p.error("El cierre requiere juntos --evaluar-prueba y --modelo.")
    if a.graficos and (not a.salida or a.evaluar_prueba):
        p.error("--graficos requiere --salida y desarrollo.")
    try:
        if a.evaluar_prueba:
            r = curso.cerrar(a.modelo, a.datos)
            m = r["evaluacion"]
            print(f"Cierre sin reajuste: CE={m['ce']:.4f}; exactas={m['n_exactas']}/{m['n_documentos']}")
            if a.salida:
                curso.guardar_json(a.salida / "cierre.json", r)
        else:
            estado, r = curso.desarrollar(a.datos)
            for nombre, c in r["candidatos"].items():
                m = c["validacion"]
                print(f"{nombre}: CE={m['ce']:.4f}; PPL={m['perplejidad']:.4f}; token={m['exactitud_token']:.4f}; exactas={m['n_exactas']}/{m['n_documentos']}")
            h = r["entrenamiento_transformer"]
            print(f"Seleccionado por CE de validación: {r['seleccionado']}; época transformer={h['epoca_elegida']}")
            print(f"Parámetros transformer={h['n_parametros']}; vocabulario={len(r['vocabulario'])}")
            print("Prueba reservada. La generación no recibe la continuación correcta.")
            if a.salida:
                curso.exportar(estado, r, a.salida, a.datos)
                print("Recarga: logits y generaciones idénticos.")
                if a.graficos:
                    from figuras_transformer import generacion
                    generacion(r, a.salida)
        if a.salida:
            print("Exportación:", a.salida)
    except (ValueError, OSError, KeyError, RuntimeError) as e:
        p.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    main()

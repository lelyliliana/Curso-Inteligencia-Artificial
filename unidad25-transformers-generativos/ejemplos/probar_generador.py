"""Genera desde un JSON guardado; no entrena ni abre el corpus de prueba."""
import argparse
from pathlib import Path
import transformer_curso as tc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--modelo",type=Path,default=tc.UNIDAD/"recursos/generacion/modelo.json")
    p.add_argument("--prefijo",default="tema energia zona norte nivel medio formato breve salida")
    p.add_argument("--metodo",choices=("codicioso","muestreo"),default="codicioso")
    p.add_argument("--temperatura",type=float,default=1.0)
    p.add_argument("--semilla",type=int,default=2502)
    p.add_argument("--max-nuevos",type=int,default=12)
    p.add_argument("--salida",type=Path,help="Archivo JSON de la generación.")
    a=p.parse_args()
    try:
        modelo,vocab=tc.cargar(a.modelo)
        r=tc.generar(modelo,vocab,a.prefijo,a.metodo,a.temperatura,a.semilla,a.max_nuevos)
        print("Generación:",r["texto"])
        print(f"Parada: {r['motivo']}; desconocidos en prefijo={r['desconocidos_prefijo']}")
        if a.salida:
            tc.guardar_json(a.salida,{"modelo_sha256":tc.huella(a.modelo),**r})
            print("Exportación:",a.salida)
    except (ValueError,OSError,KeyError,RuntimeError) as e:
        p.exit(2,f"Error: {e}\n")


if __name__ == "__main__":
    main()

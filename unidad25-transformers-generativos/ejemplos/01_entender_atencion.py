"""Contrasta atención manual, máscara causal y PyTorch en float64."""
import argparse
from pathlib import Path
from atencion import experimento
from transformer_curso import guardar_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path)
    p.add_argument("--graficos", action="store_true")
    a = p.parse_args()
    if a.graficos and not a.salida:
        p.error("--graficos requiere --salida.")
    r = experimento()
    print("Atención manual y biblioteca: error máximo < 1e-12")
    print(f"Futuro alterado: cambio en posiciones anteriores={r['cambio_pasado_causal']:.1f}")
    print(f"Sin máscara: cambio en posiciones anteriores={r['cambio_pasado_libre']:.4f}")
    if a.salida:
        guardar_json(a.salida / "informe.json", r)
        if a.graficos:
            from figuras_transformer import atencion
            atencion(r, a.salida)
        print("Exportación:", a.salida)


if __name__ == "__main__":
    main()

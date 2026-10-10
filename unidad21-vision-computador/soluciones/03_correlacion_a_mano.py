"""Una salida local y la forma completa de un filtro."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"ejemplos"))
from filtros import comprobar_manual


if __name__ == "__main__":
    caso = comprobar_manual()
    print("Primera celda: 1×1 + 2×0 + 0×0 + 1×(−1) = 0")
    print("Salida:", caso["salida"])
    print(f"Correlación comprobada: salida 3×3; error máximo={caso['error_maximo']:.1f}")

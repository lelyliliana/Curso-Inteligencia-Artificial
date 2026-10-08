"""Muestra el intérprete, el entorno y la disponibilidad de los datos del curso."""

from pathlib import Path
import platform
import sys


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    datos = raiz / "datos" / "consumo_sintetico.csv"
    version_compatible = sys.version_info >= (3, 12)
    print(f"Python: {platform.python_version()}")
    print(f"Intérprete: {sys.executable}")
    print(f"Sistema: {platform.system()}")
    print(f"Entorno venv: {sys.prefix != sys.base_prefix}")
    print(f"Python 3.12 o superior: {version_compatible}")
    print(f"Datos de práctica disponibles: {datos.is_file()}")
    if not version_compatible or not datos.is_file():
        raise SystemExit("Revisa la versión de Python y la carpeta datos del curso.")


if __name__ == "__main__":
    main()

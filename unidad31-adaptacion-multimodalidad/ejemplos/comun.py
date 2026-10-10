"""Persistencia y comprobaciones compartidas por los dos laboratorios."""

import hashlib
import json
from pathlib import Path

import torch

UNIDAD = Path(__file__).resolve().parents[1]


def configurar():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def guardar(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def estado_json(modelo):
    return {k: v.detach().tolist() for k, v in modelo.state_dict().items()}


def restaurar_estado(modelo, estado):
    esperado = modelo.state_dict()
    if not isinstance(estado, dict) or set(estado) != set(esperado):
        raise ValueError("Claves de estado incompatibles")
    nuevo = {k: torch.tensor(v, dtype=esperado[k].dtype) for k, v in estado.items()}
    if any(nuevo[k].shape != esperado[k].shape or not torch.isfinite(nuevo[k]).all() for k in nuevo):
        raise ValueError("Forma o valores de estado inválidos")
    modelo.load_state_dict(nuevo, strict=True)
    modelo.eval()
    return modelo


def comprobar_familias(*grupos):
    vistas, ids = set(), set()
    for grupo in grupos:
        familias = {r["familia"] for r in grupo}
        nuevos = [r["id"] for r in grupo]
        if not grupo or familias & vistas or ids & set(nuevos) or len(set(nuevos)) != len(nuevos):
            raise ValueError("Particiones vacías, familias cruzadas o IDs repetidos")
        vistas |= familias
        ids |= set(nuevos)


def huellas_codigo(nombres):
    rutas = ["datos/protocolo.md", "datos/generar_datos.py", "ejemplos/comun.py", *nombres]
    return {r: huella(UNIDAD / r) for r in rutas}


def verificar_huellas(huellas):
    if not isinstance(huellas, dict) or not huellas or any(huella(UNIDAD / r) != h for r, h in huellas.items()):
        raise ValueError("Cambió una fuente vinculada al modelo")

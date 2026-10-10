"""Correlación cruzada explícita y lectura de una imagen RGB pequeña."""
import hashlib
from pathlib import Path
import platform
import numpy as np
import PIL
from PIL import Image
import torch
from torch.nn.functional import conv2d

UNIDAD = Path(__file__).resolve().parents[1]
X_MANUAL = np.array([[1., 2., 0., 1.], [0., 1., 3., 2.], [2., 1., 0., 1.], [1., 0., 2., 3.]])
K_MANUAL = np.array([[1., 0.], [0., -1.]])


def correlacion2d(imagen, kernel, paso=1, relleno=0):
    x, k = np.asarray(imagen, dtype=float), np.asarray(kernel, dtype=float)
    if (x.ndim != 2 or k.ndim != 2 or not x.size or not k.size
            or not np.isfinite(x).all() or not np.isfinite(k).all()
            or type(paso) is not int or paso < 1 or type(relleno) is not int or relleno < 0):
        raise ValueError("Matrices finitas no vacías; paso positivo y relleno no negativo, enteros.")
    x = np.pad(x, relleno, mode="constant")
    alto, ancho = ((x.shape[j]-k.shape[j])//paso+1 for j in range(2))
    if alto < 1 or ancho < 1:
        raise ValueError("El filtro no cabe en la imagen con este relleno.")
    salida = np.empty((alto, ancho))
    for f in range(alto):
        for c in range(ancho):
            salida[f, c] = np.sum(x[f*paso:f*paso+k.shape[0], c*paso:c*paso+k.shape[1]]*k)
    return salida


def comprobar_manual():
    a = correlacion2d(X_MANUAL, K_MANUAL)
    b = conv2d(torch.tensor(X_MANUAL)[None, None], torch.tensor(K_MANUAL)[None, None]).numpy()[0, 0]
    error = float(np.max(np.abs(a-b)))
    if error > 1e-12:
        raise RuntimeError("El cálculo manual y conv2d no coinciden.")
    return {"imagen": X_MANUAL.tolist(), "kernel": K_MANUAL.tolist(), "salida": a.tolist(), "error_maximo": error}


def ejecutar_filtros(ruta=None):
    ruta = Path(ruta) if ruta is not None else UNIDAD/"datos/colores.png"
    with Image.open(ruta) as imagen:
        if imagen.format != "PNG" or imagen.mode != "RGB" or imagen.size != (24, 24):
            raise ValueError("Este laboratorio espera una imagen PNG RGB de 24×24.")
        rgb = np.array(imagen, dtype=np.uint8)
        gris = np.array(imagen.convert("L"), dtype=np.float64)/255
    sobel = np.array([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]])
    suave = np.full((3, 3), 1/9)
    return {"laboratorio": "filtros", "fuente": {"archivo": ruta.name, "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest()},
            "versiones": {"python": platform.python_version(), "numpy": np.__version__, "torch": str(torch.__version__), "pillow": PIL.__version__},
            "kernels": {"sobel_x": sobel.tolist(), "media": suave.tolist()},
            "rgb_hwc": rgb.tolist(), "gris": gris.tolist(), "forma_nchw": [1, 3, 24, 24],
            "sobel_x": correlacion2d(gris, sobel).tolist(), "suavizada": correlacion2d(gris, suave).tolist(),
            "manual": comprobar_manual(), "borde": "sin relleno; salida 22×22"}

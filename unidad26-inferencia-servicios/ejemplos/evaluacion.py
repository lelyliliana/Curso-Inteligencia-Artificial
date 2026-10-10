"""Casos fijos, medición y análisis del registro de inferencia."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
from statistics import median
import time

from servicios import ErrorServicio, OLLAMA, leer_ollama, numero, peticion_ollama, solicitar

UNIDAD = Path(__file__).resolve().parents[1]
CASOS = UNIDAD / "datos/casos.json"
PROTOCOLO = UNIDAD / "datos/protocolo.md"
LIMITES = (4, 48)


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def guardar(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def plan(casos):
    return [(caso, limite) for i, caso in enumerate(casos)
            for limite in (LIMITES if i % 2 == 0 else LIMITES[::-1])]


def puntuar(fila, caso):
    resultado = {"contrato_valido": False, "finalizada": False,
                 "coincide": False, "aceptada": False}
    if fila.get("error"):
        return resultado | {"error": fila["error"]}
    try:
        lectura = leer_ollama(fila.get("respuesta"))
    except ErrorServicio as exc:
        return resultado | {"error": exc.codigo}
    coincide = lectura["texto"].strip() == caso["esperado"]
    return resultado | lectura | {"contrato_valido": True, "coincide": coincide,
                                  "aceptada": coincide and lectura["finalizada"]}


def analizar(registro, casos=None):
    casos = cargar(CASOS) if casos is None else casos
    if registro.get("origen") != "ollama_local_real" or registro.get("schema") != 1:
        raise ValueError("Se necesita una captura local real con schema 1")
    if registro.get("inventario_estable") is not True:
        raise ValueError("El inventario no se confirmó estable al terminar las llamadas")
    if registro.get("casos_sha256") != huella(CASOS) or registro.get("protocolo_sha256") != huella(PROTOCOLO):
        raise ValueError("Los casos o el protocolo no corresponden al registro")
    filas = registro.get("filas", [])
    esperados = plan(casos)
    if len(filas) != len(esperados):
        raise ValueError("Registro incompleto: conservar también las llamadas fallidas")
    evaluaciones = []
    for fila, (caso, limite) in zip(filas, esperados):
        if (fila.get("caso") != caso["id"] or fila.get("limite") != limite
                or fila.get("solicitud") != peticion_ollama(registro["modelo"], caso["prompt"], limite)):
            raise ValueError("Cambió el orden, la condición o el prompt fijado")
        numero(fila.get("pared_s"), "pared_s")
        if ("respuesta" in fila) == ("error" in fila):
            raise ValueError("Cada llamada debe tener respuesta o error, de forma exclusiva")
        evaluaciones.append({"caso": caso["id"], "limite": limite,
                             "pared_s": fila["pared_s"], **puntuar(fila, caso)})
    resumen = []
    for limite in LIMITES:
        grupo = [f for f in evaluaciones if f["limite"] == limite]
        tiempos = [f["pared_s"] for f in grupo if f["contrato_valido"]]
        resumen.append({"limite": limite, "solicitudes": len(grupo),
                        **{campo: sum(f[campo] for f in grupo) for campo in
                           ("contrato_valido", "finalizada", "coincide", "aceptada")},
                        "n_latencias": len(tiempos),
                        "mediana_pared_s": median(tiempos) if tiempos else None,
                        "errores": dict(Counter(f["error"] for f in grupo if "error" in f))})
    return {"origen": "analisis_de_captura", "modelo": registro["modelo"],
            "filas": evaluaciones, "resumen": resumen}


def inventario(modelo, cliente=solicitar):
    versiones = cliente(OLLAMA + "/api/version")
    etiquetas = cliente(OLLAMA + "/api/tags")
    candidatos = [m for m in etiquetas.get("models", []) if m.get("name") == modelo]
    if len(candidatos) != 1 or candidatos[0].get("size", 0) <= 0:
        raise ValueError("El modelo debe estar instalado: esta práctica no descarga pesos")
    detalle = cliente(OLLAMA + "/api/show", {"model": modelo})
    if detalle.get("remote_model") or detalle.get("remote_host"):
        raise ValueError("La práctica requiere pesos locales, no un modelo cloud")
    m = candidatos[0]
    return {"version_ollama": versiones["version"], "digest": m["digest"],
            "bytes_modelo": m["size"], "detalles": detalle.get("details"),
            "capacidades": detalle.get("capabilities"), "parametros_modelo": detalle.get("parameters"),
            "licencia": detalle.get("model_info", {}).get("general.license"),
            "licencia_sha256": hashlib.sha256(detalle.get("license", "").encode()).hexdigest(),
            "plantilla_sha256": hashlib.sha256(detalle.get("template", "").encode()).hexdigest()}


def medir(cuerpo, timeout, cliente=solicitar):
    inicio = time.perf_counter()
    try:
        salida = {"respuesta": cliente(OLLAMA + "/api/generate", cuerpo, timeout=timeout)}
    except ErrorServicio as exc:
        salida = {"error": exc.codigo}
    return {"solicitud": cuerpo, "pared_s": time.perf_counter() - inicio, **salida}


def ejecutar_real(modelo, salida, timeout=120, cliente=solicitar):
    """Sin reintentos. Persiste cada intento antes de pasar al siguiente."""
    numero(timeout, "timeout", minimo=0.001)
    meta = inventario(modelo, cliente)
    registro = {"schema": 1, "origen": "ollama_local_real", "modelo": modelo,
                "fecha_utc": datetime.now(timezone.utc).isoformat(),
                "casos_sha256": huella(CASOS), "protocolo_sha256": huella(PROTOCOLO),
                "entorno": {"python": platform.python_version(), "sistema": platform.system(),
                            "arquitectura": platform.machine()},
                "timeout_socket_s": timeout, "inventario": meta, "filas": []}
    registro["calentamiento"] = medir(peticion_ollama(modelo, "Responde OK.", 4), timeout, cliente)
    guardar(Path(salida) / "registro.json", registro)
    for caso, limite in plan(cargar(CASOS)):
        print(f"Llamada local: {caso['id']}; máximo={limite}", flush=True)
        fila = {"caso": caso["id"], "limite": limite,
                **medir(peticion_ollama(modelo, caso["prompt"], limite), timeout, cliente)}
        registro["filas"].append(fila)
        guardar(Path(salida) / "registro.json", registro)
    # Solo recursos del modelo elegido; no volcar otros modelos del equipo.
    try:
        ps = cliente(OLLAMA + "/api/ps")
        registro["recursos_servidor"] = [{k: m.get(k) for k in
            ("name", "digest", "size", "size_vram", "context_length")}
            for m in ps.get("models", []) if m.get("name") == modelo]
    except ErrorServicio as exc:
        registro["recursos_error"] = exc.codigo
    final = inventario(modelo, cliente)
    if final != meta:
        registro["inventario_final"] = final
        guardar(Path(salida) / "registro.json", registro)
        raise ValueError("Cambió el inventario durante la ejecución; no comparar las filas")
    registro["inventario_estable"] = True
    guardar(Path(salida) / "registro.json", registro)
    return registro

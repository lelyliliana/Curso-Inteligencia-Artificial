"""Captura local y evaluación por tareas; no hay ajuste con el cierre."""

from datetime import datetime, timezone
import platform
from statistics import median
import time

from agente import MODELO, chat, ejecutar_agente, reproducir, solicitud
from herramientas import UNIDAD, cargar, evaluar, flujo_fijo, guardar, huella
from evaluacion import inventario
from servicios import OLLAMA, solicitar


def huellas():
    rutas = ["datos/sensores.json", "datos/casos.json", "datos/protocolo.md", "prompts/sistema.txt",
             "ejemplos/herramientas.py", "ejemplos/agente.py", "ejemplos/experimento.py",
             "../unidad26-inferencia-servicios/ejemplos/servicios.py",
             "../unidad26-inferencia-servicios/ejemplos/evaluacion.py"]
    return {r: huella(UNIDAD / r) for r in rutas}


def casos_fase(fase):
    if fase not in {"desarrollo", "cierre"}:
        raise ValueError("Fase inválida")
    return [c for c in cargar(UNIDAD / "datos/casos.json") if c["fase"] == fase]


def capturar(fase, salida, desarrollo=None):
    destino = salida / "registro.json"
    if destino.exists():
        raise ValueError("La captura ya existe: utiliza una carpeta nueva")
    previo = cargar(desarrollo) if fase == "cierre" else None
    if previo is not None:
        analizar(previo)
        if previo["fase"] != "desarrollo":
            raise ValueError("Falta captura de desarrollo")
    inv = inventario(MODELO)
    if "tools" not in inv.get("capacidades", []):
        raise ValueError("El modelo local debe anunciar tools")
    if previo is not None and (previo["huellas"] != huellas() or previo["inventario"] != inv):
        raise ValueError("El cierre debe conservar configuración e inventario")
    registro = {"schema": 1, "origen": "ollama_local_real", "fase": fase,
                "fecha_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                "modelo": MODELO, "inventario": inv, "huellas": huellas(),
                "desarrollo_sha256": huella(desarrollo) if previo is not None else None,
                "inventario_estable": False, "tareas": []}
    guardar(destino, registro)
    cuerpo = solicitud([{"role": "user", "content": "Responde solamente LISTO."}], herramientas=False)
    inicio = time.monotonic()
    registro["calentamiento"] = {"solicitud": cuerpo, "respuesta": chat(cuerpo), "pared_s": time.monotonic() - inicio}
    guardar(destino, registro)
    for caso in casos_fase(fase):
        print(f"Capturando {caso['id']}...", flush=True)
        tarea = ejecutar_agente(caso["pregunta"])
        registro["tareas"].append({"caso": caso["id"], **tarea})
        guardar(destino, registro)
        print(f"  parada={tarea['parada']}; llamadas={len(tarea['llamadas'])}", flush=True)
    registro["recursos_servidor"] = solicitar(OLLAMA + "/api/ps")
    registro["inventario_estable"] = inv == inventario(MODELO)
    if registro["huellas"] != huellas():
        raise ValueError("Cambió el material durante la captura")
    guardar(destino, registro)
    return registro


def analizar(registro):
    if (registro.get("schema") != 1 or registro.get("origen") != "ollama_local_real"
            or registro.get("inventario_estable") is not True or registro.get("modelo") != MODELO
            or registro.get("huellas") != huellas()):
        raise ValueError("Captura incompatible o incompleta")
    casos = casos_fase(registro["fase"])
    if [t["caso"] for t in registro["tareas"]] != [c["id"] for c in casos]:
        raise ValueError("Casos omitidos, repetidos o reordenados")
    filas = []
    for caso, tarea in zip(casos, registro["tareas"]):
        reproducir(caso["pregunta"], tarea)
        for metodo, t in (("flujo_fijo", flujo_fijo(caso["pregunta"])), ("agente", tarea)):
            llamadas = t.get("llamadas", [])
            filas.append({"caso": caso["id"], "familia": caso["familia"], "tipo": caso["tipo"], "metodo": metodo,
                          **evaluar(t["final"], t["eventos"], caso["esperado"], t["parada"]),
                          "final": t["final"], "parada": t["parada"], "propuestas": len(t["eventos"]),
                          "herramientas_ok": sum(e["resultado"]["ok"] for e in t["eventos"]),
                          "errores_herramienta": sum(not e["resultado"]["ok"] for e in t["eventos"]),
                          "llamadas_modelo": len(llamadas), "pared_modelo_s": sum(l["pared_s"] for l in llamadas),
                          "tokens_entrada": sum(l.get("respuesta", {}).get("prompt_eval_count", 0) for l in llamadas),
                          "tokens_salida": sum(l.get("respuesta", {}).get("eval_count", 0) for l in llamadas)})
    resumen = []
    for metodo in ("flujo_fijo", "agente"):
        grupo = [f for f in filas if f["metodo"] == metodo]
        familias = sorted({f["familia"] for f in grupo})
        resumen.append({"metodo": metodo, "tareas": len(grupo), "familias": len(familias),
                        "familias_completas": sum(all(f["aceptada"] for f in grupo if f["familia"] == fam) for fam in familias),
                        **{k: sum(f[k] for f in grupo) for k in ("aceptada", "forma", "coincide", "apoyo", "propuestas",
                           "herramientas_ok", "errores_herramienta", "llamadas_modelo", "tokens_entrada", "tokens_salida")},
                        "suma_pared_modelo_s": sum(f["pared_modelo_s"] for f in grupo),
                        "mediana_pared_modelo_por_tarea_s": median(f["pared_modelo_s"] for f in grupo) if metodo == "agente" else None})
    return {"fase": registro["fase"], "origen": "analisis_sin_red", "filas": filas, "resumen": resumen}


def graficar(informe, salida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 11, "svg.hashsalt": "unidad30"})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)
    r = informe["resumen"]
    nombres = ["Flujo fijo", "Agente local"]
    ax[0].bar(nombres, [x["aceptada"] for x in r], color=["#177e89", "#8b5fbf"])
    ax[0].set(ylim=(0, 9), ylabel="Tareas aceptadas de 8", title="Respuesta + evidencia de ejecución")
    for i, x in enumerate(r):
        ax[0].text(i, x["aceptada"] + .12, f"{x['aceptada']}/8", ha="center")
    ax[1].bar(nombres, [x["llamadas_modelo"] for x in r], color=["#177e89", "#8b5fbf"])
    ax[1].set(ylabel="Solicitudes a Ollama", title="Costo en llamadas al modelo")
    fig.suptitle(f"Unidad 30 · {informe['fase']} · datos ficticios, captura real")
    salida.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida / "herramientas.png", dpi=160)
    fig.savefig(salida / "herramientas.svg", metadata={"Date": None})
    plt.close(fig)
    svg = salida / "herramientas.svg"
    svg.write_text("\n".join(x.rstrip() for x in svg.read_text().splitlines()) + "\n")

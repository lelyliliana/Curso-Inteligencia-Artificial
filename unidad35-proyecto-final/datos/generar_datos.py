"""Serie nueva: niveles cambiantes y errores de entrada explícitos; no ajusta modelos."""

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import random

RAIZ = Path(__file__).resolve().parent


def guardar(ruta, objeto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def generar(destino):
    protocolo = json.loads((RAIZ / "protocolo.json").read_text(encoding="utf-8"))
    rng = random.Random(protocolo["semilla"])
    inicio = datetime(2026, 9, 7, tzinfo=timezone(timedelta(hours=-5)))
    valores = []
    for t in range(protocolo["horas"]):
        fecha = inicio + timedelta(hours=t)
        nivel = (8 if t >= 820 else 0) + (6 if t >= 1070 else 0) - (7 if t >= 1140 else 0)
        valor = (32 + 11 * math.sin(2 * math.pi * (fecha.hour - 7) / 24)
                 + 10 * (fecha.weekday() < 5) + nivel + rng.gauss(0, 1.1))
        valores.append(round(valor, 6))
    grupos = {f: [] for f in ("entrenamiento", "validacion", "prueba")}
    fallos = {742: "tardia", 801: "ausente", 887: "negativa", 941: "caducada",
              995: "tardia", 1033: "ausente", 1115: "negativa", 1188: "caducada"}
    for t in range(1, len(valores)):
        origen = inicio + timedelta(hours=t - 1)
        recibido, decision = origen + timedelta(minutes=1), origen + timedelta(minutes=5)
        valor = valores[t - 1]
        fallo = fallos.get(t)
        if fallo == "tardia":
            recibido = origen + timedelta(minutes=8)
        elif fallo == "ausente":
            valor = None
        elif fallo == "negativa":
            valor = -3
        elif fallo == "caducada":
            decision = origen + timedelta(minutes=20)
        fase = ("entrenamiento" if t <= protocolo["ultimo_objetivo_entrenamiento"] else
                "validacion" if t <= protocolo["ultimo_objetivo_validacion"] else "prueba")
        grupos[fase].append({"id": f"PF{t:04d}", "entrada": {
            "potencia_kw": valor, "medido_en": origen.isoformat(), "recibido_en": recibido.isoformat(),
            "decidir_en": decision.isoformat()}, "instante_objetivo": (origen + timedelta(hours=1)).isoformat(),
            "objetivo_kw": valores[t], "incidencia_inyectada": fallo})
    for fase, filas in grupos.items():
        guardar(Path(destino) / f"{fase}.json", filas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    generar(parser.parse_args().salida)
    print("Proyecto final: 1200 decisiones nuevas; 8 incidencias de entrada inyectadas.")

"""Demostración secuencial con casos conocidos, errores y cambio explícito a referencia."""

import argparse
import json
from pathlib import Path

from proyecto import RAIZ, guardar
from servicio import Servicio

CONSULTA = {"potencia_kw": 42.0, "medido_en": "2026-10-20T10:00:00-05:00",
            "recibido_en": "2026-10-20T10:01:00-05:00", "decidir_en": "2026-10-20T10:05:00-05:00"}


def codificar(objeto):
    return json.dumps(objeto, ensure_ascii=False).encode()


def probar(ruta):
    servicio = Servicio(ruta)
    casos = [("valida", codificar(CONSULTA)),
             ("fuera_rango", codificar({**CONSULTA, "potencia_kw": 150})),
             ("negativa", codificar({**CONSULTA, "potencia_kw": -1})),
             ("tardia", codificar({**CONSULTA, "recibido_en": "2026-10-20T10:08:00-05:00"})),
             ("json_roto", b"{"), ("exceso", b" " * 16385),
             ("clave_repetida", b'{"potencia_kw": 1, "potencia_kw": 2}')]
    respuestas = [{"caso": nombre, "respuesta": servicio.responder(entrada)} for nombre, entrada in casos]
    servicio.activo = False
    respuestas.append({"caso": "mantenimiento", "respuesta": servicio.responder(codificar(CONSULTA))})
    referencia = Servicio(ruta, referencia=True)
    respaldo = referencia.responder(codificar(CONSULTA))
    return {"tipo": "comprobacion_funcional_con_casos_conocidos", "respuestas": respuestas,
            "eventos": list(servicio.eventos), "metricas": servicio.metricas(),
            "referencia_separada": respaldo, "metricas_referencia": referencia.metricas()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", type=Path, default=RAIZ / "recursos/modelo.json")
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    informe = probar(args.modelo)
    assert informe["metricas"]["por_estado"] == {"estimacion": 1, "revisar": 1, "rechazado": 6}
    assert informe["referencia_separada"]["resultado"]["prediccion_kw"] == 42.0
    print("Entrega local: 8 respuestas y 8 eventos; referencia separada=42 kW.")
    if args.salida:
        guardar(args.salida, informe)

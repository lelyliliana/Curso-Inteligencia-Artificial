"""Datos propios y ficticios para tres talleres; no ejecuta modelos ni elige candidatos."""

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import random

RAIZ = Path(__file__).resolve().parent


def guardar(ruta, objeto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(objeto, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def generar(destino):
    destino = Path(destino)
    protocolo = json.loads((RAIZ / "protocolo.json").read_text(encoding="utf-8"))
    rng = random.Random(protocolo["energia"]["semilla"])
    inicio = datetime(2026, 7, 6, tzinfo=timezone(timedelta(hours=-5)))
    lecturas = []
    for t in range(protocolo["energia"]["horas"]):
        fecha = inicio + timedelta(hours=t)
        laboral = int(fecha.weekday() < 5)
        # Perfil diario y semanal, con un cambio de nivel al final de la serie.
        valor = (28 + 7 * math.sin(2 * math.pi * (fecha.hour - 7) / 24)
                 + 9 * laboral + (5 if t >= 840 else 0) + rng.gauss(0, 1.4))
        lecturas.append((fecha, round(valor, 6)))
    grupos = {f: [] for f in ("entrenamiento", "validacion", "prueba")}
    a, b = protocolo["energia"]["cortes_objetivo"]
    for t in range(1, len(lecturas)):
        fecha, objetivo = lecturas[t]
        anterior, valor = lecturas[t - 1]
        fase = "entrenamiento" if t < a else "validacion" if t < b else "prueba"
        grupos[fase].append({"id": f"E{t:04d}", "origen": anterior.isoformat(),
                            "instante_objetivo": fecha.isoformat(), "consumo_actual_kw": valor,
                            "hora_siguiente": fecha.hour, "laboral_siguiente": int(fecha.weekday() < 5),
                            "objetivo_kw": objetivo})
    for fase, filas in grupos.items():
        guardar(destino / "energia" / f"{fase}.json", filas)

    rng = random.Random(protocolo["ambiente"]["semilla"])
    grupos = {f: [] for f in grupos}
    for zona in range(protocolo["ambiente"]["zonas"]):
        fase = "entrenamiento" if zona < 6 else "validacion" if zona < 9 else "prueba"
        sesgo = (-0.5, 0, 0.5)[zona % 3] + (0.8 if zona >= 9 else 0)
        for i in range(protocolo["ambiente"]["filas_por_zona"]):
            residuos = round(rng.uniform(0, 12), 4)
            superficie = round(rng.uniform(0, 100), 4)
            dias = rng.randrange(0, 61)
            z = -6 + 0.45 * residuos + 0.04 * superficie + 0.025 * dias + sesgo
            etiqueta = int(rng.random() < 1 / (1 + math.exp(-z)))
            grupos[fase].append({"id": f"A{zona:02d}-{i:02d}", "zona": f"Z{zona:02d}",
                                "residuos_m2": residuos, "superficie_afectada_pct": superficie,
                                "dias_sin_visita": dias, "revision_prioritaria": etiqueta})
    for fase, filas in grupos.items():
        guardar(destino / "ambiente" / f"{fase}.json", filas)

    documentos = [
        ("D01", "Reserva de sala", "Para reservar la sala Aurora, solicita el turno en el formulario de biblioteca. Cada reserva dura dos horas."),
        ("D02", "Préstamo de equipo", "El préstamo de un portátil se solicita en la mesa de tecnología. El equipo se devuelve el mismo día antes de las 18:00."),
        ("D03", "Entrega del taller", "La entrega del taller de energía se realiza en el buzón del aula virtual. Se acepta un archivo PDF con el informe y un enlace al código."),
        ("D04", "Conexión wifi", "La red wifi del aula se llama AulaInvitada. La clave de acceso se pide en recepción y cambia cada semana."),
        ("D05", "Tutoría de datos", "La tutoría de datos se reúne los miércoles a las 15:00 en la sala Roble. La inscripción se realiza en el calendario del curso."),
        ("D06", "Certificado del taller", "El certificado del taller se solicita a coordinación después de entregar el proyecto. La revisión tarda cinco días hábiles."),
        ("D07", "Renovación de libros", "La renovación de libros se solicita en el catálogo de biblioteca. Solo se permite una renovación si el libro no tiene otra reserva."),
        ("D08", "Accesibilidad del aula", "Los materiales de accesibilidad del aula incluyen transcripciones y texto ampliado. Se solicitan al equipo de apoyo por el formulario de accesibilidad."),
        ("D09", "Cancelación de sala", "Para cancelar la sala Aurora, elimina la reserva en el formulario de biblioteca. Avisa al menos una hora antes del turno."),
        ("D10", "Devolución de equipo dañado", "Si un portátil presenta daños, interrumpe su uso e informa a la mesa de tecnología. Registra la incidencia antes de devolver el equipo.")
    ]
    guardar(destino / "documentos" / "corpus.json",
            [{"id": i, "titulo": t, "version": "1", "texto": s} for i, t, s in documentos])
    preguntas = [
        ("reserva", "D01", "¿Cómo reservar la sala Aurora?", "Necesito reservar la sala por un turno, ¿qué hago?"),
        ("prestamo", "D02", "¿Cómo solicito el préstamo de un portátil?", "¿Hasta qué hora puedo tener el equipo prestado?"),
        ("entrega", "D03", "¿Dónde se hace la entrega del taller de energía?", "¿Qué archivo debo entregar en el buzón del aula virtual?"),
        ("wifi", "D04", "¿Cómo se llama la red wifi del aula?", "¿Dónde pido la clave de acceso a wifi?"),
        ("salud", None, "¿Qué medicamento tomo para la fiebre?", "¿Hay consulta médica en la sala Aurora?"),
        ("pago", None, "¿Cuánto cuesta la matrícula del curso?", "¿Dónde se paga el préstamo de un portátil?"),
        ("tutoria", "D05", "¿Cuándo es la tutoría de datos?", "¿Cómo me inscribo para recibir orientación sobre datos?"),
        ("certificado", "D06", "¿Cómo solicito el certificado del taller?", "¿Cuánto demora coordinación en revisar mi certificado?"),
        ("renovacion", "D07", "¿Cómo se solicita la renovación de libros?", "¿Puedo extender el tiempo que tengo un libro?"),
        ("accesibilidad", "D08", "¿Qué materiales de accesibilidad ofrece el aula?", "¿Cómo pido texto ampliado y transcripciones?"),
        ("beca", None, "¿Cómo se solicita una beca de matrícula?", "¿El certificado del taller permite obtener una beca?"),
        ("transporte", None, "¿Qué bus llega a la universidad?", "¿Hay transporte hasta la tutoría de datos?")
    ]
    for fase, familias in (("validacion", protocolo["documentos"]["familias_validacion"]),
                          ("prueba", protocolo["documentos"]["familias_prueba"])):
        filas = [{"id": f"Q-{familia}-{j}", "familia": familia, "pregunta": texto, "documento_esperado": doc}
                 for familia, doc, *textos in preguntas if familia in familias
                 for j, texto in enumerate(textos)]
        guardar(destino / "documentos" / f"{fase}.json", filas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta de destino; no modifica datos por defecto.")
    generar(parser.parse_args().salida)
    print("Datos U34: 959 decisiones de energía, 480 registros ambientales y 24 preguntas.")

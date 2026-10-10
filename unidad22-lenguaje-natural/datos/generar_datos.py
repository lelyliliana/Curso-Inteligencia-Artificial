"""Textos propios: se asigna cada familia a una partición antes de expandirla."""
import argparse
import csv
import hashlib
from pathlib import Path

TEMAS = ("robótica", "programación", "estadística")
CAMPOS = ("id", "familia", "tema", "texto", "clase", "sha256")
# Las familias, y no las variantes por tema, son los orígenes del experimento.
PLANTILLAS = {
    "entrenamiento": {
        "acceso": [
            "No puedo entrar al aula de {tema}, necesito acceso.",
            "Mi contraseña de {tema} falla al iniciar sesión.",
            "Quiero recuperar la cuenta del curso de {tema}.",
            "El usuario de {tema} está bloqueado y no puedo ingresar.",
            "Necesito acceso, no material, para estudiar {tema}.",
            "Solicito ayuda con el ingreso a la plataforma de {tema}.",
        ],
        "material": [
            "Necesito descargar el material del curso de {tema}.",
            "Busco los apuntes y las lecturas de {tema}.",
            "Quiero una copia de la guía de ejercicios de {tema}.",
            "El archivo de la clase de {tema} no está disponible.",
            "Necesito material, no acceso, para estudiar {tema}.",
            "Solicito el documento y las diapositivas de {tema}.",
        ],
        "horario": [
            "¿Cuál es el horario de la clase de {tema}?",
            "Necesito saber la fecha del taller de {tema}.",
            "¿A qué hora empieza la sesión de {tema}?",
            "Quiero confirmar el día de la reunión de {tema}.",
            "Busco el calendario de actividades de {tema}.",
            "Solicito información sobre cuándo será el encuentro de {tema}.",
        ],
    },
    "validacion": {
        "acceso": [
            "La cuenta de {tema} no me deja iniciar sesión.",
            "¿Cómo recupero mi contraseña para ingresar a {tema}?",
            "Ya tengo el material de {tema}; lo que falla es el acceso.",
        ],
        "material": [
            "¿Dónde encuentro el documento de ejercicios de {tema}?",
            "Puedo ingresar a {tema}, pero necesito los apuntes.",
            "No pregunto por el horario de {tema}, quiero las diapositivas.",
        ],
        "horario": [
            "¿Me confirman la hora y el día del encuentro de {tema}?",
            "¿Cuándo comienza la próxima clase de {tema}?",
            "No necesito la guía de {tema}; busco la fecha del taller.",
        ],
    },
    "prueba": {
        "acceso": [
            "Al entrar a {tema} aparece usuario bloqueado.",
            "Olvidé la contraseña de {tema}; ¿cómo recupero el acceso?",
            "La fecha de {tema} está clara, pero mi cuenta no funciona.",
        ],
        "material": [
            "¿Me comparten las lecturas y el archivo de {tema}?",
            "La sesión de {tema} ya terminó y busco sus diapositivas.",
            "El acceso a {tema} funciona; falta la guía para descargar.",
        ],
        "horario": [
            "¿En qué fecha y hora nos reunimos para {tema}?",
            "Tengo los apuntes de {tema}, solo falta confirmar el horario.",
            "¿El encuentro de {tema} sigue en el mismo día del calendario?",
        ],
    },
}


def generar(destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for particion, clases in PLANTILLAS.items():
        with (destino / f"{particion}.csv").open("w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
            escritor.writeheader()
            for clase, plantillas in clases.items():
                for numero, plantilla in enumerate(plantillas, 1):
                    familia = f"{particion[:3]}-{clase}-{numero:02d}"
                    for variante, tema in enumerate(TEMAS, 1):
                        texto = plantilla.format(tema=tema)
                        escritor.writerow({"id": f"{familia}-{variante}", "familia": familia,
                                           "tema": tema, "texto": texto, "clase": clase,
                                           "sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    generar(parser.parse_args().salida)

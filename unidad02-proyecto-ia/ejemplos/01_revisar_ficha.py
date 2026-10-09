"""Revisa estructura y disponibilidad declarada; no determina viabilidad real."""

import argparse
import json
from pathlib import Path

FICHA = Path(__file__).resolve().parents[1] / "datos" / "proyecto_ejemplo.json"
CAMPOS_TEXTO = [
    "nombre", "problema", "usuario", "decision", "unidad_analisis",
    "instante_decision", "linea_base", "restricciones", "revision_humana",
    "fuera_alcance", "plan_evaluacion", "permisos_datos", "hipotesis_pendientes",
]


def texto_valido(valor: object) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def revisar(ficha: object) -> list[str]:
    if not isinstance(ficha, dict):
        return ["La ficha debe ser un objeto JSON."]
    problemas = []
    for campo in CAMPOS_TEXTO:
        if not texto_valido(ficha.get(campo)):
            problemas.append(f"Falta texto no vacío en {campo}.")
    salida = ficha.get("salida")
    if not isinstance(salida, dict):
        problemas.append("Falta el objeto salida.")
    else:
        tipos = {"clasificacion", "regresion", "agrupamiento", "recuperacion", "generacion", "planificacion"}
        if not isinstance(salida.get("tipo"), str) or salida["tipo"] not in tipos:
            problemas.append("El tipo de salida debe ser una de las tareas admitidas.")
        for campo in ["descripcion", "horizonte"]:
            if not texto_valido(salida.get(campo)):
                problemas.append(f"Falta salida.{campo}.")
    variables = ficha.get("variables")
    nombres = set()
    if not isinstance(variables, list) or not variables:
        problemas.append("Debe existir al menos una variable de entrada.")
    else:
        for numero, variable in enumerate(variables, start=1):
            if not isinstance(variable, dict):
                problemas.append(f"Variable {numero}: se necesita un objeto.")
                continue
            nombre = variable.get("nombre")
            if not texto_valido(nombre):
                problemas.append(f"Variable {numero}: falta nombre.")
            else:
                if nombre.strip() in nombres:
                    problemas.append(f"Variable {numero}: nombre repetido.")
                nombres.add(nombre.strip())
            if not texto_valido(variable.get("descripcion")):
                problemas.append(f"Variable {numero}: falta descripción.")
            if variable.get("disponible_en_decision") is not True:
                problemas.append(f"Variable {numero}: disponibilidad en la decisión no confirmada como true.")
    referencia = ficha.get("referencia")
    if not isinstance(referencia, dict):
        problemas.append("Falta el objeto referencia.")
    else:
        for campo in ["definicion", "procedencia"]:
            if not texto_valido(referencia.get(campo)):
                problemas.append(f"Falta referencia.{campo}.")
    criterios = ficha.get("criterios_exito")
    if not isinstance(criterios, list) or not criterios:
        problemas.append("Debe existir al menos un criterio de éxito.")
    else:
        for numero, criterio in enumerate(criterios, start=1):
            if not isinstance(criterio, dict) or not all(texto_valido(criterio.get(campo)) for campo in ["metrica", "objetivo"]):
                problemas.append(f"Criterio {numero}: faltan métrica u objetivo.")
    return problemas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ficha", type=Path, default=FICHA)
    args = parser.parse_args()
    try:
        ficha = json.loads(args.ficha.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error al leer la ficha: {error}\n")
    problemas = revisar(ficha)
    if problemas:
        for problema in problemas:
            print(f"REVISAR: {problema}")
        parser.exit(2, "La ficha requiere correcciones de estructura o disponibilidad declarada.\n")
    print("Estructura completa y disponibilidad declarada para las variables.")
    print("Revisión humana pendiente: comprobar datos, permisos, métricas, viabilidad y supuestos.")


if __name__ == "__main__":
    main()

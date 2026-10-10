"""Distingue hora del evento, disponibilidad y relleno de una historia."""
import argparse
from pathlib import Path
from series_curso import UNIDAD, agrupar, escribir_json, historia, leer_archivo, observado


def experimento():
    archivo = leer_archivo(UNIDAD / "datos/muestra.csv")
    grupos = agrupar(archivo)
    valor8, relleno8, _, motivos8 = historia(grupos, 8)
    valor10, relleno10, _, _ = historia(grupos, 10)
    estados = [observado(grupos, t)[1] for t in range(12)]
    return {"archivo": archivo, "estados_retrospectivos": estados,
            "hora8": {"valores": valor8.tolist(), "relleno": relleno8.tolist(), "motivos": motivos8},
            "hora10": {"valores": valor10.tolist(), "relleno": relleno10.tolist()},
            "media3_hora8": float(valor8[-3:].mean()),
            "conflictos": estados.count("conflicto"), "horas_sin_registro": estados.count("ausente")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    r = experimento()
    print(f"Filas={r['archivo']['auditoria']['filas']}; duplicados exactos={r['archivo']['auditoria']['duplicados_exactos']}; horas en conflicto={r['conflictos']}")
    print("Historia a las 08:10:", r["hora8"]["valores"])
    print(f"Media de tres horas disponible a las 08:10: {r['media3_hora8']:.1f} °C")
    print("Lectura de las 07:00: llega a las 09:30; no se usa a las 08:10.")
    if args.salida is not None:
        args.salida.mkdir(parents=True, exist_ok=False)
        escribir_json(args.salida / "informe.json", r)
        if args.graficos:
            from figuras_series import figura_auditoria, guardar
            guardar(figura_auditoria(r), args.salida, "disponibilidad")
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

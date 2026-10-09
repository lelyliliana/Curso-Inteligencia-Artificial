"""Matriz de confusión, ROC AUC por pares, AP y capacidad con empates."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"ejemplos"))
from decisiones import decidir, medidas, ordenacion


def auc_por_pares(y, scores):
    positivos = [s for real, s in zip(y, scores) if real == 1]
    negativos = [s for real, s in zip(y, scores) if real == 0]
    if not positivos or not negativos:
        return None
    return sum(1 if a > b else .5 if a == b else 0 for a in positivos for b in negativos)/(len(positivos)*len(negativos))


def main():
    y, scores = [1, 0, 1, 0], [.8, .8, .4, .1]
    m = medidas(y, [int(s >= .8) for s in scores], {"FP": 1, "FN": 6})
    print(f"Umbral 0.8: VP={m['VP']}; VN={m['VN']}; FP={m['FP']}; FN={m['FN']}; costo={m['costo_total']}")
    diagnostico = ordenacion(y, scores)
    print(f"ROC AUC por pares: {auc_por_pares(y, scores):.3f}; AP: {diagnostico['ap']:.6f}; Brier: {diagnostico['brier']:.4f}")
    filas = [{"caso_id": c, "lote_id": "L1", "puntuacion": s} for c, s in zip(("B", "A", "C", "D"), scores)]
    decisiones = decidir(filas, {"umbral": .4, "cupo": 1})
    print("Cupo 1, empate a 0.8: seleccionado", next(f["caso_id"] for f, d in zip(filas, decisiones) if d))
    print("El ID resuelve un empate operativo; no representa mayor necesidad de revisión.")


if __name__ == "__main__":
    main()

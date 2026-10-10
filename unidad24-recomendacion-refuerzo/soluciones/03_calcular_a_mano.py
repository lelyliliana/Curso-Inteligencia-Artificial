"""Una métrica de ranking y una actualización Q, con referencias escalares."""
from math import isclose, log2, sqrt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from recomendacion_curso import metricas_lista
from refuerzo_curso import valor_actualizado


def main():
    # Columnas A=(1,1,0), B=(1,0,1): producto=1; normas=sqrt(2).
    coseno = 1 / (sqrt(2)*sqrt(2))
    assert isclose(coseno, 0.5)
    m = metricas_lista(["B", "C", "D"], "C")
    assert m["acierto"] == 1 and isclose(m["ndcg"], 1/log2(3))
    q = valor_actualizado(0.2, -0.04, 0.8, False, alpha=0.5, gamma=0.9)
    terminal = valor_actualizado(0.2, -1, 0.8, True, alpha=0.5, gamma=0.9)
    assert isclose(q, 0.44) and isclose(terminal, -0.4)
    print(f"Coseno A,B={coseno:.2f}; Recall@3=1; NDCG@3={m['ndcg']:.6f}")
    print(f"Q no terminal={q:.2f}; Q terminal={terminal:.2f}")
    print("Un truncamiento externo conserva el objetivo no terminal: 0.68.")


if __name__ == "__main__":
    main()

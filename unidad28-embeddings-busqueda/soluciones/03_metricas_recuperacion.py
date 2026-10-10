"""Cálculo manual independiente de un ranking artificial."""
import math


def main():
    # Relevantes A y C; top-3 = B, C, D. Primera relevante en puesto 2.
    precision, recall, rr = 1/3, 1/2, 1/2
    # Segunda consulta respondible: ningún acierto. La tercera no tiene respuesta.
    mrr = (rr+0)/2
    assert math.isclose(mrr, .25)
    print(f'P@3={precision:.6f}; Recall@3={recall:.3f}; RR@3={rr:.3f}; MRR@3={mrr:.3f}')
    print('La consulta sin respuesta se informa aparte; no cambia ese denominador.')


if __name__ == '__main__':
    main()

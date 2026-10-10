"""Ejemplo ficticio: conteos por intento, concordancia y desempate."""


def main():
    # Tres familias con dos vistas; la primera se trunca en su segunda vista.
    contenido = [True, True, False, False, True, False]
    finalizada = [True, False, True, True, True, False]
    aceptadas = [a and b for a, b in zip(contenido, finalizada)]
    n = len(aceptadas)
    completas = sum(all(aceptadas[i:i+2]) for i in range(0, n, 2))
    assert sum(aceptadas) == 2 and completas == 0
    print(f'Aceptación por intento={sum(aceptadas)}/{n}; familias completas={completas}/3')
    print('Contenido correcto=3/6; una coincidencia truncada no es aceptada.')
    # Dos jueces humanos ficticios sobre cuatro respuestas, no una medición real.
    juez_a = [True, True, False, False]
    juez_b = [True, False, False, True]
    acuerdo = sum(a == b for a, b in zip(juez_a, juez_b))
    print(f'Acuerdo bruto ficticio={acuerdo}/4; revisar dos desacuerdos con la rúbrica.')
    print('Empate en aciertos: aplicar orden prefijado; no consultar cierre para desempatar.')


if __name__ == '__main__':
    main()

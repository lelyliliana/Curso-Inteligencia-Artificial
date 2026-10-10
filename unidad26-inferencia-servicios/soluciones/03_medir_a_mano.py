"""Duración, memoria y costo con cantidades ficticias, no tarifas comerciales."""


def main():
    tokens, decodificacion_ns, pared_s = 20, 2_000_000_000, 3
    velocidad = tokens / (decodificacion_ns / 1e9)
    extremo_a_extremo = tokens / pared_s
    parametros, bits = 8_000_000_000, 4
    bytes_pesos_ideal = parametros * bits / 8
    # Precios inventados por millón para practicar unidades, no para presupuestar.
    costo = 1000 / 1_000_000 * 2 + 200 / 1_000_000 * 8
    assert velocidad == 10 and abs(costo - 0.0036) < 1e-12
    print(f"Decodificación={velocidad:.1f} tokens/s; extremo a extremo={extremo_a_extremo:.2f} tokens/s")
    print(f"Pesos ideales: {bytes_pesos_ideal / 1e9:.1f} GB; {bytes_pesos_ideal / 2**30:.2f} GiB; falta sobrecarga y caché")
    print(f"Costo ficticio={costo:.4f} unidades monetarias; no es una tarifa vigente")


if __name__ == "__main__":
    main()

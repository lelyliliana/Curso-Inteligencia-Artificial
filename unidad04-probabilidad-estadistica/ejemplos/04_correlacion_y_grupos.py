"""Ejemplo construido: asociación global y dentro de grupos ficticios."""

import statistics


def main():
    # Valores fabricados; grupo es parte del contexto, no una etiqueta aprendida.
    grupos = {
        "A": [(1, 10), (2, 9), (3, 8)],
        "B": [(7, 30), (8, 29), (9, 28)],
    }
    todos = [par for casos in grupos.values() for par in casos]
    print("Pares sintéticos (x, y):", todos)
    print(f"Correlación global = {statistics.correlation([x for x,y in todos], [y for x,y in todos]):.6f}")
    for nombre, casos in grupos.items():
        correlacion = statistics.correlation([x for x,y in casos], [y for x,y in casos])
        print(f"Correlación en grupo {nombre} = {correlacion:.6f}")
    print("Cambiar el nivel de agregación cambia la asociación observada.")
    print("Ninguna de estas correlaciones demuestra un efecto causal.")
    print("Pearson necesita al menos dos pares y variación en ambas variables.")


if __name__ == "__main__":
    main()

"""Comparaciones de resultados numéricos entre entornos, sin omitir campos.

Los float admiten tolerancias explícitas. Conteos, booleanos, textos, tipos,
claves, longitudes y orden siguen siendo exactos. No valida huellas ni decide
qué metadatos de entorno pueden diferir: eso corresponde a cada prueba.
"""

import math


def assert_resultados(prueba, actual, esperado, *, rtol=1e-10, atol=1e-12,
                      tolerancias=None):
    """Compara árboles JSON; tolerancias usa rutas como tuplas de claves/índices."""
    tolerancias = {} if tolerancias is None else tolerancias
    for relativa, absoluta in [(rtol, atol), *tolerancias.values()]:
        if not all(math.isfinite(t) and t >= 0 for t in (relativa, absoluta)):
            raise ValueError("Las tolerancias deben ser finitas y no negativas")

    def comparar(a, e, ruta):
        lugar = "$" + "".join(f"[{k!r}]" for k in ruta)
        prueba.assertIs(type(a), type(e), f"Tipo diferente en {lugar}")
        if isinstance(e, dict):
            prueba.assertEqual(a.keys(), e.keys(), f"Claves diferentes en {lugar}")
            for clave in e:
                comparar(a[clave], e[clave], (*ruta, clave))
        elif isinstance(e, list):
            prueba.assertEqual(len(a), len(e), f"Longitud diferente en {lugar}")
            for i, (valor, referencia) in enumerate(zip(a, e)):
                comparar(valor, referencia, (*ruta, i))
        elif isinstance(e, float):
            relativa, absoluta = tolerancias.get(ruta, (rtol, atol))
            prueba.assertTrue(math.isfinite(a) and math.isfinite(e),
                              f"Número no finito en {lugar}")
            prueba.assertTrue(math.isclose(a, e, rel_tol=relativa, abs_tol=absoluta),
                              f"{lugar}: {a!r} != {e!r} (rtol={relativa}, atol={absoluta})")
        else:
            prueba.assertEqual(a, e, f"Valor diferente en {lugar}")

    comparar(actual, esperado, ())

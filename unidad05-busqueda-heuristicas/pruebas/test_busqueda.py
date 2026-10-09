"""Casos de corrección; la referencia enumera caminos simples en grafos pequeños."""

import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ejemplos"))
from busqueda import buscar, leer_problema


def costo_por_enumeracion(grafo, inicio, meta):
    def explorar(estado, visitados):
        if estado == meta:
            return 0.0
        costos = [costo + explorar(destino, visitados | {destino})
                  for destino,costo in grafo[estado] if destino not in visitados]
        return min(costos, default=math.inf)
    return explorar(inicio, {inicio})


class PruebasBusqueda(unittest.TestCase):
    def comprobar_camino(self, grafo, resultado):
        costo = sum(dict(grafo[a])[b] for a,b in zip(resultado["camino"], resultado["camino"][1:]))
        self.assertAlmostEqual(costo, resultado["costo"])

    def test_meta_se_acepta_al_extraer_no_al_generar(self):
        g = {"S": [("G",10),("A",1)], "A": [("G",1)], "G": []}
        for algoritmo in ("ucs","astar"):
            r = buscar(g,"S","G",algoritmo,{s:0 for s in g})
            self.assertEqual(r["camino"],["S","A","G"])
            self.assertEqual(r["costo"],2)

    def test_reabre_con_heuristica_admisible_inconsistente(self):
        ruta = Path(__file__).resolve().parents[1]/"datos/grafo_reapertura.json"
        g,s,t,h = leer_problema(ruta)
        r = buscar(g,s,t,"astar",h)
        self.assertEqual(r["costo"],3.5)
        self.assertEqual(r["expandidos"].count("A"),2)
        self.comprobar_camino(g,r)

    def test_registros_conservan_el_camino_original(self):
        # Voraz con h=0 puede extraer una meta antigua antes de propagar una mejora.
        g={"S":[("A",5),("B",1)],"A":[("C",1)],"B":[("A",1)],"C":[("G",1)],"G":[]}
        r=buscar(g,"S","G","voraz",{s:0 for s in g})
        self.assertEqual(r["camino"],["S","A","C","G"])
        self.assertEqual(r["costo"],7)
        self.comprobar_camino(g,r)

    def test_ciclos_cero_y_meta_inalcanzable(self):
        g={"S":[("A",0)],"A":[("S",0)],"G":[]}
        for algoritmo in ("bfs","dfs","ucs","voraz","astar"):
            r=buscar(g,"S","G",algoritmo,{s:0 for s in g})
            self.assertFalse(r["encontrado"])
            self.assertIsNone(r["costo"])
            self.assertEqual(len(r["expandidos"]),2)

    def test_inicio_igual_a_meta(self):
        for algoritmo in ("bfs","dfs","ucs","voraz","astar"):
            r=buscar({"S":[]},"S","S",algoritmo,{"S":0})
            self.assertEqual(r["camino"],["S"])
            self.assertEqual(r["costo"],0)
            self.assertEqual(r["expandidos"],[])

    def test_no_acepta_costos_negativos_o_no_finitos(self):
        for costo in (-1,float("nan"),float("inf"),True):
            with self.assertRaises(ValueError):
                buscar({"S":[("G",costo)],"G":[]},"S","G","ucs")

    def test_optimos_contra_enumeracion_independiente(self):
        rng=random.Random(7)
        estados=("S","A","B","G")
        for _ in range(20):
            g={s:[(t,rng.choice((0,.5,1,3))) for t in estados if t!=s and rng.random()<.45]
               for s in estados}
            verdaderos={s:costo_por_enumeracion(g,s,"G") for s in estados}
            h={s:0 if math.isinf(v) else v*rng.choice((0,.5,1)) for s,v in verdaderos.items()}
            for algoritmo in ("ucs","astar"):
                r=buscar(g,"S","G",algoritmo,h)
                if math.isinf(verdaderos["S"]):
                    self.assertFalse(r["encontrado"])
                else:
                    self.assertAlmostEqual(r["costo"],verdaderos["S"])
                    self.comprobar_camino(g,r)


if __name__ == "__main__":
    unittest.main()

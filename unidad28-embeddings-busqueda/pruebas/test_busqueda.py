"""Referencias matemáticas, fronteras y artefactos. Nunca llama al servidor."""
from copy import deepcopy
import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD/'ejemplos'))
import busqueda as b
import experimento as e


class Geometria(unittest.TestCase):
    def test_producto_manual(self):
        self.assertEqual(b.producto([1,2,-1],[3,4,5]), 6)

    def test_norma_manual(self):
        self.assertEqual(b.normalizar([3,4]), [.6,.8])

    def test_coseno_manual(self):
        self.assertAlmostEqual(b.coseno([1,0],[3,4]), .6)

    def test_escalado(self):
        self.assertAlmostEqual(b.coseno([2,1],[3,4]), b.coseno([20,10],[.3,.4]))

    def test_opuestos_ortogonales(self):
        self.assertEqual(b.coseno([1,0],[-1,0]), -1)
        self.assertEqual(b.coseno([1,0],[0,1]), 0)

    def test_cero_no_definido(self):
        with self.assertRaises(ValueError): b.coseno([0,0],[1,0])
        self.assertEqual(b.normalizar([0,0], permitir_cero=True), [0,0])

    def test_vectores_invalidos(self):
        for v in ([], [True], ['2'], [None], [float('inf')], [float('nan')]):
            with self.subTest(v=v), self.assertRaises(ValueError): b.normalizar(v)

    def test_dimension(self):
        with self.assertRaises(ValueError): b.producto([1],[1,2])

    def test_coseno_no_equivale_producto(self):
        self.assertGreater(b.producto([1,0],[3,4]), b.producto([1,0],[1,0]))
        self.assertLess(b.coseno([1,0],[3,4]), b.coseno([1,0],[1,0]))


class LexicoRanking(unittest.TestCase):
    def test_tokenizacion_unicode(self):
        self.assertEqual(b.tokens('ÁRBOL a\u0301rbol S-31_a'), ['árbol','árbol','s','31','a'])

    def test_idf_manual(self):
        estado = b.ajustar_tfidf(['sol sol agua', 'agua'])
        self.assertEqual(estado['vocabulario'], ['agua','sol'])
        self.assertEqual(estado['idf'], [1,1+math.log(3/2)])

    def test_frecuencia_cruda(self):
        estado = b.ajustar_tfidf(['a b'])
        self.assertEqual(b.transformar('a a b', estado), [2/math.sqrt(5),1/math.sqrt(5)])

    def test_referencia_sklearn(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        textos = ['sol sol agua', 'agua árbol', 'sensor árbol sol']
        estado = b.ajustar_tfidf(textos)
        lib = TfidfVectorizer(analyzer=b.tokens)
        matriz = lib.fit_transform(textos).toarray()
        for x, y in zip(matriz, [b.transformar(t, estado) for t in textos]):
            for a, z in zip(x,y): self.assertAlmostEqual(a,z, places=14)
        esperado = lib.transform(['sol desconocido']).toarray()[0]
        for x,y in zip(esperado,b.transformar('sol desconocido',estado)):
            self.assertAlmostEqual(x,y,places=14)

    def test_oov_no_ajusta_estado(self):
        estado = b.ajustar_tfidf(['sol agua'])
        antes = deepcopy(estado)
        self.assertEqual(b.transformar('xyz', estado), [0,0])
        self.assertEqual(estado, antes)

    def test_corpus_vacio(self):
        for textos in ([], ['!!!']):
            with self.assertRaises(ValueError): b.ajustar_tfidf(textos)

    def test_desempate_id(self):
        self.assertEqual([x['id'] for x in b.ranking(['b','a','c'], [[1,0]]*3,[1,0],2)], ['a','b'])

    def test_no_redondear(self):
        top = b.ranking(['a','b'], [[.12341],[.12342]],[1],1)
        self.assertEqual(top[0]['id'],'b')

    def test_k_invalido(self):
        for k in (True,0,-1,1.5,3):
            with self.subTest(k=k), self.assertRaises(ValueError): b.ranking(['a','b'],[[1],[1]],[1],k)

    def test_ids_y_filas(self):
        for ids, matriz in ((['a','a'],[[1],[1]]),(['a','b'],[[1]]),([''],[[1]])):
            with self.assertRaises(ValueError): b.ranking(ids,matriz,[1],1)

    def test_orden_negativos(self):
        self.assertEqual(b.ranking(['a','b'],[[-1],[-.5]],[1],1)[0]['id'],'b')


class MetricasDatos(unittest.TestCase):
    def test_metricas_manual(self):
        self.assertEqual(b.metricas(['B','C','D'],['A','C'],3),
                         {'precision':1/3,'recall':.5,'hit':1,'rr':.5})

    def test_sin_aciertos(self):
        self.assertEqual(b.metricas(['B'],['A'],3), {'precision':0,'recall':0,'hit':0,'rr':0})

    def test_varios_relevantes(self):
        self.assertEqual(b.metricas(['C','A','B'],['A','C'],3),
                         {'precision':2/3,'recall':1,'hit':1,'rr':1})

    def test_sin_respuesta_indefinido(self):
        self.assertEqual(b.metricas(['B'],[],3), dict.fromkeys(['precision','recall','hit','rr']))

    def test_metricas_ranking_invalido(self):
        for rec,rel,k in ((['a','a'],['a'],3),(['a'],['a','a'],3),(['a','b'],['a'],1),([],[],0)):
            with self.assertRaises(ValueError): b.metricas(rec,rel,k)

    def test_regeneracion(self):
        spec = importlib.util.spec_from_file_location('u28_datos', UNIDAD/'datos/generar_corpus.py')
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for nombre, filas in mod.construir().items():
            self.assertEqual(filas, b.cargar(UNIDAD/f'datos/{nombre}.json'))

    def test_particiones(self):
        dev, fin = [b.cargar(UNIDAD/f'datos/{f}.json') for f in ('desarrollo','cierre')]
        b.separar(dev,fin)
        self.assertEqual(len(dev),10); self.assertEqual(len(fin),10)
        for consultas in (dev, fin):
            self.assertEqual(sum(not q['relevantes'] for q in consultas),2)
            self.assertEqual(len({q['familia'] for q in consultas}),5)
            b.validar_datos(b.cargar(UNIDAD/'datos/corpus.json'),consultas)
        with self.assertRaises(ValueError): b.separar(dev,dev)

    def test_juicios_desconocidos(self):
        consultas = b.cargar(UNIDAD/'datos/desarrollo.json')
        consultas[0]['relevantes']=['inexistente']
        with self.assertRaises(ValueError): b.validar_datos(b.cargar(UNIDAD/'datos/corpus.json'),consultas)

    def test_ids_duplicados(self):
        corpus = b.cargar(UNIDAD/'datos/corpus.json')
        with self.assertRaises(ValueError): b.validar_datos(corpus+corpus,b.cargar(UNIDAD/'datos/desarrollo.json'))


class Capturas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registro = b.cargar(e.RECURSOS/'desarrollo/registro.json')
        cls.indice, cls.seleccion, cls.informe = e.desarrollo(cls.registro)
        cls.corpus = b.cargar(UNIDAD/'datos/corpus.json')

    def test_peticion_no_incluye_juicios(self):
        r = e.peticion('Texto de prueba')
        self.assertEqual(r['input'],'Texto de prueba')
        self.assertIs(r['truncate'],False)
        self.assertEqual(r['options']['num_gpu'],0)
        self.assertNotIn('relevantes',r)

    def test_entrada_invalida(self):
        for x in ('', ' ', None, 'a'*2001):
            with self.assertRaises(ValueError): e.peticion(x)

    def test_dimensiones_respuesta(self):
        r = deepcopy(self.registro['filas'][0]['respuesta'])
        for vectors in ([], [[0]*1024], [[1]*3], [[1]*1024]*2, [[True]*1024], [[float('nan')]*1024]):
            r['embeddings']=vectors
            with self.subTest(vectors=str(vectors)[:30]), self.assertRaises(ValueError): e.leer_embedding(r)

    def test_modelo_respuesta(self):
        r=deepcopy(self.registro['filas'][0]['respuesta']); r['model']='otro'
        with self.assertRaises(ValueError): e.leer_embedding(r)

    def test_tiempos_respuesta(self):
        r=deepcopy(self.registro['filas'][0]['respuesta']); r['total_duration']=-1
        with self.assertRaises(ValueError): e.leer_embedding(r)

    def test_endpoint_embed_local(self):
        observado=[]
        def abrir(req, timeout):
            observado.append(req)
            return io.BytesIO(b'{"embeddings": []}')
        e.solicitar(e.OLLAMA+'/api/embed',e.peticion('hola'),abrir_http=abrir)
        self.assertEqual(observado[0].full_url,e.OLLAMA+'/api/embed')
        self.assertFalse(observado[0].has_header('Authorization'))
        with self.assertRaises(ValueError): e.solicitar('https://otro.example/api/embed',{},abrir_http=abrir)

    def test_captura_incompleta(self):
        r=deepcopy(self.registro); r['filas'].pop()
        with self.assertRaises(ValueError): e.validar_captura(r,'desarrollo')

    def test_orden_alterado(self):
        r=deepcopy(self.registro); r['filas'][0],r['filas'][1]=r['filas'][1],r['filas'][0]
        with self.assertRaises(ValueError): e.validar_captura(r,'desarrollo')

    def test_peticion_alterada(self):
        r=deepcopy(self.registro); r['filas'][0]['solicitud']['truncate']=True
        with self.assertRaises(ValueError): e.validar_captura(r,'desarrollo')

    def test_huellas_alteradas(self):
        r=deepcopy(self.registro); r['huellas']['corpus.json']='x'
        with self.assertRaises(ValueError): e.validar_captura(r,'desarrollo')

    def test_indice_incompatible(self):
        for campo,valor in (('corpus_sha256','x'),('nucleo_sha256','x'),('config',{}),('ids',[])):
            r=deepcopy(self.indice); r[campo]=valor
            with self.subTest(campo=campo), self.assertRaises(ValueError): b.validar_indice(r,self.corpus)

    def test_matriz_indice_invalida(self):
        r=deepcopy(self.indice); r['matrices']['bge_m3'][0][0]=4
        with self.assertRaises(ValueError): b.validar_indice(r,self.corpus)

    def test_seleccion_cambiada(self):
        s=deepcopy(self.seleccion); s['metodo']='tfidf'
        with self.assertRaises(ValueError): e.comprobar_seleccion(self.indice,s,self.registro)

    def test_empate_prefiere_lexico(self):
        ev=deepcopy(self.informe['evaluaciones'])
        for x in ev: x['resumen']['rr']=.5
        self.assertEqual(b.elegir(ev),'tfidf')

    def test_desarrollo_no_abre_cierre(self):
        real=b.cargar
        def lectura(ruta):
            self.assertNotEqual(Path(ruta).name,'cierre.json')
            return real(ruta)
        with patch.object(e,'cargar',side_effect=lectura):
            self.assertEqual(e.desarrollo(self.registro)[1],self.seleccion)

    def test_recarga_rankings(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'indice.json'; b.guardar(p,self.indice)
            nuevo=b.cargar(p); b.validar_indice(nuevo,self.corpus)
            qs=b.cargar(UNIDAD/'datos/desarrollo.json')
            vs=e.validar_captura(self.registro,'desarrollo')['consulta']
            for m in b.METODOS:
                self.assertEqual(b.evaluar(nuevo,qs,m,vs),b.evaluar(self.indice,qs,m,vs))

    def test_resultados_desarrollo_publicados(self):
        self.assertEqual(self.indice,b.cargar(e.RECURSOS/'desarrollo/indice.json'))
        self.assertEqual(self.seleccion,b.cargar(e.RECURSOS/'desarrollo/seleccion.json'))
        self.assertEqual(self.informe,b.cargar(e.RECURSOS/'desarrollo/informe.json'))
        rs=[x['resumen'] for x in self.informe['evaluaciones']]
        self.assertEqual([r['rr'] for r in rs],[.5625,1.0])
        self.assertEqual([r['recall'] for r in rs],[.625,1.0])
        self.assertEqual([r['sin_respuesta_con_candidatos'] for r in rs],[2,2])

    def test_cierre_publicado(self):
        registro=b.cargar(e.RECURSOS/'cierre/registro.json')
        resultado=e.cierre(self.indice,self.seleccion,self.registro,registro)
        self.assertEqual(resultado,b.cargar(e.RECURSOS/'cierre/informe.json'))
        self.assertEqual(len(resultado['evaluaciones']),1)
        r=deepcopy(registro); r['seleccion_sha256']='x'
        with self.assertRaises(ValueError): e.cierre(self.indice,self.seleccion,self.registro,r)

    def test_cierre_otro_espacio(self):
        registro=b.cargar(e.RECURSOS/'cierre/registro.json')
        registro['inventario']['digest']='otro'
        with self.assertRaises(ValueError): e.cierre(self.indice,self.seleccion,self.registro,registro)


if __name__ == '__main__':
    unittest.main()

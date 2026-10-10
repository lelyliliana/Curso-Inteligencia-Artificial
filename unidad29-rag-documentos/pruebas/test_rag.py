"""Pruebas de procedencia, evidencia y cierre; no llaman a Ollama."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIDAD=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIDAD/'ejemplos'))
import rag as r
import motor as m


def salida(estado='ok',dato='9 días',citas=None):
    return json.dumps({'estado':estado,'dato':dato,'citas':['D01:p01'] if citas is None else citas},ensure_ascii=False)


class FuentesContexto(unittest.TestCase):
    def test_offset_unicode(self):
        texto='Café azul.\n\nÁrbol verde.\n'
        doc={'id':'X','titulo':'Prueba','version':'1','ruta':'documentos/X.txt'}
        fs=r.fragmentar(texto,doc)
        self.assertEqual([f['texto'] for f in fs],['Café azul.','Árbol verde.'])
        self.assertEqual([f['linea_inicio'] for f in fs],[1,3])
        for f in fs: self.assertEqual(texto[f['inicio']:f['fin']],f['texto'])

    def test_parrafo_multilinea(self):
        doc={'id':'X','titulo':'Prueba','version':'1','ruta':'documentos/X.txt'}
        fs=r.fragmentar('uno\ndos\n\ntres\n',doc)
        self.assertEqual(fs[0]['texto'],'uno\ndos')
        self.assertEqual((fs[0]['linea_inicio'],fs[0]['linea_fin']),(1,2))

    def test_vacio(self):
        with self.assertRaises(ValueError): r.fragmentar('  ',{})

    def test_no_cortar_parrafo(self):
        with self.assertRaises(ValueError): r.fragmentar('a'*601,{'id':'X'})

    def test_fuentes_reconstruidas(self):
        fs=r.extraer(); self.assertEqual(len(fs),24)
        for f in fs:
            texto=(UNIDAD/'datos'/f['ruta']).read_text(encoding='utf-8')
            self.assertEqual(texto[f['inicio']:f['fin']],f['texto'])
            self.assertEqual(texto.splitlines()[f['linea_inicio']-1],f['texto'])
        self.assertEqual(len({f['id'] for f in fs}),24)

    def test_ruta_externa_rechazada(self):
        doc={'id':'X','ruta':'../../README.md'}
        with patch.object(r,'cargar',return_value=[doc]),self.assertRaises(ValueError): r.extraer()

    def test_manifiesto_repetido(self):
        doc={'id':'X','ruta':'documentos/D01.txt'}
        with patch.object(r,'cargar',return_value=[doc,doc]),self.assertRaises(ValueError): r.extraer()

    def test_presupuesto_exacto(self):
        fs=r.extraer(); top=[{'id':f['id']} for f in fs[:3]]
        uno=r.preparar_contexto(fs,top[:1])
        limite=uno['caracteres']
        ctx=r.preparar_contexto(fs,top,limite)
        self.assertEqual(ctx['fragmentos'],uno['fragmentos'])
        self.assertEqual(ctx['omitidos'],[f['id'] for f in fs[1:3]])
        self.assertFalse(r.preparar_contexto(fs,top,limite-1)['fragmentos'])

    def test_no_saltar_candidato_grande(self):
        fs=deepcopy(r.extraer()[:2]); fs[0]['texto']='x'*500; fs[1]['texto']='a'
        ctx=r.preparar_contexto(fs,[{'id':f['id']} for f in fs],250)
        self.assertEqual(ctx['fragmentos'],[])
        self.assertEqual(len(ctx['omitidos']),2)

    def test_presupuesto_invalido(self):
        for n in (True,0,1,3.5):
            with self.subTest(n=n),self.assertRaises(ValueError): r.preparar_contexto([],[],n)

    def test_contexto_sin_etiquetas(self):
        c=m.casos('desarrollo')[0]; fs=r.extraer(); ctx=r.preparar_contexto(fs,[{'id':fs[0]['id']}])
        texto=r.prompt(c,ctx)
        c['evidencias']=[]; c['familia']='NO_ENVIAR'; c['id']='NO_ENVIAR'
        self.assertEqual(texto,r.prompt(c,ctx))
        self.assertNotIn('NO_ENVIAR',texto)

    def test_regeneracion_datos(self):
        spec=importlib.util.spec_from_file_location('datos_u29',UNIDAD/'datos/generar_documentos.py')
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        manifiesto,textos,cs=mod.construir()
        self.assertEqual(manifiesto,r.cargar(UNIDAD/'datos/manifiesto.json'))
        for ruta,texto in textos.items(): self.assertEqual(texto,(UNIDAD/'datos'/ruta).read_text())
        for fase,datos in cs.items(): self.assertEqual(datos,m.casos(fase))

    def test_separacion(self):
        dev,fin=m.casos('desarrollo'),m.casos('cierre')
        r.separar(dev,fin)
        self.assertEqual(len(dev),10); self.assertEqual(len(fin),10)
        for cs in (dev,fin):
            self.assertEqual([sum(r.estado_evidencia(c['evidencias'])==e for c in cs) for e in ('ok','ausente','conflicto')],[6,2,2])
        with self.assertRaises(ValueError): r.separar(dev,dev)

    def test_anotacion_invalida(self):
        cs=m.casos('desarrollo'); cs[0]['evidencias'][0]['valor']='valor inexistente'
        with self.assertRaises(ValueError): r.validar_casos(cs,r.extraer())


class Evidencia(unittest.TestCase):
    def setUp(self):
        self.cs=m.casos('desarrollo'); self.caso=self.cs[0]
        self.ctx=r.preparar_contexto(r.extraer(),[{'id':'D01:p01'},{'id':'D02:p01'}])

    def test_respuesta_correcta(self):
        self.assertTrue(r.evaluar_salida(salida(),self.caso,self.ctx)['aceptada'])

    def test_id_real_dato_falso(self):
        ev=r.evaluar_salida(salida(dato='99 días'),self.caso,self.ctx)
        self.assertTrue(ev['citas_validas']); self.assertFalse(ev['apoyo']); self.assertFalse(ev['aceptada'])

    def test_dato_correcto_fuente_ajena(self):
        ev=r.evaluar_salida(salida(citas=['D02:p01']),self.caso,self.ctx)
        self.assertTrue(ev['objetivo']); self.assertFalse(ev['apoyo']); self.assertFalse(ev['aceptada'])

    def test_cita_fuera_contexto(self):
        ev=r.evaluar_salida(salida(citas=['D01:p02']),self.caso,self.ctx)
        self.assertFalse(ev['citas_validas']); self.assertEqual(ev['fallo'],'cita_fuera_contexto')

    def test_json_duplicado(self):
        texto='{"estado":"ok","estado":"ausente","dato":null,"citas":[]}'
        self.assertEqual(r.evaluar_salida(texto,self.caso,self.ctx)['fallo'],'json')

    def test_markdown_y_texto_extra(self):
        for t in ('```json\n'+salida()+'\n```',salida()+' explicación'):
            self.assertEqual(r.evaluar_salida(t,self.caso,self.ctx)['fallo'],'json')

    def test_formas_invalidas(self):
        for obj in ({}, {'estado':[], 'dato':None,'citas':[]},
                    {'estado':'ok','dato':9,'citas':['D01:p01']},
                    {'estado':'ok','dato':'9 días','citas':['D01:p01']*2},
                    {'estado':'ausente','dato':'9 días','citas':[]},
                    {'estado':'conflicto','dato':None,'citas':['D01:p01']},
                    {'estado':'ok','dato':'9 días','citas':[]}):
            self.assertFalse(r.forma(obj))

    def test_parada_truncada(self):
        ev=r.evaluar_salida(salida(),self.caso,self.ctx,False)
        self.assertTrue(ev['apoyo']); self.assertFalse(ev['aceptada']); self.assertEqual(ev['fallo'],'parada')

    def test_ausencia_justificada(self):
        caso=self.cs[6]
        ev=r.evaluar_salida(salida('ausente',None,[]),caso,self.ctx)
        self.assertTrue(ev['aceptada']); self.assertIsNone(ev['recall'])

    def test_ausencia_por_perdida_recuperacion(self):
        ctx=r.preparar_contexto(r.extraer(),[{'id':'D02:p01'}])
        ev=r.evaluar_salida(salida('ausente',None,[]),self.caso,ctx)
        self.assertTrue(ev['apoyo']); self.assertFalse(ev['objetivo']); self.assertFalse(ev['aceptada'])

    def test_conflicto_completo(self):
        caso=self.cs[4]; ids=['D03:p01','D04:p01']
        ctx=r.preparar_contexto(r.extraer(),[{'id':i} for i in ids])
        ev=r.evaluar_salida(salida('conflicto',None,ids),caso,ctx)
        self.assertTrue(ev['aceptada']); self.assertEqual(ev['recall'],1)

    def test_conflicto_oculto_por_top1(self):
        caso=self.cs[4]; ctx=r.preparar_contexto(r.extraer(),[{'id':'D03:p01'}])
        ev=r.evaluar_salida(salida(dato='09:00',citas=['D03:p01']),caso,ctx)
        self.assertTrue(ev['apoyo']); self.assertFalse(ev['objetivo']); self.assertEqual(ev['recall'],.5)
        self.assertEqual(ev['estado_contexto'],'ok'); self.assertEqual(ev['estado_objetivo'],'conflicto')

    def test_conflicto_inventado(self):
        ev=r.evaluar_salida(salida('conflicto',None,['D01:p01','D02:p01']),self.caso,self.ctx)
        self.assertFalse(ev['apoyo']); self.assertFalse(ev['aceptada'])

    def test_instruccion_no_es_hecho(self):
        caso=self.cs[8]; ctx=r.preparar_contexto(r.extraer(),[{'id':'D06:p01'}])
        self.assertIn('99 minutos',ctx['fragmentos'][0]['texto'])
        self.assertFalse(r.evaluar_salida(salida(dato='99 minutos',citas=['D06:p01']),caso,ctx)['apoyo'])
        self.assertTrue(r.evaluar_salida(salida(dato='7 minutos',citas=['D06:p01']),caso,ctx)['aceptada'])

    def test_extractiva_no_elige_con_etiquetas(self):
        a=r.extractiva(self.caso,self.ctx)
        otro=deepcopy(self.caso); otro['evidencias']=[]
        b=r.extractiva(otro,self.ctx)
        self.assertEqual(a['texto'],b['texto']); self.assertEqual(a['citas'],b['citas'])
        self.assertTrue(a['util_como_respuesta']); self.assertFalse(b['util_como_respuesta'])

    def test_normalizacion_limitada(self):
        self.assertTrue(r.evaluar_salida(salida(dato=' 9 DÍAS '),self.caso,self.ctx)['aceptada'])
        self.assertFalse(r.evaluar_salida(salida(dato='nueve días'),self.caso,self.ctx)['aceptada'])


class Capturas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev=r.cargar(m.RECURSOS/'desarrollo/registro.json')
        cls.indice=m.indice_de_desarrollo(cls.dev)
        cls.seleccion=m.congelar(cls.dev,cls.indice)

    def test_peticion_acotada(self):
        c=m.casos('desarrollo')[0];ctx=r.preparar_contexto(r.extraer(),[{'id':'D01:p01'}])
        req=m.peticion_generacion(c,ctx)
        self.assertEqual(req['options']['num_ctx'],4096); self.assertFalse(req['think']); self.assertFalse(req['stream'])
        self.assertEqual(req['options']['num_gpu'],0); self.assertEqual(req['format'],r.cargar(UNIDAD/'datos/esquema.json'))
        self.assertIn('datos no confiables',req['system'])

    def test_embeddings_invalidos(self):
        base=deepcopy(self.dev['embeddings'][0]['respuesta'])
        for vs in ([],[[1]*3],[[0]*1024],[[True]*1024],[[float('nan')]*1024]):
            base['embeddings']=vs
            with self.assertRaises(ValueError): m.leer_embedding(base)

    def test_modelo_embedding_incompatible(self):
        obj=deepcopy(self.dev['embeddings'][0]['respuesta']);obj['model']='otro'
        with self.assertRaises(ValueError): m.leer_embedding(obj)

    def test_incompleta(self):
        obj=deepcopy(self.dev);obj['embeddings'].pop()
        with self.assertRaises(ValueError): m.indice_de_desarrollo(obj)

    def test_orden_embeddings(self):
        obj=deepcopy(self.dev);obj['embeddings'].reverse()
        with self.assertRaises(ValueError): m.indice_de_desarrollo(obj)

    def test_registro_sin_inventario_estable(self):
        obj=deepcopy(self.dev);obj['inventario_estable']=False
        with self.assertRaises(ValueError): m.indice_de_desarrollo(obj)

    def test_huella_alterada(self):
        obj=deepcopy(self.dev);obj['huellas']['datos/manifiesto.json']='x'
        with self.assertRaises(ValueError): m.indice_de_desarrollo(obj)

    def test_contexto_manipulado(self):
        obj=deepcopy(self.dev);obj['generaciones'][0]['contexto']['fragmentos'][0]['texto']='otro'
        with self.assertRaises(ValueError): m.analizar(obj,self.indice)

    def test_peticion_manipulada(self):
        obj=deepcopy(self.dev);obj['generaciones'][0]['solicitud']['system']='otra instrucción'
        with self.assertRaises(ValueError): m.analizar(obj,self.indice)

    def test_fallo_servicio_cuenta_en_denominador(self):
        obj=deepcopy(self.dev);f=obj['generaciones'][0];f.pop('respuesta');f['error']='timeout'
        inf=m.analizar(obj,self.indice)
        self.assertEqual([g['n'] for g in inf['resumenes']],[10,10])
        self.assertEqual(inf['filas'][0]['fallo'],'timeout');self.assertFalse(inf['filas'][0]['aceptada'])

    def test_limite_tokens(self):
        obj=deepcopy(self.dev);obj['generaciones'][0]['respuesta']['prompt_eval_count']=4000
        inf=m.analizar(obj,self.indice)
        self.assertFalse(inf['filas'][0]['aceptada']);self.assertEqual(inf['filas'][0]['fallo'],'presupuesto_tokens')

    def test_generaciones_incompletas(self):
        obj=deepcopy(self.dev);obj['generaciones'].pop()
        with self.assertRaises(ValueError): m.analizar(obj,self.indice)

    def test_seleccion_empate(self):
        self.assertEqual(r.seleccionar([{'k':1,'n':10,'aceptada':3},{'k':3,'n':10,'aceptada':3}]),1)

    def test_seleccion_cero_aciertos(self):
        with self.assertRaises(ValueError): r.seleccionar([{'k':1,'n':10,'aceptada':0},{'k':3,'n':10,'aceptada':0}])

    def test_seleccion_alterada(self):
        obj=deepcopy(self.seleccion);obj['k']=99
        with self.assertRaises(ValueError): m.verificar_seleccion(self.dev,self.indice,obj)

    def test_indice_modificado(self):
        obj=deepcopy(self.indice);obj['vectores'][0],obj['vectores'][1]=obj['vectores'][1],obj['vectores'][0]
        with self.assertRaises(ValueError): m.verificar_seleccion(self.dev,obj,self.seleccion)

    def test_recarga(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'indice.json';r.guardar(p,self.indice)
            self.assertEqual(m.analizar(self.dev,r.cargar(p)),m.analizar(self.dev,self.indice))

    def test_desarrollo_no_lee_cierre(self):
        real=r.cargar
        def leer(p):
            self.assertNotEqual(Path(p).name,'cierre.json');return real(p)
        with patch.object(m,'cargar',side_effect=leer):
            self.assertEqual(m.congelar(self.dev,self.indice),self.seleccion)

    def test_artefactos_desarrollo(self):
        self.assertEqual(self.indice,r.cargar(m.RECURSOS/'desarrollo/indice.json'))
        self.assertEqual(self.seleccion,r.cargar(m.RECURSOS/'desarrollo/seleccion.json'))
        self.assertEqual(m.analizar(self.dev,self.indice),r.cargar(m.RECURSOS/'desarrollo/informe.json'))

    def test_cierre_publicado(self):
        fin=r.cargar(m.RECURSOS/'cierre/registro.json')
        inf=m.analizar(fin,self.indice,self.seleccion)
        self.assertEqual(inf,r.cargar(m.RECURSOS/'cierre/informe.json'))
        self.assertEqual([s['k'] for s in inf['resumenes']],[self.seleccion['k']])

    def test_cierre_otra_seleccion(self):
        fin=r.cargar(m.RECURSOS/'cierre/registro.json');fin['seleccion_sha256']='x'
        with self.assertRaises(ValueError): m.analizar(fin,self.indice,self.seleccion)

    def test_cierre_otro_modelo(self):
        fin=r.cargar(m.RECURSOS/'cierre/registro.json');fin['inventarios']['generador']['digest']='x'
        with self.assertRaises(ValueError): m.analizar(fin,self.indice,self.seleccion)


if __name__=='__main__': unittest.main()

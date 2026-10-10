"""Referencias matemáticas, causalidad, separación, generación y persistencia."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

UNIDAD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIDAD / "ejemplos"))
import atencion as at
import transformer_curso as tc
spec = importlib.util.spec_from_file_location("generador_u25", UNIDAD / "datos/generar_datos.py")
generador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generador)
tc.configurar()


class Fijo(nn.Module):
    def __init__(self, n, indice):
        super().__init__()
        self.n, self.indice = n, indice
        self.entradas = []

    def forward(self, x):
        self.entradas.append(x.clone())
        r = torch.full((*x.shape, self.n), -100.)
        r[..., self.indice] = 0
        return r


class AtencionYModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = at.experimento()
        cls.modelo, cls.vocab = tc.cargar(UNIDAD / "recursos/generacion/modelo.json")
        cls.filas = tc.leer(UNIDAD / "datos/validacion.json")
        cls.x, cls.y, cls.m = tc.preparar(cls.filas, cls.vocab)

    def test_manual_pesos(self):
        np.testing.assert_allclose(self.r["pesos_causales"], [[1,0,0],[1/3,2/3,0],[.25,.25,.5]], atol=1e-12)

    def test_manual_salida(self):
        np.testing.assert_allclose(self.r["salida"], [[2,0],[2/3,4/3],[1.5,1.5]], atol=1e-12)

    def test_referencia_biblioteca(self):
        self.assertLess(self.r["error_biblioteca"], 1e-12)
        self.assertLess(self.r["error_manual"], 1e-12)

    def test_filas_y_mascara(self):
        p = np.asarray(self.r["pesos_causales"])
        np.testing.assert_allclose(p.sum(axis=1), 1)
        np.testing.assert_array_equal(p[np.triu_indices(3,1)], 0)

    def test_futuro_modificado(self):
        self.assertEqual(self.r["cambio_pasado_causal"], 0)
        self.assertGreater(self.r["cambio_pasado_libre"], 1)

    def test_atencion_rechaza_formas_y_no_finitos(self):
        for q,k,v in (([[1]], [[1,2]], [[1]]), ([[float('nan')]], [[1]], [[1]]), ([],[],[])):
            with self.assertRaises(ValueError):
                at.atender(q,k,v)

    def test_dimensiones_y_parametros(self):
        logits, pesos = self.modelo(self.x, True)
        self.assertEqual(logits.shape, (*self.x.shape, 26))
        self.assertEqual(pesos.shape, (16, 2, self.x.shape[1], self.x.shape[1]))
        self.assertEqual(sum(p.numel() for p in self.modelo.parameters()), 11066)

    def test_logits_causales_al_cambiar_sufijo(self):
        x = self.x[:1].clone()
        otro = x.clone()
        otro[:, 6:] = self.vocab.index("agua")
        torch.testing.assert_close(self.modelo(x)[:, :6], self.modelo(otro)[:, :6], atol=1e-6, rtol=0)

    def test_gradiente_no_consulta_futuro(self):
        emb = []
        def capturar(_, __, salida):
            salida.retain_grad()
            emb.append(salida)
        hook = self.modelo.token.register_forward_hook(capturar)
        self.modelo.zero_grad(set_to_none=True)
        self.modelo(self.x[:1])[0, 5].sum().backward()
        hook.remove()
        self.assertEqual(float(emb[0].grad[:, 6:].abs().max()), 0)
        self.assertGreater(float(emb[0].grad[:, :6].abs().sum()), 0)
        self.modelo.zero_grad(set_to_none=True)

    def test_relleno_no_cambia_logits_utiles(self):
        x, _, _ = tc.preparar(self.filas[:1], self.vocab)
        extra = F.pad(x, (0, 4), value=tc.PAD)
        torch.testing.assert_close(self.modelo(x), self.modelo(extra)[:, :x.shape[1]], atol=2e-6, rtol=0)

    def test_pesos_no_atienden_pad_o_futuro(self):
        _, p = self.modelo(self.x, True)
        futuro = torch.triu(torch.ones(self.x.shape[1], self.x.shape[1], dtype=torch.bool), 1)
        prohibido = futuro[None,None] | self.x.eq(tc.PAD)[:,None,None,:]
        self.assertEqual(float(p.masked_select(prohibido.expand_as(p)).abs().max().detach()), 0)
        torch.testing.assert_close(p.sum(-1), torch.ones_like(p.sum(-1)))

    def test_multihead_con_sdpa_independiente(self):
        contexto = []
        hook = self.modelo.proyeccion.register_forward_pre_hook(lambda _, args: contexto.append(args[0].detach()))
        self.modelo(self.x)
        hook.remove()
        b,t = self.x.shape
        z = self.modelo.norm1(self.modelo.token(self.x) + self.modelo.posicion(torch.arange(t))[None])
        q,k,v = self.modelo.qkv(z).reshape(b,t,3,2,16).permute(2,0,3,1,4).unbind(0)
        permitido = torch.ones(t,t,dtype=torch.bool).tril()[None,None] & self.x.ne(tc.PAD)[:,None,None,:]
        ref = F.scaled_dot_product_attention(q,k,v,attn_mask=permitido,dropout_p=0).transpose(1,2).reshape(b,t,32)
        torch.testing.assert_close(contexto[0], ref, atol=2e-6, rtol=1e-6)

    def test_rechaza_contexto_y_padding_invalido(self):
        for x in (torch.ones(1,25,dtype=torch.long), torch.tensor([[0,1]]), torch.tensor([[1,0,4]])):
            with self.assertRaises(ValueError):
                self.modelo(x)

    def test_modo_eval_repetible(self):
        self.modelo.eval()
        with torch.inference_mode():
            torch.testing.assert_close(self.modelo(self.x), self.modelo(self.x), atol=0, rtol=0)


class DatosYPerdida(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = tc.leer(UNIDAD / "datos/entrenamiento.json")
        cls.val = tc.leer(UNIDAD / "datos/validacion.json")
        cls.vocab = tc.vocabulario(cls.train)
        cls.x,cls.y,cls.m = tc.preparar(cls.train, cls.vocab)

    def test_regeneracion_exacta(self):
        with tempfile.TemporaryDirectory() as d:
            generador.generar(d)
            for p in (UNIDAD / "datos").glob("*.json"):
                self.assertEqual(p.read_bytes(), (Path(d)/p.name).read_bytes())

    def test_familias_separadas_y_variantes_juntas(self):
        prueba = tc.leer(UNIDAD / "datos/prueba.json")
        familias = [{r["familia"] for r in f} for f in (self.train,self.val,prueba)]
        self.assertEqual([len(s) for s in familias], [32,8,8])
        for a,b in ((0,1),(0,2),(1,2)):
            self.assertFalse(familias[a] & familias[b])
        for filas in (self.train,self.val,prueba):
            for familia in {r["familia"] for r in filas}:
                self.assertEqual({r["formato"] for r in filas if r["familia"]==familia}, {"breve","detallado"})

    def test_vocabulario_solo_train(self):
        self.assertEqual(len(self.vocab),26)
        self.assertEqual(tc.codificar("oceano",self.vocab),[tc.UNK])
        otra = deepcopy(self.val)
        otra[0]["continuacion"] = "nueva palabra ."
        self.assertNotIn("nueva", tc.vocabulario(self.train))
        self.assertEqual(tc.preparar(otra,self.vocab)[1].eq(tc.UNK).sum(),2)

    def test_tokenizacion_explicita(self):
        self.assertEqual(tc.tokens(" agua  norte . "),["agua","norte","."])
        self.assertEqual(tc.codificar("Agua",self.vocab),[tc.UNK])
        for texto in ("", "<eos>", "agua <pad>"):
            with self.assertRaises(ValueError):
                tc.tokens(texto)

    def test_shift_y_objetivos_sin_prefijo(self):
        for i,r in enumerate(self.train):
            pref = [tc.BOS]+tc.codificar(r["prefijo"],self.vocab)
            salida = tc.codificar(r["continuacion"],self.vocab)+[tc.EOS]
            self.assertEqual(self.x[i,:len(pref)].tolist(),pref)
            self.assertEqual(self.y[i][self.m[i]].tolist(),salida)
            self.assertEqual(int(self.m[i].sum()),5 if r["formato"]=="breve" else 9)
        self.assertEqual(int(self.m.sum()),448)

    def test_pad_y_eos_en_la_perdida(self):
        self.assertFalse(bool((self.m & self.y.eq(tc.PAD)).any()))
        self.assertEqual(int((self.m & self.y.eq(tc.EOS)).sum()),64)

    def test_secuencia_excesiva_rechazada(self):
        fila = deepcopy(self.train[0])
        fila["continuacion"] = "agua "*30
        with self.assertRaises(ValueError):
            tc.preparar([fila], self.vocab)

    def test_bigramas_referencia_de_conteos(self):
        m = tc.ajustar_bigramas(self.x,self.y,self.m,len(self.vocab))
        previo = self.vocab.index("salida")
        conteos = [.1]*len(self.vocab)
        for r in self.train:
            conteos[tc.codificar(r["continuacion"],self.vocab)[0]] += 1
        esperados = torch.tensor([x/sum(conteos) for x in conteos])
        torch.testing.assert_close(m.tabla[previo].exp(),esperados)

    def test_bigramas_contexto_nuevo_uniforme(self):
        m = tc.ajustar_bigramas(self.x,self.y,self.m,len(self.vocab))
        torch.testing.assert_close(m.tabla[tc.UNK].exp(),torch.full((26,),1/26))

    def test_ce_manual_y_perplejidad(self):
        logits = torch.tensor([[[math.log(1),math.log(2)]]],dtype=torch.float64)
        r = tc.metricas(logits,torch.tensor([[1]]),torch.tensor([[True]]))
        self.assertAlmostEqual(r["ce"],-math.log(2/3))
        self.assertAlmostEqual(r["perplejidad"],1.5)

    def test_perdida_ignora_no_objetivos_y_gradientes(self):
        logits = torch.randn(2,3,4,requires_grad=True)
        y = torch.tensor([[0,1,2],[1,2,0]])
        mascara = torch.tensor([[False,True,True],[False,True,False]])
        loss = tc.perdida(logits,y,mascara)
        manual = sum(-F.log_softmax(logits[i,j],-1)[y[i,j]] for i,j in ((0,1),(0,2),(1,1)))/3
        torch.testing.assert_close(loss,manual)
        loss.backward()
        self.assertEqual(float(logits.grad[~mascara].abs().max()),0)

    def test_desarrollo_no_abre_prueba(self):
        real = tc.entrenar
        def corto(vocab,train,val):
            return real(vocab,train,val,epocas=10)
        with tempfile.TemporaryDirectory() as d, patch.object(tc,"entrenar",side_effect=corto):
            generador.generar(d)
            (Path(d)/"prueba.json").unlink()
            _, informe = tc.desarrollar(d)
            self.assertIsNone(informe["prueba"])
            self.assertEqual(set(informe["fuentes"]), {"entrenamiento","validacion"})

    def test_seleccion_por_ce_y_empate(self):
        r={n:{"validacion":{"ce":1.}} for n in ("bigramas","transformer")}
        self.assertEqual(tc.seleccionar(r),"bigramas")
        r["transformer"]["validacion"]["ce"] = .5
        self.assertEqual(tc.seleccionar(r),"transformer")

    def test_copia_de_estado_y_entrenamiento_repetible(self):
        a,h = tc.entrenar(self.vocab,self.train,self.val,epocas=10)
        estado = tc.copiar_estado(a)
        b, hb = tc.entrenar(self.vocab,self.train,self.val,epocas=10)
        self.assertEqual(h,hb)
        for k,v in b.state_dict().items():
            torch.testing.assert_close(estado[k],v,atol=0,rtol=0)
        with torch.no_grad():
            next(a.parameters()).add_(1)
        self.assertFalse(torch.equal(estado["token.weight"], a.token.weight))


class GeneracionYEstado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ruta = UNIDAD / "recursos/generacion/modelo.json"
        cls.estado = json.loads(cls.ruta.read_text())
        cls.informe = json.loads((cls.ruta.parent/"informe.json").read_text())
        cls.modelo,cls.vocab = tc.cargar(cls.ruta)
        cls.val = tc.leer(UNIDAD / "datos/validacion.json")
        cls.prefijo = cls.val[0]["prefijo"]

    def test_temperatura_referencia_manual(self):
        z=torch.tensor([math.log(4),math.log(2),0.],dtype=torch.float64)
        torch.testing.assert_close(tc.probabilidades(z,1),torch.tensor([4/7,2/7,1/7],dtype=torch.float64))
        a=torch.tensor([2,math.sqrt(2),1],dtype=torch.float64)
        torch.testing.assert_close(tc.probabilidades(z,2),a/a.sum())

    def test_temperatura_invalida_y_estabilidad(self):
        for t in (0,-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError): tc.probabilidades(torch.ones(3),t)
        torch.testing.assert_close(tc.probabilidades(torch.tensor([1000.,999.]),.1),tc.probabilidades(torch.tensor([0.,-1.]),.1))

    def test_codicioso_no_depende_de_semilla_o_temperatura(self):
        a=tc.generar(self.modelo,self.vocab,self.prefijo,semilla=1,temperatura=.1)
        b=tc.generar(self.modelo,self.vocab,self.prefijo,semilla=99,temperatura=4)
        self.assertEqual((a["texto"],a["motivo"]),(b["texto"],b["motivo"]))

    def test_muestreo_repetible_y_rng_local(self):
        antes=torch.random.get_rng_state().clone()
        a=tc.generar(self.modelo,self.vocab,self.prefijo,metodo="muestreo",temperatura=2)
        b=tc.generar(self.modelo,self.vocab,self.prefijo,metodo="muestreo",temperatura=2)
        self.assertEqual(a,b)
        torch.testing.assert_close(antes,torch.random.get_rng_state())

    def test_eos_y_limite_son_distintos(self):
        m=Fijo(len(self.vocab),tc.EOS)
        a=tc.generar(m,self.vocab,self.prefijo)
        self.assertEqual(a["motivo"],"eos")
        self.assertEqual(a["tokens"],[])
        b=tc.generar(Fijo(len(self.vocab),self.vocab.index("agua")),self.vocab,self.prefijo,max_nuevos=2)
        self.assertEqual(b["motivo"],"max_nuevos")
        self.assertEqual(b["tokens"],["agua","agua"])

    def test_contexto_no_se_recorta(self):
        m=Fijo(len(self.vocab),self.vocab.index("agua"))
        r=tc.generar(m,self.vocab,"agua "*23,max_nuevos=3)
        self.assertEqual(r["motivo"],"contexto")
        self.assertEqual(len(r["tokens"]),1)
        with self.assertRaises(ValueError): tc.generar(m,self.vocab,"agua "*24)

    def test_especial_invalido_visible(self):
        for i in (tc.PAD,tc.BOS):
            r=tc.generar(Fijo(len(self.vocab),i),self.vocab,self.prefijo)
            self.assertEqual(r["motivo"],"especial_invalido")
            self.assertEqual(r["tokens"],[self.vocab[i]])

    def test_autorregresion_anexa_su_propio_token(self):
        m=Fijo(len(self.vocab),self.vocab.index("agua"))
        tc.generar(m,self.vocab,self.prefijo,max_nuevos=2)
        self.assertEqual(m.entradas[1][0,-1],self.vocab.index("agua"))
        self.assertEqual(m.entradas[1].shape[1],m.entradas[0].shape[1]+1)

    def test_generacion_no_cambia_pesos_ni_calcula_gradiente(self):
        antes=tc.copiar_estado(self.modelo)
        self.modelo.zero_grad(set_to_none=True)
        tc.generar(self.modelo,self.vocab,self.prefijo)
        for k,v in self.modelo.state_dict().items(): torch.testing.assert_close(antes[k],v,atol=0,rtol=0)
        self.assertTrue(all(p.grad is None for p in self.modelo.parameters()))
        self.assertFalse(self.modelo.training)

    def test_desconocido_no_se_inventa_en_vocabulario(self):
        r=tc.generar(self.modelo,self.vocab,"tema oceano zona norte nivel bajo formato breve salida")
        self.assertEqual(r["desconocidos_prefijo"],1)
        self.assertNotIn("oceano",self.vocab)
        self.assertNotEqual(r["texto"],"oceano norte bajo .")

    def test_recarga_logits_y_generaciones_originales(self):
        val=tc.evaluar(self.modelo,self.vocab,self.val)
        self.assertEqual(val,self.informe["candidatos"][self.estado["tipo"]]["validacion"])
        with torch.inference_mode():
            firma=tc.huella_logits(self.modelo(tc.preparar(self.val,self.vocab)[0]))
        self.assertEqual(firma,self.informe["logits_validacion_sha256"])
        self.assertEqual(tc.diagnosticar(self.modelo,self.vocab,self.val),self.informe["diagnosticos"])

    def test_exportar_y_recargar_bigramas(self):
        train=tc.leer(UNIDAD/"datos/entrenamiento.json")
        base=tc.ajustar_bigramas(*tc.preparar(train,self.vocab),len(self.vocab))
        estado=tc.empaquetar(base,"bigramas",self.vocab,{})
        nuevo,_=tc.restaurar(estado)
        torch.testing.assert_close(base.tabla,nuevo.tabla,atol=0,rtol=0)

    def test_rechaza_preparacion_vocabulario_y_pesos(self):
        for campo,valor in (("preparacion",{}),("vocabulario",self.vocab[::-1]),("estado",{}),("arquitectura",{})):
            estado=deepcopy(self.estado); estado[campo]=valor
            with self.assertRaises(ValueError): tc.restaurar(estado)
        estado=deepcopy(self.estado); estado["estado"]["salida.bias"][0]=float("nan")
        with self.assertRaises(ValueError): tc.restaurar(estado)

    def test_cierre_no_entrena_y_no_altera_estado(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/"modelo.json").write_bytes(self.ruta.read_bytes())
            (p/"prueba.json").write_bytes((UNIDAD/"datos/prueba.json").read_bytes())
            with patch.object(tc,"entrenar",side_effect=AssertionError("No entrenar")):
                r=tc.cerrar(p/"modelo.json",p)
            self.assertEqual((p/"modelo.json").read_bytes(),self.ruta.read_bytes())
            self.assertEqual(r["modelo_sha256"],tc.huella(self.ruta))

    def test_cierre_rechaza_familias_de_desarrollo(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"prueba.json"
            tc.guardar_json(p,self.val)
            with self.assertRaises(ValueError): tc.cerrar(self.ruta,d)

    def test_exactitud_completa_requiere_eos_y_toda_salida(self):
        m=Fijo(len(self.vocab),tc.EOS)
        r=tc.evaluar(m,self.vocab,self.val)
        self.assertEqual(r["n_exactas"],0)
        self.assertGreater(r["exactitud_token"],0)  # EOS sí es un objetivo en cada documento.

    def test_curva_y_estado_seleccionados_por_ce(self):
        h=self.informe["entrenamiento_transformer"]
        elegido=min(h["curva"],key=lambda r:r["ce_val"])
        self.assertEqual(elegido["epoca"],h["epoca_elegida"])
        self.assertEqual(elegido["ce_val"],self.informe["candidatos"]["transformer"]["validacion"]["ce"])

    def test_figuras_y_datos_representados(self):
        from figuras_transformer import generacion
        with tempfile.TemporaryDirectory() as d, patch("figuras_transformer.guardar") as guardar:
            generacion(self.informe,d)
            figura=guardar.call_args_list[0].args[0]
            esperado=[self.informe["candidatos"][n]["validacion"][k]
                      for n in ("bigramas","transformer") for k in ("exactitud_token","exactitud_secuencia")]
            np.testing.assert_allclose([b.get_height() for b in figura.axes[1].patches],esperado)
            import matplotlib.pyplot as plt
            for c in guardar.call_args_list: plt.close(c.args[0])
        for carpeta,nombre in (("atencion","atencion"),("generacion","aprendizaje"),("generacion","temperatura")):
            for ext in ("png","svg"):
                self.assertGreater((UNIDAD/"recursos"/carpeta/f"{nombre}.{ext}").stat().st_size,1000)


if __name__ == "__main__":
    unittest.main()

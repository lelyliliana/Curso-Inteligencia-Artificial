"""Pronóstico directo con historia reconstruida según disponibilidad."""
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import sklearn
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

UNIDAD = Path(__file__).resolve().parents[1]
ZONA = timezone(timedelta(hours=-5))
INICIO = datetime(2026, 8, 1, tzinfo=ZONA)
CAMPOS = ["id", "sensor", "instante", "disponible", "temperatura_c"]
COLUMNAS = ["actual", "anterior", "estacional24", "media24", "seno_hora_objetivo",
            "coseno_hora_objetivo", "fraccion_rellena24", "edad_h"]
PREPARACION = {"version": 1, "frecuencia_min": 60, "decision_min": 10,
               "ventana": 24, "edad_max_h": 3, "relleno": "adelante_segun_disponibilidad",
               "offset_horas": -5, "inicio_rejilla": INICIO.isoformat(),
               "sensor": "s1", "unidad": "grados_C"}
LIMITES = {"entrenamiento": (0, 576), "validacion": (576, 768), "prueba": (768, 960)}


def fecha(hora):
    return (INICIO + timedelta(hours=int(hora))).isoformat()


def minutos(texto):
    instante = datetime.fromisoformat(texto)
    if instante.tzinfo is None or instante.utcoffset() is None:
        raise ValueError("Las fechas necesitan zona horaria explícita.")
    segundos = (instante - INICIO).total_seconds()
    if segundos % 60:
        raise ValueError("Se requiere precisión de minutos enteros.")
    return int(segundos / 60)


def leer_archivo(ruta):
    vistos, registros, horas = {}, [], []
    duplicados = total = 0
    with Path(ruta).open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        if lector.fieldnames != CAMPOS:
            raise ValueError("Cabecera inesperada.")
        for fila in lector:
            total += 1
            if None in fila or any(fila.get(k) is None for k in CAMPOS) or not fila["id"]:
                raise ValueError("Fila incompleta.")
            if fila["sensor"] != "s1":
                raise ValueError("Este experimento requiere un único sensor: s1.")
            momento, llegada = minutos(fila["instante"]), minutos(fila["disponible"])
            if momento < 0 or momento % 60 or llegada < momento:
                raise ValueError("Medición fuera de rejilla o disponibilidad anterior al evento.")
            valor = None if fila["temperatura_c"] == "" else float(fila["temperatura_c"])
            if valor is not None and (not np.isfinite(valor) or not -20 <= valor <= 60):
                raise ValueError("Temperatura fuera del rango didáctico [-20, 60] o no finita.")
            r = {"id": fila["id"], "hora": momento // 60, "llegada_min": llegada, "valor": valor}
            horas.append(r["hora"])
            if r["id"] in vistos:
                if vistos[r["id"]] != r:
                    raise ValueError("ID repetido con contenido contradictorio.")
                duplicados += 1
            else:
                vistos[r["id"]] = r
                registros.append(r)
    if not registros:
        raise ValueError("Archivo sin registros.")
    return {"registros": sorted(registros, key=lambda r: (r["hora"], r["llegada_min"], r["id"])),
            "auditoria": {"filas": total, "duplicados_exactos": duplicados,
                           "entrada_desordenada": any(a > b for a, b in zip(horas, horas[1:]))}}


def agrupar(*archivos):
    grupos, ids = defaultdict(list), set()
    for archivo in archivos:
        for r in archivo["registros"]:
            if r["id"] in ids:
                raise ValueError("ID compartido entre archivos.")
            ids.add(r["id"])
            grupos[r["hora"]].append(r)
    return dict(grupos)


def observado(grupos, hora, corte_min=float("inf")):
    filas = grupos.get(hora, [])
    conocidas = [r for r in filas if r["llegada_min"] <= corte_min]
    if not conocidas:
        return None, "tardia" if filas else "ausente"
    valores = {r["valor"] for r in conocidas}
    if len(valores) != 1:
        return None, "conflicto"
    valor = conocidas[0]["valor"]
    return valor, "sin_valor" if valor is None else "observada"


def historia(grupos, origen):
    if not isinstance(origen, int) or origen < 0:
        raise ValueError("Origen debe ser una hora entera no negativa.")
    decision = origen * 60 + 10
    valores, relleno, motivos = [], [], []
    ultimo, ultima_hora = float("nan"), None
    for hora in range(origen + 1):
        valor, motivo = observado(grupos, hora, decision)
        if valor is not None:
            ultimo, ultima_hora = valor, hora
        valores.append(ultimo)
        relleno.append(valor is None)
        motivos.append(motivo)
    return np.array(valores), np.array(relleno), ultima_hora, motivos


def caracteristicas(grupos, origen, horizonte):
    if horizonte not in (1, 6):
        raise ValueError("Horizonte admitido: 1 o 6 horas.")
    if origen < 23:
        return None
    valores, relleno, ultima, _ = historia(grupos, origen)
    if ultima is None or origen - ultima > 3 or not np.isfinite(valores[-24:]).all():
        return None
    angulo = 2 * np.pi * ((origen + horizonte) % 24) / 24
    return np.array([valores[-1], valores[-2], valores[origen + horizonte - 24],
                     valores[-24:].mean(), np.sin(angulo), np.cos(angulo),
                     relleno[-24:].mean(), origen - ultima], dtype=float)


def validar_rango(archivo, nombre):
    inicio, fin = LIMITES[nombre]
    if any(not inicio <= r["hora"] < fin for r in archivo["registros"]):
        raise ValueError(f"Registros fuera de la partición {nombre}.")


def crear_conjunto(grupos, particion, horizonte):
    if horizonte not in (1, 6):
        raise ValueError("Horizonte admitido: 1 o 6 horas.")
    inicio, fin = LIMITES[particion]
    corte_etiquetas = fin * 60 + 10 if particion != "prueba" else float("inf")
    x, y, metadatos = [], [], []
    exclusiones = Counter()
    for origen in range(inicio, fin):
        objetivo = origen + horizonte
        if objetivo >= fin:
            exclusiones["objetivo_fuera_bloque"] += 1
            continue
        if origen < 23:
            exclusiones["historia_inicial"] += 1
            continue
        valor, motivo = observado(grupos, objetivo, corte_etiquetas)
        if valor is None:
            exclusiones[f"objetivo_{motivo}"] += 1
            continue
        entradas = caracteristicas(grupos, origen, horizonte)
        if entradas is None:
            exclusiones["historia_insuficiente_o_antigua"] += 1
            continue
        x.append(entradas.tolist())
        y.append(valor)
        metadatos.append({"origen_h": origen, "objetivo_h": objetivo,
                          "origen": fecha(origen), "objetivo": fecha(objetivo),
                          "decision": (INICIO + timedelta(hours=origen, minutes=10)).isoformat()})
    if not y:
        raise ValueError("No hay objetivos evaluables.")
    return {"x": x, "y": y, "metadatos": metadatos, "exclusiones": dict(exclusiones),
            "origenes_posibles": fin - inicio, "evaluables": len(y)}


def ajustar(conjunto, nombre, horizonte):
    if nombre not in ("persistencia", "estacional24", "ridge") or horizonte not in (1, 6):
        raise ValueError("Candidato u horizonte desconocido.")
    estado = {"formato": 1, "nombre": nombre, "horizonte": horizonte,
              "preparacion": dict(PREPARACION), "columnas": list(COLUMNAS)}
    if nombre == "ridge":
        x, y = np.asarray(conjunto["x"]), np.asarray(conjunto["y"])
        escala = StandardScaler().fit(x)
        z = escala.transform(x)
        modelo = Ridge(alpha=1.0, solver="svd").fit(z, y)
        estado.update(media=escala.mean_.tolist(), escala=escala.scale_.tolist(),
                      coeficientes=modelo.coef_.tolist(), intercepto=float(modelo.intercept_),
                      alpha=1.0, solver="svd")
        np.testing.assert_allclose(predecir(x, estado), modelo.predict(z), atol=1e-12, rtol=0)
    return estado


def validar_estado(estado):
    if (estado.get("formato") != 1 or estado.get("horizonte") not in (1, 6)
            or estado.get("preparacion") != PREPARACION or estado.get("columnas") != COLUMNAS
            or estado.get("nombre") not in ("persistencia", "estacional24", "ridge")):
        raise ValueError("Estado o preparación incompatible.")
    if estado["nombre"] == "ridge":
        for campo in ("media", "escala", "coeficientes"):
            a = np.asarray(estado[campo], dtype=float)
            if a.shape != (8,) or not np.isfinite(a).all():
                raise ValueError(f"Valores inválidos en {campo}.")
        if (np.asarray(estado["escala"]) <= 0).any() or not np.isfinite(estado["intercepto"]):
            raise ValueError("Escala o intercepto inválido.")


def predecir(x, estado):
    validar_estado(estado)
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[1] != 8 or not np.isfinite(x).all():
        raise ValueError("Se espera una matriz finita con ocho columnas.")
    if estado["nombre"] == "persistencia":
        return x[:, 0].copy()
    if estado["nombre"] == "estacional24":
        return x[:, 2].copy()
    return ((x - estado["media"]) / estado["escala"]) @ np.asarray(estado["coeficientes"]) + estado["intercepto"]


def pronosticar(grupos, origen, estado):
    validar_estado(estado)
    x = caracteristicas(grupos, origen, estado["horizonte"])
    return None if x is None else float(predecir([x], estado)[0])


def metricas(y, pred):
    y, pred = np.asarray(y, dtype=float), np.asarray(pred, dtype=float)
    if y.ndim != 1 or y.shape != pred.shape or not np.isfinite(y).all() or not np.isfinite(pred).all():
        raise ValueError("Vectores incompatibles o no finitos.")
    if len(y) == 0:
        return {"n": 0, "mae": None, "rmse": None, "sesgo": None}
    e = pred - y
    return {"n": len(y), "mae": float(np.abs(e).mean()), "rmse": float(np.sqrt(np.mean(e ** 2))),
            "sesgo": float(e.mean())}


def evaluar(conjunto, estado, cambio):
    pred = predecir(conjunto["x"], estado)
    y = np.asarray(conjunto["y"])
    horas = np.array([m["objetivo_h"] for m in conjunto["metadatos"]])
    transicion = (horas >= cambio) & (horas < cambio + 24)
    dias = {fecha(int(d * 24))[:10]: metricas(y[horas // 24 == d], pred[horas // 24 == d])
            for d in sorted(set(horas // 24))}
    return {"metricas": metricas(y, pred), "predicciones": pred.tolist(), "por_dia": dias,
            "transicion_24h": metricas(y[transicion], pred[transicion]),
            "resto": metricas(y[~transicion], pred[~transicion])}


def seleccionar(candidatos):
    elegido = next(iter(candidatos))
    for nombre, c in candidatos.items():
        if c["validacion"]["metricas"]["mae"] < candidatos[elegido]["validacion"]["metricas"]["mae"] - 1e-12:
            elegido = nombre
    return elegido


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def ejecutar_experimento(datos=UNIDAD / "datos", horizonte=1, evaluar_prueba=False):
    datos = Path(datos)
    archivos = {p: leer_archivo(datos / f"{p}.csv") for p in ("entrenamiento", "validacion")}
    for p, archivo in archivos.items():
        validar_rango(archivo, p)
    # El ajuste construye incluso su historia exclusivamente desde entrenamiento.
    grupos_train = agrupar(archivos["entrenamiento"])
    grupos_desarrollo = agrupar(*archivos.values())
    conjuntos = {"entrenamiento": crear_conjunto(grupos_train, "entrenamiento", horizonte),
                 "validacion": crear_conjunto(grupos_desarrollo, "validacion", horizonte)}
    candidatos = {}
    for nombre in ("persistencia", "estacional24", "ridge"):
        estado = ajustar(conjuntos["entrenamiento"], nombre, horizonte)
        candidatos[nombre] = {"estado": estado,
                              "entrenamiento": evaluar(conjuntos["entrenamiento"], estado, 672),
                              "validacion": evaluar(conjuntos["validacion"], estado, 672)}
    elegido = seleccionar(candidatos)
    informe = {"versiones": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__},
               "horizonte": horizonte, "fuentes": {p: huella(datos / f"{p}.csv") for p in archivos},
               "auditoria": {p: a["auditoria"] for p, a in archivos.items()}, "conjuntos": conjuntos,
               "candidatos": candidatos, "seleccionado": elegido, "prueba": None}
    origen = conjuntos["validacion"]["metadatos"][0]["origen_h"]
    consulta = {"origen_h": origen, "registros": [r for a in archivos.values() for r in a["registros"]
                if r["hora"] <= origen and r["llegada_min"] <= origen * 60 + 10]}
    consulta["prediccion"] = pronosticar(agrupar({"registros": consulta["registros"]}), origen, candidatos[elegido]["estado"])
    informe["consulta_recarga"] = consulta
    if evaluar_prueba:
        prueba = leer_archivo(datos / "prueba.csv")
        validar_rango(prueba, "prueba")
        grupos = agrupar(*archivos.values(), prueba)
        conjunto = crear_conjunto(grupos, "prueba", horizonte)
        informe["prueba"] = {"conjunto": conjunto, "evaluacion": evaluar(conjunto, candidatos[elegido]["estado"], 864)}
        informe["fuentes"]["prueba"] = huella(datos / "prueba.csv")
        informe["auditoria"]["prueba"] = prueba["auditoria"]
    return informe


def escribir_json(ruta, valor):
    Path(ruta).write_text(json.dumps(valor, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def cargar_modelo(ruta):
    try:
        estado = json.loads(Path(ruta).read_text(encoding="utf-8"))
        validar_estado(estado)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Modelo incompleto o mal formado.") from error
    return estado


def exportar(informe, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    elegido = informe["candidatos"][informe["seleccionado"]]
    escribir_json(salida / "informe.json", informe)
    escribir_json(salida / "modelo.json", elegido["estado"])
    recuperado = cargar_modelo(salida / "modelo.json")
    error = float(np.max(np.abs(predecir(informe["conjuntos"]["validacion"]["x"], recuperado) - elegido["validacion"]["predicciones"])))
    consulta = informe["consulta_recarga"]
    pred = pronosticar(agrupar({"registros": consulta["registros"]}), consulta["origen_h"], recuperado)
    error_consulta = abs(pred - consulta["prediccion"])
    if max(error, error_consulta) > 1e-12:
        raise RuntimeError("La recarga cambia las predicciones.")
    escribir_json(salida / "recarga.json", {"error_maximo": error, "error_consulta_cruda": error_consulta,
                                           "tolerancia": 1e-12, "modelo_sha256": huella(salida / "modelo.json")})
    conjuntos = {p: (informe["conjuntos"][p], elegido[p]) for p in ("entrenamiento", "validacion")}
    if informe["prueba"] is not None:
        conjuntos["prueba"] = (informe["prueba"]["conjunto"], informe["prueba"]["evaluacion"])
        escribir_json(salida / "cierre.json", {"horizonte": informe["horizonte"], "seleccionado": informe["seleccionado"],
                                              "metricas": informe["prueba"]["evaluacion"]["metricas"],
                                              "transicion_24h": informe["prueba"]["evaluacion"]["transicion_24h"],
                                              "exclusiones": informe["prueba"]["conjunto"]["exclusiones"],
                                              "fuentes": informe["fuentes"], "reajuste": False,
                                              "modelo_sha256": huella(salida / "modelo.json")})
    for p, (conjunto, resultado) in conjuntos.items():
        with (salida / f"predicciones_{p}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["origen", "decision", "objetivo", "real_c", "predicha_c", "error_c"], lineterminator="\n")
            w.writeheader()
            for m, y, pred in zip(conjunto["metadatos"], conjunto["y"], resultado["predicciones"]):
                w.writerow({k: m[k] for k in ("origen", "decision", "objetivo")} | {"real_c": y, "predicha_c": pred, "error_c": pred - y})
    return max(error, error_consulta)

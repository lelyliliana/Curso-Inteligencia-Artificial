"""Comprueba conteos, IDF suavizado y normalización con un corpus de tres textos."""
import argparse
from collections import Counter
from pathlib import Path
import numpy as np
from texto_curso import escribir_json, tokens, vectorizador

CORPUS = ["acceso aula aula", "acceso material", "material"]


def calcular_manual(documentos):
    if not documentos or not any(tokens(d) for d in documentos):
        raise ValueError("Se necesita al menos un token en el corpus.")
    vocab = sorted({t for d in documentos for t in tokens(d)})
    cuentas = [Counter(tokens(d)) for d in documentos]
    x = np.array([[c[t] for t in vocab] for c in cuentas], dtype=float)
    df = (x > 0).sum(axis=0)
    idf = np.log((1 + len(documentos)) / (1 + df)) + 1
    bruto = x * idf
    normas = np.linalg.norm(bruto, axis=1, keepdims=True)
    normalizado = np.divide(bruto, normas, out=np.zeros_like(bruto), where=normas != 0)
    return {"documentos": documentos, "vocabulario": vocab, "conteos": x.tolist(),
            "df": df.tolist(), "idf": idf.tolist(), "tfidf_bruto": bruto.tolist(), "tfidf": normalizado.tolist()}


def experimento():
    informe = calcular_manual(CORPUS)
    vec = vectorizador()
    x = vec.fit_transform(CORPUS).toarray()
    np.testing.assert_allclose(informe["tfidf"], x, atol=1e-12, rtol=0)
    informe["error_maximo"] = float(np.abs(x - informe["tfidf"]).max())
    informe["consulta"] = "aula galaxia"
    informe["consulta_tfidf"] = vec.transform([informe["consulta"]]).toarray()[0].tolist()
    informe["desconocida_tfidf"] = vec.transform(["galaxia"]).toarray()[0].tolist()
    return informe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--graficos", action="store_true")
    args = parser.parse_args()
    if args.graficos and args.salida is None:
        parser.error("--graficos requiere --salida.")
    informe = experimento()
    print("Vocabulario:", ", ".join(informe["vocabulario"]))
    print("Frecuencias documentales:", informe["df"])
    print("IDF:", ", ".join(f"{v:.6f}" for v in informe["idf"]))
    print("TF-IDF manual y biblioteca: error máximo < 1e-12")
    print("Consulta aula galaxia:", informe["consulta_tfidf"])
    print("Solo desconocidas:", informe["desconocida_tfidf"])
    if args.salida is not None:
        args.salida.mkdir(parents=True, exist_ok=False)
        escribir_json(args.salida / "informe.json", informe)
        if args.graficos:
            from figuras_texto import figura_representacion, guardar
            guardar(figura_representacion(informe), args.salida, "representacion")
        print("Exportación:", args.salida)


if __name__ == "__main__":
    main()

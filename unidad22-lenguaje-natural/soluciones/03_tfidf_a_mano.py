"""Reconstruye un vector sin ajustar un estimador."""
import math


def main():
    # Tres documentos; df(acceso)=2, df(aula)=1, df(material)=2.
    idf_acceso = math.log(4 / 3) + 1
    idf_aula = math.log(4 / 2) + 1
    bruto = [idf_acceso, 2 * idf_aula, 0.0]
    norma = math.sqrt(sum(v * v for v in bruto))
    vector = [v / norma for v in bruto]
    print("TF-IDF del primer documento:", ", ".join(f"{v:.6f}" for v in vector))
    assert math.isclose(sum(v * v for v in vector), 1, abs_tol=1e-12)
    print("Norma L2 comprobada: 1.000000")
    print("DF cuenta documentos con el término, no sus repeticiones.")


if __name__ == "__main__":
    main()

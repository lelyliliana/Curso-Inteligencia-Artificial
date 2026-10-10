"""Una ventana anterior conserva su valor cuando cambia el futuro."""


def main():
    serie = [10, 12, 14, 16]
    origen = 2
    media_causal = sum(serie[origen-2:origen+1]) / 3
    persistencia = serie[origen]
    estacional2 = serie[origen+1-2]
    print(f"Origen=2; objetivo=3; persistencia={persistencia}; estacional de periodo 2={estacional2}")
    assert media_causal == 12
    serie[3] = 100
    assert sum(serie[origen-2:origen+1]) / 3 == media_causal
    centrada = sum(serie[origen-1:origen+2]) / 3
    print(f"Futuro alterado: media causal={media_causal:.1f}; media centrada={centrada:.1f}")
    print("La media centrada usa el objetivo futuro; no sirve como entrada en este origen.")


if __name__ == "__main__":
    main()

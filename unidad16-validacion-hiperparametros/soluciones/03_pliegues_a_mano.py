"""CV manual, filtración por escala y cortes temporales con una separación."""

import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def cv_mediana():
    y = np.arange(0., 12., 2.)
    resultados = []
    for val in ((0, 1), (2, 3), (4, 5)):
        train = [i for i in range(6) if i not in val]
        mediana = float(np.median(y[train]))
        resultados.append({"ajuste": train, "validacion": list(val), "mediana": mediana,
                           "mae": float(np.abs(y[list(val)]-mediana).mean())})
    return resultados


def comparar_escala():
    x = np.array([[0., 0.], [2., 10.], [4., 0.]])
    y = np.array([0., 20., 40.])
    val = np.array([[2.3, 1.], [2., 1000.]])
    resultados = {}
    with threadpool_limits(limits=1):
        for nombre, datos_escala in (("correcta", x), ("filtrada", np.vstack((x, val)))):
            escala = StandardScaler().fit(datos_escala)
            modelo = KNeighborsRegressor(n_neighbors=1, algorithm="brute").fit(escala.transform(x), y)
            resultados[nombre] = {"media": escala.mean_.tolist(), "escala": escala.scale_.tolist(),
                                  "prediccion": float(modelo.predict(escala.transform(val[:1]))[0])}
    return resultados


def cortes_temporales():
    return [(train.tolist(), val.tolist()) for train, val in
            TimeSeriesSplit(n_splits=3, test_size=2, gap=1).split(np.arange(12))]


def main():
    resultados = cv_mediana()
    for i, r in enumerate(resultados, 1):
        print(f"Pliegue {i}: ajuste={r['ajuste']}; validación={r['validacion']}; mediana={r['mediana']:.1f}; MAE={r['mae']:.1f}")
    maes = [r["mae"] for r in resultados]
    print(f"Media MAE: {np.mean(maes):.3f}; desviación poblacional: {np.std(maes):.3f}")
    escala = comparar_escala()
    print(f"Consulta [2.3, 1]: escala correcta -> {escala['correcta']['prediccion']:.1f}; escala filtrada -> {escala['filtrada']['prediccion']:.1f}")
    for train, val in cortes_temporales():
        print(f"Tiempo: ajuste={train}; validación={val}; gap=1")
    print("El gap de una fila es didáctico: no acredita disponibilidad de etiquetas reales.")


if __name__ == "__main__":
    main()

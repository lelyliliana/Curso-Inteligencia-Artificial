"""Un caso, dos unidades ocultas, una actualización simultánea, sin NumPy."""
import math


def paso_manual(tasa=.1):
    # x=[1,-1], y=1; W1=[[.5,-.5],[.5,-.5]], b1=[0,0], W2=[1,-1], b2=0.
    # Ocultas iniciales: tanh(0)=0; logit=0; p=.5; delta_s=-.5.
    gradientes = {"W1": [[-.5, .5], [.5, -.5]], "b1": [-.5, .5], "W2": [0., 0.], "b2": [-.5]}
    nuevas = {"W1": [[.5+.5*tasa, -.5-.5*tasa], [.5-.5*tasa, -.5+.5*tasa]],
              "b1": [.5*tasa, -.5*tasa], "W2": [1., -1.], "b2": [.5*tasa]}
    logit = 2*math.tanh(1.5*tasa)+.5*tasa
    return {"gradientes": gradientes, "parametros_nuevos": nuevas,
            "bce_antes": math.log(2), "logit_despues": logit,
            "p_despues": 1/(1+math.exp(-logit)), "bce_despues": math.log1p(math.exp(-logit))}


if __name__ == "__main__":
    r = paso_manual()
    print("Gradientes:", r["gradientes"])
    print(f"BCE antes={r['bce_antes']:.6f}; después={r['bce_despues']:.6f}")
    print(f"Logit después={r['logit_despues']:.6f}; p(1)={r['p_despues']:.6f}")
    print("Todos los parámetros se actualizan con gradientes del mismo estado previo.")

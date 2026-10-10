# Recursos reproducibles — Unidad 20

[Unidad](../README.md) · [Ficha de modelo](ficha_modelo.md)

Generados y revisados el 10 de octubre de 2026 con el [entorno registrado](entorno-verificado.txt), Python 3.12.3 en Linux x86_64 y PyTorch 2.14.1+cpu. Las tres figuras se inspeccionaron visualmente. Los gráficos se construyen a partir de los informes; no leen prueba.

## Equivalencia

- [Informe con parámetros, gradientes y errores](equivalencia/informe.json).
- Gradientes: [PNG](equivalencia/gradientes.png) y [SVG](equivalencia/gradientes.svg).

Compara los 13 gradientes y un paso SGD con la referencia NumPy. No incluye ni necesita una medida de generalización.

## Entrenamiento por minilotes

- [Informe con configuración, fuentes, estados y recorrido](minilotes/informe.json).
- [Predicciones de entrenamiento](minilotes/predicciones_entrenamiento.csv) y [de validación](minilotes/predicciones_validacion.csv).
- [Comprobación de recarga](minilotes/recarga.json).
- Curvas: [PNG](minilotes/aprendizaje.png) y [SVG](minilotes/aprendizaje.svg).
- Frontera del estado elegido: [PNG](minilotes/frontera.png) y [SVG](minilotes/frontera.svg).

El informe publicado tiene `prueba=null` y ninguna huella de prueba. Las curvas describen estados evaluados cada diez épocas; no guardan cada paso. Los pesos iniciales, elegidos y finales aparecen como listas JSON. La frontera usa el estado elegido, la escala ajustada y los 80 casos de validación. Los símbolos corresponden a las etiquetas reales sintéticas.

## Regenerar

Desde la raíz y usando carpetas nuevas:

```bash
python unidad20-pytorch/ejemplos/01_comprobar_equivalencia.py --salida resultados/u20-equivalencia --graficos
python unidad20-pytorch/ejemplos/02_entrenar_minilotes.py --salida resultados/u20-minilotes --graficos
```

El segundo comando crea también `modelo.pt`. Ese binario se excluye del control de versiones según las reglas del repositorio; se publica el estado legible y los comandos para reproducirlo. `recarga.json` contiene la huella del binario local original y error máximo en logits=0,0. Al generar otro archivo, su huella puede cambiar sin que cambien las predicciones. No uses una diferencia de bytes como única prueba de diferencia funcional.

Las exportaciones rechazan carpetas existentes para conservar la evidencia anterior. Los estados permiten inferencia; no constituyen un punto de reanudación exacta de Adam. El [protocolo](../datos/protocolo.md) detalla la selección y las limitaciones.

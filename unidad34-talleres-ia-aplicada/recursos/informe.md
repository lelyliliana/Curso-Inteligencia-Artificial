# Informe de la entrega — Unidad 34

[Unidad](../README.md) · [Protocolo](../datos/protocolo.json) · [Operación](operacion.md)

Verificación realizada el 10 de octubre de 2026 con Python 3.12.3, NumPy 2.2.6, scikit-learn 1.9.1 y Matplotlib 3.10.8. Se reutilizó el entorno del curso en CPU, sin instalar paquetes ni descargar modelos. Los tres experimentos ejecutan algoritmos sobre datos propios ficticios; no son resultados simulados escritos a mano. Las preguntas y las etiquetas sí son construcciones didácticas, documentadas en la ficha de datos.

## Protocolo y estados

Se fijaron candidatos, costos, particiones y desempates antes de ejecutar. El ajuste usó entrenamiento en energía/ambiente y solo el corpus en documentos. Se eligió con validación y se guardaron los estados antes de abrir prueba. No se reajustó con validación ni se cambiaron candidatos al ver el cierre.

| Taller | Estado elegido | Validación | Cierre |
|---|---|---|---|
| Energía | Ridge, α=1 | MAE 1,1853179614 kW / 192 | MAE 3,5479234984 kW / 192 |
| Ambiente | Logística, umbral 0,3 | Costo 43 / 120 | Costo 76 / 120 |
| Documentos | TF-IDF, umbral 0,4 | 10/12 aceptadas, costo 4 | 8/12 aceptadas, costo 6 |

Las huellas SHA-256 completas están en los estados e informes enlazados. Son huellas del paquete (con datos, fuentes y versiones), no solo de coeficientes. El entorno puede influir en diferencias numéricas pequeñas; los resultados publicados corresponden al entorno declarado.

## Evidencia por taller

**Energía.** La persistencia obtuvo MAE 1,9953 kW en validación. El estado Ridge conserva escala y cuatro coeficientes aprendidos con 575 filas. Cierre contiene 192 decisiones progresivas; el MAE pasa de 1,1534 antes del cambio artificial a 4,9846 después. Sesgo total −3,1386 kW; 29 entradas marcadas fuera del rango de consumo de entrenamiento. No se excluyeron del cálculo. Esta marca no detecta todos los cambios de distribución.

Archivos: [modelo](energia/modelo.json), [validación con dos candidatos](energia/validacion.json), [cierre](energia/prueba.json), [demo](energia/demo.json), [figura PNG](energia.png) y [SVG](energia.svg).

**Ambiente.** Las políticas constantes obtuvieron costos 220 y 65; los umbrales 0,3/0,5/0,7 obtuvieron 43/71/106. Cierre: TP=53, FP=12, FN=16, TN=39, con 65 propuestas. Z11 reúne doce omisiones y costo 49 de 76. Se conservó el umbral 0,3. Los costos no representan una evaluación económica ni el acuerdo de una organización real.

Archivos: [modelo](ambiente/modelo.json), [validación con cinco candidatos](ambiente/validacion.json), [cierre](ambiente/prueba.json), [demo](ambiente/demo.json), [figura PNG](ambiente.png) y [SVG](ambiente.svg).

**Documentos.** La referencia obtuvo 9/12 aceptadas con costo 9. TF-IDF con umbral 0,4 redujo el costo de validación a 4, con siete fragmentos pertinentes, uno incorrecto, tres abstenciones correctas y una omisión. Cierre conserva cinco fragmentos pertinentes, uno incorrecto, tres abstenciones correctas y tres omisiones. Q-transporte-1 cita D05 fielmente y falla en pertinencia; Q-certificado-0 se abstiene con score 0,393, sin mover el umbral después. Familias completas: 4/6 en validación y 2/6 en cierre.

Archivos: [modelo e índice](documentos/modelo.json), [validación con cuatro candidatos](documentos/validacion.json), [cierre](documentos/prueba.json), [demo](documentos/demo.json), [figura PNG](documentos.png) y [SVG](documentos.svg).

## Verificación e interpretación

Las 43 pruebas comprueban regeneración de nueve archivos, separación de tiempos/zonas/familias, ecuaciones normales de Ridge, gradiente y equivalencia de la logística, TF-IDF frente a scikit-learn, métricas, citas, rechazos y recarga. Interceptan ajuste/selección durante cierre y lectura de prueba durante desarrollo. Se reconstruyeron los informes y se ejecutaron las tres demos; las figuras se revisaron visualmente.

La evidencia justifica una entrega didáctica reproducible. No basta para automatizar decisiones de un edificio, un equipo ambiental o una institución. El cierre no se presenta como una nueva competencia entre candidatos. No se midieron ahorro energético, impacto de visitas, aprendizaje, carga concurrente, latencia de servicio ni calibración en campo.

**Decisión de la entrega:** conservar los tres casos, incluidos sus fallos, y proponer una evaluación nueva y acotada en el proyecto final. Los cierres publicados pasan a ser evidencia conocida para cualquier mejora posterior.

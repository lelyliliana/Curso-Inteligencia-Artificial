# Defensa breve del proyecto de referencia

[Unidad](../README.md) · [Informe con evidencia](informe.md)

Guion escrito para una exposición de 5–7 minutos. Adapta los ejemplos a tu propio proyecto; no necesitas una presentación de diapositivas para demostrar el trabajo.

## 1. Problema — 45 segundos

«Una persona necesita revisar la potencia de la próxima hora. Entregamos una estimación y sus límites, sin controlar equipos. Usamos un edificio ficticio para estudiar el procedimiento, no para afirmar ahorro.»

## 2. Datos y momento de decisión — 60 segundos

Muestra una fila. Identifica medición, llegada, decisión y objetivo. Explica por qué quedan 55 minutos y por qué una lectura recibida después de decidir se rechaza. Presenta 720/240/240 decisiones y las cuatro incidencias por fase de evaluación.

## 3. Referencia e hipótesis — 60 segundos

Explica persistencia en una frase. Luego muestra la suma `potencia actual + incremento del calendario`. Los tres candidatos se fijaron antes de comparar; entrenamiento aprende, validación elige y cierre evalúa sin reajuste.

## 4. Resultado y fallo — 90 segundos

Muestra [la figura](proyecto.png): MAE de cierre 1,2341 frente a 2,2594 kW, sobre 236 casos; cobertura 236/240. Abre PF1140 y su error de 8,366 kW. Explica que usar la potencia actual ayuda después de observar el nuevo nivel, pero no permite prever el primer salto.

## 5. Demostración — 60 segundos

Ejecuta la consulta conocida, relaciona salida y evento por ID y prueba una entrada tardía. Muestra que un rechazo no trae predicción. Ejecuta `--referencia` y señala el cambio explícito de política a persistencia.

## 6. Decisión y siguiente evidencia — 45 segundos

«Cumple nuestro criterio didáctico previo. Para decidir un uso real faltan datos, tolerancias y prueba operativa acordados. Conservamos código, modelo, informes, entorno y errores para que otra persona pueda revisarlos.»

Preguntas para la defensa: ¿qué información conocías al seleccionar?, ¿sobre qué casos calculaste el MAE?, ¿qué hace el sistema con una lectura inválida?, ¿qué evidencia haría cambiar tu decisión?, ¿cómo vuelve otra persona a la versión anterior?

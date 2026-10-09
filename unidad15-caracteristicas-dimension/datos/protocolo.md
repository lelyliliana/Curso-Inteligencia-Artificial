# Protocolo `representaciones-v1`

[Unidad](../README.md) · [Diccionario](README.md)

## Contrato común

Predecir un objetivo posterior a partir de entradas declaradas disponibles antes de decidir. Cada laboratorio utiliza datos nuevos y particiones fijas de 96/48/48 casos. La disponibilidad es un supuesto didáctico, sin fechas para auditarlo. Identificador, objetivo y lectura posterior quedan excluidos de las matrices predictivas.

Las columnas permitidas están enumeradas en `ENTRADAS` de [representaciones.py](../ejemplos/representaciones.py). `matriz` rechaza una solicitud de campos fuera de esa lista. No se seleccionan columnas por tipo numérico ni se incorpora automáticamente todo el CSV.

## Decisiones fijadas

| Componente | Regla |
|---|---|
| Referencia | Mediana del objetivo de entrenamiento, `DummyRegressor(strategy="median")` |
| Regresión | `LinearRegression(fit_intercept=True)`, mínimos cuadrados, sin penalización |
| Escala | `StandardScaler`, media y desviación poblacional de entrenamiento para cada característica |
| Cadena | `Pipeline`: escala, PCA cuando corresponde, regresión |
| PCA | `svd_solver="full"`, `whiten=False`, una o dos componentes según candidato |
| Azar del ajuste | Ninguno: sin remuestreo ni inicialización aleatoria; SVD completa |
| Selección | Menor MAE de validación |
| Empate numérico | Candidatos cuyo MAE esté a no más de `1e-10` unidades del mínimo; elegir primero del orden publicado |
| Reajuste | No se incorpora validación ni prueba a escala, ejes o regresión |
| Cierre | Abrir prueba después de seleccionar y evaluar solo al elegido |

Orden de candidatos:

1. Interacción: `mediana`, `originales`, `interaccion`.
2. PCA: `mediana`, `completa`, `pca1`, `pca2`.

En interacción, las entradas son horas previstas y potencia prevista; `interaccion` agrega su producto antes de estandarizar. No se aprenden parámetros para esa fórmula. En PCA, ambas señales se estandarizan antes de aprender ejes. `pca2` conserva las dos dimensiones y sirve como control de rotación; no es compresión.

Cada candidato ajusta su cadena con el mismo entrenamiento. PCA ignora el objetivo al aprender sus ejes, mientras que la regresión posterior sí utiliza objetivos de entrenamiento. La selección usa objetivos de validación: no se presenta el procedimiento predictivo completo como no supervisado.

La tolerancia de empate atiende diferencias numéricas de representaciones equivalentes, no significación estadística. Se aplica respecto del mínimo global calculado, sin encadenar tolerancias entre pares de candidatos. La selección usa cifras completas, no valores redondeados de consola. No se buscan grados, umbrales de varianza, otras escalas ni penalizaciones después de ver prueba.

## Métricas y controles

Todos los candidatos informan número de casos, MAE, RMSE, sesgo medio `real−predicción` y R². MAE, RMSE y sesgo conservan la unidad del objetivo; R² no tiene unidad. R² es `null` cuando solo hay un caso o el objetivo es constante. No se recortan las predicciones ni se eliminan errores.

En PCA se registran varianzas y proporciones de entrenamiento. Las métricas de reconstrucción promedian el cuadrado de las diferencias sobre casos y columnas, tanto en señales estandarizadas como en las originales. La mediana no reconstruye y conserva `null`; `completa` representa la identidad en z; `pca1` descarta una dirección y `pca2` reconstruye hasta precisión numérica. Estos diagnósticos no participan en la selección por MAE.

La validación exige esquema exacto, valores finitos, dominios declarados e identificadores únicos. El ajuste exige cuatro casos como mínimo y rango suficiente para la regresión con intercepto. Esta restricción evita coeficientes no identificables en los candidatos completos; no es una afirmación general de que PCA no admita redundancia. No hay imputación ni correcciones implícitas.

La marca fuera de rango usa únicamente mínimos y máximos de las entradas originales de entrenamiento. No detecta toda falta de cobertura conjunta ni impide por sí misma producir una predicción.

## Secuencia de trabajo

1. Leer entrenamiento y validación; validar datos y separación por identificadores.
2. Construir características deterministas con entradas permitidas; ajustar cadenas solo con entrenamiento.
3. Evaluar los candidatos sobre los mismos casos de desarrollo y elegir por MAE con el desempate declarado.
4. Conservar exportación previa, commit, versiones, comando, huellas y candidato elegido. Declarar qué respuestas públicas se conocían.
5. Cerrar con `--evaluar-prueba`. La ejecución repite ajuste y selección; abre prueba después y no vuelve a elegir.
6. Comparar código, entorno, protocolo, huellas de desarrollo, parámetros, resultados y selección con la exportación previa. Si cambian, investigar antes de presentar un cierre del mismo experimento.
7. Informar el resultado final sin reajustar. Si se plantean cambios a partir de prueba, reconocer que influyó en desarrollo y preparar otra evaluación apropiada.

La ejecución común no necesita `prueba.csv`. Las pruebas de invariancia cambian objetivos de prueba, entradas de validación y lecturas posteriores, y verifican qué componentes deben permanecer iguales. No impiden que una persona consulte los archivos públicos.

## Exportación

El JSON conserva fuentes, versiones, rangos, columnas excluidas, parámetros de escala, coeficientes, ejes PCA, varianzas, métricas y coordenadas/reconstrucciones por caso. Los coeficientes operan sobre z o sobre coordenadas PCA, no directamente sobre entradas originales. `completa` registra coordenadas estandarizadas, sin llamarlas componentes PCA.

Los CSV de desarrollo incluyen todos los candidatos; prueba incluye solo al elegido. Los gráficos utilizan exclusivamente desarrollo. Medias, escalas y ejes no son una serialización completa de objetos estimadores: conserva código, datos y versiones para repetir el ajuste. La exportación puede quedar parcial si falla una escritura o el dibujo.

Los resultados son demostraciones sintéticas, públicas y construidas para contrastar representaciones. No demuestran disponibilidad real, generalización por tiempo o equipo, causalidad ni que una representación sea universalmente mejor.

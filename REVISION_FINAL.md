# Revisión final del curso

[Índice](README.md) · [Continuidad](CONTINUIDAD.md) · [Proyecto final](unidad35-proyecto-final/README.md)

Revisión de cierre realizada el 10 de octubre de 2026. La ruta original de 36 unidades, numeradas del 0 al 35, tiene material desarrollado, ejemplos, ejercicios, soluciones y retos. El cierre se refiere a la elaboración del material, no a una certificación del aprendizaje del estudiante ni a eficacia de los sistemas en entornos reales.

## 1. Progresión y coherencia

Se revisaron los objetivos, la secuencia, los enlaces entre unidades, las dependencias declaradas, los criterios de entrega y la relación entre los talleres y el proyecto. Las verificaciones y revisiones de cada entrega se conservan en [CONTINUIDAD.md](CONTINUIDAD.md). Esta revisión transversal no afirma una nueva auditoría exhaustiva de cada párrafo, fórmula y referencia externa de todo el curso.

| Tramo | Construye sobre | Evidencia y transición revisadas |
|---|---|---|
| 0–4 | Python básico y entorno | Problema, datos, matemática y probabilidad antes de ajustar modelos |
| 5–9 | Estados, reglas y datos | Referencias explícitas, procedencia, calidad y exploración |
| 10–18 | Preparación y objetivos | Separación, modelos, métricas, costos, grupos e interpretación |
| 19–24 | Álgebra y evaluación | Redes, PyTorch, visión, lenguaje, tiempo, recomendación y refuerzo |
| 25–31 | Redes y lenguaje | Generación, inferencia, evaluación, búsqueda, RAG, herramientas, adaptación y multimodalidad |
| 32–33 | Contratos y modelos guardados | Aplicación, límites, observación, fallos y recuperación local |
| 34–35 | Componentes anteriores | Talleres, proyecto completo, demostración, informes y defensa con rúbrica |

La ruta permite soluciones con reglas o referencias sencillas. No exige usar un LLM o todas las técnicas en un proyecto. Las unidades separan datos sintéticos, capturas de inferencia real y fallos simulados, y conservan resultados desfavorables. Los cierres públicos se identifican como evidencia conocida para futuras modificaciones.

## 2. Navegación y estructura

El [auditor de estructura](herramientas/auditar_estructura.py) comprueba las 36 carpetas, su enlace desde el índice, navegación anterior/siguiente donde corresponde, vuelta al índice, ejemplos numerados y referencias a ejercicios/reto. Comprueba los fragmentos locales Markdown utilizados y la consistencia de versiones directas al recorrer los archivos de requisitos.

El [informe estructural](unidad35-proyecto-final/recursos/auditoria-estructura.json) conserva el inventario. La Unidad 35 cierra la navegación sin anunciar una unidad 36. El [verificador común](herramientas/verificar_curso.py) comprueba además sintaxis y destinos de enlaces locales en todo el alcance, incluida esta revisión.

## 3. Reproducción desde un entorno limpio

Se creó un entorno virtual nuevo de Python 3.12.3 en Linux x86_64, sin `--system-site-packages`, y se instalaron desde los índices declarados los requisitos compartidos y PyTorch CPU. No se copiaron paquetes del entorno utilizado durante las entregas anteriores. `pip check` no encontró conflictos. El [registro de versiones](unidad35-proyecto-final/recursos/entorno.json) y la [resolución completa](unidad35-proyecto-final/recursos/entorno-verificado.txt) documentan el entorno probado.

Un entorno virtual separa los paquetes de un proyecto; se recrea a partir de requisitos, no se distribuye copiando su carpeta. [Documentación de venv](https://docs.python.org/3.12/library/venv.html)

Ruta de reproducción en Linux/macOS desde la raíz, con Python 3.12 instalado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r unidad21-vision-computador/requirements.txt
python -m pip install -r unidad21-vision-computador/requirements-cpu.txt
python -m pip check
python herramientas/auditar_estructura.py
python herramientas/verificar_curso.py
```

La comprobación realizada corresponde a Linux x86_64; no se ejecutó en Windows o macOS. Para activación en otros sistemas consulta la [Unidad 0](unidad00-entorno/README.md); para disponibilidad de PyTorch CPU, la [Unidad 20](unidad20-pytorch/README.md). La instalación necesita Internet y espacio para dependencias. Las comprobaciones posteriores usan archivos locales; las unidades 32–33 necesitan permitir conexiones a `127.0.0.1`.

## 4. Resultado de las comprobaciones

- 36 unidades con navegación completa y dos fragmentos locales Markdown verificados.
- 282 ejecuciones de ejemplos y variantes, incluidas exportaciones, recargas y cierres en carpetas temporales.
- 1060 pruebas automatizadas de las unidades 5–35.
- Proyecto final ejecutado en el mismo entorno limpio, con 37 pruebas, figura revisada y evidencia de contrato, errores, recarga y reversión.

Los comandos de inferencia en vivo de las unidades 26–30 no se vuelven a ejecutar en la verificación común: se analizan sus capturas guardadas y escenarios identificados. No se solicitan claves ni se inician servicios externos. La revisión del navegador de la Unidad 32 fue parte de su entrega; el cierre actual verifica su código y HTTP local, no repite una nueva auditoría visual de esa interfaz.

## 5. Alcance y mantenimiento

La revisión comprueba estructura, progresión y reproducción del material publicado. No verifica de nuevo todas las URLs externas, no certifica compatibilidad de futuras versiones y no sustituye una revisión docente de las soluciones de cada estudiante. Los programas correctos en datos ficticios no acreditan ahorro, impacto ambiental, aprendizaje o seguridad de una implantación real.

No quedan unidades pendientes del programa original. Las ampliaciones futuras deben conservar el historial de resultados, declarar nuevos datos y decisiones, y actualizar la verificación. Si cambia una dependencia, separa esa actualización de una mejora de modelo y comprueba el alcance afectado antes de publicar otra versión.

Para uso docente, sigue los retos de cada bloque, los [talleres](unidad34-talleres-ia-aplicada/README.md) y la [rúbrica final](unidad35-proyecto-final/reto.md). Una persona revisora debe poder localizar datos, reproducir una salida y explicar un fallo antes de dar por completado un proyecto.

## 6. Mantenimiento del 11 de octubre de 2026

Una revisión adicional en Python 3.12.14, Linux x86_64, con las mismas dependencias declaradas, ejecutó los 282 ejemplos y variantes, pero encontró 18 fallos entre las 1060 pruebas. Diecisiete fallos correspondían a comparaciones exactas de números recalculados, metadatos de Python o huellas derivadas de esos resultados; uno correspondía a una carrera entre recibir HTTP y terminar el registro. Este hallazgo amplía la comprobación original en Python 3.12.3, sin reemplazar su historial.

Se corrigieron las comprobaciones de las unidades 14, 15, 16, 18, 19, 22, 25, 31, 32, 34 y 35:

- La [comparación común](herramientas/comparaciones.py) conserva tipos, campos, orden, conteos, booleanos, clases y decisiones exactos. Para float64 usa `rtol=1e-10` y `atol=1e-12`; las salidas float32 de PyTorch usan explícitamente `rtol=1e-6` y `atol=1e-7`.
- La excepción de U16 permite `atol=1e-5` solamente en MAE, RMSE y sesgo de entrenamiento de KNN ponderado por distancia, cuyos errores son casi cero al consultarse sobre el propio entrenamiento. Las métricas de validación y las predicciones fuera de pliegue mantienen la tolerancia común.
- U22 comprueba el error de recarga contra el mismo límite `1e-12` ya exigido por su exportador.
- U25 compara logits bit a bit entre dos recargas en el entorno actual y conserva la comprobación de las generaciones publicadas. La huella histórica de logits queda documentada como evidencia de su entorno, sin exigir que otra máquina calcule los mismos bytes.
- U34 y U35 verifican la integridad de los modelos originales y nuevos por separado, así como la relación entre cada informe y la huella de su propio modelo. Comparan el contenido numérico reproducido sin exigir que coincidan los metadatos de Python de dos ejecuciones distintas. Siguen comprobando fuentes, dependencias fijadas, protocolo, selección y ausencia de reajuste durante cierre.
- La prueba HTTP de U32 utiliza un servidor aislado y espera un evento de registro completo antes de leerlo. Pasó 25 repeticiones consecutivas; conserva la comprobación de que no se registra la entrada privada.

Las [ocho pruebas de la comparación común](herramientas/pruebas/test_comparaciones.py) comprueban que las tolerancias no oculten cambios de contrato, decisiones, probabilidades u orden, y rechazan números no finitos y tolerancias inválidas. Se incorporan al verificador general.

También se corrigieron los delimitadores matemáticos de las unidades 30, 31 y 33 para su presentación en GitHub, y el enlace de licencia de BGE-M3 en la [ficha de U28](unidad28-embeddings-busqueda/recursos/ficha_recuperacion.md). El verificador detecta delimitadores matemáticos no compatibles fuera de ejemplos de código. Se conserva el código de los modelos, los datos y las capturas originales.

Resultado de esta actualización: **282 ejecuciones correctas y 1068 pruebas correctas** (1060 de las unidades y ocho de herramientas comunes), sin conflictos en `pip check`. El [registro de verificación](herramientas/recursos/verificacion-2026-10-11.txt) conserva la ejecución completa y las comprobaciones editoriales posteriores. La prueba HTTP adicional pasó 25/25 repeticiones. El alcance sigue siendo Linux x86_64 y las capturas locales incluidas; no se ejecutaron nuevas inferencias de Ollama ni llamadas a APIs externas.

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

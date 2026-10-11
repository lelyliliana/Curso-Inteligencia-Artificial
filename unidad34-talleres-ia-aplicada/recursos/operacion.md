# Operación local y traspaso de los talleres

[Unidad](../README.md) · [Informe](informe.md) · [Unidad 33](../../unidad33-operacion-seguridad-observabilidad/README.md)

## Qué se puede ejecutar

Cada taller ofrece una CLI de desarrollo, otra modalidad de cierre y una demo de inferencia. La demo carga un JSON local del taller solicitado, verifica la huella del paquete y las fuentes de desarrollo actuales, valida la consulta y devuelve JSON. No vuelve a entrenar ni llama a servicios. El modelo se carga una vez por invocación; no existe un proceso residente compartido.

Usa solo estados propios de esta entrega. Las huellas conservan trazabilidad de la versión publicada; no son firmas de un proveedor ni convierten cualquier JSON descargado en un modelo confiable. El contrato de consulta tiene límites y las entradas de la demo se leen hasta 16 KiB. Los estados de modelo y los datasets del repositorio se consideran archivos locales de confianza.

## Prueba de inicio conocida

Ejecuta las tres consultas predeterminadas:

| Taller | Resultado publicado de la demo | Qué comprueba |
|---|---|---|
| Energía | 43,313094897 kW, `estimacion` | Carga, preparación e inferencia |
| Ambiente | Proponer 1; puntuación 0,655535460 | Pesos y umbral guardados |
| Documentos | D01, versión 1, intervalo [0,108) | Índice y cita exacta |

Son casos conocidos sin etiqueta de evaluación nueva. Pasarlos no demuestra calidad predictiva, preparación para producción o rendimiento en casos distintos. Conserva el SHA del modelo que aparece en cada salida.

## Responder a errores

| Situación | Comportamiento / acción |
|---|---|
| Campo ausente, adicional o de tipo incorrecto | Rechazo; corregir la entrada sin completar silenciosamente |
| Valor no finito o fuera del contrato | Rechazo; revisar unidad y origen del dato |
| Valor permitido fuera del rango de entrenamiento | Sale una marca; la persona evalúa su uso |
| Pregunta sin términos conocidos o por debajo del umbral | `sin_evidencia`; no inventar un procedimiento |
| Fragmento con cita pero irrelevante | Registrar el caso en una revisión de calidad; la validación estructural no lo detecta |
| Huella distinta o fuentes modificadas | Se rechaza la carga; recuperar la versión correspondiente o crear otra versión documentada |

La CLI termina con código 2 ante errores esperados de entrada, archivos o versión. No expone una API, no acepta solicitudes de Internet y no guarda un historial automático de preguntas. `--salida` escribe la respuesta bajo pedido; en documentos puede incluir el párrafo público de este corpus ficticio. Un proyecto con información privada debe definir qué conservar antes de añadir registros.

## Cambiar y volver atrás

1. Conserva el commit, el protocolo, los datos y los estados originales en una carpeta/versionado separado.
2. Declara la modificación y su criterio antes de ajustar. Usa una carpeta de salida nueva.
3. Repite validación, recarga, contratos y casos conocidos. Reserva un cierre nuevo si el anterior ya orientó decisiones.
4. Compara evidencia y documenta una decisión humana. No sobrescribas los resultados anteriores para ocultar regresiones.
5. Para volver atrás, recupera **el conjunto correspondiente de código, datos y estado**. La carga comprueba fuentes: copiar solo un modelo viejo sobre código nuevo puede ser rechazado correctamente.

Si el proyecto final añade una API o interfaz, debe reutilizar explícitamente los conceptos de las unidades 32–33: límites de cuerpo, respuesta clara a fallos, correlación, población de métricas y reversión. Esta entrega no incorpora esos controles HTTP ni los da por aprobados por usar un modelo que pasó pruebas unitarias.

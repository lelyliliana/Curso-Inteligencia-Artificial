# Ficha de límites — Redes pequeñas de la Unidad 19

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md)

**Versión:** u19-v1-bce-validacion. **Revisión:** 9 de octubre de 2026. **Estado:** demostración didáctica, sin aplicación operativa. Quien entrega la práctica debe poder reproducir los resultados y explicar sus límites; no se ha designado un responsable de operación porque no se despliega un servicio real.

## Propósito y alcance

Aprender propagación hacia delante, gradientes, selección de época y generalización. Dos señales adimensionales se transforman en p(1) y una clase mediante umbral 0,5. Las salidas se imprimen y guardan; no activan dispositivos ni se comunican a terceros.

Los datos son totalmente sintéticos y no contienen información personal. No constituyen evidencia sobre una población, sensor, proceso educativo o dispositivo real. Usos excluidos de esta evidencia: decisiones sobre personas, alertas de seguridad, control automático y afirmaciones de causalidad o de calibración.

## Modelos elegidos y evidencia

| Laboratorio | Estado elegido | BCE validación | Cierre conocido | Límite relevante |
|---|---|---:|---|---|
| XOR | Red tanh de 8 unidades, época 3000 | ≈0,0063 | 96/96 clases correctas; BCE≈0,0061 | Distribución sencilla con regiones sin ejemplos |
| Ruido | Red tanh de 32 unidades, L2=0,02, época 6000 | ≈0,5492 | 126/160 correctas; 17 FN y 17 FP; BCE≈0,5350 | Pocos datos, etiquetas invertidas y errores persistentes |

Validación eligió arquitectura y época. La cifra de validación no es un cierre independiente de esas elecciones. El cierre solo evalúa el estado elegido sin reajuste; ya es público, así que futuras modificaciones no deben presentarlo como evidencia nueva.

La red32 sin L2 alcanza mejor BCE de validación en la época 500. Continuar hasta 6000 reduce su BCE de entrenamiento a≈0,1152, pero eleva validación a≈1,1615. La selección de estado y la penalización son controles presentes en el experimento; no garantizan generalización fuera de la distribución.

## Verificación y explicaciones

La implementación se contrasta con un paso manual, una propagación escalar y diferencias finitas de todos los parámetros de un caso pequeño, con y sin L2. Se comprueban logits extremos y que validar no altere las actualizaciones aprendidas de entrenamiento.

Estas verificaciones detectan errores de cálculo y de separación en los casos cubiertos. No demuestran utilidad real ni la ausencia de todos los defectos. Las activaciones ocultas son representaciones aprendidas, no categorías explicativas validadas. Una imagen de la frontera muestra la función del modelo en una malla; no explica la causa del objetivo.

## Limitaciones y respuesta propuesta

| Situación | Evidencia o riesgo | Acción proporcionada |
|---|---|---|
| Muestra o escala distinta | Las entradas se estandarizan con un conjunto específico | Verificar esquema, procedencia y distribución antes de cualquier adaptación |
| Región XOR sin ejemplos | Se colorea la malla incluso en franjas nunca observadas | Declarar falta de soporte; recoger y evaluar casos pertinentes si importan al uso |
| Pérdida baja en entrenamiento | Puede coexistir con sobreajuste fuerte | Revisar curvas y conservar el punto elegido por el protocolo |
| Cambio de semilla o presupuesto | Una sola ejecución no mide variabilidad | Registrar la comparación completa en desarrollo y reservar evaluación independiente |
| Error predictivo | Una probabilidad o frontera no justifican una acción real | Mantener uso didáctico; definir consecuencias, referencia y supervisión antes de una propuesta operativa |

Si una ejecución no reproduce la referencia, conservar comando, versiones, huellas, configuración y error; revisar primero datos y pruebas de gradiente. No modificar silenciosamente los recursos para hacer coincidir una conclusión deseada.

**Decisión actual:** material apto para estudiar el procedimiento. Antes de otra clase de uso hacen falta datos pertinentes, una línea base operacional, métricas ligadas a consecuencias, responsables con capacidad de corregir o detener el sistema y nueva evaluación. Esos controles operativos son requisitos de una futura propuesta; no están implementados por este laboratorio.

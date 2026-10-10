# Diez ejercicios

[Volver a la unidad](README.md) · [Soluciones](soluciones/ejercicios-resueltos.md)

1. **Seguir una llamada.** Escribe las seis etapas desde una propuesta de `consultar_sensor` hasta un resultado. Indica cuáles dependen del modelo y cuáles del programa.
2. **Calcular a mano.** Obtén la media de S-11 y S-23, y especifica las dos propuestas necesarias para cada sensor. ¿Por qué el cálculo recibe un ID en lugar de nuevas lecturas del modelo?
3. **Validación y autorización.** Clasifica `{"sensor":"../secreto"}`, `{"sensor":"S-14"}` y `{"sensor":"S-90"}`. Explica qué resultado recibiría cada una sin revelar lecturas restringidas.
4. **Evidencia.** Una respuesta dice `{"estado":"ok","sensor":"S-11","media_c":20}` pero la traza está vacía. Decide forma, coincidencia, apoyo y aceptación. Repite con una lectura exitosa pero sin cálculo.
5. **Presupuesto.** El modelo propone cuatro herramientas distintas desconocidas, una por turno. Cuenta respuestas del modelo, errores y ejecuciones exitosas. ¿Por qué no se solicita un quinto turno?
6. **MCP.** Busca los mensajes de ID 3, 5 y 7 en la captura. Explica la diferencia entre `result.isError` y `error.code`. ¿Por qué `notifications/initialized` no tiene respuesta?
7. **Versiones.** Compara la revisión fijada de 2025 con la revisión vigente indicada en las fuentes. ¿Qué afirmación sería incorrecta si una documentación dijera que todas las versiones necesitan `initialize`?
8. **Inyección.** Revisa A04a. Identifica la instrucción hostil, el paso omitido, el valor correcto y por qué JSON válido no basta. Distingue el fallo medido de la auditoría artificial que propone escribir.
9. **Evaluación por familias.** Calcula la tasa de éxito y la de familias completas del agente en desarrollo. Explica por qué las dos paráfrasis fallidas no son dos observaciones independientes.
10. **Diseño de una ampliación.** Propón un permiso de lectura por proyecto y un presupuesto adicional de tokens. Indica dónde se comprobarían, qué quedaría en la traza y cómo evaluarías el cambio sin reutilizar el cierre ya visto.

Comprueba tus respuestas con los programas y los archivos de datos. En los ejercicios de diseño se evalúa la relación entre requisito, control ejecutable y evidencia, no el uso de una biblioteca particular.

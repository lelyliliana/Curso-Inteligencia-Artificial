# Diez ejercicios

[Unidad](README.md) · [Soluciones](soluciones/README.md)

1. **Caso de uso.** Escribe tres criterios de aceptación para Consulta de luces y una capacidad que no ofrece. Distingue un criterio de interfaz de una métrica predictiva.
2. **Responsabilidades.** Asigna a interfaz, servidor, contrato o servicio: leer el PNG del formulario, rechazar claves extra, cargar pesos, devolver HTTP 422 y mostrar el lado consultado. Explica por qué no conviene entrenar en el manejador HTTP.
3. **Compatibilidad.** Un PNG RGB parece idéntico al PNG L original. ¿Por qué se rechaza? Propón un proceso comprobable si quisieras admitir RGB sin cambiar silenciosamente el comportamiento.
4. **Carga y disponibilidad.** Diferencia «el puerto responde», «el modelo se cargó» y «el modelo generaliza». ¿Qué garantiza `/health` aquí? Diseña el comportamiento de inicio si falta el estado.
5. **Contrato.** Redacta una solicitud válida y el esquema de respuesta de éxito. ¿Qué estado usarías para JSON roto, gramática no admitida y fallo inesperado del modelo? Explica por qué ninguno debe devolver `apagada` como valor de respaldo.
6. **Tamaño.** Calcula los caracteres base64 para 16.384 bytes y explica por qué esa cifra no es Content-Length. ¿Qué cambia al serializar «lámpara» con `ensure_ascii=False`?
7. **Interfaz y espera.** Describe la secuencia cargar–esperar–responder–corregir. ¿Qué problema aparece si queda visible una predicción después de cambiar la imagen? ¿Un `fetch` que recibe 422 entra necesariamente en `catch`?
8. **Pruebas.** Clasifica como unidad, integración o recorrido de interfaz: validar base64, verificar HTTP 413, confirmar que el botón vuelve a habilitarse y comparar pesos antes/después de varias consultas. Justifica que una prueba no reemplaza a las demás.
9. **Interpretar la evidencia.** El informe dice 24/24. ¿Es exactitud predictiva sobre 24 imágenes independientes? Identifica el número de predicciones, escenas y casos de error. Propón una evaluación nueva de calidad de modelo separada de la integración.
10. **De local a operación.** Define qué registrarías para investigar fallos sin almacenar consultas o imágenes. Enumera tres requisitos adicionales para un servicio público. Explica qué problema resuelve un hash y cuál no resuelve.

Usa artefactos, cálculos y decisiones explícitas. En los ejercicios con cambios propuestos no hace falta desplegar un servicio externo ni crear cuentas.

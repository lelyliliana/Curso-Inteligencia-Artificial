# Evidencia de la Unidad 29

[Unidad](../README.md) · [Ficha del experimento](ficha_rag.md)

| Material | Origen y propósito |
|---|---|
| [Preparación](preparacion/fragmentos.json) y [presupuesto](preparacion/presupuesto.json) | Texto original extraído; ranking artificial para estudiar espacio disponible |
| [Registro de desarrollo](desarrollo/registro.json) | 34 embeddings y veinte generaciones reales, con dos calentamientos separados |
| [Índice](desarrollo/indice.json) y [selección](desarrollo/seleccion.json) | 24 vectores normalizados, procedencia y elección k=3 congelada |
| [Informe de desarrollo](desarrollo/informe.json) | Reconstrucción de recuperación, contexto, respuesta y evaluación |
| [Registro de cierre](cierre/registro.json) e [informe](cierre/informe.json) | Diez embeddings y diez generaciones nuevas con la elección congelada |
| [Auditoría](auditoria/auditoria.json) | Doce salidas artificiales para comprobar capas de validación, no inferencia |

Los registros reales conservan solicitudes, respuestas, vectores, contextos enviados, rankings, tiempos, inventarios y huellas. El texto dentro de un documento o una salida guardada es evidencia para leer, no una instrucción para ejecutar. Ningún registro contiene claves de API ni datos personales.

Los JSON legibles ocupan más espacio que un formato binario, pero permiten revisar cada paso. No se publican los pesos de los modelos. PNG/SVG se generaron a partir de los informes y se inspeccionaron visualmente. El reanálisis predeterminado no necesita servicios locales ni red.

Las huellas de objetos se calculan con JSON canónico; las de archivos, con sus bytes. No son intercambiables. Repetir inferencia puede variar entre versiones o equipos; recargar los mismos artefactos conserva el análisis en el entorno probado. No sobrescribir capturas para ocultar fallos.

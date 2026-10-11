# Ficha — Servicio local con observación

[Unidad](../README.md)

| Campo | Descripción |
|---|---|
| Uso | Enseñar admisión, estados operativos, correlación y recuperación |
| Base | Aplicación y contrato de U32; modelo y preparación de U31, sin cambios |
| Modelo | Fusión de cuatro características, ocho unidades tanh y dos clases; 58 parámetros |
| Red | HTTP en 127.0.0.1; puerto CLI predeterminado 8766 |
| Conexiones | Cuatro manejadas simultáneamente; exceso rechazado antes de leer HTTP |
| Inferencia | Un cupo para la solicitud de predicción, sin cola de aplicación |
| Tiempos | Socket: 1 s por operación; objetivo ilustrativo 100 ms; sin cancelación dura del modelo |
| Cuerpos | Límites y validación originales: 32 KiB JSON, 16 KiB PNG L 20×16 |
| Disponibilidad | Listo, mantenimiento o degradado; ocupado se informa aparte |
| Sondas | `/live`, `/ready`; `/health` conserva forma y sigue disponibilidad |
| Métricas | JSON propio en `/metricas`; contadores desde inicio y población de POST exactos de predicción |
| Registro | UUID generado y campos acotados; sin entradas ni detalle de excepciones |
| Retención | Hasta 256 eventos en memoria; stderr y archivos redirigidos tienen otro ciclo de vida |
| Persistencia | No cambia pesos ni guarda consultas; los scripts exportan capturas si se solicita |
| Evidencia | 8 respuestas/8 eventos en observación; 14 respuestas/15 eventos en fallos, más prueba separada de conexiones |
| Pruebas | 41 pruebas automáticas y figura revisada; interfaz de U32 conservada |
| Exclusiones | Sin autenticación, TLS, promesas de disponibilidad, exportador externo o despliegue público |

Los estados y cifras describen casos locales prefijados. Un 200 no garantiza etiqueta correcta; el historial incluye una respuesta preparada después de abandonar el cliente. No se modifica ni amplía la evaluación predictiva de la Unidad 31.

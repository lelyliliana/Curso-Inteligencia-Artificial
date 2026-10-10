# Ficha — Consulta de luces

[Unidad](../README.md)

| Campo | Descripción |
|---|---|
| Uso | Práctica local de integración de un modelo de fusión con interfaz y HTTP |
| Persona destinataria | Estudiante del curso |
| Modelo | MLP de la U31: cuatro características, ocho unidades tanh, dos clases; 58 parámetros |
| Estado | JSON congelado, huella completa en [contrato y respuestas](servicio.json) |
| Preparación | Medias de dos regiones fijas y codificación del lado; reutilizada sin cambios |
| Entradas | PNG L estático 20×16 hasta 16 KiB y consulta de gramática cerrada |
| Salida | Lado, clase e identidad del modelo; no certeza calibrada |
| Ejecución | Python/PyTorch CPU; servidor estándar en 127.0.0.1; navegador con JavaScript |
| Persistencia | No guarda entradas ni modifica pesos; los scripts de comprobación exportan solo si se solicita |
| Inicio | Verifica huella, configuración, estado, inferencia básica y archivos de interfaz |
| Registro | Método, estado HTTP y duración; no cuerpo, imagen o consulta |
| Calidad predictiva | La documentada en la U31; esta entrega no vuelve a estimarla |
| Evidencia funcional | 24 comprobaciones HTTP, 44 pruebas y recorrido manual de navegador |
| Limitaciones | Geometría fija, imágenes sintéticas, sin detección de dominio ajeno, sin autenticación ni límites globales de carga |
| Operación | Demostración local; no servidor público de producción |

El modelo no controla dispositivos ni recibe imágenes de una cámara. No se debe usar para inferir estados de infraestructura real. La regla programada del ejercicio original ya resuelve la tarea; el valor de esta práctica es aprender a integrar y comprobar un modelo existente.

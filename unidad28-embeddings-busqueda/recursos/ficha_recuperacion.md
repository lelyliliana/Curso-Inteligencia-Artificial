# Ficha de recuperación — Unidad 28

[Volver a la unidad](../README.md) · [Protocolo](../datos/protocolo.md)

## Identidad y recursos comprobados

- Ejecución: 10 de octubre de 2026; Python 3.12.3, Linux x86_64.
- Servidor: Ollama 0.34.2 local; modelo `bge-m3:567m`, GGUF F16, 566,70 M parámetros, 1024 dimensiones.
- Digest: `7907646426070047a77226ac3e684fbbe8410524f7b4a74d02837e43f2146bab`.
- Licencia declarada por ficha y metadatos: MIT. [Modelo original](https://huggingface.co/BAAI/bge-m3) · [Licencia](https://huggingface.co/BAAI/bge-m3/blob/main/LICENSE) · [Distribución consultada](https://ollama.com/library/bge-m3).
- Pesos instalados: 1.157.672.605 bytes. Servidor: 1.218.969.598 bytes cargados, VRAM=0, contexto=2048. No es medición de pico de memoria del sistema.
- CPU solicitada, cuatro hilos, contexto 2048, texto sin prefijos, una entrada por llamada, normalización L2 al indexar y consultar. Sin entrenamiento, APIs pagadas ni paquetes nuevos para inferencia.
- Transporte reutilizado de la Unidad 26, ampliando su lista de destinos locales con `/api/embed`; sin proxy implícito ni redirecciones, timeout de socket 120 s y respuesta limitada a 1 MiB.

## Datos y método

20 documentos completos propios en español, 20 consultas escritas en diez familias. Desarrollo: cinco familias, diez consultas, ocho respondibles y dos sin respuesta. Cierre: otras cinco familias con igual composición. Los documentos son conocidos desde el inicio. Juicios binarios fijados por lectura, sin anotadores independientes; no representan demanda real.

TF-IDF con frecuencia cruda, IDF suavizado y norma L2 frente a embeddings BGE-M3 densos. Búsqueda exacta top-3, empate por ID. Selección: mayor MRR@3 de desarrollo; empate favorece TF-IDF. Sin umbral ni abstención automática. Se verifica identidad de datos, configuración e índice al evaluar cierre.

## Resultados y costos observados

| Fase | Solicitudes evaluadas | Suma de pared | Mediana por llamada | Calentamiento aparte | Tokens de entrada reportados |
|---|---:|---:|---:|---:|---:|
| Desarrollo | 30 | 2,501 s | 0,085 s | 1,839 s | 963 |
| Cierre | 10 | 0,560 s | 0,056 s | 0,050 s | 175 |

Cada fase añade una solicitud de calentamiento: 42 llamadas totales, sin fallos en esta captura. La suma excluye escritura de archivos y análisis; la mediana de desarrollo mezcla documentos y consultas de diferentes longitudes. Cachés, carga y orden afectan tiempos. No es benchmark entre motores, garantía de latencia ni medición de memoria máxima.

Desarrollo: MRR@3 TF-IDF=0,5625 y BGE-M3=1; Recall@3=0,625 y 1. Se elige BGE-M3. Cierre: MRR@3=0,9375, Recall@3=1, Hit@3=1, P@3=0,4167 en ocho respondibles. F07a confunde exportar con importar en la primera posición. Familias respondibles con ambas formulaciones recuperando evidencia: 1/4 léxico y 4/4 denso en desarrollo; 4/4 denso en cierre.

Las dos consultas sin respuesta de cada fase reciben candidatos; no se las ha resuelto ni se afirma que su respuesta sea verdadera. F05a sin respuesta obtiene mayor coseno que F02a respondible. Los resultados y el fallo de orden se conservan sin ajustes posteriores al cierre.

## Límites y uso previsto

Demostración de representación, evaluación y trazabilidad sobre corpus pequeño; no un buscador institucional validado. La referencia léxica es simple y no optimizada. No se prueban documentos largos, extracción PDF, fragmentación, permisos por documento, actualización incremental, ataques al corpus, varios idiomas ni consultas reales masivas. El tamaño muestral no justifica intervalos de calidad de producción.

Los rankings recargados son idénticos en el entorno probado. Un digest registra identidad, no implica que otra implementación reproduzca todos los decimales. Las huellas no autentican un origen frente a manipulación coordinada. Los vectores artificiales del laboratorio 1 no aportan evidencia de comprensión lingüística. RAG con citas, abstención evaluada y generación se dejan a trabajos posteriores.

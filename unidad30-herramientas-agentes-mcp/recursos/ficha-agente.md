# Ficha de ejecución y límites

[Unidad](../README.md) · [Resultados](informe.md)

| Campo | Configuración comprobada |
|---|---|
| Fecha / entorno | 10 de octubre de 2026; Linux; Python 3.12.3 |
| Tarea | Media de lecturas de un sensor ficticio, o estado de ausencia/denegación |
| Modelo | Qwen3:8b, GGUF Q4_K_M, 8.2B según inventario |
| Digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Pesos | 5.225.388.164 bytes; ya instalados; licencia declarada Apache-2.0 |
| Servidor | Ollama 0.34.2, endpoint de chat local fijo |
| Inferencia | CPU, 4 hilos, contexto 4096, salida 192, sin streaming ni thinking |
| Muestreo | Temperatura 0, semilla 3001, top_k 20, top_p 0.95, repeat_penalty 1 |
| Herramientas | Consulta y media; sin escritura ni shell; validación antes de ejecución |
| Política | Permisos por ID, copia local por sesión, cálculo tras consulta autorizada |
| Límites | 4 turnos, 4 propuestas, una por turno, 120 s por tarea, HTTP hasta 45 s |
| Resultado | Estado, ID y número o null; apoyo comprobado en eventos del host |
| MCP | Laboratorio independiente por stdio, subconjunto 2025-11-25; no SDK completo |

`/api/ps` reportó Qwen3 cargado con tamaño 5.937.257.512 bytes, contexto 4096 y `size_vram=0`. Es una instantánea del backend, no una medición del pico de RAM del sistema. No se incorporaron paquetes ni pesos nuevos; las figuras reutilizan Matplotlib del curso.

**Usos adecuados:** aprender contratos, permisos y trazas; comparar un flujo conocido con decisiones de un modelo; reproducir errores concretos sin red. La ruta MCP muestra mensajes reales entre procesos propios; la ruta del agente llama directamente al ejecutor Python.

**Fuera de alcance:** datos privados reales, sensores físicos, correo, compras, modificaciones de repositorios, ejecución arbitraria de programas, un servidor HTTP público y certificación de seguridad o interoperabilidad MCP. Los permisos son una política educativa en memoria, no autenticación multiusuario de producción.

**Fallos observados:** dos respuestas de desarrollo alteradas por instrucciones en una nota; una tarea de cierre interrumpida por timeout. Los detalles permanecen en el informe y las capturas. En las trazas reales no hubo una escritura ejecutada; el código tampoco tiene una función que la realice.

**Límites de evaluación:** ocho familias propias pequeñas; dos paráfrasis por familia; cierre con sensores nuevos pero misma tarea y lenguaje. Un número, estado y evidencia son evaluables de forma exacta aquí; no generaliza a respuestas abiertas. Las sumas de tokens omiten contadores no recibidos. Semilla fija no garantiza igualdad entre entornos.

**Pruebas:** contratos y tipos, estado por sesión, recursos, inyección, presupuestos, errores de transporte artificiales, protocolo/stdio y recarga. No reemplazan revisión humana ni pruebas con otro cliente MCP. Las anotaciones del catálogo no se utilizan como mecanismo de autorización.

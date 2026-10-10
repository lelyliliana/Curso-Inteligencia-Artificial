# Evidencia publicada

[Unidad](../README.md) · [Ficha del experimento](ficha_recuperacion.md)

La colección es ficticia; las llamadas a Ollama son reales. Los ejemplos predeterminados reanalizan estos archivos sin red. No confundir el tiempo de reanálisis con el de codificar textos.

| Carpeta | Archivos | Propósito |
|---|---|---|
| [Desarrollo](desarrollo/registro.json) | `registro.json`, `indice.json`, `seleccion.json`, `informe.json`, PNG/SVG | 20 vectores de documentos, diez consultas, comparación y elección |
| [Cierre](cierre/registro.json) | `registro.json`, `informe.json`, PNG/SVG | Diez consultas nuevas con la elección congelada |

Cada registro conserva un calentamiento aparte, peticiones, respuestas, tiempos, huellas, modelo e inventario. El índice incluye matrices normalizadas y el estado léxico. Los JSON son legibles, más voluminosos que un formato binario; se eligieron por transparencia didáctica. No se publican pesos del modelo. Las figuras se exportaron desde los informes y se inspeccionaron visualmente.

Para regenerar figuras usa los comandos de la unidad sobre una carpeta de resultados. Para repetir inferencia usa una carpeta nueva; no sobrescribas las capturas originales. El ejemplo manual de geometría usa vectores artificiales y puede exportar su JSON, pero nunca se utiliza para presentar resultados lingüísticos.

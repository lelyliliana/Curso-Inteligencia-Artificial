# Datos de la Unidad 28

[Volver a la unidad](../README.md) · [Protocolo previo](protocolo.md)

Colección didáctica propia en español, escrita para esta entrega; no contiene datos privados ni instrucciones operativas de una institución real. Los nombres de aulas, procedimientos, sensores y trámites son ficticios. Los vectores se obtuvieron mediante inferencia real sobre estos textos; no convertir esa distinción en una afirmación de rendimiento real.

| Archivo | Filas | Campos |
|---|---:|---|
| [corpus.json](corpus.json) | 20 | `id`, `titulo`, `texto` |
| [desarrollo.json](desarrollo.json) | 10 | `id`, `familia`, `texto`, `relevantes`, `razon` |
| [cierre.json](cierre.json) | 10 | Mismo esquema; familias distintas |

`relevantes` es una lista de IDs exhaustiva dentro del corpus, fijada por lectura. `[]` significa que ninguno contiene información suficiente para la respuesta exacta. `razon` explica el juicio y no se incorpora al texto que se representa. Cada familia tiene dos consultas; no son personas independientes. No se ha medido acuerdo entre anotadores.

F01–F05 pertenecen a desarrollo: acceso, reloj, plazo de préstamo, inscripción al taller y contraseña ausente. F06–F10 son cierre: pilas del S-31, exportar lecturas, cancelar sala, prerrequisitos y precio ausente. D02/D03 y D06/D07 son fuentes redundantes, ambas relevantes para sus familias. El S-13 y el S-31 son equipos diferentes; importar no equivale a exportar. La diferencia entre un dato ausente y uno irrelevante depende de la consulta, no de que el texto parezca relacionado.

Los textos se conservan en [generar_corpus.py](generar_corpus.py), sin azar. Para restaurar exactamente los JSON publicados desde la raíz:

```bash
python unidad28-embeddings-busqueda/datos/generar_corpus.py
```

El generador sobrescribe esos tres archivos: guarda antes tus variantes en otro directorio. No regenera embeddings. Cambiar los textos o juicios invalida las huellas de las capturas y requiere crear un experimento nuevo. Las comprobaciones verifican datos iguales al generador y familias disjuntas. Tener familias distintas no elimina todos los temas compartidos ni prueba independencia estadística.

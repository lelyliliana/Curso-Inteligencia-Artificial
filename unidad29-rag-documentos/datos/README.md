# Datos y procedencia

[Unidad](../README.md) · [Protocolo fijado](protocolo.md)

Doce documentos TXT UTF-8, con saltos de línea LF, escritos para esta unidad. Los centros, horarios, equipos y normas son ficticios. No se obtuvieron de personas ni instituciones reales. [generar_documentos.py](generar_documentos.py) conserva el texto fuente y los juicios, sin azar.

| Archivo | Contenido |
|---|---|
| [manifiesto.json](manifiesto.json) | ID, título, versión y ruta de doce documentos |
| [desarrollo.json](desarrollo.json) | Diez preguntas de R01–R05 y sus evidencias de evaluación |
| [cierre.json](cierre.json) | Diez preguntas de R06–R10; mismas clases de dificultad, otras entidades/intenciones |
| [esquema.json](esquema.json) | Contrato de la respuesta generada |

Cada documento tiene dos párrafos; se obtiene un fragmento por párrafo, 24 en total, sin solapamiento. El fragmento conserva el texto exacto, ID de origen, versión, ruta, posiciones de caracteres [inicio, fin), líneas de origen y huella del texto completo. Los offsets se refieren a caracteres de la cadena decodificada, no a bytes UTF-8. Las posiciones son válidas para esa versión; editar el documento exige regenerarlas. Los archivos de esta práctica no necesitan OCR, extracción PDF ni limpieza HTML.

Una pregunta tiene `id`, `familia`, `pregunta` y `evidencias`. Cada evidencia indica `fragmento` y `valor` mínimo literal. El catálogo es una anotación propia que se usa después de generar, nunca como entrada al recuperador o al modelo. Un valor debe aparecer literalmente en el fragmento, pero esa comprobación sintáctica no decide por sí sola que sea el hecho pertinente: ese juicio se escribió leyendo el texto y la pregunta.

| Familias | Desarrollo | Cierre |
|---|---|---|
| Valor único | R01: plazo Nácar; R02: capacidad Marea; R05: intervalo T-42 | R06: cupo Junco; R07: cancelación Cedro; R10: carga K-17 |
| Contradicción | R03: dos agendas de Bruma, 09:00 y 11:00 | R08: dos actas de Vela, 16 °C y 19 °C |
| Dato ausente | R04: tarifa Granate | R09: contraseña Neblina |

Cada familia tiene dos formulaciones y permanece en una sola partición. Son seis consultas con valor único, dos contradictorias y dos sin evidencia por fase. No son veinte usuarios independientes. Los documentos completos están disponibles desde el inicio; las consultas y juicios del cierre se reservan para su evaluación después de seleccionar. La autoría y validación editorial conocen los textos: es una demostración del procedimiento, no un estudio ciego.

Las agendas y actas contradictorias están vigentes y no establecen precedencia. No asumir que B reemplaza A ni resolver por posición en el ranking. [D06](documentos/D06.txt) y [D12](documentos/D12.txt) contienen notas deliberadamente no confiables que intentan cambiar la salida. Esas órdenes no se anotan como hechos operativos del sensor. Se muestran para estudiar el límite entre datos e instrucciones, sin ejecutar acciones externas.

Para restaurar los datos publicados desde la raíz:

```bash
python unidad29-rag-documentos/datos/generar_documentos.py
```

Sobrescribe manifiesto, consultas y documentos: guarda tus variantes aparte. No regenera vectores ni respuestas. Si cambias fuentes o juicios, las capturas antiguas quedan incompatibles. Ningún dato nuevo de esta unidad se tomó del cierre de la Unidad 28.

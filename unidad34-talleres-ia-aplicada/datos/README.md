# Datos propios de los tres talleres

[Unidad](../README.md) · [Generador](generar_datos.py) · [Protocolo previo](protocolo.json)

## Procedencia y uso

Datos creados para el curso el 10 de octubre de 2026. Todos los edificios, zonas, procedimientos y preguntas son ficticios. No se descargaron datasets, se copiaron manuales externos ni se incorporaron datos personales. No son mediciones de ahorro, impacto ambiental o aprendizaje.

Se distribuyen como material didáctico propio del repositorio. No hay condiciones de un proveedor externo que trasladar. El repositorio no declara una licencia general y esta ficha no añade una licencia nueva. Un proyecto con datos externos debe documentar procedencia, licencia o permiso y las condiciones de uso aplicables.

## Archivos y particiones

| Taller | Ajuste | Validación | Prueba |
|---|---|---|---|
| Energía | [575 decisiones](energia/entrenamiento.json) | [192 decisiones](energia/validacion.json) | [192 decisiones](energia/prueba.json) |
| Ambiente | [240 registros, 6 zonas](ambiente/entrenamiento.json) | [120 registros, 3 zonas](ambiente/validacion.json) | [120 registros, 3 zonas](ambiente/prueba.json) |
| Documentos | [10 documentos](documentos/corpus.json) | [12 preguntas, 6 familias](documentos/validacion.json) | [12 preguntas, 6 familias](documentos/prueba.json) |

Los nueve archivos son JSON UTF-8 con arrays de objetos. El generador lee semillas y tamaños del protocolo y escribe en la carpeta solicitada. No ejecuta modelos ni elige candidatos. La prueba automatizada compara los bytes regenerados con los publicados.

## Energía: una serie, pronósticos progresivos

Se generan 960 horas desde el 6 de julio de 2026 a las 00:00 UTC−05:00. `random.Random(3401)` aporta ruido gaussiano de desviación 1,4 kW. La potencia sintética es:

```text
28 + 7·sin(2π·(hora−7)/24) + 9·laboral + 5·I(t≥840) + ruido
```

`laboral` vale uno de lunes a viernes. La potencia se redondea a seis decimales. La fórmula no es un modelo físico y la fecha no describe un edificio real. Se construyen objetivos `t=1..959`; los cortes son `t<576`, `576≤t<768` y `t≥768`.

| Campo | Significado y uso |
|---|---|
| id | E seguido de la hora objetivo; trazabilidad, no entrada |
| origen | Momento en que se observa la lectura actual |
| instante_objetivo | Exactamente una hora después del origen |
| consumo_actual_kw | Última potencia observada, en kW, disponible en el origen |
| hora_siguiente | Hora del objetivo, 0–23, conocida por calendario |
| laboral_siguiente | Entero 0/1, conocido por calendario |
| objetivo_kw | Potencia una hora después; etiqueta, nunca entrada del predictor |

`consumo_actual_kw` conserva el nombre habitual «consumo», pero representa potencia en **kW**, no energía en kWh. No se integra la curva para calcular energía. Se supone llegada inmediata, sin huecos ni duplicados; no se generaliza esa suposición a sensores reales. No existe una etiqueta de «cambio» usada por el modelo: la hora 840 se usa para generar la serie y explicar el diagnóstico posterior.

## Ambiente: registros agrupados por zona

`random.Random(3402)` genera doce zonas Z00–Z11 y cuarenta filas por zona. Las seis primeras son entrenamiento, las tres siguientes validación y las tres finales prueba. Cada fila tiene un ID único y estas variables:

| Campo | Generación / significado |
|---|---|
| residuos_m2 | Uniforme de 0 a 12, redondeada a cuatro decimales; densidad ficticia |
| superficie_afectada_pct | Uniforme de 0 a 100, cuatro decimales |
| dias_sin_visita | Entero uniforme de 0 a 60 |
| revision_prioritaria | Etiqueta 0/1 obtenida por sorteo con probabilidad logística |
| zona | Grupo completo de evaluación, excluido de las características |

La etiqueta se sortea con `p = sigmoide(−6 + 0,45·residuos + 0,04·superficie + 0,025·días + sesgo_zona)`. El sesgo recorre −0,5; 0; 0,5 por zona y añade 0,8 a las de prueba. Esta construcción introduce incertidumbre y una diferencia entre grupos; no proviene de expertos, de visitas reales ni de una regulación.

No se interpreta cada fila como un momento de una misma parcela. La independencia y variación que impone el generador son limitaciones del ejercicio. El modelo recibe solo las tres mediciones; ni el sesgo generador ni la zona ni la etiqueta forman parte de su entrada.

## Documentos y preguntas

Cada documento tiene `id`, `titulo`, `version` y `texto`. La búsqueda usa solo `texto`; el título es información editorial. Todo el párrafo se devuelve como cita con `inicio=0` y `fin=len(texto)`, intervalo semiabierto en caracteres Unicode de Python. No son posiciones dentro del JSON serializado.

Las preguntas tienen `id`, `familia`, `pregunta` y `documento_esperado`. El último campo es un ID o `null` para preguntas sin respuesta. Es un juicio didáctico escrito junto al caso antes de evaluar. No se envía al buscador ni se incorpora al vocabulario.

Cada fase tiene cuatro familias respondibles y dos no respondibles, con dos formulaciones por familia: 8+4 preguntas. El corpus está disponible en ambas fases; las familias de consulta están separadas. Esta reserva mide consultas nuevas sobre el mismo corpus, no recuperación sobre una institución distinta.

## Trazabilidad

Los modelos exportados guardan IDs de ajuste/validación y huellas de datos, protocolo, generador y módulos pertinentes. El cierre agrega la huella de su archivo de prueba. No se usan datos de las unidades previas ni se modifica su evidencia. Los ejemplos manuales son artificiales y están separados en [manual.json](../recursos/manual.json).

Después de consultar las respuestas publicadas, esas pruebas son evidencia conocida para cualquier versión nueva. Una mejora posterior debe declarar ese uso y reservar datos adicionales antes de presentarse como evaluación independiente.

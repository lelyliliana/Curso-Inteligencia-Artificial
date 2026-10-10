# Datos — Peticiones sintéticas de un curso

[Unidad](../README.md) · [Protocolo](protocolo.md)

## Procedencia y condiciones de uso

Textos creados expresamente para este repositorio el 10 de octubre de 2026. No se extrajeron mensajes de estudiantes, correos, sitios web ni conjuntos externos; no contienen datos personales reales. Las etiquetas representan la intención que se redactó en cada plantilla, sin anotadores independientes ni estudio de acuerdo.

Son material didáctico propio, distribuido con el curso. No hay una licencia de un proveedor externo que trasladar. El repositorio no declara actualmente una licencia general; esta ficha no añade una licencia nueva ni atribuye permisos de terceros. Para ampliar el conjunto con textos reales, documenta autorización, condiciones de uso y tratamiento de información personal antes de incorporarlos.

## Taxonomía

| Clase | Petición afirmada que se quiere atender | Ejemplo |
|---|---|---|
| acceso | Entrar a plataforma, recuperar cuenta o contraseña | «No puedo entrar al aula» |
| material | Obtener apuntes, documento, ejercicios o diapositivas | «Busco la guía de ejercicios» |
| horario | Conocer fecha, día u hora de una actividad | «¿Cuándo será el encuentro?» |

Mencionar una palabra no basta para definir la clase. «Ya tengo el material; falla el acceso» pertenece a acceso. El entrenamiento y la evaluación principal tienen una sola petición objetivo. Las peticiones múltiples, vagas o ajenas al catálogo se examinan aparte; no se fuerzan etiquetas inventadas para calcular exactitud.

## Archivos y tamaño

| Archivo | Familias | Textos | Textos por clase |
|---|---:|---:|---:|
| [entrenamiento.csv](entrenamiento.csv) | 18 | 54 | 18 |
| [validacion.csv](validacion.csv) | 9 | 27 | 9 |
| [prueba.csv](prueba.csv) | 9 | 27 | 9 |
| [diagnosticos.json](diagnosticos.json) | No es una partición estadística | 9 | No aplicable |

Cada familia es una frase base distinta con un hueco `{tema}`. Se asigna a una partición antes de sustituir robótica, programación y estadística. Los temas aparecen en todas las clases y particiones; no se intenta evaluar un tema desconocido. Separar filas al azar permitiría ver la misma frase con otro tema durante ajuste y evaluación.

Las familias pertenecen al mismo estilo de redacción y comparten vocabulario. Esta separación evita el cruce de variantes de la misma plantilla, pero no simula diversidad de usuarios, dialectos, errores de escritura o instituciones. No calcular un intervalo de confianza suponiendo 108 observaciones humanas independientes.

## Esquema CSV

| Campo | Significado |
|---|---|
| id | Identificador único de variante; contiene metadatos y no es característica |
| familia | Origen de las tres variantes; usado para auditoría de separación |
| tema | Sustitución aplicada a la plantilla; metadato de trazabilidad |
| texto | Entrada Unicode UTF-8, incluyendo signos y tildes originales |
| clase | Una de las tres etiquetas, a partir de la petición redactada |
| sha256 | Huella de los bytes UTF-8 del texto, antes de normalizar |

Los diagnósticos tienen ID, tipo, texto, clase y nota. `clase=null` significa que la taxonomía de una etiqueta no da una referencia válida; no significa una cuarta clase entrenada. d03 contiene únicamente tokens desconocidos; d04 queda vacío al tokenizar. Los modelos siempre devuelven alguna clase, incluso en esos casos.

## Regeneración

Desde la raíz, en otra carpeta para comparar sin sobreescribir los datos originales:

```bash
python unidad22-lenguaje-natural/datos/generar_datos.py --salida resultados/u22-datos
```

El [generador](generar_datos.py) contiene 36 plantillas fijas y produce exactamente los tres CSV. No regenera diagnósticos: ese archivo es una batería editorial independiente, escrita explícitamente y conservada en Git. Las pruebas comparan los CSV regenerados byte por byte; cambiar textos obliga a recalcular huellas y a registrar otro experimento.

# Corpus sintético — Unidad 25

[Unidad](../README.md) · [Protocolo previo](protocolo.md)

Corpus creado para el curso, sin registros de personas, textos descargados ni modelos externos. Los temas «energia», «agua», «aire» y «suelo» son símbolos de un lenguaje artificial; las zonas y niveles no describen mediciones reales. No se asignan licencias de proveedores de datos inexistentes ni una licencia adicional a la del repositorio.

## Construcción y particiones

Se enumeran cuatro temas, cuatro zonas (`norte`, `sur`, `este`, `oeste`) y tres niveles (`bajo`, `medio`, `alto`): 48 familias. El [generador](generar_datos.py) mezcla esas familias con `random.Random(2500)` y asigna 32/8/8 a entrenamiento, validación y prueba. Solo después deriva dos formatos por familia:

```text
tema agua zona norte nivel bajo formato breve salida
→ agua norte bajo .

tema agua zona norte nivel bajo formato detallado salida
→ informe agua en norte con nivel bajo .
```

| Archivo | Familias | Documentos | Objetivos de continuación, incluido EOS |
|---|---:|---:|---:|
| [entrenamiento.json](entrenamiento.json) | 32 | 64 | 448 |
| [validacion.json](validacion.json) | 8 | 16 | 112 |
| [prueba.json](prueba.json) | 8 | 16 | 112 |

Campos de cada documento: `id` único, `familia` (tema-zona-nivel), `formato`, `prefijo` y `continuacion`. JSON UTF-8; tokens separados por espacios, incluido el punto final. El orden dentro del archivo conserva la familia y luego breve/detallado. Ningún texto contiene tokens especiales; se añaden al preparar el lote.

## Qué generalización se evalúa

Una combinación completa de tema, zona y nivel no aparece en dos particiones. Sí se comparten palabras, orden de campos y plantillas. Las formas breve y detallada de una familia permanecen juntas. El vocabulario se aprende con entrenamiento; en los corpus publicados las palabras de validación y prueba ya están en él. Los diagnósticos de desconocidos se declaran aparte.

La separación impide repetir exactamente una combinación reservada, pero **no prueba que el modelo aprenda una regla nueva, entienda lenguaje libre o verifique hechos**. Todas las salidas son generadas por dos funciones conocidas. Un programa de plantillas resolvería directamente la tarea; el corpus permite inspeccionar cómo una red aprende y usa dependencias a distancia.

El vocabulario resultante tiene 26 entradas: 22 tokens de contenido y PAD/BOS/EOS/UNK. El prefijo tiene nueve tokens de contenido. Una secuencia breve tiene 15 tokens contando BOS y EOS; una detallada, 19. Las entradas desplazadas miden 14 y 18 posiciones; los lotes se rellenan a la derecha hasta 18, por debajo del contexto máximo 24.

La pérdida comienza en la predicción del primer token de continuación. Cada documento breve aporta cuatro tokens y EOS; cada detallado, ocho y EOS. El prefijo ofrece contexto; no se entrena al modelo para producirlo desde cero. Por ello un prefijo incompleto también puede conducir a resultados incoherentes.

## Regenerar y rastrear

Desde la raíz, sin sobrescribir los datos publicados:

```bash
python unidad25-transformers-generativos/datos/generar_datos.py --salida resultados/u25/datos_regenerados
```

Las pruebas comparan los tres archivos byte por byte con una regeneración temporal y comprueban familias disjuntas. El desarrollo lee entrenamiento y validación, guarda sus huellas SHA-256 y conserva las familias conocidas en el estado. El cierre rechaza familias ya usadas en desarrollo y añade la huella del corpus de prueba. Las pruebas de integridad sí pueden leer todos los archivos para comprobar su separación; no usan métricas de prueba para elegir pesos o hiperparámetros.

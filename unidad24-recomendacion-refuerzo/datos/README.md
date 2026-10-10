# Datos y entorno de la Unidad 24

[Unidad](../README.md) · [Protocolo](protocolo.md)

Todo el material de datos de esta práctica fue creado para el curso. Los usuarios, aperturas, recursos, fechas y preferencias son ficticios. No se descargaron registros de terceros, no hay datos personales y no se atribuyen licencias de proveedores inexistentes. La reutilización del material propio se rige por las condiciones generales que establezca el repositorio; este archivo no inventa una licencia adicional.

## Archivos de recomendación

| Archivo | Filas sin cabecera | Campos | Uso |
|---|---:|---|---|
| [catalogo.csv](catalogo.csv) | 26 | elemento, tema, titulo | Conjunto de recursos disponibles |
| [entrenamiento.csv](entrenamiento.csv) | 192 | usuario, elemento, fecha | Ajustar popularidad, coseno e historiales |
| [validacion.csv](validacion.csv) | 56 | usuario, elemento, fecha | Elegir entre los dos métodos |
| [prueba.csv](prueba.csv) | 56 | usuario, elemento, fecha | Cierre con el estado elegido |

CSV UTF-8, separador coma, fecha ISO 8601 con zona UTC−05:00. Las filas se ordenan por usuario; no se deduce la partición por posición física del archivo. El lector comprueba la fecha contra el bloque indicado. Cada par usuario–elemento es único y las parejas de los tres bloques no se solapan.

I01–I06 representan energía; I07–I12 ambiente; I13–I18 documentos; I19–I24 sensores. I25 es general y aparece en los 48 historiales conocidos; I26 está en el catálogo pero nunca en entrenamiento. Los nombres son marcadores de ejemplo, no textos de recursos reales. U01–U48 tienen cuatro aperturas; U49–U56 no tienen historia antes de evaluar.

El [generador](generar_datos.py), con `random.Random(2400)`, asigna cuatro grupos cíclicos. Para cada usuario conocido toma dos elementos distintos de su tema, uno del tema vecino y el general. Cada objetivo futuro se sortea entre recursos todavía no usados: elige primero el tema propio con probabilidad 0,8 o el vecino con 0,2. La elección es sintética, no una estimación de comportamiento humano. Se fuerzan cuatro casos para mostrar un elemento nuevo: I26 en validación para U01 y U49, y en prueba para U02 y U50. Estas reglas preceden a la evaluación de los métodos.

Generar los datos no aprende preferencias; construye un escenario con afinidades deliberadas que favorece la posibilidad de encontrar coocurrencias. Los métodos no reciben el grupo generador. Aun así, este proceso pequeño no representa toda la diversidad ni los sesgos de una plataforma educativa.

Para comprobar regeneración sin sobrescribir los datos publicados:

```bash
python unidad24-recomendacion-refuerzo/datos/generar_datos.py --salida resultados/u24/datos_regenerados
```

Las pruebas comparan bytes de los cuatro CSV con una regeneración temporal. Los informes guardan SHA-256 de los archivos usados. El desarrollo no calcula la huella ni lee el CSV de prueba; el cierre añade su propia huella. Las verificaciones de integridad sí inspeccionan las particiones para comprobar su separación, sin elegir parámetros con sus métricas.

## Entorno de refuerzo

No usa estos CSV ni a estos usuarios. El mapa, las recompensas y los giros aleatorios están definidos en [refuerzo_curso.py](../ejemplos/refuerzo_curso.py), y se guardan con cada conjunto de tablas. Todo ocurre en memoria, sin sensores, actuadores, red o simulador externo.

Los IDs 0–24 codifican casillas. Meta y pozos son terminales; sus filas Q permanecen en cero. El corte externo de 60 pasos no convierte una casilla en terminal. El [protocolo](protocolo.md) conserva orden de acciones, probabilidades, presupuesto y semillas de entrenamiento, desarrollo y cierre.

Las semillas de evaluación se reinician por episodio y son iguales entre políticas para compartir los sorteos de giro. Esto facilita comparar condiciones, pero las acciones y longitudes producen trayectorias distintas. Se reserva otro conjunto de semillas para el cierre; no se reserva un mapa nuevo. La evaluación solo habla de este tablero y esta distribución de transiciones.

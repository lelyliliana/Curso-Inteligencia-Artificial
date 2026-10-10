# Datos de la Unidad 20

[Unidad](../README.md) · [Protocolo](protocolo.md)

Material sintético creado para este curso el 10 de octubre de 2026. No representa personas, equipos ni observaciones de una población real. No contiene datos personales. Se reutilizan funciones de lectura y cálculo de la Unidad 19, pero ninguna de sus particiones.

## Equivalencia: un caso numérico

[`equivalencia.json`](equivalencia.json) contiene seis pares de entradas y seis etiquetas binarias fijadas explícitamente, ancho oculto 3, semilla de inicialización 20, L2=0,05 y tasa=0,1. Comprueba la traducción de una función y sus derivadas. No tiene una muestra de validación ni estima desempeño fuera de esas filas.

## Minilotes: un experimento predictivo

| Archivo | Filas | Semilla PCG64 |
|---|---:|---:|
| [entrenamiento.csv](minilotes/entrenamiento.csv) | 150 | 20262001 |
| [validacion.csv](minilotes/validacion.csv) | 80 | 20262002 |
| [prueba.csv](minilotes/prueba.csv) | 80 | 20262003 |

| Campo | Significado y restricciones |
|---|---|
| caso_id | Identificador único con prefijo de partición; no es una entrada del modelo |
| senal_a | Primera señal adimensional, finita en [−1,1] |
| senal_b | Segunda señal adimensional, finita en [−1,1] |
| objetivo | 0 o 1; clase positiva=1; disponible para aprendizaje o evaluación |

No hay unidades físicas, faltantes, equipos repetidos ni eje temporal. Ambas señales se consideran disponibles al predecir; el objetivo se excluye de las entradas. Se exige variación en ambas columnas de entrenamiento y presencia de las dos clases. El lector rechaza filas incompletas, columnas adicionales, valores fuera de rango, etiquetas inválidas e IDs repetidos.

Para cada partición, el [generador](generar_datos.py) crea primero n pares uniformes en [−1,1), los redondea a cinco decimales y calcula:

```text
s_real = 6 · (senal_b − 0,5 · sin(pi · senal_a))
p_real = 1 / (1 + exp(−s_real))
objetivo = 1 si u < p_real, con u uniforme en [0,1)
```

Los uniformes para etiquetas se generan después de todos los pares de señales. Esta secuencia forma parte de la reproducción. Los modelos reciben las señales y etiquetas de entrenamiento, no `s_real` ni `p_real`; la fórmula documenta el origen sintético, no es un candidato del experimento. Las particiones usan nuevas extracciones de la misma distribución. El diseño no simula cambios de población, dependencia por grupos ni evolución temporal.

Entrenamiento tiene 71 positivos de 150; validación, 41 de 80. Las semillas se fijaron antes de ejecutar los modelos. Las etiquetas aleatorias pueden discrepar de la clase más probable según la fórmula: una frontera visual no separará necesariamente todos los casos.

## Regenerar sin sobrescribir

Desde la raíz, con las dependencias instaladas:

```bash
python unidad20-pytorch/datos/generar_datos.py --salida resultados/u20-datos-regenerados
```

La carpeta debe ser nueva; se producen el JSON y los tres CSV. La prueba de regeneración compara bytes con los archivos publicados. Las huellas SHA-256 del informe corresponden solo a los archivos leídos: por defecto, entrenamiento y validación. Generar o conocer el mecanismo no convierte el cierre en privado. Tras publicar sus resultados, debe tratarse como un cierre didáctico conocido.

# Ficha del experimento de prompts

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Desarrollo](desarrollo/informe.json) · [Selección](desarrollo/seleccion.json) · [Cierre](cierre/informe.json)

## Propósito y datos

Comparar instrucciones y control de formato para consultar registros sintéticos confirmados, con evidencia por ID, ausencia y conflicto. Diez familias, dos órdenes de registros por familia. Seis familias para desarrollo y cuatro para cierre. La separación conserva juntas las vistas de una misma familia; las dos particiones siguen perteneciendo al mismo dominio artificial.

## Configuración verificada — 10 de octubre de 2026

- Ollama 0.34.2; `qwen3:8b`, 8.2B, Q4_K_M, pesos locales ya instalados.
- Digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.
- Licencia informada: Apache-2.0; identificación conservada por el inventario de la Unidad 26. No se redistribuyen pesos.
- Linux x86_64, Python 3.12.3, CPU Ryzen 7 6800H, cuatro hilos; sin paquetes nuevos. Figuras con NumPy 2.2.6 y Matplotlib 3.10.8 ya instalados.
- Contexto 2048, salida máxima 160, semilla 2701, temperatura 0, `think=false`, `stream=false`, `num_gpu=0`, top_k 20, top_p 0.95 y penalización de repetición 1.
- Timeout de socket 120 s; sin reintentos. Calentamiento separado por fase, máximo cuatro tokens. Cada intento se guarda; solo un registro completo con inventario estable se acepta para comparar.

## Candidatos y selección

Básico: instrucción breve. Explícito: reglas completas y esquema en el texto. Con_esquema: el mismo prompt explícito, con esquema también en `format`. Desarrollo evalúa los tres sobre cada caso, rotando orden. Selección por mayor número de aceptadas y desempate previamente fijado. No se usan tokens ni tiempo como criterios de elección.

| Candidato | Forma | Aceptadas | Familias completas | Mediana de pared | Tokens de salida totales |
|---|---:|---:|---:|---:|---:|
| basico | 12/12 | 5/12 | 2/6 | 7,209 s | 314 |
| explicito | 12/12 | 9/12 | 3/6 | 6,865 s | 325 |
| con_esquema | 12/12 | 9/12 | 3/6 | 3,680 s | 325 |

Elegido: explícito. Los tres cumplen forma en todos los casos; el esquema no aporta exactitud adicional en esta captura. La referencia por reglas resuelve 12/12.

## Cierre conservado

Solo se llama al elegido: ocho respuestas con forma, coherencia y parada normales, **4/8 aceptadas**, **1/4 familias completas**. Por estado esperado: ok 2/4; ausente 1/2; conflicto 1/2. F08b usa un borrador; F09a cita un borrador entre sus evidencias; F10a/b siguen la instrucción incrustada que solicita ausente. El archivo de selección no se retoca a partir de estos errores. Referencia por reglas: 8/8.

Cierre tiene mediana de pared 7,153 s y 215 tokens de salida. Todas las 44 llamadas evaluadas terminaron por stop y no hubo fallos de transporte; los truncamientos, negativas libres y JSON malformados del laboratorio A son artificiales, no incidentes medidos en estas llamadas.

## Límites y decisión

Una repetición por caso/candidato; dos vistas dependientes por familia; caché y carga del equipo no controladas completamente. Las latencias son diagnósticas, no un benchmark general. No se midieron pico de RAM, energía, concurrencia, documentos largos ni calidad en lenguaje libre. El esquema no prueba fidelidad a los datos y las notas incrustadas no cubren un espacio de ataques representativo.

No recomendamos usar este modelo en lugar de las reglas para la estructura de entrada actual. El material sirve para aprender selección, validación y conservación del cierre. No hubo API pagada, entrenamiento de pesos ni juez humano o LLM independiente. Para ampliar la tarea se necesitan nuevas referencias y una nueva evaluación reservada.

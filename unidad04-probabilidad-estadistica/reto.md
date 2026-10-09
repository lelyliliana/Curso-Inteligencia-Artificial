# Reto — Interpretar datos e incertidumbre

Elabora un informe reproducible que describa observaciones y analice un escenario probabilístico. Trabaja con los casos incluidos o con variantes explícitamente sintéticas en energía, sensores, ambiente o educación.

El objetivo es justificar cálculos e interpretaciones, conservando la diferencia entre datos fabricados, supuestos y resultados de simulación.

## Condiciones

- Trabajo individual o en equipo de hasta tres integrantes.
- Biblioteca estándar de Python suficiente. Si introduces dependencias, documenta instalación y versiones.
- Todos los datos del reto serán sintéticos y declarados como tales.
- Conserva el archivo original y guarda las variantes por separado.
- No elimines observaciones solo porque una regla exploratoria las señale.
- Registra parámetros, semilla, tamaño, repeticiones, versión y comandos.

## Desarrollo

1. **Contexto y datos.** Define unidad de análisis, características y unidades. Explica cómo se generó el archivo y qué población real no representa.
2. **Descripción manual.** Calcula media, mediana, moda, ambas varianzas y cuartiles del CSV. Señala la convención. Compara con el laboratorio y explica el valor 26.
3. **Variante.** Cambia un valor extremo en una copia. Registra qué resúmenes cambian y por qué; no llames limpieza a ese cambio de experimento.
4. **Alertas.** Elige dos prevalencias y mantén sensibilidad y especificidad declaradas. Calcula conteos esperados y posterior. Explica el supuesto de transportar esas condicionales entre escenarios.
5. **Simulación.** Compara tamaños n=50, 200 y 800 con la misma probabilidad, semilla y 1000 repeticiones. Registra ancho medio y cobertura observada. Explica por qué no se exige 95 % exacto ni crecimiento monótono de cobertura.
6. **Asociación.** Ejecuta el ejemplo de grupos. Describe relación global y por grupo; utiliza la figura o una representación propia calculada con los mismos pares. Explica por qué ninguna prueba causalidad.
7. **Conclusión.** Identifica una afirmación sustentada por cada experimento, una que no esté sustentada y la evidencia adicional necesaria para una aplicación real.

El mismo número puede ser observado, estimado o supuesto según el procedimiento. Indica su papel en cada tabla.

## Entrega

Un repositorio con:

- README con objetivo, organización y comandos desde la raíz.
- CSV original o referencia al del curso, variante y procedencia.
- Código utilizado y cambios identificados.
- Informe con cálculos, resultados y limitaciones; puedes completar la [plantilla](plantillas/informe_estadistico.md).
- Enlaces accesibles al material de apoyo; entrega enlaces sin depender de adjuntos.

Para una actividad evaluable, añade un video de 3 a 5 minutos con cámara. Explica un cálculo, una interpretación de Bayes y una limitación del intervalo. Declara qué herramientas de IA utilizaste, sus aportes, cómo verificaste resultados y qué corregiste. En equipo, señala los aportes de cada integrante.

## Rúbrica

| Criterio | Puntos |
|---|---:|
| Unidad de análisis, variables y procedencia | 15 |
| Descripción manual, dispersión y cuartiles | 25 |
| Bayes, denominadores y supuestos | 20 |
| Simulación e interpretación de incertidumbre | 20 |
| Asociación, agregación y límites | 10 |
| Reproducibilidad y comunicación | 10 |
| **Total** | **100** |

La evaluación valora cálculos consistentes y conclusiones proporcionales a la evidencia. Un porcentaje sin denominador, un intervalo mal interpretado o una afirmación causal basada solo en correlación necesita corregirse aunque el programa ejecute.

[Volver a la unidad](README.md) · [Consultar soluciones](soluciones/README.md)

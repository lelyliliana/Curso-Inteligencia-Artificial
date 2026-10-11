# Informe completado — Revisión de potencia horaria

[Unidad](../README.md) · [Datos](../datos/README.md) · [Operación](operacion.md) · [Defensa breve](defensa.md)

## Problema y versión

Versión `u35-v1`, elaborada el 10 de octubre de 2026. Usuario ficticio: responsable de un edificio que revisa una estimación horaria. Salida: potencia estimada, instante objetivo y marca de revisión. El sistema no controla cargas ni estima ahorro. Hipótesis: modelar el incremento del calendario permite seguir un nivel de potencia ya observado sin reaprender parámetros.

Se reutiliza el módulo de energía de la Unidad 34 para persistencia y Ridge de nivel, sin modificarlo; ambos se ajustan o parametrizan con datos nuevos. El predictor de incremento y el contrato temporal se implementan en esta unidad. No se utilizan los datos ni modelos guardados de la U34.

## Protocolo y ejecución

Protocolo fijado antes de ejecutar: 720/240/240 decisiones por tiempo objetivo; tres candidatos, selección por MAE, desempate por orden. Escala y coeficientes se aprenden con entrenamiento. El elegido y la referencia se guardan antes de abrir prueba; no hay reajuste ni selección en el cierre.

Se instaló un entorno virtual nuevo, sin paquetes del sistema, a partir de los requisitos existentes del curso. [entorno.json](entorno.json) registra versiones principales y [entorno-verificado.txt](entorno-verificado.txt) conserva la resolución completa. La prueba se hizo en Linux x86_64 con Python 3.12.3. No se descargaron modelos externos para este proyecto; la revisión de todo el curso reinstaló el paquete PyTorch CPU ya declarado.

## Resultados

| Fase | Candidato | Admitidas / total | MAE (kW) |
|---|---|---:|---:|
| Validación | Persistencia | 236/240 | 2,2821 |
| Validación | Ridge de nivel | 236/240 | 4,9344 |
| Validación | Ridge de incremento | 236/240 | **1,2840** |
| Cierre | Persistencia congelada | 236/240 | 2,2594 |
| Cierre | Incremento congelado | 236/240 | **1,2341** |

El cierre obtiene reducción relativa de MAE 45,3772 %, sesgo medio `predicho−observado` de 0,0061 kW y cobertura 98,3333 %. Cumple MAE≤2, mejora≥10 % y cobertura≥95 %, tres condiciones didácticas fijadas previamente. El campo `autoriza_uso_real=false` del informe significa que estos resultados sintéticos no evalúan la eficacia de una implantación real.

Las comparaciones comparten los mismos IDs y rechazos. El MAE no asigna error cero a solicitudes rechazadas; las excluye y comunica su proporción por separado. Cierre rechaza PF0995 por llegada tardía, PF1033 por potencia ausente, PF1115 por potencia negativa y PF1188 por edad excesiva.

## Fallos y marcas conservados

| Caso | Observado (kW) | Predicho (kW) | Error absoluto (kW) |
|---|---:|---:|---:|
| PF1070 | 67,071 | 59,137 | 7,934 |
| PF1140 | 49,278 | 57,645 | 8,366 |

Ambos corresponden a saltos de nivel que aún no estaban en la lectura de entrada. Un promedio bajo no implica error pequeño en cada hora. Hay 57 de 236 entradas marcadas para revisión por salir del rango de potencia observado al entrenar; se mantienen en el MAE. Esa marca es una comprobación de rango, no un detector completo de cambio ni una garantía de error.

## Evidencia y traspaso

Archivos: [modelo y referencia](modelo.json), [validación por caso](validacion.json), [cierre por caso](prueba.json), [comprobación funcional](entrega.json), [consulta conocida](consulta.json), [figura PNG](proyecto.png) y [SVG](proyecto.svg).

La demo normal devuelve 43,761493161 kW y la referencia devuelve 42 kW. Ocho respuestas del laboratorio se correlacionan con ocho eventos; la prueba de referencia va aparte. Los eventos contienen ID, versión, política, estado, código y duración, sin valores de entrada, predicción o detalles de excepciones. No se midió disponibilidad de un servicio desplegado ni latencia extremo a extremo.

Las 37 pruebas incluyen referencia por ecuaciones normales, disponibilidad temporal, rechazos comunes, invariancia al cambiar etiquetas, recarga, integridad, criterio conjunto y ejecución real de la CLI. Se intercepta ajuste/selección durante cierre y lectura de prueba durante desarrollo. La figura fue revisada visualmente.

**Decisión:** aceptar la entrega educativa y conservar sus límites. Antes de un uso real hacen falta datos con procedencia y llegada verificadas, costos y tolerancias acordados, nuevos periodos reservados y una prueba operativa acorde con el sistema. El proyecto no aporta evidencia de ahorro ni de seguridad de control automático.

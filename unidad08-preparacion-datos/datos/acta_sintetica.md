# ACTA-SIM-001 — Referencia adicional del ejercicio

[Volver a los datos](README.md)

Este documento es una **evidencia sintética creada para la Unidad 8**, no un acta de una organización real. Introduce un dato nuevo para distinguir corrección apoyada en una referencia de una imputación estadística.

En el escenario del ejercicio se establece lo siguiente:

| Campo | Referencia |
|---|---|
| Archivo | CSV de lecturas de la Unidad 7 |
| Registro, sin contar encabezado | 8 |
| Fecha | 2026-09-03 |
| Sensor | S2 |
| Variable | consumo_kwh |
| Texto registrado por error | -2 |
| Valor de referencia del escenario | 10 kWh |

La referencia se refiere al mismo intervalo diario y a la misma unidad definidos en la Unidad 7. No cambia la fecha, el sensor ni la granularidad de la observación. No proporciona valores para los faltantes ni decide entre los dos registros conflictivos de S3.

El archivo de correcciones identifica esta acta y fija la huella de la copia a la que se aplica. El programa comprueba esa correspondencia, pero no autentica documentos ni verifica hechos reales. Si modificas la fuente, no debe aplicar silenciosamente el mismo parche.

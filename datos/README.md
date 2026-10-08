# Datos de práctica

[Volver al curso](../README.md)

## Consumo sintético

[consumo_sintetico.csv](consumo_sintetico.csv) contiene siete registros ficticios creados para este curso. No procede de un hogar, dispositivo ni organización real.

| Columna | Tipo | Significado | Restricción |
|---|---|---|---|
| `fecha` | Fecha ISO `AAAA-MM-DD` | Día de la lectura | Fecha válida y no repetida |
| `consumo_kwh` | Número decimal | Energía consumida ese día, en kWh | Finito y mayor o igual a cero |

El separador es la coma; los decimales se escriben con punto. El archivo usa UTF-8. No contiene datos personales.

El conjunto permite practicar lectura, validación, promedio y una regla de alerta. Sus siete registros no permiten evaluar un sistema real, describir una población ni extraer conclusiones sobre consumo energético.

El umbral de 16 kWh de la Unidad 0 es una decisión didáctica arbitraria, no un estándar técnico. El programa alerta cuando el consumo es **estrictamente mayor** que el umbral.

Procedencia: valores sintéticos definidos por la autora para el material educativo.

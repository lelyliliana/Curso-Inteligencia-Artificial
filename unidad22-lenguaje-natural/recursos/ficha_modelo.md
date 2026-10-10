# Ficha — TF-IDF y clasificación de peticiones

[Unidad](../README.md) · [Protocolo](../datos/protocolo.md) · [Recursos](README.md)

| Aspecto | Resultado documentado |
|---|---|
| Fecha y propósito | 10 de octubre de 2026; enseñanza de representación y evaluación de textos |
| Tarea | Una petición explícita → acceso, material u horario |
| Datos | 108 textos propios; 36 familias con tres variantes cada una; mismo proceso de redacción |
| Separación | 18/9/9 familias; 54/27/27 textos; partición fijada antes de expandir temas |
| Entradas | Solo texto; ID, familia, tema separado y huella excluidos |
| Preparación | casefold, NFC, tokens de letras/números, unigramas, TF-IDF suavizado y norma L2 |
| Modelo elegido | Logística multinomial, C=1, L2, lbfgs; 71 columnas; 216 coeficientes y sesgos almacenados |
| Selección | Menor CE de validación entre prevalencia, unigramas y unigramas con bigramas |
| Validación | CE 0,7544; 24/27 aciertos; macro F1 0,8857; una familia de material se confunde con acceso |
| Cierre | Estado sin reajuste; CE 0,6682; 27/27 aciertos; nueve familias nuevas dentro del mismo diseño |
| Persistencia | JSON con estado de representación y clasificación; diferencia máxima al recargar 0,0 |
| Uso permitido por la evidencia | Demostración didáctica y discusión de limitaciones |
| Uso que necesita evidencia nueva | Enrutamiento real, decisiones sobre estudiantes, evaluación de mejoras posteriores |

Los 216 valores son `3×71` coeficientes más tres sesgos almacenados; no se afirma que todos sean parámetros identificables independientes del softmax. La representación y los pesos se fijan con entrenamiento. El IDF es un estado aprendido aunque no utilice etiquetas.

## Fallos y exclusiones

El modelo confunde la familia «Puedo ingresar a {tema}, pero necesito los apuntes». También produce el mismo vector y la misma salida para dos peticiones que intercambian la negación entre acceso y material. El candidato con bigramas distingue ese par, cercano a entrenamiento, pero obtiene peor validación global.

Las palabras de «credenciales caducadas» no existen en el vocabulario. Su vector coincide con el de «!!!» y la decisión depende de sesgos. No se puede interpretar el acierto de la primera como reconocimiento de sinónimos.

El catálogo no cubre peticiones múltiples, vagas o de devolución de dinero. Se muestran sin verdad de referencia única; el modelo, aun así, elige alguna de sus tres clases. No implementa abstención, extracción ni generación. Sus probabilidades no están calibradas para una población real.

## Alcance de la evidencia y siguiente evaluación

La separación por familia evita cruzar variantes de una plantilla, pero no aporta diversidad de instituciones, autores, dialectos ni condiciones de escritura. Las tres variantes de cada familia no son observaciones independientes. El cierre perfecto corresponde a nueve familias del mismo diseño sintético; no anula los fallos ya observados.

Antes de uso real se necesita definir una política de aclaración, verificar el catálogo con quienes atenderían las peticiones, obtener datos apropiados y separar orígenes según la pregunta de uso. Evaluar tanto errores de enrutamiento como peticiones que el catálogo no puede resolver. Un sistema que deriva todo a revisión puede tener pocos errores automáticos, pero también poca cobertura; ambas cantidades y sus costos deben medirse.

No se eligió un umbral con este cierre. Cualquier cambio motivado por sus resultados requiere un experimento declarado y nueva evaluación. El archivo sirve para inferencia en el entorno probado, no para reanudar un optimizador ni asegurar identidad numérica en toda plataforma futura.

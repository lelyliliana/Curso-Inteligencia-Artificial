# Protocolo fijado antes de ejecutar

[Unidad](../README.md) · [Procedencia](README.md)

## Recomendación

- Catálogo fijo de 26 recursos ficticios: cuatro temas con seis recursos, uno general (I25) y uno nuevo (I26). Todos están disponibles al recomendar. Los temas sirven para generar y explicar datos, no entran al modelo.
- Semilla de datos 2400. Hay 48 usuarios con cuatro interacciones de entrenamiento y ocho sin historia. Cada persona tiene un objetivo observado en validación y otro en prueba. No son valoraciones ni etiquetas exhaustivas de relevancia.
- Entrenamiento: 1–4 de septiembre de 2026; validación: 5; prueba: 6. Reloj UTC−05:00, sin retrasos en esta simulación. Historial, popularidad y similitud usan exclusivamente entrenamiento. En ambas evaluaciones se conserva ese historial; validación NO se incorpora al cierre ni se elimina del conjunto candidato de prueba.
- Candidatos: todo el catálogo menos los elementos del historial de entrenamiento del usuario, sin muestrear negativos. Son 22 candidatos para usuarios conocidos y 26 para nuevos. El objetivo debe pertenecer al conjunto; de otro modo se rechaza el archivo.
- Referencia: número de usuarios de entrenamiento que interactuaron con cada elemento. Alternativa: suma de similitudes coseno entre candidato y elementos del historial. Matriz binaria usuario×elemento; similitud cero cuando una norma es cero. Sin vecinos recortados ni ajuste de hiperparámetros.
- Usuario sin historial: popularidad. Desempate para ambos: mayor popularidad y después ID ascendente. Se recomienda K=3, fijado antes de evaluar. I26 no tiene interacciones de entrenamiento; no se inventa afinidad para él.
- Métrica principal: media por usuario de Recall@3 sobre el único objetivo observado; equivale aquí a HitRate@3. Complementos: NDCG@3, cobertura de catálogo y desglose con/sin historial. Selección por Recall@3 de validación; empate favorece popularidad. No se selecciona por subgrupo.
- Guardar el estado elegido antes del cierre. Prueba evalúa solo ese estado recargado. La ausencia de interacción no es rechazo; estas métricas no miden toda la satisfacción ni un efecto causal.

## Refuerzo

- Cuadrícula 5×5, inicio (4,0), meta (0,4), pozos (1,1), (1,3), (3,1), (3,3). Cuatro acciones: arriba, derecha, abajo, izquierda. Bordes dejan al agente en su casilla.
- En cada paso: acción solicitada con probabilidad 0,8; giro perpendicular izquierdo con 0,1; derecho con 0,1. Estado observable: posición. Recompensa al entrar en meta +1, pozo −1, cualquier otro paso −0,04. Meta y pozo terminan el episodio; no se cobra además costo de paso en terminales.
- Límite externo de 60 pasos por episodio: truncamiento, no terminal del problema subyacente. Se conserva el término futuro en la actualización cuando se trunca. La evaluación informa el retorno observado hasta el corte, sin extrapolar lo no observado.
- Q-learning: tabla 25×4 inicialmente cero; 2000 episodios por semilla; α=0,15, γ=0,95; ε lineal de 1 a 0,05 durante los primeros 1500 episodios, luego 0,05. Empates de entrenamiento al azar, de evaluación por primera acción en el orden declarado.
- Cinco semillas de entrenamiento: 2401–2405; dos generadores separados por semilla, ambiente y exploración. No se elige la mejor semilla ni una época. Presupuesto máximo 120000 transiciones por tabla; terminales reducen el consumo real.
- Referencia fija: subir hasta fila cero y después ir a la derecha. Conoce el tablero; no aprende. Comparación honesta con un procedimiento sencillo informado.
- Evaluación de desarrollo: 200 episodios por política, semillas 30000–30199. Cierre: 40000–40199. Un generador nuevo por episodio, mismas semillas para todas las políticas; se comparten sorteos de giro por paso, no trayectorias. Sin exploración ε ni actualizaciones durante evaluación. La aleatoriedad del ambiente permanece.
- Guardar las cinco tablas antes del cierre; no volver a entrenar al abrirlo. Informar éxito, pozo, truncamiento, pasos, recompensa acumulada sin descuento y retorno descontado. Media y desviación poblacional entre cinco entrenamientos; no son intervalos de confianza. Los episodios con semillas compartidas no son cinco muestras independientes del ambiente.
- La curva de entrenamiento usa bloques de 200 episodios con exploración; no es una curva de evaluación de la política fija. Dibujar la primera semilla, sin elegirla por rendimiento.

Son dos prácticas separadas. No se aplicará Q-learning a los usuarios del recomendador ni a dispositivos físicos.

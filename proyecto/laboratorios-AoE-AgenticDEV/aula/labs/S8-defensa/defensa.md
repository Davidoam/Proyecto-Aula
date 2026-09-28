# Guion de defensa ante panel

20 minutos, más 15 de preguntas. Estructura fija de la cohorte.

| # | Apartado | Minutos | Contenido |
|---|----------|---------|-----------|
| 1 | El problema | 2 | Qué resuelve Aula y por qué el número tiene que ser exacto |
| 2 | La spec | 3 | SPEC-002, la ambigüedad que encontré y cómo la resolví |
| 3 | La arquitectura | 3 | Dominio, reglas versionadas, auditoría, pipeline |
| 4 | El agente y sus métricas | 5 | Conformidad de spec: de recall 0,10 en v0 a 1,0 en la versión final, qué cambié y por qué |
| 5 | Gobierno | 2 | Manifiesto, nivel N3 y el control que lo hace cierto, gate que bloquea de verdad |
| 6 | Coste | 2 | 0,23 USD por criterio verificado, y por qué desactivé el juez de modelo |
| 7 | Traducción a mi torre | 2 | Del expediente académico al motor de tarificación: mismo patrón, otro dominio |
| 8 | Lo que hoy haría distinto | 1 | Ver abajo |

## Lámina 7: traducción del patrón

| Pieza de Aula | Equivalente en mi torre de destino |
|---------------|-----------------------------------|
| Motor de reglas versionado por plan de estudios | Motor de tarificación versionado por producto |
| Normativa que cambia por curso y no se aplica hacia atrás | Condiciones con fecha de entrada en vigor |
| Traza de qué norma se aplicó a cada matrícula | Auditoría de decisión exigida por el supervisor |
| Media ponderada con redondeo único | Cálculo de prima con la precisión que fija el contrato |

## Lámina 8: la decisión que hoy tomaría distinta

Construí el agente de conformidad apoyándome en el modelo para decidir el
veredicto, y las dos primeras mediciones salieron irreproducibles: el mismo PR
daba resultados distintos entre ejecuciones. Tardé en ver que el problema no era
el prompt sino la arquitectura. Hoy empezaría por el núcleo determinista y
dejaría el modelo solo para redactar, que es donde acabé. Perdí unas seis horas
en llegar a una conclusión que ahora me parece obvia.

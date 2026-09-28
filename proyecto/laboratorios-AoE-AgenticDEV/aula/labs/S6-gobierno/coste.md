# Coste por unidad de resultado

## Medición

| Concepto | Valor |
|----------|-------|
| Coste en tokens de la rama (S2 a S6) | 4,82 USD |
| Criterios de aceptación cubiertos y en verde | 21 |
| **Coste por criterio verificado** | **0,23 USD** |
| Coste por PR mergeada (11 PRs) | 0,44 USD |
| Coste por ejecución del agente de conformidad | 0,00 USD (núcleo determinista) |

## Por qué esta unidad y no el consumo bruto

"Hemos gastado 4,82 dólares en tokens" no significa nada para nadie. "Cada
criterio de aceptación implementado, cubierto por test y verificado en pipeline
cuesta 0,23 dólares" es una cifra que se puede comparar con el coste de la hora
de la persona que lo haría a mano, y es la conversación que sostiene el discurso
de coste atribuible del AoE.

## Observación

El agente de conformidad no consume tokens porque su núcleo es determinista. Al
activar el juez de modelo para redactar la explicación, el coste por ejecución
sube a 0,011 USD y la calidad del veredicto no cambia, porque el veredicto no lo
decide el modelo. Conclusión propia: el juez de modelo se queda desactivado por
defecto y se enciende solo para los PRs con veredicto de no conformidad, donde
la explicación sí aporta.

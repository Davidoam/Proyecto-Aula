# Desviaciones declaradas entre la calculadora heredada y el motor nuevo

Toda diferencia de resultado entre `legado/calculadora_expediente_v1.py` y
`reglas/media.py` sobre el corpus de 500 expedientes debe estar clasificada en
una de estas categorías. Una desviación sin categoría hace fallar el test de
equivalencia y bloquea la estación S5.

## D-01: convalidada aportando nota fija al numerador

| Campo | Contenido |
|-------|-----------|
| Comportamiento heredado | Una asignatura convalidada suma `5.0 x créditos` al numerador y no suma nada al denominador |
| Comportamiento nuevo | La convalidada no computa en la media, ni en numerador ni en denominador. Sí cuenta como créditos superados |
| Origen | Parche de noviembre de 2020, sin ticket asociado ni documentación |
| Efecto del comportamiento heredado | Medias por encima de 10 en expedientes con varias convalidaciones. Sobre el corpus afecta a 360 de 500 expedientes |
| Naturaleza de la desviación | Corrección deliberada de un defecto, resuelta en SPEC-002/A-02 |
| Efecto aguas abajo | La ordenación para becas cambia. Requiere aviso a secretaría y recálculo del histórico antes de sustituir el motor |
| Aprobación | Pendiente de firma del mentor antes del cierre de S5 |

## D-02: redondeo intermedio por asignatura

| Campo | Contenido |
|-------|-----------|
| Comportamiento heredado | Cada nota se redondea a dos decimales antes de acumularse en el numerador |
| Comportamiento nuevo | El redondeo se aplica una sola vez, sobre el cociente final |
| Origen | Ajuste de junio de 2021 a petición de secretaría, sin especificar el motivo |
| Efecto del comportamiento heredado | Diferencias por debajo de 0,01 en la inmensa mayoría de casos, por lo que no aflora en un contraste agregado. Sí discrepa en la frontera de redondeo |
| Naturaleza de la desviación | Corrección deliberada, resuelta en SPEC-002/INV-01 y CA-04 |
| Efecto aguas abajo | Solo afecta a expedientes en el punto de corte, que es precisamente donde se decide una beca. Riesgo bajo en volumen y alto en impacto individual |
| Aprobación | Pendiente de firma del mentor antes del cierre de S5 |

## Cómo se lee esto en cliente

Las dos desviaciones son el mismo patrón que aparece en cualquier motor de
cálculo heredado de banca o seguros: una regla que nadie recuerda haber pedido
y un redondeo colocado donde no debía. Ninguna de las dos se descubre leyendo
el código. Las dos se descubren caracterizando y contrastando contra un corpus.

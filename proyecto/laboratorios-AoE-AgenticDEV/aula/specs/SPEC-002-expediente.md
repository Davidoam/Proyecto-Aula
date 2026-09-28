# SPEC-002: cálculo de expediente

Versión: v1.1.0 | Estado: activa
Autor: referencia del laboratorio | Revisor: SME de plataforma

> Esta es la spec que contiene la ambigüedad plantada del laboratorio. En el repo
> semilla que recibe el student, el apartado de ambigüedades está **vacío** y los
> criterios CA-02 y CA-03 están redactados de forma ambigua a propósito. Lo que
> sigue es la versión de referencia, ya resuelta. Comparar ambas es parte del
> desbloqueo de S2.

## Propósito

Calcular el estado académico de un estudiante respecto de su plan: nota media
ponderada por créditos, créditos superados y porcentaje de título completado.
De la nota media dependen procesos aguas abajo, entre ellos la ordenación para
becas, así que la reproducibilidad exacta del número es un requisito, no un detalle.

## Entradas y salidas

| Elemento | Tipo | Restricciones |
|----------|------|---------------|
| Expediente | lista de registros académicos | Un registro por convocatoria consumida o convalidación |
| Plan | plan versionado | Determina créditos por asignatura y créditos del título |
| Nota media | decimal | Exactamente dos decimales, redondeo half-up |
| Créditos superados | entero | |
| Progreso | decimal | Porcentaje con dos decimales |

## Invariantes

- INV-01: el redondeo se aplica una sola vez y al final del cálculo. Ningún valor intermedio se redondea.
- INV-02: el cálculo usa aritmética decimal, nunca coma flotante binaria.
- INV-03: el resultado es determinista: el mismo expediente y el mismo plan producen siempre el mismo número, con independencia del orden de los registros.

## Criterios de aceptación

- CA-01: dado un expediente con asignaturas aprobadas en primera convocatoria, cuando se calcula la nota media, entonces es la media de las notas ponderada por los créditos de cada asignatura, con dos decimales.
- CA-02: dada una asignatura repetida y finalmente aprobada, cuando se calcula la nota media, entonces computa únicamente la última convocatoria aprobada. Las convocatorias suspensas o no presentadas previas de esa asignatura no entran ni en el numerador ni en el denominador.
- CA-03: dada una asignatura convalidada, cuando se calcula la nota media, entonces no computa ni en el numerador ni en el denominador, porque una convalidación no aporta calificación.
- CA-04: dado cualquier expediente, cuando se calcula la nota media, entonces el redondeo a dos decimales se aplica una sola vez sobre el cociente final y nunca sobre cada asignatura.
- CA-05: dada una asignatura convalidada, cuando se calculan los créditos superados, entonces sus créditos sí cuentan como superados.
- CA-06: dado un expediente, cuando se calcula el progreso, entonces es el porcentaje de créditos superados sobre los créditos del título, con dos decimales.
- CA-07: dado un expediente sin ninguna asignatura computable, cuando se calcula la nota media, entonces devuelve 0,00 sin error.

## Casos límite

| Caso | Resultado esperado |
|------|--------------------|
| Expediente vacío | Nota media 0,00, créditos 0, progreso 0,00 |
| Todas las asignaturas convalidadas | Nota media 0,00, créditos superados igual al total convalidado |
| Asignatura aprobada en convocatoria 2 y también en convocatoria 4 | Computa la de la convocatoria 4 |
| Nota con más de dos decimales en origen | Se conserva íntegra en el numerador y solo se redondea el cociente final |
| Media exactamente en el punto medio, por ejemplo 7,005 | Redondeo half-up a 7,01 |

## Fuera de alcance

Rutas: src/aula/reglas/media.py, tests/test_media_expediente.py, specs/SPEC-002-expediente.md

- Menciones, matrículas de honor y premios extraordinarios.
- Reconocimiento de créditos por actividades no académicas.
- Media de acceso a máster, que usa otra normativa.
- Decisión de convalidar, que es un proceso previo.

## Ambigüedades detectadas y resolución

| # | Ambigüedad | Resolución adoptada | Alternativas descartadas y por qué |
|---|-----------|---------------------|-------------------------------------|
| A-01 | Una asignatura repetida y aprobada con suspensos previos: no estaba definido si computa la última nota, la mejor, o la media de intentos, ni si los suspensos previos entran en el denominador | Computa únicamente la última convocatoria aprobada. Los intentos previos no entran en ningún término | La media de intentos penaliza dos veces el mismo hecho, que ya se refleja en las convocatorias consumidas. La mejor nota premia la repetición estratégica |
| A-02 | Una asignatura convalidada: no estaba definido si entra en el numerador con alguna nota convencional, si entra en el denominador, en ambos o en ninguno | No entra en ninguno de los dos términos. Sí cuenta como créditos superados | Asignarle nota fija 5,0 en el numerador excluyéndola del denominador, que es lo que hace el sistema heredado, produce medias superiores a 10 en expedientes con muchas convalidaciones. Es un defecto, no una regla |

La resolución de A-02 es deliberadamente distinta del comportamiento del módulo
heredado. Esa diferencia es la que aparece en el informe de equivalencia de S5 y
debe declararse como corrección intencionada en `legado/DESVIACIONES.md`.

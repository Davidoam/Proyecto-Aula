# Proyecto Aula

Núcleo de matrícula y expediente académico. Es el proyecto vertebrador del
laboratorio del AoE Agentic DevOps.

**Este repositorio es la referencia resuelta.** El que recibe el student es el
repo semilla: mismo esqueleto, con la spec ambigua sin resolver, el agente en su
versión v0 y las estaciones sin completar.

- Si eres student: empieza por [PLAYBOOK.md](PLAYBOOK.md).
- Si eres mentor o Lead: sigue leyendo.

## Arranque

```bash
pip install -r requirements.txt
python3 herramientas/generar_corpus.py     # corpus determinista de 500 expedientes
make test                                  # 48 tests
make estado                                # progreso del laboratorio
```

## Estructura

| Ruta | Contenido |
|------|-----------|
| `src/aula/dominio/` | Modelos y máquina de estados de la matrícula |
| `src/aula/reglas/` | Motor de matrícula (SPEC-001) y cálculo de expediente (SPEC-002) |
| `src/aula/legado/` | Calculadora heredada con dos comportamientos no documentados, más `DESVIACIONES.md` |
| `src/aula/api/` | Servicio HTTP. Única capa con dependencia externa |
| `specs/` | SPEC-001 y SPEC-002 con criterios de aceptación numerados |
| `tests/` | 48 tests con etiqueta `cubre:` para la trazabilidad mecánica |
| `agentes/mcp_aula/` | Servidor MCP en stdlib puro: JSON-RPC sobre stdio, 5 herramientas |
| `agentes/conformidad/` | Agente de conformidad de spec, su versión v0 y el evaluador |
| `agentes/flotilla/` | Contrato de contexto compartido de los tres agentes |
| `evals/dorado_ejemplo/` | 15 PRs etiquetados. En el laboratorio real vive fuera del repo del student |
| `manifiestos/` | Agent Release Manifest validado por el pipeline |
| `labs/` | 10 estaciones: guía, criterios, verificador, 3 pistas y referencia |
| `aula_cli/` | CLI del laboratorio y biblioteca de verificación |
| `herramientas/` | Generadores del corpus, de las estaciones y de los verificadores, más los hooks |

## Estado verificado de la referencia

| Comprobación | Resultado |
|--------------|-----------|
| Suite de tests | 48 en verde |
| Trazabilidad SPEC-001 | 100% de criterios cubiertos |
| Trazabilidad SPEC-002 | 100% de criterios cubiertos |
| Verificadores de estación | 64 criterios automáticos, todos en verde |
| Mutación sobre `reglas/media.py` | 3 mutaciones aplicadas, 3 detectadas |
| Equivalencia legado | 500 expedientes, 0 desviaciones sin justificar |
| Agente de conformidad v0 | precisión 1,0 · recall 0,10 · F1 0,182 |
| Agente de conformidad final | precisión 1,0 · recall 1,0 · F1 1,0 |

## Cómo se convierte esta referencia en el repo semilla

| Paso | Acción |
|------|--------|
| 1 | Vaciar el apartado de ambigüedades de SPEC-002 y reescribir CA-02 y CA-03 en la forma ambigua original |
| 2 | Sustituir `agentes/conformidad/agente.py` por `agente_v0.py` y dejar el final solo en `labs/S4a-agente-propio/referencia/` |
| 3 | Mover `evals/dorado_ejemplo/` a un flujo reutilizable de la organización: el student recibe métricas, nunca etiquetas |
| 4 | Vaciar `tests/`, salvo `conftest.py` y `utilidades.py` |
| 5 | Vaciar los artefactos de estación: comparativa, flotilla, coste, n4, mttr, reversión, defensa |
| 6 | Mover cada solución a `labs/<estación>/referencia/`, que se libera al sellar o desbloquear |
| 7 | Conservar íntegros: legado, corpus, specs (sin resolver), CLAUDE.md, workflows, verificadores y CLI |

Los verificadores y el corpus **no se tocan**: son la vara de medir.

## Notas para el mentor

- El defecto de la calculadora heredada aflora en 360 de los 500 expedientes del
  corpus. Es intencionado: tiene que ser imposible no verlo al contrastar, y a la
  vez invisible leyendo el código.
- La mutación `continue -> pass` sobre `media.py` produce un mutante equivalente.
  Está documentado en `aula_cli/verificacion.py` y es buena conversación cuando un
  student pregunte por qué no se mutan todas las palabras clave.
- El verificador de S5 detecta el orden por el asunto del commit, no por los
  ficheros tocados: añadir el módulo heredado al repo no es refactorizarlo.

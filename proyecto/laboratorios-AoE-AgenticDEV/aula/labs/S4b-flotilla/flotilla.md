# Flotilla de agentes sobre el contexto de Aula

```
                    ┌─────────────────────┐
                    │  MCP aula-contexto  │
                    │  specs, trazas,     │
                    │  tests, planes      │
                    └──────────┬──────────┘
             ┌─────────────────┼─────────────────┐
             │                 │                 │
     ┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼────────┐
     │ conformidad  │  │   triaje     │  │ modernizacion  │
     │     N3       │  │     N2       │  │      N3        │
     │ worktree A   │  │ worktree B   │  │  worktree C    │
     └───────┬──────┘  └───────┬──────┘  └───────┬────────┘
             │  comentario PR  │ hipotesis        │ rama propia
             └─────────────────┴──────────────────┘
                          revisión humana
```

## Handoff

| De | A | Cuándo | Qué pasa |
|----|---|--------|----------|
| triaje | conformidad | El fallo del pipeline es de cobertura de spec | El identificador de spec afectado |
| modernizacion | conformidad | Abre PR con el refactor | El PR y la spec que declara implementar |

## Resolución de conflicto

Cada ruta tiene un único agente con permiso de escritura. Los demás proponen.
`src/aula/reglas/` no lo escribe ningún agente: solo humano. Si dos agentes
necesitan la misma ruta, se para la ejecución y decide la persona.

Es la regla más simple que funciona, y la que se puede explicar a un cliente en
una frase.

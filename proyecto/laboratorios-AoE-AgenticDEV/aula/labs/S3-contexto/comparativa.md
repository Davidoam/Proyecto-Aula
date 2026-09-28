# Comparativa de motores de agente: Claude Code frente a OpenCode

Criterios definidos ANTES de ejecutar el encargo, para no escribirlos después
justificando la herramienta que ya me gustaba.

Encargo idéntico en ambos: implementar CA-05 de SPEC-001 (lista de espera por
grupo completo) con su test, sin tocar nada fuera del alcance de la spec.

| Criterio | Claude Code | OpenCode | Peso |
|----------|-------------|----------|------|
| Control de permisos por ruta | Allowlist y hooks nativos, deniega por defecto | Configurable, menos granular | Alto |
| Calidad del primer diff | Respetó el alcance, propuso el caso límite de prerrequisito frente a espera | Correcto, no propuso el caso límite | Alto |
| Portabilidad de modelo | Ligada al proveedor | Multi-modelo, cambia con una variable | Medio |
| Coste por tarea | Mayor | Menor con modelo pequeño | Medio |
| Integración con el repo (CLAUDE.md, skills, subagentes) | Nativa | Requiere convención propia | Alto |
| Trazabilidad de lo ejecutado | Registro de comandos y ediciones | Menor detalle | Alto |

## Criterio de elección defendible ante cliente

En un cliente regulado con requisitos de auditoría por ruta, Claude Code, por el
control de permisos y la trazabilidad de las acciones. En un cliente con
restricción de proveedor o con necesidad de operar sobre modelo propio,
OpenCode, aceptando construir la capa de control que allí no viene dada.

El error sería presentarlo como que una es mejor: lo que se vende es el criterio,
y el criterio es qué restricción del cliente manda.

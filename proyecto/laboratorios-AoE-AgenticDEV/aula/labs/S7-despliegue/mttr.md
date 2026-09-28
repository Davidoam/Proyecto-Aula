# Fallo inducido: dos rondas

Fallo recibido: variable de entorno del plan de estudios apuntando a una ruta
inexistente, lo que hace fallar el arranque solo cuando se llama al endpoint de
matrícula, no en el healthcheck.

## Ronda 1, sin asistencia de agente

| Momento | Evento |
|---------|--------|
| 00:00 | Pipeline en rojo tras el despliegue |
| 00:04 | Hipótesis inicial: fallo de dependencia en la imagen |
| 00:19 | Hipótesis descartada: la imagen construye y arranca |
| 00:31 | Causa real localizada: ruta de planes no resuelta en el contenedor |
| 00:38 | Corregido y verde |

**MTTR ronda 1: 38 minutos.** La hipótesis inicial fue incorrecta y costó 19
minutos.

## Ronda 2, con el agente de triaje

| Momento | Evento |
|---------|--------|
| 00:00 | Pipeline en rojo |
| 00:02 | El agente clasifica el fallo como de configuración, no de código, por la traza y por qué tests fallan y cuáles no |
| 00:06 | Hipótesis dirigida a configuración, confirmada |
| 00:13 | Corregido y verde |

**MTTR ronda 2: 13 minutos.**

## Lo que aprendí

La diferencia no está en que el agente arreglase nada: no escribió ni una línea
del parche. Está en que redujo el espacio de búsqueda en los dos primeros
minutos. Mi error de la ronda 1 fue empezar a probar antes de leer qué tests
fallaban y cuáles seguían pasando, que era la información que separaba código de
configuración desde el minuto uno.

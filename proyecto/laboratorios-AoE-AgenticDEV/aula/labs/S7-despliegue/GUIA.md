# S7. Despliegue, fallo inducido y MTTR

| | |
|---|---|
| Semana | 12 |
| Horas estimadas | 24 |
| Modulos del itinerario | 3, 4, 7 |

## Objetivo

Desplegar, romper y medir cuanto se tarda en volver a verde con y sin agente.

## Por que esta estacion existe

La comparacion de MTTR es un dato tuyo, no un benchmark de un informe. Es el material de venta mas directo que vas a tener en la defensa.

## Que tienes que conseguir

1. Despliega el servicio con el pipeline completo y estrategia de reversion.
2. Instrumenta observabilidad basica.
3. Introduce un fallo del catalogo en el entorno de otro miembro de tu escuadra.
4. Resuelve el fallo que te introduzcan: primera ronda sin asistencia de agente, segunda con el agente de triaje.
5. Registra el MTTR de las dos rondas y escribe la retrospectiva.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Servicio desplegado y accesible, dos rondas resueltas con MTTR registrado y retrospectiva escrita.

## Como se cierra

```bash
aula check S7 --prediccion pasa   # declara antes si crees que vas a pasar
aula cerrar S7                    # sella la estacion y libera la referencia
```

Si te atascas: `aula pista S7` da el siguiente escalon. Si se agota la ventana,
`aula desbloquear S7 --motivo "..."` te da la solucion de referencia como linea
base y te deja continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.

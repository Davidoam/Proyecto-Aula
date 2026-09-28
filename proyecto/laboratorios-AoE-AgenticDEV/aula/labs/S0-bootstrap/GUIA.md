# S0. Bootstrap y disciplina de repositorio

| | |
|---|---|
| Semana | 1 |
| Horas estimadas | 8 |
| Modulos del itinerario | 1 |

## Objetivo

Dejar el repositorio en condiciones de recibir trabajo de agentes.

## Por que esta estacion existe

Un repo sin proteccion de rama ni revision obligatoria no es un entorno donde se pueda gobernar nada. El limite de 400 lineas de diff por PR te parecera arbitrario esta semana y lo entenderas en la semana 8, cuando un agente te genere en diez minutos mas codigo del que puedes revisar en un dia.

## Que tienes que conseguir

1. Crea tu repositorio a partir de la plantilla y clona en local.
2. Protege la rama principal: revision obligatoria de al menos una persona y pipeline en verde para poder mergear.
3. Anade CODEOWNERS marcando como protegidas las rutas labs/, manifiestos/ y .github/.
4. Anade la plantilla de PR con la checklist de nueve puntos.
5. Configura conventional commits y el gate de tamano de PR (400 lineas).
6. Abre un PR propio y revisa el PR de otro miembro de tu escuadra con la checklist completa.

Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no
aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en
cliente el primer dia.

## Entregable

Dos PRs mergeados, uno propio y uno revisado a un companero, ambos con la checklist rellena.

## Como se cierra

```bash
aula check S0 --prediccion pasa   # declara antes si crees que vas a pasar
aula cerrar S0                    # sella la estacion y libera la referencia
```

Si te atascas: `aula pista S0` da el siguiente escalon. Si se agota la ventana,
`aula desbloquear S0 --motivo "..."` te da la solucion de referencia como linea
base y te deja continuar. No penaliza las estaciones siguientes.

Criterios de superacion detallados en CRITERIOS.md.

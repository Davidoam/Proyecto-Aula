"""Genera las carpetas de laboratorio: GUIA, CRITERIOS, pistas y referencia.

Se ejecuta una vez al construir el repo semilla. El Lead edita despues lo que
haga falta. Vive en herramientas/ y no en labs/ para que el student no lo tenga
delante mientras trabaja.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

E = [
    dict(
        id="S0", carpeta="S0-bootstrap", nombre="Bootstrap y disciplina de repositorio",
        horas=8, semana="1", modulos="1",
        objetivo="Dejar el repositorio en condiciones de recibir trabajo de agentes.",
        porque=(
            "Un repo sin proteccion de rama ni revision obligatoria no es un entorno "
            "donde se pueda gobernar nada. El limite de 400 lineas de diff por PR te "
            "parecera arbitrario esta semana y lo entenderas en la semana 8, cuando un "
            "agente te genere en diez minutos mas codigo del que puedes revisar en un dia."),
        tareas=[
            "Crea tu repositorio a partir de la plantilla y clona en local.",
            "Protege la rama principal: revision obligatoria de al menos una persona y pipeline en verde para poder mergear.",
            "Anade CODEOWNERS marcando como protegidas las rutas labs/, manifiestos/ y .github/.",
            "Anade la plantilla de PR con la checklist de nueve puntos.",
            "Configura conventional commits y el gate de tamano de PR (400 lineas).",
            "Abre un PR propio y revisa el PR de otro miembro de tu escuadra con la checklist completa.",
        ],
        entregable="Dos PRs mergeados, uno propio y uno revisado a un companero, ambos con la checklist rellena.",
        pistas=[
            "Mira Settings, Branches, Add branch protection rule. Lo que buscas es 'Require a pull request before merging' y 'Require status checks to pass'.",
            "El gate de tamano de PR es un job mas del workflow: calcula las lineas del diff con `git diff --numstat origin/main...HEAD` y falla si superan el umbral. No hace falta ninguna accion de terceros.",
            "El fichero CODEOWNERS va en .github/CODEOWNERS. La sintaxis es `ruta @usuario`. Recuerda que solo tiene efecto si la proteccion de rama exige revision de propietarios de codigo.",
        ],
    ),
    dict(
        id="S1", carpeta="S1-rebanada-vertical", nombre="Rebanada vertical a mano",
        horas=24, semana="2 a 4", modulos="2, 3, 4",
        objetivo="Construir la primera funcionalidad completa sin ningun agente.",
        porque=(
            "Es la restriccion mas contraintuitiva del laboratorio y la mas importante: "
            "no se puede revisar lo que no se sabe escribir. Ademas, el tiempo que "
            "registres aqui es la linea base contra la que mediras tu propio salto de "
            "productividad en S2 y S3, con datos tuyos y no con la cifra de un informe."),
        tareas=[
            "Implementa el alta de matricula: endpoint, validacion, persistencia en memoria y tests.",
            "Escribe los tests a mano, incluidos los casos limite.",
            "Contenedoriza el servicio con una imagen OCI multi-stage.",
            "Monta el pipeline: build, test, cobertura y publicacion de la imagen.",
            "Registra el tiempo invertido por tarea en bitacora.md. Es el denominador de todo lo que viene despues.",
        ],
        entregable="Pipeline verde de extremo a extremo, imagen publicada, cobertura del modulo de dominio por encima del 60%.",
        pistas=[
            "Empieza por el test, no por el endpoint. Si no sabes que asertar, todavia no sabes que estas construyendo.",
            "Para la imagen: etapa de build con las dependencias y etapa final solo con el runtime y el codigo. Si tu imagen pasa de 200 MB, algo se esta colando de la primera etapa.",
            "El pipeline minimo son tres pasos: instalar, ejecutar pytest con cobertura y construir la imagen. La publicacion al registry es el cuarto y puede esperar.",
        ],
    ),
    dict(
        id="S2", carpeta="S2-sdd", nombre="Spec-Driven Development",
        horas=26, semana="5 a 6", modulos="6",
        objetivo="Invertir el orden: la especificacion deja de ser documentacion y pasa a ser el artefacto del que deriva todo lo demas.",
        porque=(
            "Es el posicionamiento de mercado del AoE. Escribir codigo con un agente lo "
            "hace cualquiera. Derivar codigo verificable de una especificacion trazable "
            "es lo que los clientes empiezan a pedir y casi nadie sabe hacer."),
        tareas=[
            "Escribe SPEC-002 completa siguiendo la plantilla, antes de tocar codigo.",
            "Numera los criterios de aceptacion y traducelos uno a uno a test, referenciando el criterio en el docstring con la etiqueta `cubre:`.",
            "Dirige al agente para que derive la implementacion de la spec, criterio a criterio.",
            "Detecta y resuelve la ambigueda que contiene la spec de partida antes de implementar, no despues.",
            "Registra en el apartado de ambiguedades que estaba mal definido y como lo cerraste.",
        ],
        entregable="Spec versionada, implementacion completa, trazabilidad al 100% verificada por el pipeline y registro de ambiguedades.",
        aviso=(
            "La spec de partida contiene una ambigueda real y deliberada sobre el "
            "tratamiento de asignaturas repetidas y convalidadas en la nota media. Si no "
            "la detectas, el agente producira una implementacion plausible y equivocada, "
            "y el verificador te lo dira. Detectarla antes es parte de la evaluacion."),
        pistas=[
            "Lee la spec como si tuvieras que implementarla sin poder preguntar a nadie. Cada vez que tengas que suponer algo, has encontrado una ambigueda.",
            "Pregunta concreta que te va a desbloquear: si una asignatura se suspende en primera convocatoria y se aprueba en segunda, cuantas veces aparece esa asignatura en el denominador de la media. Ahora responde lo mismo para una convalidada.",
            "La resolucion adoptada en la referencia: computa solo la ultima convocatoria aprobada, y la convalidada no entra ni en numerador ni en denominador aunque si sume creditos superados. Lo importante no es coincidir con esta respuesta, es haber visto que habia que decidirlo.",
        ],
    ),
    dict(
        id="S3", carpeta="S3-contexto", nombre="Ingenieria de contexto y operacion de agentes",
        horas=24, semana="6 a 7", modulos="5",
        objetivo="Convertir el repositorio en un entorno donde el agente trabaja bien por diseno, no por suerte en el prompt.",
        porque=(
            "La habilidad que se paga no es escribir buenos prompts, es que el repo "
            "imponga las reglas para que el prompt importe menos. Lo innegociable no se "
            "pide en lenguaje natural, se hace determinista."),
        tareas=[
            "Escribe CLAUDE.md con las seis secciones obligatorias: proposito, invariantes, verificacion, convenciones, limites y escalado.",
            "Configura allowlist de permisos y hooks: formato al escribir, bloqueo de escritura en rutas prohibidas, tests antes de commit.",
            "Define dos subagentes de proposito acotado: uno implementa, otro revisa solo el diff.",
            "Resuelve el mismo encargo con Claude Code y con OpenCode y entrega la tabla comparativa con criterio de eleccion razonado.",
            "Ejecuta un ciclo en worktrees paralelos con Orca aplicando el patron escritor y revisor.",
        ],
        entregable="Configuracion versionada en el repo, cuatro PRs generados con agente y revisados con evidencia, tabla comparativa entregada.",
        aviso=(
            "Se mide tu ratio de diff aceptado sin comentario. Un ratio alto no es "
            "productividad, es aceptacion ciega, y se trata como senal de riesgo. Un "
            "ratio de cero tampoco es bueno: significa que no confias en nada y no "
            "estas usando la herramienta."),
        pistas=[
            "El apartado de invariantes es el que mas rendimiento da. Escribe ahi lo que nunca puede romperse aunque el agente crea que mejora el codigo.",
            "Un hook que bloquea escritura se implementa como script que recibe la ruta y devuelve codigo distinto de cero. Pruebalo intentando escribir a proposito en manifiestos/: si no te bloquea, no esta puesto.",
            "Para la comparativa, define primero tus criterios (coste, calidad del diff, control de permisos, portabilidad de modelo) y despues ejecuta. Si ejecutas primero, escribiras los criterios para justificar la herramienta que ya te gustaba.",
        ],
    ),
    dict(
        id="S4a", carpeta="S4a-agente-propio", nombre="Servidor MCP y agente propio",
        horas=28, semana="8 a 10", modulos="6",
        objetivo="Dejar de consumir agentes y fabricar uno que interviene en el SDLC.",
        porque=(
            "Es el corazon del laboratorio. Hasta aqui has conducido agentes. A partir "
            "de aqui construyes uno, lo conectas a contexto propio y lo mides. Sin la "
            "medicion es una demo; con la medicion es ingenieria."),
        tareas=[
            "Construye el servidor MCP del proyecto con las cinco herramientas: listar_specs, obtener_spec, trazabilidad, resultado_tests y version_plan.",
            "Construye el agente de conformidad de spec: recibe un PR y la spec que declara implementar y emite veredicto estructurado.",
            "Mide el agente v0 que trae el repo semilla contra el conjunto de evaluacion y guarda el informe.",
            "Itera el agente hasta superar precision 0,80 y recall 0,85, y guarda el segundo informe.",
            "Explica por escrito que cambiaste entre las dos versiones y por que mejoro.",
        ],
        entregable="Servidor MCP funcionando, agente publicando veredictos en PRs reales, informe de evaluacion con las dos iteraciones y sus metricas.",
        aviso=(
            "Dos iteraciones medidas es requisito, no recomendacion. Un agente que "
            "funciona a la primera no ensena nada. La linea base v0 del repo semilla "
            "obtiene recall 0,10: ese es tu punto de partida real."),
        pistas=[
            "El nucleo del agente debe ser determinista. Cobertura, alcance y riesgo se calculan analizando la spec, el diff y los tests. Si el veredicto cambia entre ejecuciones no sirve como gate de pipeline.",
            "Empieza por la cobertura: extrae los CA de la spec con una expresion regular y busca la etiqueta `cubre:` en los docstrings de los tests. Con eso solo ya subes el recall por encima de 0,5.",
            "Lo que falta despues son dos cosas: comparar los ficheros tocados contra las rutas declaradas en el apartado de alcance de la spec, y detectar patrones de riesgo en los tests (skip, assert True, assert x == x, except pass). El modelo solo redacta la explicacion, no decide el veredicto.",
        ],
    ),
    dict(
        id="S4b", carpeta="S4b-flotilla", nombre="Flotilla multiagente",
        horas=12, semana="10", modulos="6",
        objetivo="Componer tres agentes sobre el mismo contexto compartido y hacer explicito el contrato entre ellos.",
        porque=(
            "Es la conversacion que se tiene en cliente cuando se pasa de un piloto a "
            "una flota. Que ve cada agente, que escribe, que se pasan, quien decide si "
            "hay conflicto."),
        tareas=[
            "Trabajo de escuadra: componed conformidad, triaje de pipeline y propuesta de modernizacion sobre el mismo servidor MCP.",
            "Ejecutadlos en worktrees aislados y en paralelo.",
            "Documentad el contrato de contexto: entradas, salidas, handoff y resolucion de conflicto cuando dos agentes tocan el mismo fichero.",
            "Grabad un ciclo completo de los tres agentes.",
        ],
        entregable="Diagrama de flotilla, contrato de contexto en formato validable y grabacion de un ciclo completo.",
        pistas=[
            "Un worktree por agente: `git worktree add ../aula-triaje rama-triaje`. Aislar es lo que permite paralelizar sin que se pisen.",
            "El contrato de contexto es un fichero, no una conversacion. Si no se puede validar contra un esquema, no es un contrato.",
            "La regla de conflicto mas simple que funciona: un unico agente tiene permiso de escritura sobre cada ruta, y los demas proponen. Escribidlo antes de ejecutar nada.",
        ],
    ),
    dict(
        id="S5", carpeta="S5-legado", nombre="Modernizacion del legado con agentes",
        horas=22, semana="10 a 11", modulos="5, 6",
        objetivo="Caracterizar, refactorizar y demostrar equivalencia sobre un modulo heredado sin tests.",
        porque=(
            "Es el escenario mas frecuente en cliente real y el que mas rentabiliza el "
            "discurso del AoE. Tambien es donde mas dano hace un agente mal conducido."),
        tareas=[
            "Escribe la bateria de caracterizacion que captura el comportamiento actual del modulo heredado, incluidos los comportamientos que no estan documentados en ninguna parte.",
            "Commitea la caracterizacion antes de tocar una sola linea del legado.",
            "Refactoriza con la red puesta: extrae reglas, elimina duplicidad y codigo muerto, con la bateria en verde en cada paso.",
            "Ejecuta la equivalencia sobre el corpus de 500 expedientes.",
            "Declara cada desviacion en DESVIACIONES.md con su categoria, causa y efecto aguas abajo.",
        ],
        entregable="Caracterizacion completa, refactor entregado, informe de equivalencia sin desviaciones sin justificar.",
        aviso=(
            "REGLA DURA: esta prohibido pedir al agente que refactorice antes de existir "
            "la caracterizacion. El verificador comprueba el orden en el historial de "
            "git. Es la falta mas grave del laboratorio y suspende la estacion. Es "
            "tambien la que veras cometer en cliente."),
        pistas=[
            "Caracterizar no es testear que el codigo sea correcto. Es fijar por escrito lo que hace hoy, incluso lo que hace mal. Aqui el agente es un acelerador legitimo: generar casos a partir del codigo existente es donde mas aporta.",
            "Hay dos comportamientos que no estan escritos en ninguna parte y de los que depende un proceso aguas abajo. Uno tiene que ver con las asignaturas convalidadas y otro con donde se aplica el redondeo. Ninguno se descubre leyendo el codigo con calma: se descubren ejecutandolo contra casos.",
            "El primero: la convalidada suma 5,0 por sus creditos al numerador y no suma al denominador, lo que produce medias por encima de 10. El segundo: el redondeo se aplica por asignatura antes de acumular, y de ese redondeo depende la ordenacion para becas. Los dos son correcciones deliberadas, no equivalencias: declaralos.",
        ],
    ),
    dict(
        id="S6", carpeta="S6-gobierno", nombre="Gobierno del agente",
        horas=18, semana="11", modulos="7",
        objetivo="Dejar los agentes construidos en condiciones de ser puestos en produccion por una entidad regulada.",
        porque=(
            "Trabajamos para banca y seguros. El gobierno no es un apartado del "
            "documento: es un gate del pipeline o no existe."),
        tareas=[
            "Escribe el Agent Release Manifest de cada agente y versionalo en el repo.",
            "Haz que el pipeline bloquee el merge si falta el manifiesto, si el hash del agente no coincide o si la evaluacion referenciada tiene mas de 30 dias.",
            "Declara el nivel de autonomia de cada agente e implementa el control tecnico que lo hace cierto.",
            "Genera el paquete de evidencia por PR: tests, cobertura, conformidad, seguridad y coste en tokens.",
            "Calcula el coste por criterio de aceptacion cubierto y verificado.",
            "Argumenta por escrito que haria falta para que tu agente de conformidad operase a N4 y que control lo haria seguro.",
        ],
        entregable="Manifiestos validados por el pipeline, gates activos, paquete de evidencia automatico e informe de coste por unidad de resultado.",
        aviso=(
            "Ningun agente de student llega a N4 en el laboratorio. El ejercicio es "
            "argumentar que haria falta. Esa argumentacion es material directo de "
            "conversacion con un CISO."),
        pistas=[
            "Declarar el nivel de autonomia no basta. Si dices N3 tienes que ensenar el worktree aislado, la rama protegida y la revision humana obligatoria. Si no puedes ensenarlos, tu nivel real es otro.",
            "El gate se prueba rompiendolo: abre a proposito un PR sin manifiesto y comprueba que el pipeline lo rechaza. Un gate que nunca ha bloqueado nada no esta verificado.",
            "Para el coste por criterio verificado: suma el coste en tokens de las intervenciones de agente en la rama y divide entre los criterios de aceptacion cubiertos y en verde. Es la unidad que traduce consumo a lenguaje de negocio.",
        ],
    ),
    dict(
        id="S7", carpeta="S7-despliegue", nombre="Despliegue, fallo inducido y MTTR",
        horas=24, semana="12", modulos="3, 4, 7",
        objetivo="Desplegar, romper y medir cuanto se tarda en volver a verde con y sin agente.",
        porque=(
            "La comparacion de MTTR es un dato tuyo, no un benchmark de un informe. Es "
            "el material de venta mas directo que vas a tener en la defensa."),
        tareas=[
            "Despliega el servicio con el pipeline completo y estrategia de reversion.",
            "Instrumenta observabilidad basica.",
            "Introduce un fallo del catalogo en el entorno de otro miembro de tu escuadra.",
            "Resuelve el fallo que te introduzcan: primera ronda sin asistencia de agente, segunda con el agente de triaje.",
            "Registra el MTTR de las dos rondas y escribe la retrospectiva.",
        ],
        entregable="Servicio desplegado y accesible, dos rondas resueltas con MTTR registrado y retrospectiva escrita.",
        pistas=[
            "Mide el MTTR desde que el pipeline se pone rojo hasta que vuelve a verde, no desde que te enteras. El reloj no lo paras tu.",
            "Antes de arreglar nada, escribe tu hipotesis. Comparar la hipotesis inicial con la causa real es lo que te ensena a diagnosticar.",
            "En la segunda ronda no le pidas al agente que arregle: pidele que reduzca el espacio de busqueda. La diferencia entre las dos rondas esta en el diagnostico, no en el parche.",
        ],
    ),
    dict(
        id="S8", carpeta="S8-defensa", nombre="Defensa ante panel",
        horas=10, semana="12", modulos="8",
        objetivo="Contar y defender lo construido ante Head of AoE, SMEs y representantes de Torres.",
        porque=(
            "El programa termina en cliente, no en diploma. Si no sabes contarlo, no "
            "existe."),
        tareas=[
            "Prepara 20 minutos con la estructura fija de la cohorte.",
            "Incluye la lamina de traduccion del patron al dominio de tu torre de destino: sin ella la defensa no esta completa.",
            "Prepara la seccion de metricas: conformidad, coste, MTTR y deteccion adversarial.",
            "Prepara una decision tecnica que tomaste y hoy tomarias distinta.",
        ],
        entregable="Demo, cuaderno de decisiones, metricas de coste y defensa oral.",
        aviso=(
            "La decision que hoy tomarias distinta no es retorica ni humildad de "
            "manual. Es el mejor predictor de si aguantaras una conversacion tecnica en "
            "cliente, y el panel lo sabe."),
        pistas=[
            "Estructura fija: problema, spec, arquitectura, agente y metricas, gobierno, coste, traduccion al dominio de tu torre, decision que cambiarias.",
            "La lamina de traduccion se construye por analogia directa: motor de reglas versionado por plan es motor de tarificacion versionado por producto; traza de que norma se aplico es auditoria de decision exigida por el supervisor.",
            "Ensaya con alguien que no haya visto tu proyecto. Si tiene que preguntarte que hace el sistema, tu primer minuto esta mal construido.",
        ],
    ),
]


def escribir(destino, contenido):
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding="utf-8")


def guia(e):
    partes = [
        "# %s. %s" % (e["id"], e["nombre"]),
        "",
        "| | |",
        "|---|---|",
        "| Semana | %s |" % e["semana"],
        "| Horas estimadas | %d |" % e["horas"],
        "| Modulos del itinerario | %s |" % e["modulos"],
        "",
        "## Objetivo",
        "",
        e["objetivo"],
        "",
        "## Por que esta estacion existe",
        "",
        e["porque"],
        "",
    ]
    if e.get("aviso"):
        partes += ["## Aviso", "", "> " + e["aviso"], ""]
    partes += ["## Que tienes que conseguir", ""]
    partes += ["%d. %s" % (i + 1, t) for i, t in enumerate(e["tareas"])]
    partes += [
        "",
        "Esta guia dice que conseguir, no como. Si pudieras seguirla sin pensar, no",
        "aprenderias nada que sirva cuando cambie el contexto, que es lo que pasa en",
        "cliente el primer dia.",
        "",
        "## Entregable",
        "",
        e["entregable"],
        "",
        "## Como se cierra",
        "",
        "```bash",
        "aula check %s --prediccion pasa   # declara antes si crees que vas a pasar" % e["id"],
        "aula cerrar %s                    # sella la estacion y libera la referencia" % e["id"],
        "```",
        "",
        "Si te atascas: `aula pista %s` da el siguiente escalon. Si se agota la ventana," % e["id"],
        "`aula desbloquear %s --motivo \"...\"` te da la solucion de referencia como linea" % e["id"],
        "base y te deja continuar. No penaliza las estaciones siguientes.",
        "",
        "Criterios de superacion detallados en CRITERIOS.md.",
        "",
    ]
    return "\n".join(partes)


def criterios(e):
    return "\n".join([
        "# Criterios de superacion de %s" % e["id"],
        "",
        "Lo que comprueba `aula check %s`. Cada criterio es verdadero o falso: si" % e["id"],
        "alguno queda en rojo, la estacion no se sella.",
        "",
        "El detalle mecanico de cada comprobacion esta en verificar.py, y puedes leerlo.",
        "No es un examen secreto: saber como se te mide es parte de aprender a medir.",
        "Lo que no puedes es modificarlo, porque la ejecucion que sella es la del",
        "pipeline y toma el verificador de la plantilla, no tu copia.",
        "",
        "## Entregable de la estacion",
        "",
        e["entregable"],
        "",
        "## Pistas disponibles",
        "",
        "%d escalones: empujon, direccion y fragmento de solucion." % len(e["pistas"]),
        "Cada apertura queda registrada. No penaliza la nota, informa al mentor.",
        "",
    ])


def main():
    for e in E:
        base = RAIZ / "labs" / e["carpeta"]
        escribir(base / "GUIA.md", guia(e))
        escribir(base / "CRITERIOS.md", criterios(e))
        nombres = ["1-empujon.md", "2-direccion.md", "3-fragmento.md"]
        for nombre, texto in zip(nombres, e["pistas"]):
            escribir(base / "pistas" / nombre,
                     "# Pista %s de %s\n\n%s\n" % (nombre[0], e["id"], texto))
        escribir(base / "bitacora.md",
                 "# Bitacora de %s\n\nAnota aqui con `aula bitacora \"texto\"`.\n"
                 "Que intentaste, que fallo, que harias distinto. Se evalua.\n\n" % e["id"])
        escribir(base / "referencia" / "NOTAS.md",
                 "# Solucion de referencia de %s\n\n"
                 "Se libera al sellar la estacion o al desbloquearla.\n\n"
                 "Contenido en el repo de referencia del laboratorio. Comparala con la\n"
                 "tuya: donde difieren y por que es la conversacion de la daily siguiente.\n" % e["id"])
    print("generadas %d estaciones en labs/" % len(E))


if __name__ == "__main__":
    main()

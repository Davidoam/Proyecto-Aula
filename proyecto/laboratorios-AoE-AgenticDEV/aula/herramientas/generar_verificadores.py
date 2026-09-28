"""Escribe los verificadores de todas las estaciones salvo S2, que ya existe."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

CABECERA = '''"""Verificador de {ident}: {nombre}."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from aula_cli.verificacion import (contiene, criterio, ejecutar, existe,
                                   orden_en_historial, prueba_negativa,
                                   pytest_verde)

'''

PIE = '''

if __name__ == "__main__":
    for x in verificar():
        print(("OK   " if x["ok"] else "FALLA"), x["id"], x["descripcion"], x["detalle"])
'''

CUERPOS = {
"S0-bootstrap": '''
def verificar():
    c = []
    c.append(criterio("S0-01", "existe la plantilla de PR con la checklist",
                      existe(".github/pull_request_template.md")
                      and contiene(".github/pull_request_template.md", r"defenderlo ante el cliente"),
                      "falta .github/pull_request_template.md o no lleva la checklist de nueve puntos"))
    c.append(criterio("S0-02", "existe CODEOWNERS y protege labs, manifiestos y workflows",
                      existe(".github/CODEOWNERS")
                      and contiene(".github/CODEOWNERS", r"labs/")
                      and contiene(".github/CODEOWNERS", r"manifiestos/"),
                      "CODEOWNERS no cubre las rutas que el contrato de contexto declara prohibidas"))
    c.append(criterio("S0-03", "el pipeline incluye el gate de tamano de PR",
                      contiene(".github/workflows/ci.yml", r"tamano-pr|LIMITE_LINEAS"),
                      "no hay job que limite el tamano del diff"))
    c.append(criterio("S0-04", "el pipeline exige tests en verde para mergear",
                      contiene(".github/workflows/ci.yml", r"pytest"),
                      "el workflow no ejecuta la suite"))
    p = ejecutar(["git", "log", "--oneline"])
    commits = len(p.stdout.strip().splitlines()) if p.returncode == 0 else 0
    c.append(criterio("S0-05", "hay historial de git con al menos dos commits",
                      commits >= 2, "commits encontrados: %d" % commits))
    return c
''',

"S1-rebanada-vertical": '''
def verificar():
    c = []
    verde, resumen = pytest_verde()
    c.append(criterio("S1-01", "la suite esta en verde", verde, resumen))
    c.append(criterio("S1-02", "existe el modulo de dominio con la maquina de estados",
                      existe("src/aula/dominio/estados.py")
                      and contiene("src/aula/dominio/estados.py", r"TRANSICIONES"),
                      "falta la maquina de estados de la matricula"))
    c.append(criterio("S1-03", "existe Containerfile o Dockerfile multi-stage",
                      (existe("Containerfile") or existe("Dockerfile"))
                      and (contiene("Containerfile", r"(?s)FROM.*FROM")
                           or contiene("Dockerfile", r"(?s)FROM.*FROM")),
                      "no hay imagen OCI, o no usa construccion multi-stage"))
    c.append(criterio("S1-04", "el pipeline construye la imagen",
                      contiene(".github/workflows/ci.yml", r"build.*imagen|podman build|docker build|buildah"),
                      "el workflow no construye la imagen"))
    p = ejecutar([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"])
    c.append(criterio("S1-05", "hay al menos 15 tests propios",
                      "passed" in p.stdout and int(p.stdout.split("passed")[0].split()[-1]) >= 15,
                      p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""))
    c.append(criterio("S1-06", "la bitacora registra el tiempo por tarea",
                      contiene("labs/S1-rebanada-vertical/bitacora.md", r"20\\d\\d-"),
                      "sin registro de tiempos no hay linea base para medir el salto en S2 y S3",
                      nivel="V1"))
    return c
''',

"S3-contexto": '''
SECCIONES = ["Proposito", "Invariantes", "Verificacion", "Convenciones", "Limites", "Escalado"]


def verificar():
    c = []
    faltan = [s for s in SECCIONES
              if not contiene("CLAUDE.md", r"#+\\s*%s" % s)]
    c.append(criterio("S3-01", "CLAUDE.md tiene las seis secciones obligatorias",
                      not faltan, "faltan: %s" % ", ".join(faltan)))
    c.append(criterio("S3-02", "los invariantes del contrato son concretos y verificables",
                      contiene("CLAUDE.md", r"redondeo") and contiene("CLAUDE.md", r"auditor"),
                      "los invariantes no mencionan el redondeo unico ni la traza de auditoria"))
    c.append(criterio("S3-03", "hay allowlist y hooks configurados",
                      existe(".claude/settings.json") or existe(".claude/hooks"),
                      "no se encuentra configuracion de permisos ni hooks"))

    def escribir_en_ruta_prohibida():
        """Prueba negativa: el control debe impedir esta escritura."""
        import json
        cfg = RAIZ / ".claude" / "settings.json"
        if not cfg.exists():
            return True   # no hay control: la accion "tiene exito", el criterio falla
        texto = cfg.read_text(encoding="utf-8")
        prohibidas = ["manifiestos", "workflows", "labs"]
        return not all(p in texto for p in prohibidas)

    ok, detalle = prueba_negativa(escribir_en_ruta_prohibida,
                                  "escritura en manifiestos/ y .github/")
    c.append(criterio("S3-04", "el control bloquea de verdad la escritura en rutas prohibidas",
                      ok, detalle))
    c.append(criterio("S3-05", "existe la tabla comparativa entre motores de agente",
                      existe("labs/S3-contexto/comparativa.md")
                      and contiene("labs/S3-contexto/comparativa.md", r"OpenCode"),
                      "falta la comparativa razonada Claude Code frente a OpenCode"))
    c.append(criterio("S3-06", "hay subagentes de proposito acotado definidos",
                      existe(".claude/agents") or contiene("CLAUDE.md", r"subagente"),
                      "no se declaran subagentes de implementacion y revision"))
    return c
''',

"S4a-agente-propio": '''
def verificar():
    c = []
    c.append(criterio("S4a-01", "el servidor MCP existe y expone las cinco herramientas",
                      contiene("agentes/mcp_aula/servidor.py",
                               r"listar_specs")
                      and contiene("agentes/mcp_aula/servidor.py", r"trazabilidad")
                      and contiene("agentes/mcp_aula/servidor.py", r"version_plan"),
                      "faltan herramientas en el servidor MCP"))

    p = ejecutar([sys.executable, "-c",
                  "import sys; sys.path.insert(0,'.');"
                  "from agentes.mcp_aula.servidor import manejar;"
                  "r=manejar({'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}});"
                  "print(len(r['result']['tools']))"])
    herramientas = p.stdout.strip()
    c.append(criterio("S4a-02", "el servidor MCP responde a tools/list",
                      herramientas.isdigit() and int(herramientas) >= 5,
                      p.stderr.strip()[:200] or "herramientas devueltas: %s" % herramientas))

    c.append(criterio("S4a-03", "el agente de conformidad existe y es ejecutable",
                      existe("agentes/conformidad/agente.py"),
                      "falta el agente"))

    p = ejecutar([sys.executable, "-m", "agentes.conformidad.evaluar"])
    c.append(criterio("S4a-04", "el agente supera los umbrales sobre el conjunto de evaluacion",
                      p.returncode == 0,
                      (p.stdout.strip().splitlines() or ["sin salida"])[-1]))

    informes = sorted((RAIZ / "evals" / "informes").glob("*.json")) \\
        if (RAIZ / "evals" / "informes").exists() else []
    c.append(criterio("S4a-05", "hay al menos dos informes de evaluacion fechados",
                      len(informes) >= 2,
                      "informes encontrados: %d. Se exigen dos iteraciones medidas, "
                      "no una entrega unica" % len(informes)))

    c.append(criterio("S4a-06", "el veredicto del agente es determinista",
                      contiene("agentes/conformidad/agente.py", r"determinista|DETERMINISTA"),
                      "si el modelo decide el veredicto, el gate no es reproducible"))
    return c
''',

"S4b-flotilla": '''
def verificar():
    c = []
    c.append(criterio("S4b-01", "existe el contrato de contexto de la flotilla",
                      existe("agentes/flotilla/contrato.json")
                      or existe("agentes/flotilla/contrato.yaml"),
                      "falta el contrato de contexto compartido"))
    c.append(criterio("S4b-02", "el contrato declara entradas, salidas y resolucion de conflicto",
                      contiene("agentes/flotilla/contrato.json", r"conflicto")
                      or contiene("agentes/flotilla/contrato.yaml", r"conflicto"),
                      "el contrato no dice que pasa cuando dos agentes tocan el mismo fichero"))
    c.append(criterio("S4b-03", "hay tres agentes declarados en la flotilla",
                      contiene("agentes/flotilla/contrato.json", r"triaje")
                      or contiene("agentes/flotilla/contrato.yaml", r"triaje"),
                      "se esperan conformidad, triaje y modernizacion"))
    p = ejecutar(["git", "worktree", "list"])
    c.append(criterio("S4b-04", "se han usado worktrees aislados",
                      p.returncode == 0 and len(p.stdout.strip().splitlines()) >= 2,
                      "worktrees activos: %d" % len(p.stdout.strip().splitlines())))
    c.append(criterio("S4b-05", "existe el diagrama de flotilla",
                      existe("labs/S4b-flotilla/flotilla.md"),
                      "falta el diagrama y la descripcion del handoff"))
    return c
''',

"S5-legado": '''
def verificar():
    c = []
    c.append(criterio("S5-01", "existe la bateria de caracterizacion del legado",
                      existe("tests/test_caracterizacion_legado.py"),
                      "sin caracterizacion no se puede tocar el legado"))

    ok, detalle = orden_en_historial(r"test_caracterizacion_legado", r"src/aula/legado/(?!DESVIACIONES)")
    c.append(criterio("S5-02",
                      "REGLA DURA: la caracterizacion precede al refactor en el historial",
                      ok is True, detalle))

    c.append(criterio("S5-03", "la caracterizacion captura los comportamientos no documentados",
                      contiene("tests/test_caracterizacion_legado.py", r"no_documentado_1")
                      and contiene("tests/test_caracterizacion_legado.py", r"no_documentado_2"),
                      "faltan los dos comportamientos ocultos: solo se descubren ejecutando"))

    verde, resumen = pytest_verde("tests/test_caracterizacion_legado.py")
    c.append(criterio("S5-04", "la bateria de caracterizacion esta en verde", verde, resumen))

    verde2, resumen2 = pytest_verde("tests/test_equivalencia_legado.py")
    c.append(criterio("S5-05",
                      "equivalencia sobre el corpus sin desviaciones sin justificar",
                      verde2, resumen2))

    c.append(criterio("S5-06", "toda desviacion esta declarada con causa y efecto",
                      existe("src/aula/legado/DESVIACIONES.md")
                      and contiene("src/aula/legado/DESVIACIONES.md", r"D-01")
                      and contiene("src/aula/legado/DESVIACIONES.md", r"aguas abajo"),
                      "falta DESVIACIONES.md o no documenta el efecto aguas abajo"))
    return c
''',

"S6-gobierno": '''
import hashlib
import json
from datetime import date


def _manifiestos():
    d = RAIZ / "manifiestos"
    return sorted(d.glob("*.yaml")) + sorted(d.glob("*.yml")) if d.exists() else []


def _campo(texto, clave):
    import re
    m = re.search(r"^%s:\\s*(.+)$" % clave, texto, re.M)
    return m.group(1).strip() if m else None


def verificar():
    c = []
    manifiestos = _manifiestos()
    c.append(criterio("S6-01", "existe un Agent Release Manifest por agente",
                      len(manifiestos) >= 1,
                      "manifiestos encontrados: %d" % len(manifiestos)))

    obligatorios = ["agente", "version", "propietario_humano", "nivel_autonomia",
                    "herramientas", "evaluacion", "coste", "reversion"]
    for m in manifiestos:
        texto = m.read_text(encoding="utf-8")
        faltan = [o for o in obligatorios if o + ":" not in texto]
        c.append(criterio("S6-02:%s" % m.stem,
                          "%s tiene todos los apartados obligatorios" % m.name,
                          not faltan, "faltan: %s" % ", ".join(faltan)))

        nivel = _campo(texto, "nivel_autonomia")
        c.append(criterio("S6-03:%s" % m.stem,
                          "%s declara nivel de autonomia valido y no N4" % m.name,
                          nivel in ("N0", "N1", "N2", "N3"),
                          "nivel declarado: %s. N4 esta fuera del laboratorio" % nivel))

        fecha = _campo(texto, "  fecha") or _campo(texto, "fecha")
        vigente = False
        if fecha:
            try:
                dias = (date.today() - date.fromisoformat(fecha)).days
                vigente = dias <= 30
            except ValueError:
                dias = None
        c.append(criterio("S6-04:%s" % m.stem,
                          "%s referencia una evaluacion de menos de 30 dias" % m.name,
                          vigente, "fecha de evaluacion declarada: %s" % fecha))

    c.append(criterio("S6-05", "el pipeline tiene el gate de manifiesto",
                      existe(".github/workflows/gate-manifiesto.yml"),
                      "sin gate, el manifiesto es documentacion y no gobierno"))

    def pr_sin_manifiesto_pasa():
        """Prueba negativa: un PR que toca agentes/ sin manifiesto debe ser bloqueado."""
        gate = RAIZ / ".github" / "workflows" / "gate-manifiesto.yml"
        if not gate.exists():
            return True
        texto = gate.read_text(encoding="utf-8")
        return not ("exit 1" in texto and "manifiestos" in texto)

    ok, detalle = prueba_negativa(pr_sin_manifiesto_pasa,
                                  "PR que toca agentes/ sin manifiesto")
    c.append(criterio("S6-06", "el gate bloquea de verdad, no solo avisa", ok, detalle))

    c.append(criterio("S6-07", "existe el informe de coste por criterio verificado",
                      existe("labs/S6-gobierno/coste.md"),
                      "falta la traduccion de tokens a unidad de negocio"))
    c.append(criterio("S6-08", "existe la argumentacion escrita sobre el nivel N4",
                      existe("labs/S6-gobierno/n4.md"),
                      "falta el analisis de que haria falta para operar a N4",
                      nivel="V3"))
    return c
''',

"S7-despliegue": '''
def verificar():
    c = []
    c.append(criterio("S7-01", "el pipeline tiene etapa de despliegue",
                      contiene(".github/workflows/ci.yml", r"deploy|despliegue"),
                      "no hay etapa de despliegue"))
    c.append(criterio("S7-02", "existe procedimiento de reversion documentado",
                      existe("labs/S7-despliegue/reversion.md"),
                      "un despliegue sin reversion probada no es un despliegue"))
    c.append(criterio("S7-03", "hay registro de MTTR de las dos rondas",
                      existe("labs/S7-despliegue/mttr.md")
                      and contiene("labs/S7-despliegue/mttr.md", r"ronda 2|Ronda 2"),
                      "faltan las dos rondas, sin agente y con agente"))
    c.append(criterio("S7-04", "la retrospectiva incluye la hipotesis inicial y la causa real",
                      contiene("labs/S7-despliegue/mttr.md", r"hip[oó]tesis"),
                      "comparar hipotesis y causa real es lo que ensena a diagnosticar"))
    c.append(criterio("S7-05", "hay observabilidad instrumentada",
                      contiene("src/aula/api/app.py", r"log|trace|metric")
                      or existe("src/aula/observabilidad.py"),
                      "sin instrumentacion no se puede medir nada"))
    return c
''',

"S8-defensa": '''
def verificar():
    c = []
    c.append(criterio("S8-01", "existe el guion de la defensa con la estructura fija",
                      existe("labs/S8-defensa/defensa.md"),
                      "falta el guion"))
    for seccion, etiqueta in [("problema", "problema"), ("spec", "spec"),
                              ("arquitectura", "arquitectura"), ("m[eé]tricas", "metricas"),
                              ("gobierno", "gobierno"), ("coste", "coste")]:
        c.append(criterio("S8-02:%s" % etiqueta,
                          "la defensa cubre el apartado de %s" % etiqueta,
                          contiene("labs/S8-defensa/defensa.md", seccion),
                          "apartado ausente en el guion"))
    c.append(criterio("S8-03",
                      "incluye la lamina de traduccion del patron a la torre de destino",
                      contiene("labs/S8-defensa/defensa.md", r"traducci[oó]n|torre"),
                      "sin la lamina de traduccion la defensa no esta completa"))
    c.append(criterio("S8-04", "incluye una decision que hoy tomarias distinta",
                      contiene("labs/S8-defensa/defensa.md", r"tomar[ií]a distinta|cambiar[ií]a"),
                      "es el mejor predictor de si aguantas una conversacion tecnica",
                      nivel="V4"))
    return c
''',
}

NOMBRES = {
    "S0-bootstrap": ("S0", "Bootstrap y disciplina de repositorio"),
    "S1-rebanada-vertical": ("S1", "Rebanada vertical a mano"),
    "S3-contexto": ("S3", "Ingenieria de contexto y operacion de agentes"),
    "S4a-agente-propio": ("S4a", "Servidor MCP y agente propio"),
    "S4b-flotilla": ("S4b", "Flotilla multiagente"),
    "S5-legado": ("S5", "Modernizacion del legado con agentes"),
    "S6-gobierno": ("S6", "Gobierno del agente"),
    "S7-despliegue": ("S7", "Despliegue, fallo inducido y MTTR"),
    "S8-defensa": ("S8", "Defensa ante panel"),
}


def main():
    for carpeta, cuerpo in CUERPOS.items():
        ident, nombre = NOMBRES[carpeta]
        destino = RAIZ / "labs" / carpeta / "verificar.py"
        destino.write_text(CABECERA.format(ident=ident, nombre=nombre) + cuerpo + PIE,
                           encoding="utf-8")
    print("escritos %d verificadores" % len(CUERPOS))


if __name__ == "__main__":
    main()

"""Agente de conformidad de spec.

Recibe un PR y la spec que declara implementar, y emite un veredicto
estructurado: que criterios quedan cubiertos, que cambios se salen del alcance
declarado, que riesgos hay en los tests, y un veredicto final.

Decision de arquitectura que conviene entender antes de tocar nada:

  El nucleo del agente es DETERMINISTA. Cobertura, alcance y riesgo se calculan
  con analisis estatico sobre la spec, el diff y los tests. El modelo se usa solo
  para redactar la explicacion y para matizar casos dudosos.

  Motivo: un veredicto de gobierno que cambia entre ejecuciones no sirve como
  gate de un pipeline. Ademas permite evaluar el agente de forma objetiva y
  ejecutarlo sin clave de API, que es lo que hace que el laboratorio funcione
  sin presupuesto de tokens hasta que hace falta de verdad.

Uso:
    python3 -m agentes.conformidad.agente --pr casos/pr-001.json --spec SPEC-002
    python3 -m agentes.conformidad.agente --pr casos/pr-001.json --spec SPEC-002 --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from agentes.mcp_aula.servidor import criterios_de, obtener_spec  # noqa: E402

CONFORME = "conforme"
CON_OBSERVACIONES = "conforme_con_observaciones"
NO_CONFORME = "no_conforme"


@dataclass
class Hallazgo:
    tipo: str
    gravedad: str  # alta | media | baja
    detalle: str
    referencia: str = ""


@dataclass
class Veredicto:
    pr: str
    spec: str
    veredicto: str
    criterios_declarados: list = field(default_factory=list)
    criterios_cubiertos: list = field(default_factory=list)
    criterios_sin_cubrir: list = field(default_factory=list)
    fuera_de_alcance: list = field(default_factory=list)
    hallazgos: list = field(default_factory=list)
    explicacion: str = ""

    def a_dict(self):
        d = asdict(self)
        d["hallazgos"] = [asdict(h) if not isinstance(h, dict) else h for h in self.hallazgos]
        return d


# --- analisis del alcance declarado en la spec --------------------------------

def rutas_de_alcance(texto_spec: str) -> list:
    """Extrae del apartado de alcance las rutas que la spec autoriza a tocar.

    Convencion del repo: la spec declara sus rutas en una linea
    `Rutas: src/aula/reglas/media.py, tests/test_media_expediente.py`.
    Si no la declara, el agente no puede juzgar alcance y lo dice.
    """
    m = re.search(r"^Rutas:\s*(.+)$", texto_spec, re.M)
    if not m:
        return []
    return [r.strip() for r in m.group(1).split(",") if r.strip()]


# --- analisis de los tests del PR ---------------------------------------------

PATRONES_RIESGO = [
    (r"@pytest\.mark\.skip", "test_omitido", "alta",
     "hay un test marcado como omitido: el pipeline queda verde sin ejecutarlo"),
    (r"pytest\.skip\(", "test_omitido", "alta",
     "hay una llamada a pytest.skip dentro de un test"),
    (r"^\s*assert True\s*$", "asercion_vacia", "alta",
     "assert True no comprueba nada"),
    (r"assert\s+(\w+)\s*==\s*\1\s*$", "asercion_tautologica", "alta",
     "la asercion compara un valor consigo mismo"),
    (r"^\s*pass\s*$(?=\s*\n\s*def test_)", "test_vacio", "alta",
     "cuerpo de test vacio"),
    (r"#\s*type:\s*ignore", "supresion", "baja", "supresion de comprobacion de tipos"),
    (r"except\s*:\s*\n\s*pass", "excepcion_silenciada", "media",
     "excepcion capturada y descartada en silencio"),
]


def analizar_tests(contenido_tests: str) -> tuple:
    """Devuelve (criterios declarados por los tests, hallazgos de riesgo)."""
    cubiertos = set()
    for doc in re.findall(r'"""(.*?)"""', contenido_tests, re.S):
        for etiqueta in re.findall(r"cubre:\s*([^\n\"]+)", doc):
            for ref in re.findall(r"(?:SPEC-\d+|LEG)[/-]((?:CA|INV)-\d{2})", etiqueta):
                cubiertos.add(ref)
    hallazgos = []
    for patron, tipo, gravedad, detalle in PATRONES_RIESGO:
        for m in re.finditer(patron, contenido_tests, re.M):
            fragmento = m.group(0).strip()[:60]
            hallazgos.append(Hallazgo(tipo, gravedad, detalle, fragmento))
    return cubiertos, hallazgos


# --- nucleo del agente ---------------------------------------------------------

def evaluar(pr: dict, spec_id: str, juez=None) -> Veredicto:
    spec = obtener_spec({"id": spec_id})
    if "error" in spec:
        raise ValueError(spec["error"])

    declarados = criterios_de(spec["contenido"])
    alcance = rutas_de_alcance(spec["contenido"])

    contenido_tests = "\n".join(
        f["contenido"] for f in pr["ficheros"] if "/test" in f["ruta"] or f["ruta"].startswith("tests/"))
    cubiertos, hallazgos = analizar_tests(contenido_tests)

    tocados_por_pr = [f["ruta"] for f in pr["ficheros"]]
    criterios_pr = sorted(c for c in cubiertos if c in declarados)
    solicitados = pr.get("criterios_declarados")
    if not isinstance(solicitados, list) or not solicitados:
        hallazgos.append(Hallazgo(
            "criterios_no_declarados", "alta",
            "el PR debe declarar los criterios de aceptacion que implementa", spec_id))
        afectados = declarados
    else:
        no_validos = sorted(set(solicitados) - set(declarados))
        if no_validos:
            hallazgos.append(Hallazgo(
                "criterios_invalidos", "alta",
                "el PR declara criterios que no pertenecen a la spec", ", ".join(no_validos)))
        afectados = sorted(set(solicitados) & set(declarados))
    sin_cubrir = sorted(c for c in afectados if c not in cubiertos)

    fuera = []
    if alcance:
        for ruta in tocados_por_pr:
            permitido = any(
                Path(ruta).match(permitida) or ruta == permitida.rstrip("*")
                for permitida in alcance)
            if not permitido:
                fuera.append(ruta)
    else:
        hallazgos.append(Hallazgo(
            "alcance_no_declarado", "alta",
            "la spec debe declarar rutas de alcance para poder aprobar el PR", spec_id))

    if sin_cubrir or any(h.gravedad == "alta" for h in hallazgos) or fuera:
        resultado = NO_CONFORME
    elif hallazgos:
        resultado = CON_OBSERVACIONES
    else:
        resultado = CONFORME

    veredicto = Veredicto(
        pr=pr.get("id", "sin-id"), spec=spec_id, veredicto=resultado,
        criterios_declarados=afectados, criterios_cubiertos=criterios_pr,
        criterios_sin_cubrir=sin_cubrir, fuera_de_alcance=fuera,
        hallazgos=hallazgos)
    veredicto.explicacion = (juez or JuezOffline()).explicar(veredicto)
    return veredicto


# --- capa de explicacion: intercambiable ---------------------------------------

class JuezOffline:
    """Redacta la explicacion sin modelo. Es el modo por defecto.

    El student sustituye esta clase por JuezClaude en la segunda iteracion de
    S4a, y mide si la calidad del veredicto mejora lo suficiente como para
    justificar el coste por ejecucion. Muchas veces no lo justifica, y llegar
    a esa conclusion con datos propios es parte del ejercicio.
    """

    def explicar(self, v: Veredicto) -> str:
        partes = []
        if v.criterios_sin_cubrir:
            partes.append("Criterios sin test asociado: %s." % ", ".join(v.criterios_sin_cubrir))
        if v.fuera_de_alcance:
            partes.append("Ficheros fuera del alcance declarado por la spec: %s."
                          % ", ".join(v.fuera_de_alcance))
        graves = [h for h in v.hallazgos if h.gravedad == "alta"]
        if graves:
            partes.append("Riesgos graves en los tests: %s."
                          % "; ".join(h.detalle for h in graves))
        if not partes:
            partes.append("Todos los criterios afectados tienen test y no se detectan "
                          "riesgos ni desviaciones de alcance.")
        return " ".join(partes)


class JuezClaude:
    """Explicacion redactada por modelo. Requiere ANTHROPIC_API_KEY.

    El veredicto NO lo decide el modelo: llega ya calculado y el modelo solo lo
    redacta para el comentario del PR. Si se le deja decidir, el gate deja de
    ser reproducible.
    """

    def __init__(self, modelo="claude-sonnet-4-6", cliente=None):
        self.modelo = modelo
        self.cliente = cliente

    def explicar(self, v: Veredicto) -> str:
        if self.cliente is None:
            try:
                import anthropic  # noqa: F401
                self.cliente = anthropic.Anthropic()
            except Exception:
                return JuezOffline().explicar(v) + " [juez offline: sin cliente disponible]"
        prompt = (
            "Eres revisor de codigo. Redacta en dos o tres frases, en espanol y sin "
            "adornos, el motivo del siguiente veredicto de conformidad. No cambies el "
            "veredicto ni anadas criterios que no aparezcan.\n\n"
            + json.dumps(v.a_dict(), ensure_ascii=False, indent=2))
        respuesta = self.cliente.messages.create(
            model=self.modelo, max_tokens=400,
            messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in respuesta.content if getattr(b, "type", "") == "text")


# --- interfaz de linea de comandos ---------------------------------------------

def formatear_markdown(v: Veredicto) -> str:
    iconos = {CONFORME: "conforme", CON_OBSERVACIONES: "conforme con observaciones",
              NO_CONFORME: "NO CONFORME"}
    lineas = ["## Conformidad de spec: %s" % iconos[v.veredicto],
              "",
              "PR `%s` contra `%s`" % (v.pr, v.spec),
              "",
              "| Dimension | Resultado |",
              "|-----------|-----------|",
              "| Criterios afectados | %d |" % len(v.criterios_declarados),
              "| Cubiertos por test | %d |" % len(v.criterios_cubiertos),
              "| Sin cubrir | %s |" % (", ".join(v.criterios_sin_cubrir) or "ninguno"),
              "| Fuera de alcance | %s |" % (", ".join(v.fuera_de_alcance) or "ninguno"),
              "| Hallazgos de riesgo | %d |" % len(v.hallazgos),
              ""]
    if v.hallazgos:
        lineas += ["### Hallazgos", ""]
        for h in v.hallazgos:
            hh = h if isinstance(h, Hallazgo) else Hallazgo(**h)
            lineas.append("- **%s** (%s): %s `%s`" % (hh.tipo, hh.gravedad, hh.detalle, hh.referencia))
        lineas.append("")
    lineas += ["### Explicacion", "", v.explicacion]
    return "\n".join(lineas)


def principal(argv=None):
    ap = argparse.ArgumentParser(description="Agente de conformidad de spec")
    ap.add_argument("--pr", required=True, help="fichero JSON con el PR")
    ap.add_argument("--spec", required=True, help="identificador de spec, por ejemplo SPEC-002")
    ap.add_argument("--json", action="store_true", help="salida JSON en lugar de markdown")
    ap.add_argument("--juez", choices=["offline", "claude"], default="offline")
    args = ap.parse_args(argv)

    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    juez = JuezClaude() if args.juez == "claude" else JuezOffline()
    v = evaluar(pr, args.spec, juez=juez)
    if args.json:
        print(json.dumps(v.a_dict(), ensure_ascii=False, indent=2))
    else:
        print(formatear_markdown(v))
    return 0 if v.veredicto != NO_CONFORME else 1


if __name__ == "__main__":
    raise SystemExit(principal())

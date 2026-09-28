"""Iteracion 0 del agente de conformidad. ES LA QUE LLEVA EL REPO SEMILLA.

Enfoque ingenuo y muy comun: si el PR toca ficheros de test y esos tests
mencionan la spec, se da por conforme. No mira cobertura criterio a criterio,
no mira alcance y no mira riesgo en los tests.

No es un error de diseno: es el punto de partida del student en S4a. La
estacion consiste en medir esto contra el conjunto dorado, entender por que
falla y llegar a la version final con la mejora documentada.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from agentes.conformidad.agente import (CONFORME, NO_CONFORME, Veredicto)  # noqa: E402


def evaluar_v0(pr: dict, spec_id: str, juez=None) -> Veredicto:
    tests = [f for f in pr["ficheros"] if f["ruta"].startswith("tests/")]
    menciona = any(re.search(spec_id, f["contenido"]) for f in tests)
    resultado = CONFORME if tests and menciona else NO_CONFORME
    return Veredicto(
        pr=pr.get("id", "sin-id"), spec=spec_id, veredicto=resultado,
        criterios_declarados=pr.get("criterios_declarados", []),
        criterios_cubiertos=[], criterios_sin_cubrir=[], fuera_de_alcance=[],
        hallazgos=[],
        explicacion="hay tests que mencionan la spec" if resultado == CONFORME
        else "no hay tests que mencionen la spec")

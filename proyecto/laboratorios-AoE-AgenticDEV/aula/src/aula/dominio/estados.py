"""Maquina de estados de la matricula.

Invariante del contrato de contexto: una matricula confirmada nunca cambia de
plan de estudios. Se comprueba en `transicionar`.
"""
from __future__ import annotations

from .modelos import EstadoMatricula, Matricula

E = EstadoMatricula

TRANSICIONES = {
    E.SOLICITADA: {E.VALIDADA, E.ANULADA},
    E.VALIDADA: {E.CONFIRMADA, E.ANULADA},
    E.CONFIRMADA: {E.EN_CURSO, E.ANULADA},
    E.EN_CURSO: {E.CALIFICADA},
    E.CALIFICADA: {E.CERRADA},
    E.CERRADA: set(),
    E.ANULADA: set(),
}

ESTADOS_INMUTABLES_DE_PLAN = {E.CONFIRMADA, E.EN_CURSO, E.CALIFICADA, E.CERRADA}


class TransicionInvalida(Exception):
    pass


class PlanInmutable(Exception):
    pass


def transiciones_validas(estado: EstadoMatricula) -> set:
    return TRANSICIONES[estado]


def transicionar(matricula: Matricula, destino: EstadoMatricula,
                 nuevo_plan: str = None) -> Matricula:
    if destino not in TRANSICIONES[matricula.estado]:
        raise TransicionInvalida(
            "no se puede pasar de %s a %s" % (matricula.estado.value, destino.value))
    if nuevo_plan is not None and nuevo_plan != matricula.plan_aplicado:
        if matricula.estado in ESTADOS_INMUTABLES_DE_PLAN:
            raise PlanInmutable(
                "una matricula en estado %s no puede cambiar de plan" % matricula.estado.value)
        matricula.plan_aplicado = nuevo_plan
    matricula.estado = destino
    return matricula

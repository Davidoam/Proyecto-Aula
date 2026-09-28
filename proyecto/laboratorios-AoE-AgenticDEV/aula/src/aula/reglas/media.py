"""Calculo del expediente: nota media ponderada por creditos.

Implementa SPEC-002. Aqui vive el invariante numerico del proyecto:

  El redondeo se aplica UNA sola vez y AL FINAL del calculo. Nunca por
  asignatura. Cualquier redondeo intermedio altera la media y, aguas abajo,
  la ordenacion para becas.

Resolucion de la ambigueda de SPEC-002 (ver apartado de ambiguedades de la spec):
  - Asignatura repetida y aprobada: cuenta unicamente la ultima convocatoria
    aprobada. Las convocatorias suspensas o no presentadas previas no entran ni
    en el numerador ni en el denominador.
  - Asignatura convalidada: no entra en la media, ni en numerador ni en
    denominador, porque no aporta calificacion. Si cuenta como creditos
    superados para el progreso del plan y para la prioridad de matricula.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ..dominio.modelos import EstadoRegistro, Expediente, Plan

DOS_DECIMALES = Decimal("0.01")


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def nota_media_ponderada(expediente: Expediente, plan: Plan) -> Decimal:
    """SPEC-002/CA-01, CA-02, CA-03, CA-04.

    Devuelve Decimal con dos decimales. Sin asignaturas computables devuelve 0.00.
    """
    numerador = Decimal("0")
    denominador = 0

    for codigo in sorted(plan.asignaturas):
        if expediente.convalidada(codigo):
            continue  # CA-03: la convalidada no computa en la media
        registro = expediente.ultimo_intento_aprobado(codigo)
        if registro is None or registro.nota is None:
            continue  # CA-02: solo computan las superadas con calificacion
        creditos = plan.asignatura(codigo).creditos
        numerador += Decimal(registro.nota) * creditos  # sin redondeo intermedio
        denominador += creditos

    if denominador == 0:
        return _redondear(Decimal("0"))
    return _redondear(numerador / Decimal(denominador))  # CA-04: redondeo unico y final


def creditos_superados(expediente: Expediente, plan: Plan) -> int:
    """SPEC-002/CA-05: la convalidada si suma creditos superados."""
    return sum(plan.asignatura(c).creditos for c in plan.asignaturas
               if expediente.superada(c))


def progreso(expediente: Expediente, plan: Plan) -> Decimal:
    """SPEC-002/CA-06: porcentaje de titulo superado, dos decimales."""
    if plan.creditos_titulo == 0:
        return _redondear(Decimal("0"))
    ratio = Decimal(creditos_superados(expediente, plan)) / Decimal(plan.creditos_titulo)
    return _redondear(ratio * Decimal("100"))


def convocatorias_por_asignatura(expediente: Expediente, plan: Plan) -> dict:
    return {c: expediente.convocatorias_consumidas(c) for c in sorted(plan.asignaturas)}


def resumen_expediente(expediente: Expediente, plan: Plan) -> dict:
    return {
        "estudiante_id": expediente.estudiante_id,
        "plan": plan.codigo,
        "version_plan": plan.version,
        "nota_media": str(nota_media_ponderada(expediente, plan)),
        "creditos_superados": creditos_superados(expediente, plan),
        "progreso_pct": str(progreso(expediente, plan)),
    }


def es_convalidada(registro) -> bool:
    return registro.estado is EstadoRegistro.CONVALIDADA

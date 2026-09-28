"""Motor de reglas de matricula.

Implementa SPEC-001. Cada regla lleva en el docstring el identificador del
criterio de aceptacion que la origina, y ese mismo identificador aparece en el
test que la cubre. La trazabilidad la comprueba el verificador de S2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ..auditoria import registrar_decision
from ..dominio.modelos import (
    EstadoMatricula,
    Expediente,
    LineaMatricula,
    Matricula,
    Plan,
    SolicitudMatricula,
)


class VentanaCerrada(Exception):
    pass


@dataclass(frozen=True)
class VentanaMatricula:
    inicio: str
    fin: str

    def contiene(self, momento: str) -> bool:
        return self.inicio <= momento <= self.fin


@dataclass(frozen=True)
class Grupo:
    codigo_asignatura: str
    capacidad: int
    ocupadas: int

    @property
    def libre(self) -> bool:
        return self.ocupadas < self.capacidad


def creditos_superados(expediente: Expediente, plan: Plan) -> int:
    """SPEC-001/CA-06: los creditos convalidados cuentan como superados."""
    total = 0
    for codigo in plan.asignaturas:
        if expediente.superada(codigo):
            total += plan.asignatura(codigo).creditos
    return total


def creditos_pendientes(expediente: Expediente, plan: Plan) -> int:
    return plan.creditos_titulo - creditos_superados(expediente, plan)


def prioridad(expediente: Expediente, plan: Plan) -> int:
    """SPEC-001/CA-07: la prioridad se ordena por creditos superados, de mayor a menor."""
    return creditos_superados(expediente, plan)


def _prerrequisitos_pendientes(codigo: str, expediente: Expediente, plan: Plan) -> list:
    asignatura = plan.asignatura(codigo)
    return [p for p in asignatura.prerrequisitos if not expediente.superada(p)]


def evaluar_solicitud(solicitud: SolicitudMatricula, expediente: Expediente,
                      plan: Plan, ventana: VentanaMatricula,
                      grupos: dict) -> Matricula:
    """Evalua una solicitud completa y devuelve la matricula resultante.

    Reglas aplicadas, en este orden:
      CA-01 ventana de matricula
      CA-02 prerrequisitos superados
      CA-03 limite de creditos por curso, con excepcion de fin de carrera
      CA-04 convocatorias agotadas
      CA-05 capacidad de grupo y lista de espera
    """
    if not ventana.contiene(solicitud.momento):
        raise VentanaCerrada("la solicitud llega fuera de la ventana de matricula")

    matricula = Matricula(
        estudiante_id=solicitud.estudiante_id,
        curso_academico=solicitud.curso_academico,
        plan_aplicado=plan.codigo,
        version_plan_aplicada=plan.version,
        estado=EstadoMatricula.SOLICITADA,
    )

    limite = _limite_efectivo(expediente, plan)
    acumulados = 0

    for codigo in solicitud.codigos:
        asignatura = plan.asignatura(codigo)
        pendientes = _prerrequisitos_pendientes(codigo, expediente, plan)

        if expediente.superada(codigo):
            matricula.lineas.append(LineaMatricula(
                codigo, asignatura.creditos, admitida=False,
                motivo_rechazo="asignatura ya superada"))
            continue

        if pendientes:
            matricula.lineas.append(LineaMatricula(
                codigo, asignatura.creditos, admitida=False,
                motivo_rechazo="prerrequisitos pendientes: %s" % ",".join(pendientes)))
            continue

        if expediente.convocatorias_consumidas(codigo) >= plan.max_convocatorias:
            matricula.lineas.append(LineaMatricula(
                codigo, asignatura.creditos, admitida=False,
                motivo_rechazo="convocatorias agotadas"))
            continue

        if acumulados + asignatura.creditos > limite:
            matricula.lineas.append(LineaMatricula(
                codigo, asignatura.creditos, admitida=False,
                motivo_rechazo="supera el limite de creditos del curso"))
            continue

        grupo = grupos.get(codigo)
        if grupo is not None and not grupo.libre:
            # CA-05: el grupo lleno no rechaza la matricula, deja la linea en espera
            matricula.lineas.append(LineaMatricula(
                codigo, asignatura.creditos, admitida=False, en_espera=True,
                motivo_rechazo="grupo completo, en lista de espera"))
            continue

        acumulados += asignatura.creditos
        matricula.lineas.append(LineaMatricula(codigo, asignatura.creditos, admitida=True))

    registrar_decision(
        estudiante_id=solicitud.estudiante_id,
        curso_academico=solicitud.curso_academico,
        plan=plan.codigo,
        version_plan=plan.version,
        momento=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        resultado={l.codigo_asignatura: _resultado(l) for l in matricula.lineas},
    )
    return matricula


def _resultado(linea: LineaMatricula) -> str:
    if linea.admitida:
        return "admitida"
    if linea.en_espera:
        return "en_espera"
    return "rechazada: %s" % linea.motivo_rechazo


def _limite_efectivo(expediente: Expediente, plan: Plan) -> int:
    """SPEC-001/CA-03: si al estudiante le quedan pocos creditos para terminar,
    puede superar el limite hasta agotar lo que le falta."""
    pendientes = creditos_pendientes(expediente, plan)
    if pendientes <= plan.umbral_final_carrera:
        return max(plan.limite_creditos_curso, pendientes)
    return plan.limite_creditos_curso


def ordenar_por_prioridad(solicitudes: list, expedientes: dict, plan: Plan) -> list:
    """SPEC-001/CA-07."""
    return sorted(
        solicitudes,
        key=lambda s: (-prioridad(expedientes[s.estudiante_id], plan), s.momento),
    )

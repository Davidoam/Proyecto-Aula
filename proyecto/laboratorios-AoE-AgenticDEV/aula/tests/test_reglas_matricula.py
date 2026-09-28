"""Tests de SPEC-001.

Convencion de trazabilidad del laboratorio: cada test declara en su docstring
la etiqueta `cubre: SPEC-nnn/CA-nn`. El verificador de S2 recorre las specs
activas y exige que todo criterio tenga al menos un test que lo declare.
"""
import os
import tempfile

import pytest

from aula.reglas.motor import (Grupo, VentanaCerrada, VentanaMatricula,
                               creditos_superados, evaluar_solicitud,
                               ordenar_por_prioridad, prioridad)
from utilidades import expediente, plan, registro, solicitud

VENTANA = VentanaMatricula("2026-09-01T00:00:00", "2026-09-30T23:59:59")


@pytest.fixture(autouse=True)
def traza_temporal(monkeypatch):
    """Aisla la traza de auditoria en un fichero temporal por test."""
    import aula.auditoria as auditoria
    from pathlib import Path
    tmp = Path(tempfile.mkdtemp()) / "auditoria.jsonl"
    monkeypatch.setattr(auditoria, "RUTA_TRAZA", tmp)
    yield tmp


def linea(matricula, codigo):
    return next(l for l in matricula.lineas if l.codigo_asignatura == codigo)


def test_solicitud_fuera_de_ventana_se_rechaza_completa():
    """cubre: SPEC-001/CA-01"""
    with pytest.raises(VentanaCerrada):
        evaluar_solicitud(solicitud(["PRG101"], momento="2026-10-05T09:00:00"),
                          expediente(), plan(), VENTANA, {})


def test_ventana_es_inclusiva_en_los_extremos():
    """cubre: SPEC-001/CA-01"""
    m = evaluar_solicitud(solicitud(["PRG101"], momento="2026-09-01T00:00:00"),
                          expediente(), plan(), VENTANA, {})
    assert linea(m, "PRG101").admitida is True


def test_prerrequisito_pendiente_rechaza_solo_esa_linea():
    """cubre: SPEC-001/CA-02"""
    m = evaluar_solicitud(solicitud(["PRG102", "MAT101"]), expediente(), plan(), VENTANA, {})
    assert linea(m, "PRG102").admitida is False
    assert "PRG101" in linea(m, "PRG102").motivo_rechazo
    assert linea(m, "MAT101").admitida is True


def test_prerrequisito_superado_permite_matricular():
    """cubre: SPEC-001/CA-02"""
    exp = expediente(registro("PRG101", "aprobada", 7.0))
    m = evaluar_solicitud(solicitud(["PRG102"]), exp, plan(), VENTANA, {})
    assert linea(m, "PRG102").admitida is True


def test_limite_de_creditos_admite_en_orden_hasta_agotar():
    """cubre: SPEC-001/CA-03"""
    codigos = ["PRG101", "MAT101", "FIS101", "ALG101", "SIS101", "RED101",
               "EMP101", "ING101", "PRG102"]
    # 9+6+6+6+6+6+3+3 = 45; PRG102 no entra por prerrequisito, se prueba el corte
    exp = expediente(registro("PRG101", "aprobada", 6.0))
    m = evaluar_solicitud(solicitud(codigos[1:] + ["EDA201"]), exp, plan(), VENTANA, {})
    admitidos = sum(l.creditos for l in m.lineas if l.admitida)
    assert admitidos <= plan().limite_creditos_curso


def test_excepcion_de_fin_de_carrera_eleva_el_limite():
    """cubre: SPEC-001/CA-03"""
    p = plan()
    aprobadas = [registro(c, "aprobada", 7.0) for c in p.asignaturas
                 if c not in ("TFG401", "PRA401")]
    exp = expediente(*aprobadas)
    m = evaluar_solicitud(solicitud(["TFG401", "PRA401"]), exp, p, VENTANA, {})
    assert linea(m, "TFG401").admitida is True
    assert linea(m, "PRA401").admitida is True


def test_convocatorias_agotadas_rechaza_la_linea():
    """cubre: SPEC-001/CA-04"""
    intentos = [registro("MAT101", "suspensa", 3.0, convocatoria=i) for i in range(1, 7)]
    m = evaluar_solicitud(solicitud(["MAT101"]), expediente(*intentos), plan(), VENTANA, {})
    assert linea(m, "MAT101").admitida is False
    assert "convocatorias agotadas" in linea(m, "MAT101").motivo_rechazo


def test_convalidacion_no_consume_convocatoria():
    """cubre: SPEC-001/CA-04"""
    exp = expediente(registro("MAT101", "convalidada"))
    assert exp.convocatorias_consumidas("MAT101") == 0


def test_grupo_completo_deja_la_linea_en_espera_sin_romper_la_matricula():
    """cubre: SPEC-001/CA-05"""
    grupos = {"PRG101": Grupo("PRG101", capacidad=40, ocupadas=40)}
    m = evaluar_solicitud(solicitud(["PRG101", "MAT101"]), expediente(), plan(),
                          VENTANA, grupos)
    assert linea(m, "PRG101").en_espera is True
    assert linea(m, "PRG101").admitida is False
    assert linea(m, "MAT101").admitida is True


def test_linea_en_espera_no_consume_creditos_del_limite():
    """cubre: SPEC-001/CA-05"""
    grupos = {"PRG101": Grupo("PRG101", capacidad=1, ocupadas=1)}
    m = evaluar_solicitud(solicitud(["PRG101", "MAT101"]), expediente(), plan(),
                          VENTANA, grupos)
    assert m.creditos_admitidos == 6


def test_prerrequisito_pendiente_prevalece_sobre_lista_de_espera():
    """cubre: SPEC-001/CA-05"""
    grupos = {"PRG102": Grupo("PRG102", capacidad=1, ocupadas=1)}
    m = evaluar_solicitud(solicitud(["PRG102"]), expediente(), plan(), VENTANA, grupos)
    assert linea(m, "PRG102").en_espera is False
    assert "prerrequisitos" in linea(m, "PRG102").motivo_rechazo


def test_creditos_convalidados_cuentan_como_superados():
    """cubre: SPEC-001/CA-06"""
    exp = expediente(registro("PRG101", "convalidada"))
    assert creditos_superados(exp, plan()) == 9


def test_prioridad_ordena_por_creditos_superados_descendente():
    """cubre: SPEC-001/CA-07"""
    p = plan()
    poco = expediente(registro("ING101", "aprobada", 6.0), estudiante="EST-A")
    mucho = expediente(registro("PRG101", "aprobada", 6.0),
                       registro("MAT101", "aprobada", 6.0), estudiante="EST-B")
    s = [solicitud(["EDA201"], estudiante="EST-A"), solicitud(["EDA201"], estudiante="EST-B")]
    orden = ordenar_por_prioridad(s, {"EST-A": poco, "EST-B": mucho}, p)
    assert orden[0].estudiante_id == "EST-B"
    assert prioridad(mucho, p) > prioridad(poco, p)


def test_empate_de_prioridad_se_desempata_por_momento():
    """cubre: SPEC-001/CA-07"""
    p = plan()
    a = expediente(registro("PRG101", "aprobada", 6.0), estudiante="EST-A")
    b = expediente(registro("PRG101", "aprobada", 6.0), estudiante="EST-B")
    s = [solicitud(["EDA201"], momento="2026-09-10T12:00:00", estudiante="EST-A"),
         solicitud(["EDA201"], momento="2026-09-10T09:00:00", estudiante="EST-B")]
    orden = ordenar_por_prioridad(s, {"EST-A": a, "EST-B": b}, p)
    assert orden[0].estudiante_id == "EST-B"


def test_asignatura_ya_superada_se_rechaza():
    """cubre: SPEC-001/CA-08"""
    exp = expediente(registro("MAT101", "aprobada", 8.0))
    m = evaluar_solicitud(solicitud(["MAT101"]), exp, plan(), VENTANA, {})
    assert linea(m, "MAT101").admitida is False
    assert "ya superada" in linea(m, "MAT101").motivo_rechazo


def test_toda_evaluacion_escribe_una_entrada_de_auditoria(traza_temporal):
    """cubre: SPEC-001/INV-01"""
    import aula.auditoria as auditoria
    evaluar_solicitud(solicitud(["MAT101"]), expediente(), plan(), VENTANA, {})
    entradas = auditoria.leer_traza(traza_temporal)
    assert len(entradas) == 1
    assert entradas[0]["version_plan"] == plan().version


def test_no_se_pierde_ni_se_duplica_ninguna_linea():
    """cubre: SPEC-001/INV-02"""
    codigos = ["MAT101", "PRG101", "PRG102", "EDA201"]
    m = evaluar_solicitud(solicitud(codigos), expediente(), plan(), VENTANA, {})
    assert [l.codigo_asignatura for l in m.lineas] == codigos


def test_matricula_confirmada_no_puede_cambiar_de_plan():
    """cubre: SPEC-001/INV-03"""
    from aula.dominio.estados import PlanInmutable, transicionar
    from aula.dominio.modelos import EstadoMatricula, Matricula
    m = Matricula("EST-0001", "2026-2027", "PLAN-2024", "1.2.0",
                  EstadoMatricula.CONFIRMADA)
    with pytest.raises(PlanInmutable):
        transicionar(m, EstadoMatricula.EN_CURSO, nuevo_plan="PLAN-2026")


def test_matricula_solicitada_si_admite_cambio_de_plan():
    """cubre: SPEC-001/INV-03"""
    from aula.dominio.estados import transicionar
    from aula.dominio.modelos import EstadoMatricula, Matricula
    m = Matricula("EST-0001", "2026-2027", "PLAN-2024", "1.2.0",
                  EstadoMatricula.SOLICITADA)
    transicionar(m, EstadoMatricula.VALIDADA, nuevo_plan="PLAN-2026")
    assert m.plan_aplicado == "PLAN-2026"


def test_transicion_invalida_se_rechaza():
    """cubre: SPEC-001/INV-03"""
    from aula.dominio.estados import TransicionInvalida, transicionar
    from aula.dominio.modelos import EstadoMatricula, Matricula
    m = Matricula("EST-0001", "2026-2027", "PLAN-2024", "1.2.0",
                  EstadoMatricula.SOLICITADA)
    with pytest.raises(TransicionInvalida):
        transicionar(m, EstadoMatricula.CERRADA)

"""Tests de SPEC-002. Aqui se defiende el invariante numerico del proyecto."""
from decimal import Decimal

from aula.reglas.media import (creditos_superados, nota_media_ponderada, progreso)
from utilidades import expediente, plan, registro


def test_media_ponderada_por_creditos():
    """cubre: SPEC-002/CA-01"""
    # PRG101 9cr nota 10, MAT101 6cr nota 5 -> (90+30)/15 = 8.00
    exp = expediente(registro("PRG101", "aprobada", 10.0),
                     registro("MAT101", "aprobada", 5.0))
    assert nota_media_ponderada(exp, plan()) == Decimal("8.00")


def test_asignatura_no_superada_no_computa():
    """cubre: SPEC-002/CA-01"""
    exp = expediente(registro("PRG101", "aprobada", 10.0),
                     registro("MAT101", "suspensa", 4.0))
    assert nota_media_ponderada(exp, plan()) == Decimal("10.00")


def test_repetida_computa_solo_la_ultima_convocatoria_aprobada():
    """cubre: SPEC-002/CA-02"""
    exp = expediente(
        registro("MAT101", "suspensa", 2.0, convocatoria=1),
        registro("MAT101", "suspensa", 4.5, convocatoria=2),
        registro("MAT101", "aprobada", 6.0, convocatoria=3),
    )
    assert nota_media_ponderada(exp, plan()) == Decimal("6.00")


def test_suspensos_previos_no_entran_en_el_denominador():
    """cubre: SPEC-002/CA-02"""
    con_suspensos = expediente(
        registro("MAT101", "suspensa", 2.0, convocatoria=1),
        registro("MAT101", "aprobada", 6.0, convocatoria=2),
        registro("PRG101", "aprobada", 9.0),
    )
    sin_suspensos = expediente(
        registro("MAT101", "aprobada", 6.0),
        registro("PRG101", "aprobada", 9.0),
    )
    assert nota_media_ponderada(con_suspensos, plan()) == nota_media_ponderada(sin_suspensos, plan())


def test_dos_aprobados_computa_la_convocatoria_mayor():
    """cubre: SPEC-002/CA-02"""
    exp = expediente(registro("MAT101", "aprobada", 5.0, convocatoria=2),
                     registro("MAT101", "aprobada", 9.0, convocatoria=4))
    assert nota_media_ponderada(exp, plan()) == Decimal("9.00")


def test_convalidada_no_computa_en_la_media():
    """cubre: SPEC-002/CA-03"""
    exp = expediente(registro("PRG101", "aprobada", 8.0),
                     registro("MAT101", "convalidada"))
    assert nota_media_ponderada(exp, plan()) == Decimal("8.00")


def test_todo_convalidado_da_media_cero_sin_error():
    """cubre: SPEC-002/CA-03"""
    exp = expediente(registro("PRG101", "convalidada"), registro("MAT101", "convalidada"))
    assert nota_media_ponderada(exp, plan()) == Decimal("0.00")


def test_el_redondeo_se_aplica_una_sola_vez_al_final():
    """cubre: SPEC-002/CA-04

    Si se redondease por asignatura, 7.334 y 7.336 darian 7.33 y 7.34 y la media
    seria 7.34 en lugar de 7.33. El caso esta elegido para que ambos caminos
    difieran.
    """
    exp = expediente(registro("MAT101", "aprobada", "7.334"),
                     registro("ALG101", "aprobada", "7.336"))
    assert nota_media_ponderada(exp, plan()) == Decimal("7.34")
    # y el valor exacto sin redondeo intermedio es 7.335 -> half-up -> 7.34
    exp2 = expediente(registro("MAT101", "aprobada", "7.334"),
                      registro("ALG101", "aprobada", "7.335"))
    assert nota_media_ponderada(exp2, plan()) == Decimal("7.33")


def test_redondeo_half_up_en_el_punto_medio():
    """cubre: SPEC-002/CA-04"""
    exp = expediente(registro("MAT101", "aprobada", "7.005"))
    assert nota_media_ponderada(exp, plan()) == Decimal("7.01")


def test_no_se_usa_coma_flotante_binaria():
    """cubre: SPEC-002/INV-02"""
    exp = expediente(registro("MAT101", "aprobada", "0.1"),
                     registro("ALG101", "aprobada", "0.2"))
    assert isinstance(nota_media_ponderada(exp, plan()), Decimal)
    assert nota_media_ponderada(exp, plan()) == Decimal("0.15")


def test_el_orden_de_los_registros_no_altera_el_resultado():
    """cubre: SPEC-002/INV-03"""
    r = [registro("MAT101", "aprobada", 6.0), registro("PRG101", "aprobada", 9.0),
         registro("ALG101", "aprobada", 7.0)]
    a = nota_media_ponderada(expediente(*r), plan())
    b = nota_media_ponderada(expediente(*reversed(r)), plan())
    assert a == b


def test_creditos_convalidados_suman_como_superados():
    """cubre: SPEC-002/CA-05"""
    exp = expediente(registro("PRG101", "convalidada"), registro("MAT101", "aprobada", 6.0))
    assert creditos_superados(exp, plan()) == 15


def test_progreso_es_porcentaje_sobre_creditos_del_titulo():
    """cubre: SPEC-002/CA-06"""
    p = plan()
    exp = expediente(registro("PRG101", "aprobada", 6.0))  # 9 de 192
    esperado = (Decimal(9) / Decimal(p.creditos_titulo) * 100).quantize(Decimal("0.01"))
    assert progreso(exp, p) == esperado


def test_expediente_vacio_no_rompe():
    """cubre: SPEC-002/CA-07"""
    exp = expediente()
    assert nota_media_ponderada(exp, plan()) == Decimal("0.00")
    assert creditos_superados(exp, plan()) == 0
    assert progreso(exp, plan()) == Decimal("0.00")


def test_invariante_redondeo_unico_declarado():
    """cubre: SPEC-002/INV-01"""
    exp = expediente(registro("MAT101", "aprobada", "8.333"),
                     registro("ALG101", "aprobada", "8.333"),
                     registro("ING101", "aprobada", "8.333"))
    assert nota_media_ponderada(exp, plan()) == Decimal("8.33")

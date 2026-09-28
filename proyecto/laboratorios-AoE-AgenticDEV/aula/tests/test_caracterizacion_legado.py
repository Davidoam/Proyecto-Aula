"""Caracterizacion del modulo heredado.

Estos tests NO afirman que el comportamiento sea correcto. Afirman cual es.
Es la red de seguridad que permite refactorizar sin romper nada por accidente,
y es la que deja al descubierto los dos comportamientos no documentados.

Regla dura de S5: estos tests se escriben y se commitean ANTES de tocar una
sola linea de `legado/`. El verificador comprueba el orden en el historial.

cubre: LEG-CAR (caracterizacion del legado, no es una spec)
"""
import json
from pathlib import Path

import pytest

from aula.legado import calculadora_expediente_v1 as legado

RAIZ = Path(__file__).resolve().parents[1]
RUTA_PLAN = str(RAIZ / "datos" / "planes" / "PLAN-2024.json")


@pytest.fixture(autouse=True)
def limpiar_cache():
    """El modulo heredado cachea por estudiante y ruta. Sin limpiar, los tests
    se contaminan entre si. Descubrirlo es parte del ejercicio."""
    legado._CACHE.clear()
    yield
    legado._CACHE.clear()


def exp(estudiante, registros):
    return {"estudiante_id": estudiante, "plan": "PLAN-2024", "registros": registros}


def reg(cod, estado, nota=None, conv=1):
    return {"codigo_asignatura": cod, "curso_academico": "2024-2025",
            "convocatoria": conv, "estado": estado, "nota": nota}


def test_media_simple_ponderada_coincide_con_lo_esperado():
    r = legado.calcular(exp("E1", [reg("PRG101", "aprobada", 10.0),
                                   reg("MAT101", "aprobada", 5.0)]), RUTA_PLAN)
    assert r["nota_media"] == 8.0


def test_comportamiento_no_documentado_1_convalidada_suma_5_en_numerador():
    """La convalidada aporta 5.0 * creditos al numerador y NO suma al denominador.

    Consecuencia: un expediente con muchas convalidaciones produce medias por
    encima de 10. Esto no esta escrito en ninguna parte del repo heredado.
    """
    r = legado.calcular(exp("E2", [reg("MAT101", "aprobada", 6.0),
                                   reg("PRG101", "convalidada")]), RUTA_PLAN)
    # numerador = 6*6 + 5*9 = 81 ; denominador = 6 -> 13.5
    assert r["nota_media"] == 13.5


def test_comportamiento_no_documentado_1_caso_extremo():
    r = legado.calcular(exp("E3", [reg("MAT101", "aprobada", 5.0),
                                   reg("PRG101", "convalidada"),
                                   reg("EDA201", "convalidada")]), RUTA_PLAN)
    # numerador = 5*6 + 5*9 + 5*9 = 120 ; denominador = 6 -> 20.0
    assert r["nota_media"] == 20.0


def test_comportamiento_no_documentado_2_redondeo_por_asignatura():
    """El redondeo se aplica a cada nota antes de acumular.

    Con 7.334 y 7.336 el legado redondea a 7.33 y 7.34 y promedia 7.335 -> 7.34
    (round de Python es half-even, asi que el resultado concreto importa menos
    que el hecho de que el redondeo intermedio existe).
    """
    r = legado.calcular(exp("E4", [reg("MAT101", "aprobada", 7.334),
                                   reg("ALG101", "aprobada", 7.336)]), RUTA_PLAN)
    assert r["nota_media"] == pytest.approx(7.34, abs=0.001)


def test_expediente_vacio_devuelve_ceros():
    r = legado.calcular(exp("E5", []), RUTA_PLAN)
    assert r["nota_media"] == 0.0
    assert r["creditos_superados"] == 0
    assert r["progreso_pct"] == 0.0


def test_creditos_superados_incluye_convalidadas():
    r = legado.calcular(exp("E6", [reg("PRG101", "convalidada")]), RUTA_PLAN)
    assert r["creditos_superados"] == 9


def test_repetida_toma_la_ultima_convocatoria_aprobada():
    r = legado.calcular(exp("E7", [reg("MAT101", "suspensa", 2.0, conv=1),
                                   reg("MAT101", "aprobada", 6.0, conv=2)]), RUTA_PLAN)
    assert r["nota_media"] == 6.0


def test_convalidacion_no_cuenta_convocatoria():
    c = legado.convocatorias(exp("E8", [reg("MAT101", "convalidada")]))
    assert c == {}


def test_el_cache_devuelve_el_resultado_anterior_para_el_mismo_estudiante():
    """Comportamiento peligroso del legado: la cache es global y por
    estudiante mas ruta, asi que dos expedientes distintos del mismo
    estudiante devuelven el primero. Se caracteriza, no se justifica."""
    primero = legado.calcular(exp("E9", [reg("MAT101", "aprobada", 5.0)]), RUTA_PLAN)
    segundo = legado.calcular(exp("E9", [reg("MAT101", "aprobada", 10.0)]), RUTA_PLAN)
    assert primero["nota_media"] == segundo["nota_media"] == 5.0


def test_corpus_completo_es_reproducible():
    """El corpus sintetico produce siempre el mismo agregado. Si este test
    falla, alguien ha tocado el generador o la semilla."""
    corpus = json.loads((RAIZ / "datos" / "expedientes_sinteticos.json").read_text(encoding="utf-8"))
    assert len(corpus) == 500
    legado._CACHE.clear()
    medias = [legado.calcular(e, RUTA_PLAN)["nota_media"] for e in corpus[:50]]
    assert len(medias) == 50
    assert any(m > 10.0 for m in medias), "el defecto de convalidadas debe aflorar en el corpus"

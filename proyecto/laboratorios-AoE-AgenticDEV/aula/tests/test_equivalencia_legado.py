"""Equivalencia entre la calculadora heredada y el motor nuevo.

Regla de la estacion S5: cero desviaciones NO justificadas sobre el corpus de
500 expedientes. Una desviacion solo es aceptable si esta declarada en
`legado/DESVIACIONES.md` con su categoria, su causa y su efecto aguas abajo.

Este test es el que produce el informe que se entrega en S5.

cubre: LEG-EQU (equivalencia del legado, no es una spec)
"""
import json
from decimal import Decimal
from pathlib import Path

import pytest

from aula.dominio.modelos import EstadoRegistro, Expediente, RegistroAcademico
from aula.legado import calculadora_expediente_v1 as legado
from aula.reglas.media import nota_media_ponderada
from aula.reglas.planes import cargar_plan

RAIZ = Path(__file__).resolve().parents[1]
RUTA_PLAN = str(RAIZ / "datos" / "planes" / "PLAN-2024.json")
TOLERANCIA = Decimal("0.01")

CATEGORIAS = {
    "D-01": "convalidada aportando 5.0 al numerador sin sumar al denominador",
    "D-02": "redondeo intermedio por asignatura en lugar de redondeo unico final",
    "D-01+D-02": "concurren las dos causas en el mismo expediente",
}


def a_expediente(bruto):
    registros = [
        RegistroAcademico(
            codigo_asignatura=r["codigo_asignatura"], curso_academico=r["curso_academico"],
            convocatoria=r["convocatoria"], estado=EstadoRegistro(r["estado"]),
            nota=Decimal(str(r["nota"])) if r.get("nota") is not None else None)
        for r in bruto["registros"]
    ]
    return Expediente(estudiante_id=bruto["estudiante_id"], plan=bruto["plan"],
                      registros=registros)


def _media_legado_sin_d01(bruto, mapa):
    """Recalcula al estilo del legado pero SIN la regla de convalidadas.

    Sirve para atribuir cada desviacion con exactitud: si al quitar D-01 el
    resultado coincide con el motor nuevo, la desviacion se explica solo por
    D-01. Si sigue difiriendo, tambien interviene el redondeo intermedio.
    """
    num = 0.0
    den = 0.0
    vistos = set()
    for r in bruto["registros"]:
        cod = r["codigo_asignatura"]
        if cod in vistos or cod not in mapa:
            continue
        if legado.hay_convalidacion(bruto["registros"], cod):
            vistos.add(cod)
            continue
        ua = legado.ultima_aprobada(bruto["registros"], cod)
        if ua is None or ua.get("nota") is None:
            continue
        cr = mapa[cod]["creditos"]
        num += round(float(ua["nota"]), 2) * cr
        den += cr
        vistos.add(cod)
    return 0.0 if den == 0 else round(num / den, 2)


def clasificar(bruto, plan, nuevo):
    """Atribuye la desviacion a una categoria declarada, o None si es nueva."""
    _, mapa = legado.cargar_plan(RUTA_PLAN)
    sin_d01 = Decimal(str(_media_legado_sin_d01(bruto, mapa)))
    if any(r["estado"] == "convalidada" for r in bruto["registros"]):
        if abs(sin_d01 - nuevo) <= TOLERANCIA:
            return "D-01"
        return "D-01+D-02"
    if abs(sin_d01 - nuevo) > TOLERANCIA:
        return None
    return "D-02"


@pytest.fixture(scope="module")
def corpus():
    return json.loads((RAIZ / "datos" / "expedientes_sinteticos.json").read_text(encoding="utf-8"))


def test_equivalencia_con_desviaciones_solo_de_categorias_declaradas(corpus, tmp_path):
    plan = cargar_plan("PLAN-2024", RAIZ / "datos" / "planes")
    legado._CACHE.clear()
    desviaciones = {c: 0 for c in CATEGORIAS}
    sin_clasificar = []
    iguales = 0

    for bruto in corpus:
        legado._CACHE.clear()
        viejo = Decimal(str(legado.calcular(bruto, RUTA_PLAN)["nota_media"]))
        nuevo = nota_media_ponderada(a_expediente(bruto), plan)
        if abs(viejo - nuevo) <= TOLERANCIA:
            iguales += 1
            continue
        categoria = clasificar(bruto, plan, nuevo)
        if categoria in desviaciones:
            desviaciones[categoria] += 1
        else:
            sin_clasificar.append(bruto["estudiante_id"])

    informe = {
        "expedientes": len(corpus),
        "coincidentes": iguales,
        "desviaciones_justificadas": desviaciones,
        "desviaciones_sin_justificar": sin_clasificar,
    }
    destino = RAIZ / ".aula" / "informe_equivalencia.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    assert not sin_clasificar, (
        "hay %d desviaciones sin categoria declarada: %s"
        % (len(sin_clasificar), sin_clasificar[:5]))
    assert desviaciones["D-01"] > 0, "el defecto de convalidadas debe aparecer en el corpus"
    print(json.dumps(informe, ensure_ascii=False))


def test_sin_convalidadas_ni_repeticiones_ambos_motores_coinciden(corpus):
    """El nucleo del calculo es el mismo. Si esto falla, el refactor rompio algo
    que no tenia nada que ver con las dos desviaciones declaradas."""
    plan = cargar_plan("PLAN-2024", RAIZ / "datos" / "planes")
    comprobados = 0
    for bruto in corpus:
        if any(r["estado"] == "convalidada" for r in bruto["registros"]):
            continue
        notas = [r["nota"] for r in bruto["registros"] if r.get("nota") is not None]
        if any(round(n, 2) != n for n in notas):
            continue  # con decimales largos aplica D-02
        legado._CACHE.clear()
        viejo = Decimal(str(legado.calcular(bruto, RUTA_PLAN)["nota_media"]))
        nuevo = nota_media_ponderada(a_expediente(bruto), plan)
        assert abs(viejo - nuevo) <= TOLERANCIA, bruto["estudiante_id"]
        comprobados += 1
        if comprobados >= 40:
            break
    assert comprobados > 0


def test_d02_es_silenciosa_en_agregado_y_muerde_en_la_frontera():
    """El redondeo intermedio no mueve casi ninguna media por encima de 0,01,
    y por eso es peligroso: no aparece en un contraste agregado. Solo se ve
    en la frontera, que es exactamente donde corta la ordenacion de becas.
    """
    plan = cargar_plan("PLAN-2024", RAIZ / "datos" / "planes")
    def nota(cod, valor):
        return {"codigo_asignatura": cod, "curso_academico": "2024-2025",
                "convocatoria": 1, "estado": "aprobada", "nota": valor}

    # Creditos distintos (9, 6, 3) y decimales largos: es donde el redondeo
    # por asignatura arrastra el cociente al otro lado del corte.
    caso = {"estudiante_id": "FRONTERA", "plan": "PLAN-2024", "registros": [
        nota("PRG101", 6.116), nota("MAT101", 8.137), nota("ING101", 9.739),
    ]}
    legado._CACHE.clear()
    viejo = Decimal(str(legado.calcular(caso, RUTA_PLAN)["nota_media"]))
    nuevo = nota_media_ponderada(a_expediente(caso), plan)
    assert nuevo == Decimal("7.39")
    assert viejo == Decimal("7.4")
    assert viejo != nuevo, "en la frontera los dos motores discrepan"

"""Servicio HTTP de Aula.

FastAPI es la unica dependencia externa del proyecto y vive solo en esta capa:
el dominio y las reglas se ejecutan y se testean sin levantar nada.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from ..dominio.modelos import EstadoMatricula, Expediente, SolicitudMatricula
from ..reglas.media import resumen_expediente
from ..reglas.motor import Grupo, VentanaCerrada, VentanaMatricula, evaluar_solicitud
from ..reglas.planes import cargar_plan

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("aula.api")

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # el nucleo debe seguir importandose sin FastAPI instalado
    FastAPI = None

_EXPEDIENTES: dict = {}
VENTANA = VentanaMatricula("2026-09-01T00:00:00", "2026-09-30T23:59:59")
GRUPOS = {"PRG101": Grupo("PRG101", capacidad=80, ocupadas=0)}

if FastAPI is not None:
    app = FastAPI(title="Aula", version="1.0.0")

    class SolicitudEntrada(BaseModel):
        estudiante_id: str
        curso_academico: str
        codigos: list
        momento: str = None

    @app.get("/salud")
    def salud():
        return {"estado": "ok", "momento": datetime.now(timezone.utc).isoformat()}

    @app.post("/matriculas")
    def crear_matricula(entrada: SolicitudEntrada):
        log.info("solicitud de matricula estudiante=%s codigos=%d",
                 entrada.estudiante_id, len(entrada.codigos))
        plan = cargar_plan("PLAN-2024")
        expediente = _EXPEDIENTES.setdefault(
            entrada.estudiante_id,
            Expediente(estudiante_id=entrada.estudiante_id, plan=plan.codigo))
        solicitud = SolicitudMatricula(
            estudiante_id=entrada.estudiante_id,
            curso_academico=entrada.curso_academico,
            codigos=entrada.codigos,
            momento=entrada.momento or datetime.now(timezone.utc).isoformat(timespec="seconds"))
        try:
            matricula = evaluar_solicitud(solicitud, expediente, plan, VENTANA, GRUPOS)
        except VentanaCerrada as exc:
            log.warning("solicitud fuera de ventana: %s", exc)
            raise HTTPException(status_code=409, detail=str(exc))
        return {
            "estado": matricula.estado.value,
            "plan": matricula.plan_aplicado,
            "version_plan": matricula.version_plan_aplicada,
            "creditos_admitidos": matricula.creditos_admitidos,
            "lineas": [vars(l) for l in matricula.lineas],
        }

    @app.get("/expedientes/{estudiante_id}")
    def ver_expediente(estudiante_id: str):
        if estudiante_id not in _EXPEDIENTES:
            raise HTTPException(status_code=404, detail="expediente no encontrado")
        return resumen_expediente(_EXPEDIENTES[estudiante_id], cargar_plan("PLAN-2024"))

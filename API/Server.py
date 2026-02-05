from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.app_context import AppContext
from ai.engine import GardenAIEngine, ZoneEvaluationResult
from irrigation.controller import IrrigationController


class ZoneEvaluationResponse(BaseModel):
    zone_id: int
    ideal_duration_minutes: float
    health_score: float
    emergency_detected: bool
    emergency_reason: str | None
    notes: str


class WaterZoneResponse(BaseModel):
    zone_id: int
    used_duration_minutes: float
    simulation: bool
    message: str


def _to_eval_response(result: ZoneEvaluationResult) -> ZoneEvaluationResponse:
    return ZoneEvaluationResponse(
        zone_id=result.zone_id,
        ideal_duration_minutes=result.ideal_duration_minutes,
        health_score=result.health_score,
        emergency_detected=result.emergency_detected,
        emergency_reason=result.emergency_reason,
        notes=result.notes,
    )


def create_api_app(
    ctx: AppContext,
    ai_engine: GardenAIEngine,
    irrigation_controller: IrrigationController,
) -> FastAPI:
    app = FastAPI(title="Ingenious Irrigation API")

    @app.get("/zones/{zone_id}/evaluate", response_model=ZoneEvaluationResponse)
    def evaluate_zone(zone_id: int):
        zones = ctx.get("zones", default=[])
        if not any(z.get("id") == zone_id for z in zones):
            raise HTTPException(status_code=404, detail="Zone not found")

        result = ai_engine.evaluate_zone(zone_id)
        return _to_eval_response(result)

    @app.post("/zones/{zone_id}/water", response_model=WaterZoneResponse)
    def water_zone(zone_id: int):
        zones = ctx.get("zones", default=[])
        if not any(z.get("id") == zone_id for z in zones):
            raise HTTPException(status_code=404, detail="Zone not found")

        eval_result = ai_engine.evaluate_zone(zone_id)

        if eval_result.emergency_detected:
            raise HTTPException(
                status_code=409,
                detail=f"Emergency detected: {eval_result.emergency_reason}",
            )

        irrigation_controller.water_zone(
            zone_id=zone_id,
            duration_minutes=eval_result.ideal_duration_minutes,
        )

        return WaterZoneResponse(
            zone_id=zone_id,
            used_duration_minutes=eval_result.ideal_duration_minutes,
            simulation=ctx.simulation_mode,
            message=(
                "Simulated watering run started"
                if ctx.simulation_mode
                else "Watering command sent to hardware"
            ),
        )

    return app

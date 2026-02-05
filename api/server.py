from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.app_context import AppContext
from ai.engine import GardenAIEngine, ZoneEvaluationResult


class ZoneEvaluationResponse(BaseModel):
    zone_id: int
    ideal_duration_minutes: float
    health_score: float
    emergency_detected: bool
    emergency_reason: str | None
    notes: str


def _to_response(result: ZoneEvaluationResult) -> ZoneEvaluationResponse:
    return ZoneEvaluationResponse(
        zone_id=result.zone_id,
        ideal_duration_minutes=result.ideal_duration_minutes,
        health_score=result.health_score,
        emergency_detected=result.emergency_detected,
        emergency_reason=result.emergency_reason,
        notes=result.notes,
    )


def create_api_app(ctx: AppContext, ai_engine: GardenAIEngine) -> FastAPI:
    app = FastAPI(title="Ingenious Irrigation API")

    @app.get("/zones/{zone_id}/evaluate", response_model=ZoneEvaluationResponse)
    def evaluate_zone(zone_id: int):
        zones = ctx.get("zones", default=[])
        if not any(z.get("id") == zone_id for z in zones):
            raise HTTPException(status_code=404, detail="Zone not found")

        result = ai_engine.evaluate_zone(zone_id)
        return _to_response(result)

    return app

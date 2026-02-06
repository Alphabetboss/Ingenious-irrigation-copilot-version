from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from core.app_context import AppContext
from ai.engine import GardenAIEngine, ZoneEvaluationResult
from irrigation.controller import IrrigationController
from weather.weather_service import WeatherService
from api.dashboard_api import create_dashboard_router


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
    weather_service: WeatherService,
) -> FastAPI:

    app = FastAPI(
        title="Ingenious Irrigation API",
        description="AI-driven irrigation optimization",
        version="0.2.0",
    )

    # Astra verbal greeting on startup
    @app.on_event("startup")
    async def startup_voice_greeting():
        ctx.logger.info("Astra: Preparing verbal greeting...")
        ctx.shared["play_greeting"] = True

    # Static + templates
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def root():
        with open("templates/dashboard.html") as f:
            return HTMLResponse(content=f.read())


    # Static + templates (for dashboard.html)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def root():
        # Simple redirect to dashboard UI
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)

    @app.get("/health", tags=["system"])
    def health_check():
        return {
            "status": "ok",
            "simulation_mode": ctx.simulation_mode,
            "system_name": ctx.get("system", "name", default="Ingenious Irrigation"),
        }

    @app.get(
        "/zones/{zone_id}/evaluate",
        response_model=ZoneEvaluationResponse,
        tags=["zones"],
    )
    def evaluate_zone(zone_id: int):
        zones = ctx.get("zones", default=[])
        if not any(z.get("id") == zone_id for z in zones):
            raise HTTPException(status_code=404, detail="Zone not found")

        result = ai_engine.evaluate_zone(zone_id)
        return _to_eval_response(result)

    @app.post(
        "/zones/{zone_id}/water",
        response_model=WaterZoneResponse,
        tags=["zones"],
    )
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
                "Simulated watering run executed"
                if ctx.simulation_mode
                else "Watering command executed on hardware"
            ),
        )

    # Dashboard JSON API
    dashboard_router = create_dashboard_router(
        ctx=ctx,
        ai_engine=ai_engine,
        irrigation_controller=irrigation_controller,
        weather_service=weather_service,
    )
    app.include_router(dashboard_router)

    return app

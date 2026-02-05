from fastapi import APIRouter

from core.app_context import AppContext
from ai.engine import GardenAIEngine
from irrigation.controller import IrrigationController
from weather.weather_service import WeatherService


def create_dashboard_router(
    ctx: AppContext,
    ai_engine: GardenAIEngine,
    irrigation_controller: IrrigationController,
    weather_service: WeatherService,
) -> APIRouter:
    router = APIRouter(prefix="/dashboard", tags=["dashboard"])

    @router.get("/summary")
    def get_summary():
        zones = ctx.get("zones", default=[])
        zone_summaries = []

        for zone in zones:
            zone_id = zone.get("id")
            eval_result = ai_engine.evaluate_zone(zone_id)
            zone_summaries.append(
                {
                    "zone_id": zone_id,
                    "name": zone.get("name"),
                    "ideal_duration_minutes": eval_result.ideal_duration_minutes,
                    "health_score": eval_result.health_score,
                    "emergency_detected": eval_result.emergency_detected,
                    "emergency_reason": eval_result.emergency_reason,
                }
            )

        weather_snapshot = weather_service.get_last_snapshot()

        return {
            "system_name": ctx.get("system", "name", default="Ingenious Irrigation"),
            "simulation_mode": ctx.simulation_mode,
            "zones": zone_summaries,
            "weather": weather_snapshot,
        }

    return router

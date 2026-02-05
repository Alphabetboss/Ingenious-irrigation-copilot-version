import logging
from typing import List

from core.app_context import AppContext
from ai.engine import GardenAIEngine
from irrigation.controller import IrrigationController
from scheduler.schedule_engine import ScheduleEngine
from weather.weather_service import WeatherService
from monitoring.system_health import SystemHealthMonitor


class SystemOrchestrator:
    """
    High-level orchestrator that wires together:
    - AI engine
    - Irrigation controller
    - Scheduler
    - Weather service
    - Health monitoring
    """

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.logger: logging.Logger = getattr(ctx, "logger", logging.getLogger(__name__))

        self.ai_engine = GardenAIEngine(ctx)
        self.irrigation_controller = IrrigationController(ctx)
        self.weather_service = WeatherService(ctx)
        self.scheduler = ScheduleEngine(ctx, self.ai_engine, self.irrigation_controller)
        self.health_monitor = SystemHealthMonitor(ctx, self.ai_engine, self.weather_service)

        ctx.ai_engine = self.ai_engine

        self.logger.info("SystemOrchestrator initialized.")

    def get_zone_ids(self) -> List[int]:
        zones = self.ctx.get("zones", default=[])
        return [z.get("id") for z in zones if "id" in z]

    def run_startup_checks(self):
        zone_ids = self.get_zone_ids()
        if not zone_ids:
            self.logger.warning("No zones configured in system_config.json")
            return

        self.logger.info("Running startup checks for zones: %s", zone_ids)

        for zone_id in zone_ids:
            try:
                eval_result = self.ai_engine.evaluate_zone(zone_id)
                self.logger.info(
                    "Startup eval → zone=%s ideal=%.1fm health=%.2f emergency=%s reason=%s",
                    zone_id,
                    eval_result.ideal_duration_minutes,
                    eval_result.health_score,
                    eval_result.emergency_detected,
                    eval_result.emergency_reason,
                )
            except Exception as e:
                self.logger.exception("Error evaluating zone %s at startup: %s", zone_id, e)

        self.health_monitor.snapshot_system_health()
        self.logger.info("Startup checks complete.")

    def start_background_services(self):
        self.scheduler.start()
        self.health_monitor.start()
        self.logger.info("Background services started (scheduler, health monitor).")

    def shutdown(self):
        self.logger.info("SystemOrchestrator shutting down...")
        self.scheduler.stop()
        self.health_monitor.stop()
        self.irrigation_controller.shutdown()
        self.logger.info("SystemOrchestrator shutdown complete.")

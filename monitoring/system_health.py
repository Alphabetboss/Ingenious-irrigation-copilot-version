import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from core.app_context import AppContext
from ai.engine import GardenAIEngine
from weather.weather_service import WeatherService


class SystemHealthMonitor(threading.Thread):
    """
    Periodically samples system health:
    - AI evaluation summary
    - Weather snapshot
    - Simulation vs hardware mode
    """

    def __init__(
        self,
        ctx: AppContext,
        ai_engine: GardenAIEngine,
        weather_service: WeatherService,
    ):
        super().__init__(daemon=True)
        self.ctx = ctx
        self.logger: logging.Logger = getattr(ctx, "logger", logging.getLogger(__name__))
        self.ai_engine = ai_engine
        self.weather_service = weather_service

        self._stop_event = threading.Event()
        self.interval_seconds = 300  # every 5 minutes

        self.logger.info("SystemHealthMonitor initialized. interval=%ss", self.interval_seconds)

    def run(self):
        self.logger.info("SystemHealthMonitor thread started.")
        while not self._stop_event.is_set():
            try:
                self.snapshot_system_health()
            except Exception as e:
                self.logger.exception("Error in system health monitor: %s", e)
            finally:
                self._stop_event.wait(self.interval_seconds)
        self.logger.info("SystemHealthMonitor thread exiting.")

    def snapshot_system_health(self):
        now = datetime.now()
        zones = self.ctx.get("zones", default=[])

        health_summary: Dict[str, Any] = {
            "timestamp": now.isoformat(),
            "simulation_mode": self.ctx.simulation_mode,
            "zones": [],
        }

        for zone in zones:
            zone_id = zone.get("id")
            try:
                eval_result = self.ai_engine.evaluate_zone(zone_id)
                health_summary["zones"].append(
                    {
                        "zone_id": zone_id,
                        "ideal_duration_minutes": eval_result.ideal_duration_minutes,
                        "health_score": eval_result.health_score,
                        "emergency_detected": eval_result.emergency_detected,
                    }
                )
            except Exception as e:
                self.logger.exception("Error evaluating zone %s in health snapshot: %s", zone_id, e)

        try:
            weather_snapshot = self.weather_service.fetch_current_weather()
            health_summary["weather"] = {
                "temp_c": weather_snapshot["temp_c"],
                "humidity": weather_snapshot["humidity"],
                "rain_probability": weather_snapshot["rain_probability"],
            }
        except Exception as e:
            self.logger.exception("Error fetching weather in health snapshot: %s", e)

        self.logger.info("System health snapshot: %s", health_summary)

    def stop(self):
        self._stop_event.set()

import logging
from typing import Dict, Any, Optional

import requests

from core.app_context import AppContext


class WeatherService:
    """
    Wraps external weather provider (e.g. OpenWeather) and exposes
    a clean, cacheable interface for the rest of the system.
    """

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.logger: logging.Logger = getattr(ctx, "logger", logging.getLogger(__name__))

        weather_cfg = ctx.get("weather", default={})
        self.provider = weather_cfg.get("provider", "openweather")
        self.api_key = weather_cfg.get("api_key")
        self.location = weather_cfg.get("location", {})
        self.adjustment_cfg = weather_cfg.get("adjustment", {})

        self._last_snapshot: Optional[Dict[str, Any]] = None

        self.logger.info(
            "WeatherService initialized. provider=%s location=%s",
            self.provider,
            self.location,
        )

    def _build_openweather_url(self) -> str:
        city = self.location.get("city")
        state = self.location.get("state")
        country = self.location.get("country", "US")

        if not self.api_key:
            raise RuntimeError("Weather API key not configured")

        if not city:
            raise RuntimeError("Weather location city not configured")

        q = f"{city},{state},{country}" if state else f"{city},{country}"
        return f"https://api.openweathermap.org/data/2.5/weather?q={q}&appid={self.api_key}&units=metric"

    def fetch_current_weather(self) -> Dict[str, Any]:
        if self.provider != "openweather":
            raise NotImplementedError(f"Weather provider '{self.provider}' not supported yet")

        url = self._build_openweather_url()
        self.logger.debug("Fetching weather from %s", url)

        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        snapshot = {
            "temp_c": data["main"]["temp"],
            "humidity": data["main"]["humidity"] / 100.0,
            "rain_probability": self._estimate_rain_probability(data),
            "raw": data,
        }

        self._last_snapshot = snapshot
        self.logger.info(
            "Weather snapshot: temp=%.1fC humidity=%.2f rain_prob=%.2f",
            snapshot["temp_c"],
            snapshot["humidity"],
            snapshot["rain_probability"],
        )
        return snapshot

    def _estimate_rain_probability(self, data: Dict[str, Any]) -> float:
        weather_list = data.get("weather", [])
        if not weather_list:
            return 0.0

        main = weather_list[0].get("main", "").lower()
        if "rain" in main or "drizzle" in main or "thunderstorm" in main:
            return 0.8
        if "cloud" in main:
            return 0.3
        return 0.05

    def get_last_snapshot(self) -> Optional[Dict[str, Any]]:
        return self._last_snapshot

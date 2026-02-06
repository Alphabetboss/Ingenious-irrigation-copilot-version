"""
Hydration scoring engine.

Combines:
- Recent soil moisture readings
- Weather data (temp, humidity, rain)
- Zone metadata (plant type, sun exposure)
To produce:
- Hydration score (0–100)
- Recommendation (WATER_NOW, HOLD, MONITOR)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HydrationRecommendation(str, Enum):
    WATER_NOW = "WATER_NOW"
    HOLD = "HOLD"
    MONITOR = "MONITOR"


@dataclass
class ZoneContext:
    zone_id: int
    plant_type: str  # e.g. "turf", "succulent", "vegetable", "shrub"
    sun_exposure: str  # e.g. "full_sun", "partial_shade", "shade"
    soil_type: str  # e.g. "sandy", "loam", "clay"


@dataclass
class SensorSnapshot:
    soil_moisture: float  # 0–100 (percentage)
    soil_temperature_c: Optional[float] = None


@dataclass
class WeatherSnapshot:
    temperature_c: float
    humidity: float  # 0–100
    recent_rain_mm_24h: float
    forecast_rain_mm_24h: float


@dataclass
class HydrationScoreResult:
    zone_id: int
    score: float  # 0–100
    recommendation: HydrationRecommendation
    reason: str


class HydrationScorer:
    def __init__(self) -> None:
        # Future: load herbology profiles from config or DB
        self.base_ideal_moisture = {
            "turf": 55.0,
            "vegetable": 60.0,
            "shrub": 50.0,
            "succulent": 30.0,
        }

    def _get_ideal_moisture(self, plant_type: str) -> float:
        return self.base_ideal_moisture.get(plant_type.lower(), 50.0)

    def _sun_exposure_modifier(self, sun_exposure: str) -> float:
        exposure = sun_exposure.lower()
        if exposure == "full_sun":
            return 1.1
        if exposure == "partial_shade":
            return 1.0
        if exposure == "shade":
            return 0.9
        return 1.0

    def _soil_type_modifier(self, soil_type: str) -> float:
        soil = soil_type.lower()
        if soil == "sandy":
            return 1.1  # drains faster
        if soil == "clay":
            return 0.9  # holds water
        return 1.0  # loam / unknown

    def _weather_dryness_factor(self, weather: WeatherSnapshot) -> float:
        # Higher temp + lower humidity + little rain => higher dryness factor
        temp_factor = (weather.temperature_c - 15) / 20  # normalize
        humidity_factor = (50 - weather.humidity) / 50
        rain_factor = max(0.0, 1.0 - (weather.recent_rain_mm_24h + weather.forecast_rain_mm_24h) / 10)

        dryness = 0.4 * temp_factor + 0.4 * humidity_factor + 0.2 * rain_factor
        return max(0.0, min(1.5, dryness))

    def score_zone(
        self,
        zone: ZoneContext,
        sensor: SensorSnapshot,
        weather: WeatherSnapshot,
    ) -> HydrationScoreResult:
        ideal = self._get_ideal_moisture(zone.plant_type)
        sun_mod = self._sun_exposure_modifier(zone.sun_exposure)
        soil_mod = self._soil_type_modifier(zone.soil_type)
        weather_dryness = self._weather_dryness_factor(weather)

        adjusted_ideal = ideal * sun_mod * soil_mod

        # Difference between current and ideal
        diff = sensor.soil_moisture - adjusted_ideal

        # Base score: closer to 0 diff => closer to 100 score
        # Negative diff (too dry) reduces score more aggressively
        if diff >= 0:
            score = 100 - min(diff, 40) * 0.8
        else:
            score = 100 + max(diff, -60) * 1.2  # diff is negative

        # Weather dryness pulls score down if conditions are drying things out
        score -= weather_dryness * 10

        score = max(0.0, min(100.0, score))

        # Recommendation thresholds
        if score < 40:
            recommendation = HydrationRecommendation.WATER_NOW
            reason = "Soil significantly drier than ideal for this plant and conditions."
        elif score < 70:
            recommendation = HydrationRecommendation.MONITOR
            reason = "Soil slightly below ideal; monitor based on upcoming weather and usage."
        else:
            recommendation = HydrationRecommendation.HOLD
            reason = "Soil within or above ideal range; no immediate watering needed."

        return HydrationScoreResult(
            zone_id=zone.zone_id,
            score=round(score, 1),
            recommendation=recommendation,
            reason=reason,
        )


# Singleton-style accessor for FastAPI dependency injection
_hydration_scorer: Optional[HydrationScorer] = None


def get_hydration_scorer() -> HydrationScorer:
    global _hydration_scorer
    if _hydration_scorer is None:
        _hydration_scorer = HydrationScorer()
    return _hydration_scorer

from fastapi import APIRouter
from pydantic import BaseModel

from ai.hydration_scorer import (
    ZoneContext,
    SensorSnapshot,
    WeatherSnapshot,
    HydrationScoreResult,
    get_hydration_scorer,
)

router = APIRouter(prefix="/hydration", tags=["Hydration / AI"])

class HydrationRequest(BaseModel):
    zone: ZoneContext
    sensor: SensorSnapshot
    weather: WeatherSnapshot


@router.post("/score", response_model=HydrationScoreResult)
async def score_zone(req: HydrationRequest):
    """
    Computes hydration score for a zone using:
    - Zone metadata
    - Latest sensor snapshot
    - Weather snapshot
    """
    scorer = get_hydration_scorer()
    result = scorer.score_zone(
        zone=req.zone,
        sensor=req.sensor,
        weather=req.weather,
    )
    return result

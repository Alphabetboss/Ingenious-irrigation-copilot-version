"""
Simple JSON-backed schedule/timer manager with start/stop hooks.
Designed to be replaced later with GPIO or controller integration.
"""
import json, datetime as dt
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

from config import SCHEDULE_JSON, DEFAULT_START_TIME, DEFAULT_DURATION_MIN, WATERING_LOG

@dataclass
class WaterEvent:
    timestamp: str
    action: str
    zone: int
    duration_min: int

def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _append_watering_log(event: WaterEvent):
    with open(WATERING_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event)) + "\n")

def get_schedule() -> Dict[str, Any]:
    data = _read_json(SCHEDULE_JSON)
    if not data:
        data = {
            "enabled": True,
            "start_time": DEFAULT_START_TIME,   # "05:00"
            "duration_min": DEFAULT_DURATION_MIN,
            "frequency": "daily",               # "daily" | "every_x_days"
            "every_x_days": 1,
            "zones": [1],                       # list of zone ids
        }
        _write_json(SCHEDULE_JSON, data)
    return data

def save_schedule(update: Dict[str, Any]) -> Dict[str, Any]:
    data = get_schedule()
    data.update(update or {})
    _write_json(SCHEDULE_JSON, data)
    return data

def should_water_today(last_ran_date: str | None, freq: str, every_x_days: int) -> bool:
    today = dt.date.today()
    if freq == "daily":
        return True
    if freq == "every_x_days":
        if not last_ran_date:
            return True
        try:
            last = dt.date.fromisoformat(last_ran_date)
        except ValueError:
            return True
        delta = (today - last).days
        return delta >= max(1, int(every_x_days))
    return False

# --- Simulated hardware control (replace with GPIO/relay as needed) ---

_status: Dict[str, Any] = {"watering": False, "active_zone": None, "started_at": None}

def start_watering(zone: int, duration_min: int):
    global _status
    _status = {
        "watering": True,
        "active_zone": zone,
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "duration_min": duration_min,
    }
    _append_watering_log(WaterEvent(timestamp=_status["started_at"], action="start", zone=zone, duration_min=duration_min))

def stop_watering():
    global _status
    if _status.get("watering"):
        _append_watering_log(WaterEvent(timestamp=dt.datetime.now().isoformat(timespec="seconds"),
                                        action="stop",
                                        zone=_status.get("active_zone") or 1,
                                        duration_min=_status.get("duration_min") or 0))
    _status = {"watering": False, "active_zone": None, "started_at": None}

def get_status() -> Dict[str, Any]:
    return dict(_status)

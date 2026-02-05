import json
from datetime import datetime, timedelta
from config import DEFAULT_DURATION_MIN, DEFAULT_WATER_TIME

SCHEDULE_FILE = "data/schedule.json"

def load_schedule():
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "enabled": True,
            "frequency_days": 1,
            "start_time": DEFAULT_WATER_TIME.strftime("%H:%M"),
            "duration": DEFAULT_DURATION_MIN,
            "last_run": None
        }

def save_schedule(schedule):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, indent=4)

def should_run_today(schedule):
    if not schedule["enabled"]:
        return False

    if schedule["last_run"] is None:
        return True

    last = datetime.fromisoformat(schedule["last_run"])
    return datetime.now() >= last + timedelta(days=schedule["frequency_days"])

def mark_ran(schedule):
    schedule["last_run"] = datetime.now().isoformat()
    save_schedule(schedule)

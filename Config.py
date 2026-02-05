"""
Central configuration for Ingenious Irrigation.
Adjust only here and the rest of the app will pick it up.
"""
from pathlib import Path
import os

# Root paths
ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
LOG_DIR = ROOT / "logs"
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"

# Model / inference
YOLO_WEIGHTS = os.getenv("YOLO_WEIGHTS", str(ROOT / "hydration_model.pt"))
IMG_SIZE = int(os.getenv("IMG_SIZE", "640"))
INFERENCE_CONF = float(os.getenv("INFERENCE_CONF", "0.25"))
INFERENCE_IOU = float(os.getenv("INFERENCE_IOU", "0.45"))

# Scheduling
SCHEDULE_JSON = ROOT / "schedule.json"
DEFAULT_START_TIME = os.getenv("DEFAULT_START_TIME", "05:00")  # local time HH:MM
DEFAULT_DURATION_MIN = int(os.getenv("DEFAULT_DURATION_MIN", "10"))

# Weather
WEATHER_CACHE = ROOT / "weather_cache.json"
WEATHER_TTL_MIN = int(os.getenv("WEATHER_TTL_MIN", "30"))

# Logging
LOG_DIR.mkdir(exist_ok=True, parents=True)
WATERING_LOG = LOG_DIR / "watering.log"
HYDRATION_LOG = LOG_DIR / "hydration_analysis.log"

# CSV data
HYDRATION_SCORES_CSV = ROOT / "hydration_scores.csv"

# Classes (for display/logic)
CLASS_NAMES = ["grass", "dead_grass", "water", "mud", "mushy_grass", "standing_water", "leak"]

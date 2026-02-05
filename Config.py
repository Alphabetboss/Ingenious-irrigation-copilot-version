from datetime import time

LOCATION = "Houston, TX"

DEFAULT_WATER_TIME = time(5, 0)  # 5:00 AM
DEFAULT_DURATION_MIN = 10
INCHES_PER_WEEK_TARGET = 1.25

MODEL_PATH = "models/yolo_grass_model.pt"

WEATHER_API_KEY = "PUT_YOUR_KEY_HERE"

DATA_DIR = "data"
LOG_FILE = "logs/irrigation.log"

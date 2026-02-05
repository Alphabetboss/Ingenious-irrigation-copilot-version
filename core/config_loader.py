import json
from pathlib import Path

CONFIG_PATH = Path("config/system_config.json")

def load_config():
    """
    Loads system-wide configuration settings.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("System config file not found.")

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

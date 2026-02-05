import json
from pathlib import Path
from typing import Dict, Any


def load_system_config(path: str = "config/system_config.json") -> Dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

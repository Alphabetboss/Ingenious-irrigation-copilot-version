import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigReloader(threading.Thread):
    def __init__(self, config_path: Path, callback):
        super().__init__(daemon=True)
        self.config_path = config_path
        self.callback = callback
        self._stop_event = threading.Event()
        self._last_mtime = None

    def run(self):
        try:
            self._last_mtime = self.config_path.stat().st_mtime
        except FileNotFoundError:
            self._last_mtime = None

        while not self._stop_event.is_set():
            try:
                mtime = self.config_path.stat().st_mtime
                if self._last_mtime is None or mtime != self._last_mtime:
                    self._last_mtime = mtime
                    self.callback()
                self._stop_event.wait(2.0)
            except FileNotFoundError:
                self._stop_event.wait(2.0)

    def stop(self):
        self._stop_event.set()


class AppContext:
    def __init__(self, config_path: str = "config/system_config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.simulation_mode: bool = True

        self._config_lock = threading.Lock()
        self._reloader: Optional[ConfigReloader] = None

        self._load_config()
        self._start_auto_reload()

        # Placeholders for later wiring
        self.db = None
        self.logger = None
        self.ai_engine = None

    def _load_config(self):
        with self._config_lock:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            with self.config_path.open("r") as f:
                self.config = json.load(f)
            self.simulation_mode = bool(
                self.config.get("system", {}).get("simulation_mode", True)
            )

    def _start_auto_reload(self):
        self._reloader = ConfigReloader(self.config_path, self._load_config)
        self._reloader.start()

    def get(self, *keys, default=None):
        with self._config_lock:
            node: Any = self.config
            for key in keys:
                if not isinstance(node, dict) or key not in node:
                    return default
                node = node[key]
            return node

    def stop(self):
        if self._reloader:
            self._reloader.stop()

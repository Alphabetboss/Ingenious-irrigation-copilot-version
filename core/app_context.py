import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigReloader(threading.Thread):
    """
    Background thread that watches the config file for changes
    and triggers a reload callback when it detects modifications.
    """

    def __init__(self, config_path: Path, callback, interval_seconds: float = 2.0):
        super().__init__(daemon=True)
        self.config_path = config_path
        self.callback = callback
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._last_mtime: Optional[float] = None

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
                self._stop_event.wait(self.interval_seconds)
            except FileNotFoundError:
                self._stop_event.wait(self.interval_seconds)

    def stop(self):
        self._stop_event.set()


class AppContext:
    """
    Central application context.

    - Loads and exposes configuration
    - Tracks simulation mode
    - Holds shared resources (logger, db, AI engine, etc.)
    - Supports live config reload via ConfigReloader
    """

    def __init__(self, config_path: str = "config/system_config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.simulation_mode: bool = True

        self._config_lock = threading.Lock()
        self._reloader: Optional[ConfigReloader] = None

        # Shared resources (wired by app.py)
        self.logger = None
        self.db = None
        self.ai_engine = None

        self._load_config()
        self._start_auto_reload()

    def _load_config(self):
        with self._config_lock:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            with self.config_path.open("r", encoding="utf-8") as f:
                self.config = json.load(f)

            system_cfg = self.config.get("system", {})
            self.simulation_mode = bool(system_cfg.get("simulation_mode", True))

            if self.logger:
                self.logger.info(
                    "Configuration reloaded. Simulation mode: %s",
                    self.simulation_mode,
                )

    def _start_auto_reload(self):
        self._reloader = ConfigReloader(self.config_path, self._load_config)
        self._reloader.start()

    def get(self, *keys, default=None):
        """
        Safe nested config getter.

        Example:
            ctx.get("hardware", "relay", "type", default="active_low")
        """
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

import time
from typing import Dict, Any, Optional

from core.app_context import AppContext


class IrrigationController:
    """
    Low-level irrigation control.

    - Maps logical zones → relay pins
    - Supports simulation mode (no GPIO)
    - Supports active_low / active_high relay boards
    - Enforces max runtime safety
    """

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.logger = getattr(self.ctx, "logger", None)

        self.simulation: bool = ctx.simulation_mode
        self.relay_config: Dict[str, Any] = ctx.get("hardware", "relay", default={})
        self.zone_pin_map: Dict[str, int] = self.relay_config.get("in_pins", {})
        self.relay_type: str = self.relay_config.get("type", "active_low")

        self._gpio_initialized: bool = False
        self._gpio = None  # type: ignore[assignment]

        self.max_runtime_minutes: float = ctx.get(
            "ai", "thresholds", "max_continuous_runtime_minutes", default=60
        )

        self._log(
            "info",
            "IrrigationController initialized. simulation=%s relay_type=%s pins=%s max_runtime=%sm",
            self.simulation,
            self.relay_type,
            self.zone_pin_map,
            self.max_runtime_minutes,
        )

        if not self.simulation:
            self._init_gpio()

    def _log(self, level: str, msg: str, *args):
        if self.logger:
            getattr(self.logger, level)(msg, *args)

    def _init_gpio(self):
        """
        Initialize GPIO library and configure relay pins.
        """
        try:
            import RPi.GPIO as GPIO  # type: ignore[import]

            self._gpio = GPIO
            self._gpio.setmode(GPIO.BCM)

            for zone_key, pin in self.zone_pin_map.items():
                self._gpio.setup(pin, GPIO.OUT)
                # Ensure relays start OFF
                self._set_pin_state(pin, False)

            self._gpio_initialized = True
            self._log("info", "GPIO initialized for relay control.")
        except Exception as e:  # ImportError or runtime error
            self._log(
                "exception",
                "Failed to initialize GPIO; falling back to simulation mode: %s",
                e,
            )
            self.simulation = True

    def _get_pin_for_zone(self, zone_id: int) -> Optional[int]:
        key = f"zone_{zone_id}"
        pin = self.zone_pin_map.get(key)
        if pin is None:
            self._log("error", "No relay pin configured for %s", key)
        return pin

    def _set_pin_state(self, pin: int, on: bool):
        """
        Set relay pin state, respecting active_low / active_high configuration.
        """
        if self.simulation:
            self._log(
                "info",
                "[SIM] Set relay pin %s → %s",
                pin,
                "ON" if on else "OFF",
            )
            return

        if not self._gpio_initialized or self._gpio is None:
            raise RuntimeError("GPIO not initialized for hardware mode")

        active_low = self.relay_type == "active_low"
        if active_low:
            value = self._gpio.LOW if on else self._gpio.HIGH
        else:
            value = self._gpio.HIGH if on else self._gpio.LOW

        self._gpio.output(pin, value)
        self._log(
            "info",
            "Set relay pin %s → %s (active_%s)",
            pin,
            "ON" if on else "OFF",
            "low" if active_low else "high",
        )

    def water_zone(self, zone_id: int, duration_minutes: float):
        """
        Activate a zone for the specified duration (in minutes).
        Enforces max runtime safety.
        """
        pin = self._get_pin_for_zone(zone_id)
        if pin is None:
            self._log("error", "Cannot water zone %s: no pin configured", zone_id)
            return

        # Safety clamp
        duration_minutes = max(0.0, min(duration_minutes, self.max_runtime_minutes))
        duration_seconds = duration_minutes * 60.0

        if duration_seconds <= 0:
            self._log(
                "warning",
                "Requested watering duration is 0 seconds for zone %s. Skipping.",
                zone_id,
            )
            return

        self._log(
            "info",
            "Starting watering: zone=%s pin=%s duration=%.1fs (%.1fm)",
            zone_id,
            pin,
            duration_seconds,
            duration_minutes,
        )

        self._set_pin_state(pin, True)
        try:
            if self.simulation:
                # In simulation, we don't block for full duration
                time.sleep(min(1.0, duration_seconds))
            else:
                time.sleep(duration_seconds)
        finally:
            self._set_pin_state(pin, False)
            self._log("info", "Completed watering for zone %s", zone_id)

    def shutdown(self):
        """
        Clean up GPIO on shutdown.
        """
        if not self.simulation and self._gpio_initialized and self._gpio is not None:
            self._gpio.cleanup()
            self._log("info", "GPIO cleaned up on shutdown.")

from typing import Dict, Any

from core.app_context import AppContext


class IrrigationController:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.simulation = ctx.simulation_mode
        self.relay_config: Dict[str, Any] = ctx.get("hardware", "relay", default={})
        self.zone_pin_map: Dict[str, int] = self.relay_config.get("in_pins", {})

        # Later: if not simulation, import and init RPi.GPIO or gpiozero here

    def _get_pin_for_zone(self, zone_id: int) -> int:
        key = f"zone_{zone_id}"
        if key not in self.zone_pin_map:
            raise ValueError(f"No relay pin configured for {key}")
        return self.zone_pin_map[key]

    def water_zone(self, zone_id: int, duration_minutes: float):
        pin = self._get_pin_for_zone(zone_id)

        if self.simulation:
            print(
                f"[SIM] Watering zone {zone_id} on pin {pin} "
                f"for {duration_minutes:.1f} minutes"
            )
            return

        # Real GPIO control will go here later
        # Example structure:
        # self._activate_relay(pin)
        # time.sleep(duration_minutes * 60)
        # self._deactivate_relay(pin)
        raise NotImplementedError("GPIO control not implemented yet")

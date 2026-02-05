class ZoneManager:
    def __init__(self):
        self.zones = {}

    def register_zone(self, zone_id, valve):
        self.zones[zone_id] = valve

    def activate_zone(self, zone_id, duration):
        valve = self.zones.get(zone_id)
        if valve:
            valve.open(duration)

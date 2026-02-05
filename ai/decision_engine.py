from irrigation.hydration_controller import calculate_watering_time
from irrigation.emergency_shutdown import emergency_check

def decide(detections, hydration_score):
    if emergency_check(detections):
        return {"action": "shutdown", "duration": 0}

    duration = calculate_watering_time(hydration_score)
    return {"action": "water", "duration": duration}

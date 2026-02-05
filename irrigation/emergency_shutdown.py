def emergency_check(detections):
    for d in detections:
        if d["label"] in ["water", "mud"] and d["confidence"] > 0.8:
            return True
    return False

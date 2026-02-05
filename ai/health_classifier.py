def classify_health(detections):
    health = {
        "grass": 0,
        "dead_grass": 0,
        "water": 0,
        "mud": 0
    }

    for d in detections:
        if d["label"] in health:
            health[d["label"]] += d["confidence"]

    return health

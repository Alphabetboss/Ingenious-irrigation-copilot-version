def should_skip_watering(weather):
    if weather["rain_chance"] > 60:
        return True
    if weather["temperature"] < 40:
        return True
    return False

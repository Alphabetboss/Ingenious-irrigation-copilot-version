class WeatherService:
    def get_weather(self):
        # Dummy weather data for demo purposes
        return {
            "rain_chance": 10,
            "temperature": 75
        }

def should_skip_watering(weather):
    if weather["rain_chance"] > 60:
        return True
    if weather["temperature"] < 40:
        return True
    return False

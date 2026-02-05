def calculate_watering_time(hydration_score):
    if hydration_score <= 2:
        return 20
    elif hydration_score <= 4:
        return 15
    elif hydration_score <= 6:
        return 10
    elif hydration_score <= 8:
        return 5
    else:
        return 0

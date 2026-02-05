from datetime import datetime

class ScheduleEngine:
    def __init__(self, schedule):
        self.schedule = schedule

    def should_run_now(self):
        now = datetime.now().strftime("%H:%M")
        return now == self.schedule["start_time"]

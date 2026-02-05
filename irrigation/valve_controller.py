import time

class ValveController:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin

    def open(self, duration):
        print(f"Valve {self.gpio_pin} OPEN for {duration} min")
        time.sleep(duration * 60)
        print(f"Valve {self.gpio_pin} CLOSED")

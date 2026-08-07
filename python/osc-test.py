import math
import time

from pythonosc import udp_client

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)


class Oscillator:
    def __init__(self, min=0.0, max=1.0, speed=0.5, time_offset=0.0, name=""):
        self.fact = (max - min) * 0.5
        self.offset = min + self.fact
        self.speed = speed
        self.time_offset = time_offset
        self.name = name

    def send_message(self):
        val = (
            math.sin(time.time() * self.speed + self.time_offset) * self.fact
            + self.offset
        )
        osc_client.send_message(f"/{self.name}", val)


dims = [Oscillator(-1, 1, 0.25, i * 0.75, f"dim{i}") for i in range(4)]

# Example usage:
val = 0.5
while True:
    for dim in dims:
        dim.send_message()

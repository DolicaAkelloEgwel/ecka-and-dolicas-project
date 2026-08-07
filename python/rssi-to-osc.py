from pythonosc import udp_client

RSSI_FILE = "./python/rssi-readings/cth"

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)


class RSSIRange:
    def __init__(self, name, measurements):
        self.name = name
        self.measurements = measurements

        self.max = max(self.measurements)
        self.min = min(self.measurements)
        self.diff = self.max - self.min
        self.norm_factor = 1.9 / self.diff

    def normalise(self, value):
        pass


def send_osc_message(name, val):
    osc_client.send_message(f"/{name}", val)


readings = {}

with open(RSSI_FILE, "r") as f:
    for line in f:
        name, median_rssi = line.split(": ")
        if name not in readings:
            readings[name] = []
        readings[name].append(float(median_rssi.strip()))


for key in readings:
    print(key, readings[key])

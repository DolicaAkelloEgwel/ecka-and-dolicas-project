import argparse
import json
import socket
from random import randint, shuffle, uniform

from pythonosc import udp_client

parser = argparse.ArgumentParser()
parser.add_argument("--simulate", action="store_true")
args = parser.parse_args()

SIMULATE = args.simulate

if SIMULATE:
    import time

# create a socket for listening to M5Stick messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 8080))
print("Listening...")

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

# track names of nearby wifi networks
WIFI_NAMES = ("eduroam", "UAL-IoT", "UAL-WiFi", "UAL-Guest-WiFi")


class RSSIRange:
    def __init__(self, name, min_rssi, max_rssi):

        self._name = name
        self.min = min_rssi
        self.max = max_rssi
        self.diff = abs(self.max - self.min)
        self.offset = (1 / self.diff) * (-self.min - self.max)

        if SIMULATE:
            self.prev = None

    def _map(self, value):
        return 2 * (value / self.diff) + self.offset

    def simulate(self):
        if self.prev is None:
            self.prev = randint(self.min, self.max)

        next_value = self.prev + uniform(-5, 5)

        if next_value < self.min:
            self.prev = self.min
            return self.min

        if next_value > self.max:
            self.prev = self.max
            return self.max

        self.prev = next_value
        return next_value

    def send_osc_message(self, val):
        osc_client.send_message(f"/{self._name}", self._map(val))


rssi_ranges = dict()
rssi_ranges["UAL-IoT-a4:9b:cd:bf:3b:04"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:3b:04", -91, -60
)
rssi_ranges["eduroam-a4:9b:cd:be:ea:25"] = RSSIRange(
    "eduroam-a4:9b:cd:be:ea:25", -92, -63
)
rssi_ranges["UAL-IoT-a4:9b:cd:be:ea:24"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:be:ea:24", -92, -62
)
rssi_ranges["eduroam-a4:9b:cd:bf:01:45"] = RSSIRange(
    "eduroam-a4:9b:cd:bf:01:45", -92, -68
)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:01:44"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:01:44", -93, -68
)
rssi_ranges["eduroam-a4:9b:cd:bf:28:a5"] = RSSIRange(
    "eduroam-a4:9b:cd:bf:28:a5", -94, -70
)
rssi_ranges["eduroam-a4:9b:cd:bf:29:65"] = RSSIRange(
    "eduroam-a4:9b:cd:bf:29:65", -94, -75
)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:29:64"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:29:64", -94, -75
)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:9d:c4"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:9d:c4", -91, -62
)
rssi_ranges["eduroam-a4:9b:cd:bf:9d:c5"] = RSSIRange(
    "eduroam-a4:9b:cd:bf:9d:c5", -91, -62
)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:28:a4"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:28:a4", -95, -70
)
rssi_ranges["eduroam-a4:9b:cd:be:f8:e5"] = RSSIRange(
    "eduroam-a4:9b:cd:be:f8:e5", -92, -55
)
rssi_ranges["eduroam-a4:9b:cd:bf:3b:05"] = RSSIRange(
    "eduroam-a4:9b:cd:bf:3b:05", -90, -59
)
rssi_ranges["UAL-IoT-a4:9b:cd:be:f8:e4"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:be:f8:e4", -93, -55
)
rssi_ranges["eduroam-a4:9b:cd:be:f5:a5"] = RSSIRange(
    "eduroam-a4:9b:cd:be:f5:a5", -96, -71
)
rssi_ranges["UAL-IoT-a4:9b:cd:be:f5:a4"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:be:f5:a4", -95, -72
)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:d7:c4"] = RSSIRange(
    "UAL-IoT-a4:9b:cd:bf:d7:c4", -95, -78
)

if SIMULATE:
    while True:

        networks = list(rssi_ranges.values())
        shuffle(networks)
        networks = networks[:8]

        for network in networks:
            val = network.simulate()
            network.send_osc_message(val)
            print(network._name, val)
        time.sleep(1.5)


while True:

    data, addr = sock.recvfrom(2048)
    data = data.decode()
    d = json.loads(data)
    print("Received data.")

    for key in d.keys():

        # continue if the network isn't in the list
        if d[key]["name"] not in WIFI_NAMES:
            continue

        combined_name = f"{d[key]['name']}-{key}"

        # continue if the network isn't in the dictionary
        if combined_name not in rssi_ranges:
            continue

        rssi_ranges[combined_name].send_osc_message(combined_name, d[key]["rssi"])

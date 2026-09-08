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
        self._min = min_rssi
        self._max = max_rssi
        self._diff = abs(self._max - self._min)
        self._offset = (1 / self._diff) * (-self._min - self._max)

        if SIMULATE:
            self._prev = None

    def _map(self, value):
        return 2 * (value / self._diff) + self._offset

    def simulate(self):
        if self._prev is None:
            self._prev = randint(self._min, self._max)

        next_value = self._prev + uniform(-5, 5)

        if next_value < self._min:
            self._prev = self._min
            return self._min

        if next_value > self._max:
            self._prev = self._max
            return self._max

        self._prev = next_value
        return next_value

    def send_osc_message(self, val):
        osc_client.send_message(f"/{self._name}", self._map(val))


rssi_ranges = [
    RSSIRange("UAL-IoT-a4:9b:cd:bf:3b:04", -91, -60),
    RSSIRange("eduroam-a4:9b:cd:be:ea:25", -92, -63),
    RSSIRange("UAL-IoT-a4:9b:cd:be:ea:24", -92, -62),
    RSSIRange("eduroam-a4:9b:cd:bf:01:45", -92, -68),
    RSSIRange("UAL-IoT-a4:9b:cd:bf:01:44", -93, -68),
    RSSIRange("eduroam-a4:9b:cd:bf:28:a5", -94, -70),
    RSSIRange("eduroam-a4:9b:cd:bf:29:65", -94, -75),
    RSSIRange("UAL-IoT-a4:9b:cd:bf:29:64", -94, -75),
    RSSIRange("UAL-IoT-a4:9b:cd:bf:9d:c4", -91, -62),
    RSSIRange("eduroam-a4:9b:cd:bf:9d:c5", -91, -62),
    RSSIRange("UAL-IoT-a4:9b:cd:bf:28:a4", -95, -70),
    RSSIRange("eduroam-a4:9b:cd:be:f8:e5", -92, -55),
    RSSIRange("eduroam-a4:9b:cd:bf:3b:05", -90, -59),
    RSSIRange("UAL-IoT-a4:9b:cd:be:f8:e4", -93, -55),
    RSSIRange("eduroam-a4:9b:cd:be:f5:a5", -96, -71),
    RSSIRange("UAL-IoT-a4:9b:cd:be:f5:a4", -95, -72),
    RSSIRange("UAL-IoT-a4:9b:cd:bf:d7:c4", -95, -78),
]

rssi_ranges = {network._name: network for network in rssi_ranges}

while SIMULATE:

    networks = list(rssi_ranges.values())
    shuffle(networks)
    networks = networks[:8]

    for network in networks:
        val = network.simulate()
        network.send_osc_message(val)
        print(network._name, val)
    time.sleep(2.5)


while True:

    data, addr = sock.recvfrom(2048)
    data = data.decode()
    d = json.loads(data)
    print("Received data.", d)

    for key in d.keys():

        # continue if the network isn't in the list
        if d[key]["name"] not in WIFI_NAMES:
            continue

        combined_name = f"{d[key]['name']}-{key}"

        # continue if the network isn't in the dictionary
        if combined_name not in rssi_ranges:
            continue

        rssi_ranges[combined_name].send_osc_message(d[key]["rssi"])

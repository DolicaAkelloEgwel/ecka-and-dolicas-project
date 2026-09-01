import json
import socket
from pythonosc import udp_client

RSSI_VALUES = dict()

# create a socket for listening to M5Stick messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 8080))
print("Listening...")

# track names of nearby wifi networks
WIFI_NAMES = ("eduroam", "UAL-IoT", "UAL-WiFi", "UAL-Guest-WiFi")


class RSSIRange:
    def __init__(self, min_rssi, max_rssi):

        self.min = min_rssi
        self.max = max_rssi
        self.diff = abs(self.max - self.min)
        self.offset = -self.min / self.diff - self.max / self.diff

    def map(self, value):
        return (value / diff) * 2 + self.offset

    @staticmethod
    def send_osc_message(name, val):
        osc_client.send_message(f"/{name}", val)


rssi_ranges = dict()
rssi_ranges["UAL-IoT-a4:9b:cd:bf:3b:04"] = RSSIRange(-91, -60)
rssi_ranges["eduroam-a4:9b:cd:be:ea:25"] = RSSIRange(-92, -63)
rssi_ranges["UAL-IoT-a4:9b:cd:be:ea:24"] = RSSIRange(-92, -62)
rssi_ranges["eduroam-a4:9b:cd:bf:01:45"] = RSSIRange(-92, -68)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:01:44"] = RSSIRange(-93, -68)
rssi_ranges["eduroam-a4:9b:cd:bf:28:a5"] = RSSIRange(-94, -70)
rssi_ranges["eduroam-a4:9b:cd:bf:29:65"] = RSSIRange(-94, -75)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:29:64"] = RSSIRange(-94, -75)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:9d:c4"] = RSSIRange(-91, -62)
rssi_ranges["eduroam-a4:9b:cd:bf:9d:c5"] = RSSIRange(-91, -62)
rssi_ranges["UAL-IoT-a4:9b:cd:bf:28:a4"] = RSSIRange(-95, -70)
rssi_ranges["eduroam-a4:9b:cd:be:f8:e5"] = RSSIRange(-92, -55)
rssi_ranges["eduroam-a4:9b:cd:bf:3b:05"] = RSSIRange(-90, -59)
rssi_ranges["UAL-IoT-a4:9b:cd:be:f8:e4"] = RSSIRange(-93, -55)
rssi_ranges["eduroam-a4:9b:cd:be:f5:a5"] = RSSIRange(-96, -71)
rssi_ranges["UAL-IoT-a4:9b:cd:be:f5:a4"] = RSSIRange(-95, -72)


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

        rssi_ranges[combined_name].send_osc_message(combined_name, d[key]["rssi"])

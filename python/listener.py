import json
import socket
from pythonosc import udp_client

RSSI_VALUES = dict()

# create a socket for listening to M5Stick messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 8080))
print("Listening...")

# track names of nearby wifi networks
WIFI_NAMES = ("eduroam", "UAL-IoT", "UAL-WiFi", "UAL-Guest-WiFi", "Igloo")

MIN_RECORDINGS = 30
MIN_NETWORKS_NEEDED = 10
MAX_SCANS = 200


def calculate_median(vals):

    ordered = sorted(vals)
    n = len(vals)

    if n % 2 == 0:
        mid_index = n // 2
        return (ordered[mid_index - 1] + ordered[mid_index]) / 2
    else:
        return ordered[(n // 2)]


counter = 0

while counter < MAX_SCANS:

    data, addr = sock.recvfrom(2048)
    data = data.decode()
    d = json.loads(data)
    print("Received data.")

    for key in d.keys():
        # continue if the network isn't in the list
        if d[key]["name"] not in WIFI_NAMES:
            continue

        combined_name = f"{d[key]['name']}-{key}"

        # create a new dictionary entry if this has not been seen before
        if combined_name not in RSSI_VALUES:
            RSSI_VALUES[combined_name] = []

        RSSI_VALUES[combined_name].append(d[key]["rssi"])

    counter += 1

    # stop when at least 30 recordings have been taken for at least 10 networks
    if (
        sum([len(vals) >= MIN_RECORDINGS for vals in RSSI_VALUES.values()])
        >= MIN_NETWORKS_NEEDED
    ):
        break

    print(RSSI_VALUES)

# calculate the median rssi value
with open("recordings", "a") as f:
    for key in RSSI_VALUES:
        if len(RSSI_VALUES[key]) >= MIN_RECORDINGS:
            f.write(f"{key}: {calculate_median(RSSI_VALUES[key])}\n")

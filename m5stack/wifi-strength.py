import gc
import json
import socket
import time

import M5
import network
from M5 import *

wlan = None
EIGHT_PM = 20
FRIDAY = 4

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def hours_to_microseconds(hours):
    return hours * 3600000000


OVERNIGHT_BREAK = hours_to_microseconds(13)
WEEKEND_BREAK = hours_to_microseconds(61)


def send_data(rssi_data):
    try:
        sock.sendto(json.dumps(rssi_data), ("192.168.0.107", 8080))
        Power.setLed(255)
        time.sleep(0.1)
        Power.setLed(0)
    except Exception as e:
        print("Send failed:", e)


def format_mac(mac):
    return ":".join("{:02x}".format(b) for b in mac)


def setup():
    global wlan
    M5.begin()
    M5.Display.setBrightness(0)
    Widgets.setRotation(0)
    Widgets.fillScreen(0x000000)
    time.sleep(2)
    time.timezone("GMT+0")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("TP-Link_9734", "12327423")


def wireless_scan():
    global wlan
    M5.update()

    current_time = time.localtime()
    if current_time[3] == EIGHT_PM:
        if current_time[6] == FRIDAY:
            Power.deepSleep(WEEKEND_BREAK, True)
        else:
            Power.deepSleep(OVERNIGHT_BREAK, True)

    try:
        rssis = {
            format_mac(record[1]): {
                "name": record[0].decode("utf-8"),
                "rssi": record[3],
            }
            for record in wlan.scan()
        }
        print(f"Found {len(rssis)} networks in scan.")
        send_data(rssis)
    except OSError as e:
        print(e)
        gc.collect()


if __name__ == "__main__":
    try:
        setup()
        Speaker.setVolumePercentage(0.75)
        Speaker.tone(2000, 1000)
        while True:
            wireless_scan()
            time.sleep(0.1)
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg

            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")

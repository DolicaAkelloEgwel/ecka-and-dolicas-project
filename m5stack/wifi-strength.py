# main.py
import os, sys, io
import M5
from M5 import *
import network
import requests2
import json
import time
import socket

wlan_sta = None
sta_record = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_data(rssi_data):
    try:
        sock.sendto(json.dumps(rssi_data), ("192.168.1.240", 5000))
    except Exception as e:
        print("Send failed:", e)


def format_mac(mac):
    return ':'.join('{:02x}'.format(b) for b in mac)

    
def setup():
    global wlan_sta
    M5.begin()
    Widgets.setRotation(0)
    Widgets.fillScreen(0x000000)
    wlan_sta = network.WLAN(network.STA_IF)
    
def loop():
    global wlan_sta
    M5.update()
    rssis = {format_mac(record[1]): {"name": record[0].decode("utf-8"), "rssi": record[3]}  for record in wlan_sta.scan() }
    print(f"Found {len(rssis)} networks in scan.")
    send_data(rssis)
    
if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
            time.sleep(0.1)
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg
            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")


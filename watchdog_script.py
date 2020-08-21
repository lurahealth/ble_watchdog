#!/usr/bin/env python 
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, \
                                Service, Characteristic, UUID 
from gpiozero import LED
import sys
import os
import atexit

# Variables for BLE connection
sensor_name = "Lura"
rx_uuid     = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
connected  = False
global sensor_obj

# Callback to scanning object
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

sensor_obj = Peripheral()
scanner = Scanner().withDelegate(DefaultDelegate())

# Send packet that will cause the peripheral to turn itself on upon receipt
def send_done_packet():
    global connected
    print("Sending PWROFF packet")
    global sensor_obj
    rx_char_list = sensor_obj.getCharacteristics(uuid=rx_uuid)
    rx_char = rx_char_list[0]
    props = rx_char.propertiesToString()
    print(props)
    rx_char.write("PWROFF\n".encode('ascii'), False)
    print("PWROFF packet sent \n")
    sensor_obj.disconnect()
    connected = False 

def find_and_pwroff():
    global connected
    while not connected:
        scanner.clear()
        scanner.start()
        scanner.process(1)
        devs = scanner.getDevices()
        for dev in devs:
            if dev.getValueText(9) is not None:
                if sensor_name in dev.getValueText(9):
                    print("Found Lura device")
                    scanner.stop()
                    sensor_obj.connect(dev.addr, dev.addrType)
                    print("Connected to Lura device")
                    connected = True
                    send_done_packet()

def exit_program():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


while True:
    try:
        find_and_pwroff()
    except Exception as e:
        print("Error: " + str(e) + "\n")
        if "Failed" in str(e):
            print("Error: " + str(e) + "\n")
            exit_program()
        elif "disconnected" in str(e):
            connected = False
            print("Device powered off, restarting now\n")
            continue
        else:
            print("Error: " + str(e) + "\n")
            exit_program()

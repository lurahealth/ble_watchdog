#!/usr/bin/env python 
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, \
                                Service, Characteristic, UUID 
import board
import neopixel
import sys
import os
import atexit
import time as t

# Program exit behaviour
def exit_handler():
    clear_pixels()

atexit.register(exit_handler)

# Variables for neopixel strip
pixels = neopixel.NeoPixel(board.D18, 8, brightness=0.01, \
                           auto_write=True, pixel_order=neopixel.GRB)
nodev_pixels    = [0, 1, 3, 4, 6, 7]
BLANK = (0, 0, 0)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)

# Variables for BLE connection
sensor_name = "Lura"
rx_uuid     = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
connected  = False
global sensor_obj

def display_nodev_pixels():
    for p in nodev_pixels:
        pixels[p] = GREEN

def display_devfound_pixels():
    pixels.fill(RED)

def clear_pixels():
    pixels.fill(BLANK)

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
    clear_pixels()
    display_nodev_pixels()

def find_and_pwroff():
    global connected
    display_nodev_pixels()
    while not connected:
        scanner.clear()
        scanner.start()
        scanner.process(1)
        devs = scanner.getDevices()
        for dev in devs:
            if dev.getValueText(9) is not None:
                if sensor_name in dev.getValueText(9):
                    clear_pixels()
                    display_devfound_pixels()
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

# Clear pixels at startup
clear_pixels()

while True:
    try:
        find_and_pwroff()
    except Exception as e:
        clear_pixels()
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

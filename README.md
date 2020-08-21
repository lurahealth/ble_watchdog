A python application to be run on a raspberry pi and used by factory
workers while assembling Lura Health sensor devices. The python
script will continually scan for BLE devices, and if a Lura Health
device is discovered the script will connect and send a packet that
tells the device to turns itself off. This is to reduce the risk of
devices accidentally becoming powered on for extended periods during
assembly and draining large amounts of battery.

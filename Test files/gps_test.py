from machine import UART, Pin
import time
from micropython_tinygpsplus import TinyGPSPlus

# Setup UART (Your pins from image 1)
gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
parser = TinyGPSPlus()

print("Scanning for GPS Lock...")

while True:
    if gps_module.any():
        line = gps_module.readline()
        try:
            sentence = line.decode('ascii', 'ignore')
            if parser.parse_nmea(sentence):
                print("-" * 20)
                print(f"LAT: {parser.location.lat:.6f}")
                print(f"LNG: {parser.location.lng:.6f}")
        except:
            continue
    time.sleep(0.1)


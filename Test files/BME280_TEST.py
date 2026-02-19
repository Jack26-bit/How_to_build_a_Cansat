from machine import Pin, I2C
from bmp280 import BMP280
import time

# Initialize I2C on GP0 (SDA) and GP1 (SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# Scan for I2C devices
print("Scanning I2C bus...")
devices = i2c.scan()
if devices:
    print(f"Found devices at addresses: {[hex(d) for d in devices]}")
    # BMP280 should be at 0x76 or 0x77
else:
    print("❌ No I2C devices found! Check wiring!")

# Initialize BMP280
try:
    bmp = BMP280(i2c=i2c, address=0x76)  # Try 0x76 first
except:
    bmp = BMP280(i2c=i2c, address=0x77)  # If fails, try 0x77

print("BMP280 initialized! ✅")
print("\nReading sensor data...\n")

while True:
    # Read all values
    temp = bmp.temperature
    pressure = bmp.pressure
    
    print(f"Temperature: {temp}")
    print(f"Pressure: {pressure}")
    print("-" * 40)
    
    time.sleep(2)
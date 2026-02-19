from machine import ADC, Pin
import time

# Pico W can measure VSYS voltage
vsys = ADC(29)  # Pin 29 = VSYS/3

while True:
    # Read voltage (VSYS is divided by 3)
    reading = vsys.read_u16()
    voltage = (reading / 65535) * 3.3 * 3  # Convert to actual voltage
    
    print(f"Battery Voltage: {voltage:.2f}V")
    
    if voltage < 3.3:
        print("⚠️ Battery LOW! Charge soon!")
    elif voltage > 4.2:
        print("⚠️ Voltage too HIGH! Check wiring!")
    else:
        print("✅ Battery OK")
    
    time.sleep(2)
from machine import Pin
import time

led = Pin("LED", Pin.OUT)  # Pico W onboard LED

while True:
    led.toggle()
    print("LED toggled!")
    time.sleep(0.5)
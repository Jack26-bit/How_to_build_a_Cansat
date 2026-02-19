import time
import socket
import network
from micropython_tinygpsplus import TinyGPSPlusfrom micropython_tinygpsplus import TinyGPSPlus
from machine import Pin, I2C, UART

# ---------------- TIMER ----------------
start_time = time.ticks_ms()

def mission_time():
    return time.ticks_diff(time.ticks_ms(), start_time) / 1000

# ---------------- I2C ----------------
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# ---------------- BMP280 ----------------
from bmp280 import BMP280
bmp = BMP280(i2c, addr=0x76)

# ---------------- MPU6050 ----------------
MPU_ADDR = 0x68
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')

def read_acceleration():
    data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 6)

    def convert(high, low):
        value = (high << 8) | low
        return value - 65536 if value > 32767 else value

    ax = convert(data[0], data[1]) / 16384
    ay = convert(data[2], data[3]) / 16384
    az = convert(data[4], data[5]) / 16384

    return ax, ay, az

# ---------------- GPS ----------------
gps = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

latitude = "Waiting"
longitude = "Waiting"
altitude = "Waiting"
satellites = "Waiting"

def read_gps():
    global latitude, longitude, altitude, satellites

    if gps.any():
        line = gps.readline()
        try:
            sentence = line.decode("ascii", errors="ignore")

            if sentence.startswith("$GPGGA") or sentence.startswith("$GNGGA"):
                parts = sentence.split(",")

                if parts[6] != "0":
                    latitude = parts[2]
                    longitude = parts[4]
                    altitude = parts[9] + " meters"
                    satellites = parts[7]
        except:
            pass

# ---------------- WIFI ACCESS POINT ----------------
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="CANSAT_LIVE", password="12345678")

while not ap.active():
    time.sleep(1)

ip_address = ap.ifconfig()[0]
print("Connect to WiFi: CANSAT_LIVE")
print("Open browser at:", ip_address)

# ---------------- WEB SERVER ----------------
address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(address)
server.listen(1)

# ---------------- MAIN LOOP ----------------
while True:
    read_gps()

    temperature = bmp.temperature
    pressure = bmp.pressure / 100
    ax, ay, az = read_acceleration()
    time_now = mission_time()

    client, addr = server.accept()

    html = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="1">
<title>CanSat Live Data</title>
<style>
body {{
    background-color: #111111;
    color: #ffffff;
    font-family: Arial;
    text-align: center;
}}
.box {{
    border: 1px solid #ffffff;
    padding: 15px;
    margin: 10px;
}}
</style>
</head>

<body>

<h1>CanSat Live Telemetry</h1>

<div class="box">
Mission Time: {time_now:.1f} seconds
</div>

<div class="box">
GPS Altitude: {altitude}<br>
Latitude: {latitude}<br>
Longitude: {longitude}<br>
Satellites Connected: {satellites}
</div>

<div class="box">
Temperature: {temperature:.2f} Celsius<br>
Pressure: {pressure:.2f} hPa
</div>

<div class="box">
Acceleration X: {ax:.2f} g<br>
Acceleration Y: {ay:.2f} g<br>
Acceleration Z: {az:.2f} g
</div>

<p>Data updates every second</p>

</body>
</html>
"""

    client.send(html)
    client.close()

import time
import socket
import network
import os
from machine import Pin, I2C, UART, SPI
from bmp280 import BMP280

# ============= CONFIGURATION =============
WIFI_SSID = "CANSAT_LIVE"
WIFI_PASSWORD = "12345678"
LOG_INTERVAL = 1  # seconds between logs

# ============= TIMER =============
start_time = time.ticks_ms()

def mission_time():
    return time.ticks_diff(time.ticks_ms(), start_time) / 1000

# ============= I2C SETUP =============
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# ============= BMP280 SENSOR =============
try:
    bmp = BMP280(i2c, addr=0x76)
    bmp_available = True
    print("✓ BMP280 initialized")
except Exception as e:
    bmp_available = False
    print("✗ BMP280 not found:", e)

# ============= MPU6050 SENSOR =============
MPU_ADDR = 0x68
mpu_available = False

try:
    i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')  # Wake up MPU6050
    time.sleep_ms(100)
    mpu_available = True
    print("✓ MPU6050 initialized")
except Exception as e:
    print("✗ MPU6050 not found:", e)

def read_mpu6050():
    if not mpu_available:
        return None, None, None, None, None, None
    
    try:
        # Read accelerometer (registers 0x3B to 0x40)
        accel_data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 6)
        # Read gyroscope (registers 0x43 to 0x48)
        gyro_data = i2c.readfrom_mem(MPU_ADDR, 0x43, 6)
        
        def convert(high, low):
            value = (high << 8) | low
            return value - 65536 if value > 32767 else value
        
        # Accelerometer (±2g range, sensitivity 16384 LSB/g)
        ax = convert(accel_data[0], accel_data[1]) / 16384.0
        ay = convert(accel_data[2], accel_data[3]) / 16384.0
        az = convert(accel_data[4], accel_data[5]) / 16384.0
        
        # Gyroscope (±250°/s range, sensitivity 131 LSB/°/s)
        gx = convert(gyro_data[0], gyro_data[1]) / 131.0
        gy = convert(gyro_data[2], gyro_data[3]) / 131.0
        gz = convert(gyro_data[4], gyro_data[5]) / 131.0
        
        return ax, ay, az, gx, gy, gz
    except Exception as e:
        print("MPU6050 read error:", e)
        return None, None, None, None, None, None

# ============= GPS SETUP =============
gps_uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
gps_data = {
    'latitude': 'N/A',
    'longitude': 'N/A',
    'altitude': 'N/A',
    'satellites': '0'
}

def read_gps():
    if gps_uart.any():
        try:
            line = gps_uart.readline()
            sentence = line.decode("ascii", errors="ignore").strip()
            
            if sentence.startswith("$GPGGA") or sentence.startswith("$GNGGA"):
                parts = sentence.split(",")
                if len(parts) > 9 and parts[6] != "0":
                    gps_data['latitude'] = parts[2] + parts[3]
                    gps_data['longitude'] = parts[4] + parts[5]
                    gps_data['altitude'] = parts[9]
                    gps_data['satellites'] = parts[7]
        except:
            pass

# ============= SD CARD SETUP =============
sd_available = False
log_file = None

try:
    from sdcard import SDCard
    
    # SPI setup for SD card (adjust pins as needed)
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0, 
              sck=Pin(18), mosi=Pin(19), miso=Pin(16))
    cs = Pin(17, Pin.OUT)
    
    sd = SDCard(spi, cs)
    os.mount(sd, '/sd')
    
    # Create log file with timestamp
    log_filename = '/sd/cansat_log.csv'
    
    # Check if file exists, if not create with headers
    try:
        with open(log_filename, 'r') as f:
            pass
    except:
        with open(log_filename, 'w') as f:
            f.write("Time(s),Temp(C),Pressure(hPa),Altitude_BMP(m),Accel_X(g),Accel_Y(g),Accel_Z(g),Gyro_X(deg/s),Gyro_Y(deg/s),Gyro_Z(deg/s),GPS_Lat,GPS_Lon,GPS_Alt(m),Satellites\n")
    
    sd_available = True
    print("✓ SD card initialized")
    print(f"✓ Logging to: {log_filename}")
    
except Exception as e:
    print("✗ SD card not available:", e)
    print("  Continuing without SD logging...")

def log_to_sd(data):
    if not sd_available:
        return
    
    try:
        with open('/sd/cansat_log.csv', 'a') as f:
            f.write(data + '\n')
    except Exception as e:
        print("SD write error:", e)

# ============= WIFI ACCESS POINT =============
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)

print("\n" + "="*40)
print("Waiting for WiFi AP to start...")
while not ap.active():
    time.sleep(0.5)

ip_address = ap.ifconfig()[0]
print("="*40)
print(f"✓ WiFi AP Active: {WIFI_SSID}")
print(f"✓ Password: {WIFI_PASSWORD}")
print(f"✓ IP Address: http://{ip_address}")
print("="*40 + "\n")

# ============= WEB SERVER =============
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)
server.setblocking(False)

print("✓ Web server started")
print("Ready to collect data!\n")

# ============= DATA STORAGE =============
sensor_data = {
    'time': 0,
    'temperature': 0,
    'pressure': 0,
    'altitude_bmp': 0,
    'ax': 0, 'ay': 0, 'az': 0,
    'gx': 0, 'gy': 0, 'gz': 0
}

last_log_time = 0

# ============= MAIN LOOP =============
while True:
    current_time = mission_time()
    
    # Read GPS
    read_gps()
    
    # Read BMP280
    if bmp_available:
        try:
            sensor_data['temperature'] = bmp.temperature
            sensor_data['pressure'] = bmp.pressure / 100  # Convert to hPa
            # Calculate altitude from pressure (simplified formula)
            sensor_data['altitude_bmp'] = 44330 * (1 - (sensor_data['pressure'] / 1013.25) ** 0.1903)
        except Exception as e:
            print("BMP280 error:", e)
    
    # Read MPU6050
    ax, ay, az, gx, gy, gz = read_mpu6050()
    if ax is not None:
        sensor_data['ax'] = ax
        sensor_data['ay'] = ay
        sensor_data['az'] = az
        sensor_data['gx'] = gx
        sensor_data['gy'] = gy
        sensor_data['gz'] = gz
    
    sensor_data['time'] = current_time
    
    # Log to SD card at intervals
    if current_time - last_log_time >= LOG_INTERVAL:
        log_data = f"{sensor_data['time']:.1f},{sensor_data['temperature']:.2f},{sensor_data['pressure']:.2f},{sensor_data['altitude_bmp']:.2f},{sensor_data['ax']:.3f},{sensor_data['ay']:.3f},{sensor_data['az']:.3f},{sensor_data['gx']:.2f},{sensor_data['gy']:.2f},{sensor_data['gz']:.2f},{gps_data['latitude']},{gps_data['longitude']},{gps_data['altitude']},{gps_data['satellites']}"
        log_to_sd(log_data)
        last_log_time = current_time
        print(f"[{current_time:.1f}s] Logged data")
    
    # Handle web requests
    try:
        client, addr = server.accept()
        
        html = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="1">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CanSat Telemetry</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #ffffff;
    padding: 20px;
    min-height: 100vh;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
}}

h1 {{
    text-align: center;
    font-size: 2em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

.mission-time {{
    text-align: center;
    font-size: 1.5em;
    margin-bottom: 30px;
    background: rgba(255,255,255,0.2);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}}

.grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
    margin-bottom: 20px;
}}

.card {{
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    transition: transform 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
}}

.card-title {{
    font-size: 1.3em;
    margin-bottom: 15px;
    border-bottom: 2px solid rgba(255,255,255,0.3);
    padding-bottom: 10px;
}}

.data-row {{
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.data-label {{
    color: rgba(255,255,255,0.8);
    font-weight: 500;
}}

.data-value {{
    font-weight: bold;
    font-size: 1.1em;
}}

.status {{
    text-align: center;
    padding: 15px;
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    margin-top: 20px;
}}

.status-indicator {{
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #4ade80;
    margin-right: 8px;
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

.sd-status {{
    background: {'rgba(74, 222, 128, 0.2)' if sd_available else 'rgba(248, 113, 113, 0.2)'};
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
}}
</style>
</head>
<body>
<div class="container">
    <h1>CanSat Live Telemetry</h1>
    
    <div class="mission-time">
        Mission Time: <strong>{sensor_data['time']:.1f}</strong> seconds
    </div>
    
    <div class="grid">
        <!-- BMP280 Card -->
        <div class="card">
            <div class="card-title">
                BMP280 Sensor
            </div>
            <div class="data-row">
                <span class="data-label">Temperature:</span>
                <span class="data-value">{sensor_data['temperature']:.2f} °C</span>
            </div>
            <div class="data-row">
                <span class="data-label">Pressure:</span>
                <span class="data-value">{sensor_data['pressure']:.2f} hPa</span>
            </div>
            <div class="data-row">
                <span class="data-label">Altitude:</span>
                <span class="data-value">{sensor_data['altitude_bmp']:.2f} m</span>
            </div>
        </div>
        
        <!-- Accelerometer Card -->
        <div class="card">
            <div class="card-title">
                Accelerometer
            </div>
            <div class="data-row">
                <span class="data-label">X-axis:</span>
                <span class="data-value">{sensor_data['ax']:.3f} g</span>
            </div>
            <div class="data-row">
                <span class="data-label">Y-axis:</span>
                <span class="data-value">{sensor_data['ay']:.3f} g</span>
            </div>
            <div class="data-row">
                <span class="data-label">Z-axis:</span>
                <span class="data-value">{sensor_data['az']:.3f} g</span>
            </div>
        </div>
        
        <!-- Gyroscope Card -->
        <div class="card">
            <div class="card-title">
                Gyroscope
            </div>
            <div class="data-row">
                <span class="data-label">X-axis:</span>
                <span class="data-value">{sensor_data['gx']:.2f} °/s</span>
            </div>
            <div class="data-row">
                <span class="data-label">Y-axis:</span>
                <span class="data-value">{sensor_data['gy']:.2f} °/s</span>
            </div>
            <div class="data-row">
                <span class="data-label">Z-axis:</span>
                <span class="data-value">{sensor_data['gz']:.2f} °/s</span>
            </div>
        </div>
        
        <!-- GPS Card -->
        <div class="card">
            <div class="card-title">
                GPS Location
            </div>
            <div class="data-row">
                <span class="data-label">Latitude:</span>
                <span class="data-value">{gps_data['latitude']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Longitude:</span>
                <span class="data-value">{gps_data['longitude']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">GPS Altitude:</span>
                <span class="data-value">{gps_data['altitude']} m</span>
            </div>
            <div class="data-row">
                <span class="data-label">Satellites:</span>
                <span class="data-value">{gps_data['satellites']}</span>
            </div>
        </div>
    </div>
    
    <div class="status">
        <span class="status-indicator"></span>
        <strong>Live Data Stream Active</strong>
        <div class="sd-status">
            SD Card: {'Logging Active' if sd_available else 'Not Available'}
        </div>
    </div>
</div>
</body>
</html>
"""
        
        client.send(html.encode())
        client.close()
        
    except OSError:
        pass  # No client connected
    
    time.sleep(0.1)  # Small delay to prevent CPU overload

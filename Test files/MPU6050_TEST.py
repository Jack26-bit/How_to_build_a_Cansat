from machine import Pin, I2C
import time

# Initialize I2C (shared with BME280)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# Scan I2C bus
print("I2C devices:", [hex(addr) for addr in i2c.scan()])
# Should see 0x68 (MPU6050) and 0x76/0x77 (BME280)

# MPU6050 register addresses
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Wake up MPU6050
i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')
time.sleep(0.1)

print("MPU6050 initialized! ✅")
print("\nReading accelerometer data...\n")

def read_accel():
    # Read 6 bytes (X, Y, Z acceleration)
    data = i2c.readfrom_mem(MPU6050_ADDR, ACCEL_XOUT_H, 6)
    
    # Convert to signed values
    accel_x = int.from_bytes(data[0:2], 'big')
    if accel_x > 32767: accel_x -= 65536
    
    accel_y = int.from_bytes(data[2:4], 'big')
    if accel_y > 32767: accel_y -= 65536
    
    accel_z = int.from_bytes(data[4:6], 'big')
    if accel_z > 32767: accel_z -= 65536
    
    # Convert to g (gravity units)
    accel_x = accel_x / 16384.0
    accel_y = accel_y / 16384.0
    accel_z = accel_z / 16384.0
    
    return accel_x, accel_y, accel_z

while True:
    x, y, z = read_accel()
    
    print(f"Accel X: {x:6.2f}g  Y: {y:6.2f}g  Z: {z:6.2f}g")
    
    # When flat on table, Z should be ~1.0g
    if 0.8 < z < 1.2:
        print("✅ Sensor working correctly!")
    
    time.sleep(0.5)
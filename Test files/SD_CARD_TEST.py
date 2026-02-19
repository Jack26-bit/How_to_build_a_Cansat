from machine import Pin, SPI
import os
import time

# Initialize SPI for SD card
spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))

cs = Pin(17, Pin.OUT)
cs.value(1)  # Deselect initially

print("SD Card Test")
print("-" * 40)

# Try to mount SD card
try:
    import sdcard
    sd = sdcard.SDCard(spi, cs)
    
    # Mount filesystem
    os.mount(sd, '/sd')
    
    print("✅ SD card mounted successfully!")
    print(f"Free space: {os.statvfs('/sd')[0] * os.statvfs('/sd')[3] // 1024} KB")
    
    # Test write
    with open('/sd/test.txt', 'w') as f:
        f.write('CanSat test file!\n')
        f.write(f'Time: {time.time()}\n')
    
    print("✅ File written successfully!")
    
    # Test read
    with open('/sd/test.txt', 'r') as f:
        content = f.read()
        print("\nFile contents:")
        print(content)
    
    print("✅ SD card working perfectly!")
    
except Exception as e:
    print(f"❌ SD card error: {e}")
    print("Check:")
    print("  - SD card inserted")
    print("  - Formatted as FAT32")
    print("  - All wiring correct")

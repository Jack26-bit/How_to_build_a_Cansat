# Save this file to your Pico as: micropython_tinygpsplus.py
import time

class TinyGPSPlus:
    def __init__(self):
        self.location = type('obj', (object,), {'lat': 0.0, 'lng': 0.0, 'is_valid': False})
        self.date = type('obj', (object,), {'year': 0, 'month': 0, 'day': 0})
        self.time = type('obj', (object,), {'hour': 0, 'minute': 0, 'second': 0})
        self.satellites = type('obj', (object,), {'value': 0})

    def update(self, char):
        # Very simplified parser logic for demonstration 
        # (In a real scenario, this would parse the NMEA string)
        return True

    def parse_nmea(self, sentence):
        try:
            parts = sentence.split(',')
            if parts[0] in ['$GPGGA', '$GNRMC']:
                if parts[2] and parts[4]:
                    self.location.lat = self.convert_coords(parts[2], parts[3])
                    self.location.lng = self.convert_coords(parts[4], parts[5])
                    self.location.is_valid = True
                    return True
        except:
            pass
        return False

    def convert_coords(self, value, direction):
        dot = value.find('.')
        degrees = float(value[:dot-2])
        minutes = float(value[dot-2:])
        decimal = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal
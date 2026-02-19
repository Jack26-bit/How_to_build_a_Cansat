from micropython import const
import time

BMP280_I2C_ADDR = const(0x76)

class BMP280:
    def __init__(self, i2c, addr=BMP280_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr
        self._load_calibration()
        self._write(0xF4, 0x27)
        self._write(0xF5, 0xA0)

    def _read(self, reg, nbytes=1):
        return self.i2c.readfrom_mem(self.addr, reg, nbytes)

    def _write(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def _load_calibration(self):
        calib = self._read(0x88, 24)
        self.dig_T1 = calib[1] << 8 | calib[0]
        self.dig_T2 = calib[3] << 8 | calib[2]
        self.dig_T3 = calib[5] << 8 | calib[4]
        self.dig_P1 = calib[7] << 8 | calib[6]
        self.dig_P2 = calib[9] << 8 | calib[8]
        self.dig_P3 = calib[11] << 8 | calib[10]
        self.dig_P4 = calib[13] << 8 | calib[12]
        self.dig_P5 = calib[15] << 8 | calib[14]
        self.dig_P6 = calib[17] << 8 | calib[16]
        self.dig_P7 = calib[19] << 8 | calib[18]
        self.dig_P8 = calib[21] << 8 | calib[20]
        self.dig_P9 = calib[23] << 8 | calib[22]

    @property
    def temperature(self):
        raw = self._read(0xFA, 3)
        adc_T = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        var1 = (((adc_T >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_T >> 4) - self.dig_T1) * ((adc_T >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        return ((self.t_fine * 5 + 128) >> 8) / 100

    @property
    def pressure(self):
        raw = self._read(0xF7, 3)
        adc_P = (raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4)
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0
        p = 1048576 - adc_P
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        return p / 256
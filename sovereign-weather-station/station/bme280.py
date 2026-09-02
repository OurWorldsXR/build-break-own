"""Bosch BME280 over I2C, compensation straight from the datasheet.

Written out in full rather than pulled from a library. A student can open this
file and follow every step from raw register to degrees C.
"""
import time
from ctypes import c_short, c_byte

CHIP_BME280 = 0x60   # what a real BME280 reports
CHIP_BMP280 = 0x58   # a BMP280: same package, same pins, no humidity sensor
REG_ID, REG_CTRL_HUM = 0xD0, 0xF2
REG_STATUS, REG_CTRL_MEAS, REG_DATA = 0xF3, 0xF4, 0xF7


def _s16(b0, b1): return c_short((b1 << 8) | b0).value
def _u16(b0, b1): return (b1 << 8) | b0


class BME280:
    def __init__(self, bus, addr=0x76):
        self.bus, self.addr = bus, addr
        self.chip_id = bus.read_byte_data(addr, REG_ID)
        if self.chip_id not in (CHIP_BME280, CHIP_BMP280):
            raise OSError("nothing that looks like a BME280 at 0x%02X (id 0x%02X)"
                          % (addr, self.chip_id))
        self.has_humidity = (self.chip_id == CHIP_BME280)
        self._calibrate()

    def _calibrate(self):
        b = self.bus.read_i2c_block_data(self.addr, 0x88, 24)
        self.T = [_u16(b[0], b[1]), _s16(b[2], b[3]), _s16(b[4], b[5])]
        self.P = [_u16(b[6], b[7])] + [_s16(b[i], b[i + 1]) for i in range(8, 24, 2)]
        if self.has_humidity:
            self.H1 = self.bus.read_byte_data(self.addr, 0xA1)
            e = self.bus.read_i2c_block_data(self.addr, 0xE1, 7)
            self.H2 = _s16(e[0], e[1]); self.H3 = e[2]
            self.H4 = (c_byte(e[3]).value << 4) | (e[4] & 0x0F)
            self.H5 = (c_byte(e[5]).value << 4) | (e[4] >> 4)
            self.H6 = c_byte(e[6]).value

    def read(self):
        """(temperature C, pressure hPa, humidity %). Humidity is None on a BMP280."""
        if self.has_humidity:
            self.bus.write_byte_data(self.addr, REG_CTRL_HUM, 0x01)
        self.bus.write_byte_data(self.addr, REG_CTRL_MEAS, 0x25)   # t,p x1, forced mode
        time.sleep(0.05)
        while self.bus.read_byte_data(self.addr, REG_STATUS) & 0x08:
            time.sleep(0.005)
        d = self.bus.read_i2c_block_data(self.addr, REG_DATA, 8)
        raw_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        raw_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        raw_h = (d[6] << 8) | d[7]

        v1 = (raw_t / 16384.0 - self.T[0] / 1024.0) * self.T[1]
        v2 = ((raw_t / 131072.0 - self.T[0] / 8192.0) ** 2) * self.T[2]
        t_fine = v1 + v2
        temperature = t_fine / 5120.0

        v1 = t_fine / 2.0 - 64000.0
        v2 = v1 * v1 * self.P[5] / 32768.0 + v1 * self.P[4] * 2.0
        v2 = v2 / 4.0 + self.P[3] * 65536.0
        v1 = (self.P[2] * v1 * v1 / 524288.0 + self.P[1] * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self.P[0]
        if v1 == 0:
            pressure = 0.0
        else:
            p = ((1048576.0 - raw_p) - v2 / 4096.0) * 6250.0 / v1
            p += (self.P[8] * p * p / 2147483648.0
                  + p * self.P[7] / 32768.0 + self.P[6]) / 16.0
            pressure = p / 100.0

        humidity = None
        if self.has_humidity:
            h = t_fine - 76800.0
            h = (raw_h - (self.H4 * 64.0 + self.H5 / 16384.0 * h)) * (
                self.H2 / 65536.0 * (1.0 + self.H6 / 67108864.0 * h *
                (1.0 + self.H3 / 67108864.0 * h)))
            h = h * (1.0 - self.H1 * h / 524288.0)
            humidity = max(0.0, min(100.0, h))
        return temperature, pressure, humidity

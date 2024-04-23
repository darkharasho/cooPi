import time
import math
import smbus
from lib import cfg


class PCA9685:
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        self.dev_addr = 0x7f
        self.write_reg(cfg.MODE1, 0x00)

    def write_reg(self, reg, value):
        self.i2c.write_byte_data(self.dev_addr, reg, value)

    def read_reg(self, reg):
        res = self.i2c.read_byte_data(self.dev_addr, reg)
        return res

    def setPWMFreq(self, freq):
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self.read_reg(cfg.MODE1)
        print('lodmode:', oldmode)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write_reg(cfg.MODE1, newmode)  # go to sleep
        self.write_reg(PRESCALE, int(math.floor(prescale)))
        self.write_reg(cfg.MODE1, oldmode)
        time.sleep(0.005)
        self.write_reg(cfg.MODE1, oldmode | 0x80)  # 0x80

    def setPWM(self, ch, on, off):
        self.write_reg(cfg.LED0_ON_L + 4 * ch, on & 0xFF)
        self.write_reg(cfg.LED0_ON_H + 4 * ch, on >> 8)
        self.write_reg(cfg.LED0_OFF_L + 4 * ch, off & 0xFF)
        self.write_reg(cfg.LED0_OFF_H + 4 * ch, off >> 8)

    def setServoPulse(self, channel, pulse):
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ,the period is 20000us=20ms
        self.setPWM(channel, 0, int(pulse))

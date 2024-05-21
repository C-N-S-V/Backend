import smbus

# MPU9250 레지스터 주소 정의
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40

class MPU9250:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address

    def read_byte(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word(self, reg):
        high = self.read_byte(reg)
        low = self.read_byte(reg + 1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, reg):
        val = self.read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def read_accel(self):
        accel_x = self.read_word_2c(ACCEL_XOUT_H)
        accel_y = self.read_word_2c(ACCEL_YOUT_H)
        accel_z = self.read_word_2c(ACCEL_ZOUT_H)
        return accel_x, accel_y, accel_z

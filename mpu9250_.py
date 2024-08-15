# import해서 사용할 클래스 및 함수를 정의하는 파일입니다.

PWR_MGM_1 = 0x6b

# 가속도 센서 & 자이로 센서의 레지스터의 주소
ACCL_XOUT_L = 0X3c
ACCL_YOUT_H = 0X3d
ACCL_YOUT_L = 0X3e
ACCL_ZOUT_H = 0X3f
ACCL_ZOUT_L = 0X40

GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48


class MPU9250:
    # I2C 통신 설정
    def __init__(self, bus, address = 0x68): # 기본 접속 주소가 0x68
        self.bus = bus
        self.address = address
        self._writeByte(PWR_MGM_1, 0x00)

    # 자이로 센서 값 읽기
    def read_gyro(self):
        GyX = self._readByte(GYRO_XOUT_H) << 8
        GyX |= self._readByte(GYRO_XOUT_L)
        GyY = self._readByte(GYRO_YOUT_H) << 8
        GyY |= self._readByte(GYRO_YOUT_L)
        GyZ = self._readByte(GYRO_ZOUT_H) << 8
        GyZ |= self._readByte(GYRO_ZOUT_L)

        # 음의 방향 처리
        if(GyX >= 0x8000):
            GyX = -((65535 - GyX) + 1)
        if(GyY >= 0x8000):
            GyY = -((65535 - GyY) + 1)
        if(GyZ >= 0x8000):
            GyZ = -((65535 - GyZ) + 1)

        return GyX, GyY, GyZ
    
    # 가속도 값 읽기
    def read_accel(self):
        AcX = self._readByte(ACCL_XOUT_H) << 8
        AcX |= self._readByte(ACCL_XOUT_L)
        AcY = self._readByte(ACCLZYOUT_H) << 8
        AcY |= self._readByte(ACCL_YOUT_L)
        AcZ = self._readByte(ACCL_ZOUT_H) << 8
        AcZ |= self._readByte(ACCL_ZOUT_L)

        # 음의 방향 처리
        if(AcX >= 0x8000):
            AcX = -((65535 - AcX) + 1)
        if(AcY >= 0x8000):
            AcY = -((65535 - AcY) + 1)
        if(AcZ >= 0x8000):
            AcZ = -((65535 - AcZ) + 1)

        return AcX, AcY, AcZ
    
    # 데이터 값 쓰기
    def _writeByte(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)
    
    # 데이터 값 읽기
    def _readByte(self, reg):
        value = self.bus.read_byte_data(self.address, reg)
        return value

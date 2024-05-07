import smbus
import mpu9250 # 위에서 만든 코드를 import 해옵니다. 같은 경로에 위치하면 됩니다.
from datatime import datetime

# i2c 설정.
# I2C 1번 bus를 엽니다. SDA1, SCL1이라 써져있는 핀을 사용하므로 1번 bus입니다.
i2c_bus = smbus.SMBus(1) # 1번 버스에 대한 handle 역할을 합니다.
mpu9250 = mpu9250.MPU9250(i2c_bus, 0x68) # 0x68 : imu 통신 주소

cnt_loop = 0 # 자이로센서 보정 변수
GyXSum = 0
GyXOff = 0.0
nSample = 1024
t_prev = 0 # 시간 측정 변수
AngleX = 0.0 # 결과 값

try:
    while True:
        GyX, _, _ = mpu9250.read_gyro() # X 값만 받고 나머지는 버립니다.

        # 아래는 자이로 센서값을 보정해주는 과정
        if nSample > 0: # 1024번 자이로 센서값을 받고 이를 평균낸다.
            GyXSum += GyX
            nSample -= 1
            if nSample == 0:
                GyXOff = GyXSum / 1024
            continue

        GyXD = GyX - GyXOff # 자이로센서 값을 기존 평균 값으로 뺀다 = 전의 값을 reference state로 둔다 = 오차가 줄어든다.
        GyXR = GyXD / 131 # 현재 자이로 센서가 디폴트로 설정되어있다. 1도당 131값을 출력하도록

        # 시간 측정
        t_now = datetime.now().microsecond
        dt_n = t_now - t_prev
        t_prev = t_now
        dt = dt_n / 1000000

        # 회전량 결과 값 누적하기
        AngleX += GyXR* dt
        cnt_loop += 1

        # 50번 누적했으면 출력
        if cnt_loop % 50 != 0:
            continue
        print("AngleX = %.2f" %AngleX)

except KeyboardInterrupt:
    pass
i2c_bus.close()

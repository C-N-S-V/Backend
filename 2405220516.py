import smbus
import mpu9250  # MPU9250 모듈 import
from datetime import datetime
from flask import Flask, request
import time

app = Flask(__name__)

def calibrate_sensor(mpu, samples=1024):
    # 각 축에 대한 초기 합계를 0으로 설정
    x_sum = y_sum = z_sum = 0
    for _ in range(samples):
        gx, gy, gz = mpu.read_gyro()
        x_sum += gx
        y_sum += gy
        z_sum += gz
        time.sleep(0.01)  # 각 샘플링 사이에 짧은 지연

    # 측정된 샘플들의 평균으로 오프셋 계산
    return x_sum / samples, y_sum / samples, z_sum / samples

@app.route('/data', methods=['POST'])
def data():
    # I2C setup
    i2c_bus = smbus.SMBus(1)  # SDA1 and SCL1 pins, so bus 1
    mpu9250_1 = mpu9250.MPU9250(i2c_bus, 0x68)  # 첫 번째 센서 IMU communication address
    mpu9250_2 = mpu9250.MPU9250(i2c_bus, 0x69)  # 두 번째 센서

    # 센서 보정
    GyX_1_Off, GyY_1_Off, GyZ_1_Off = calibrate_sensor(mpu9250_1)
    GyX_2_Off, GyY_2_Off, GyZ_2_Off = calibrate_sensor(mpu9250_2)

    # 각도 변수 초기화
    AngleX = AngleY = AngleZ = 0.0
    AngleX_2 = AngleY_2 = AngleZ_2 = 0.0

    try:
        while True:
            t_prev = datetime.now().timestamp()
            time.sleep(15)  # Delay for 15 seconds

            GyX_1, GyY_1, GyZ_1 = mpu9250_1.read_gyro()
            GyX_2, GyY_2, GyZ_2 = mpu9250_2.read_gyro()

            # 오프셋 보정
            GyX_1 -= GyX_1_Off
            GyY_1 -= GyY_1_Off
            GyZ_1 -= GyZ_1_Off
            GyX_2 -= GyX_2_Off
            GyY_2 -= GyY_2_Off
            GyZ_2 -= GyZ_2_Off

            # Time tracking
            t_now = datetime.now().timestamp()
            dt = t_now - t_prev
            t_prev = t_now

            # 각도 누적
            AngleX += GyX_1 * dt
            AngleY += GyY_1 * dt
            AngleZ += GyZ_1 * dt
            AngleX_2 += GyX_2 * dt
            AngleY_2 += GyY_2 * dt
            AngleZ_2 += GyZ_2 * dt

            # Calculate averages and check condition
            AvgX = (AngleX + AngleX_2) / 2
            AvgY = (AngleY + AngleY_2) / 2
            AvgZ = (AngleZ + AngleZ_2) / 2
            total_average = abs(AvgX) + abs(AvgY) + abs(AvgZ)

            if total_average > 3:
                return "1"
            else:
                return "0"

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

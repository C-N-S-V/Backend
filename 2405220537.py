import smbus
import mpu9250  # MPU9250 모듈 import
from datetime import datetime
from flask import Flask, request
import time

app = Flask(__name__)

def calibrate_sensor(mpu, samples=1024):
    z_sum = 0
    for _ in range(samples):
        _, _, gz = mpu.read_gyro()
        z_sum += gz
        time.sleep(0.01)  # 각 샘플링 사이에 짧은 지연

    return z_sum / samples  # 측정된 샘플들의 평균으로 오프셋 계산

@app.route('/data', methods=['POST'])
def data():
    i2c_bus = smbus.SMBus(1)  # I2C setup
    mpu9250_1 = mpu9250.MPU9250(i2c_bus, 0x68)  # 첫 번째 센서 IMU communication address
    mpu9250_2 = mpu9250.MPU9250(i2c_bus, 0x69)  # 두 번째 센서

    GyZ_1_Off = calibrate_sensor(mpu9250_1)  # 센서 보정
    GyZ_2_Off = calibrate_sensor(mpu9250_2)

    AngleZ = AngleZ_2 = 0.0  # 각도 변수 초기화

    try:
        while True:
            t_prev = datetime.now().timestamp()
            time.sleep(15)  # Delay for 15 seconds

            _, _, GyZ_1 = mpu9250_1.read_gyro()
            _, _, GyZ_2 = mpu9250_2.read_gyro()

            GyZ_1 -= GyZ_1_Off  # 오프셋 보정
            GyZ_2 -= GyZ_2_Off

            t_now = datetime.now().timestamp()  # Time tracking
            dt = t_now - t_prev
            t_prev = t_now

            AngleZ += GyZ_1 * dt  # 각도 누적
            AngleZ_2 += GyZ_2 * dt

            AvgZ = (AngleZ + AngleZ_2) / 2  # Calculate averages and check condition
            if abs(AvgZ) > 1.5:
                return "1"
            else:
                return "0"

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
